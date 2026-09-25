"""P123 local-only Qwen3 LoRA model and training-only morphology head.

Pinned interface: transformers 4.57.6 / peft 0.18.1. No tokenizer replacement,
downloads, chat template or auxiliary feature inputs. Targets are already shifted:
hidden at t predicts labels[t], not labels[t+1].
"""
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.checkpoint import checkpoint
import peft
import transformers
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, Qwen3Config, Qwen3ForCausalLM

EXPECTED_VERSIONS = {"transformers": "4.57.6", "peft": "0.18.1"}


def verify_versions():
    actual = {"transformers": transformers.__version__, "peft": peft.__version__}
    if actual != EXPECTED_VERSIONS:
        raise RuntimeError(f"P123 dependency mismatch: {actual} != {EXPECTED_VERSIONS}")
    return actual


class MorphTeacherLM(nn.Module):
    def __init__(self, peft_model, aux_labels, seed):
        super().__init__()
        self.peft_model = peft_model
        self.config = peft_model.get_base_model().config
        self.aux_labels = int(aux_labels)
        self.seed = int(seed)
        if self.aux_labels <= 0:
            raise ValueError("aux_labels must be positive")
        self.aux_head = nn.Linear(self.config.hidden_size, self.aux_labels,
                                  dtype=torch.float32)
        nn.init.normal_(self.aux_head.weight, std=0.02)
        nn.init.zeros_(self.aux_head.bias)
        self.aux_head.to(next(peft_model.parameters()).device)
        self.assert_parameter_contract()

    @property
    def causal_model(self):
        # For ordinary LoRA the injected modules remain active through this
        # public accessor. Prompt/adaption/activated LoRA are not supported.
        return self.peft_model.get_base_model()

    @property
    def output_layer(self):
        return self.causal_model.get_output_embeddings()

    def assert_parameter_contract(self):
        for name, parameter in self.peft_model.named_parameters():
            expected = ".lora_A." in name or ".lora_B." in name
            if parameter.requires_grad != expected:
                raise AssertionError(f"Unexpected trainability: {name}")
            if expected and parameter.dtype != torch.float32:
                raise AssertionError(f"LoRA must be FP32: {name}")
        if any(not p.requires_grad or p.dtype != torch.float32
               for p in self.aux_head.parameters()):
            raise AssertionError("Auxiliary head must be trainable FP32")
        if self.config.tie_word_embeddings:
            assert (self.causal_model.get_input_embeddings().weight
                    is self.output_layer.weight)

    def parameter_counts(self):
        lora = sum(p.numel() for p in self.peft_model.parameters() if p.requires_grad)
        auxiliary = sum(p.numel() for p in self.aux_head.parameters())
        frozen = sum(p.numel() for p in self.peft_model.parameters() if not p.requires_grad)
        return {"frozen_base": frozen, "lora": lora, "auxiliary": auxiliary,
                "trainable": lora + auxiliary, "total": frozen + lora + auxiliary}

    def hidden_states(self, input_ids, attention_mask):
        if input_ids.ndim != 2 or input_ids.dtype != torch.long:
            raise ValueError("input_ids must be int64 [B,T]")
        if attention_mask is None or attention_mask.shape != input_ids.shape:
            raise ValueError("Explicit attention_mask [B,T] is required")
        if input_ids.shape[0] == 0 or input_ids.shape[1] == 0:
            raise ValueError("Empty input shape")
        visible = attention_mask.to(device=input_ids.device, dtype=torch.bool)
        # EOS, BOS and PAD may share an ID. Only explicit mask selects padding.
        positions = (visible.long().cumsum(-1) - 1).clamp_min(0)
        output = self.causal_model.model(
            input_ids=input_ids, attention_mask=visible, position_ids=positions,
            use_cache=False, return_dict=True,
        )
        return output.last_hidden_state.masked_fill(~visible.unsqueeze(-1), 0)

    def forward(self, input_ids, attention_mask):
        """Return hidden states only. Teacher labels are never model inputs."""
        return self.hidden_states(input_ids, attention_mask)

    def _chunk_ce(self, states, labels):
        # Head remains in the frozen base dtype; reduction is always FP32.
        logits = self.output_layer(states)
        return F.cross_entropy(logits.float(), labels, reduction="sum")

    def loss_terms(self, hidden, labels, aux_targets=None, aux_mask=None,
                   ce_chunk_size=64, checkpoint_ce=True):
        if hidden.ndim != 3 or labels.shape != hidden.shape[:2]:
            raise ValueError("hidden/labels shape mismatch")
        if labels.dtype != torch.long or ce_chunk_size <= 0:
            raise ValueError("int64 labels and positive CE chunk size required")
        flat_h = hidden.reshape(-1, hidden.shape[-1])
        flat_y = labels.reshape(-1)
        valid = flat_y.ne(-100)
        chosen_h, chosen_y = flat_h[valid], flat_y[valid]
        ce_count = valid.sum()
        ce_sum = hidden.float().sum() * 0.0
        for start in range(0, chosen_y.numel(), ce_chunk_size):
            h = chosen_h[start:start + ce_chunk_size]
            y = chosen_y[start:start + ce_chunk_size]
            if checkpoint_ce and torch.is_grad_enabled() and h.requires_grad:
                # Plain chunking retains every softmax graph until backward.
                # Non-reentrant checkpointing recomputes one chunk's logits.
                value = checkpoint(self._chunk_ce, h, y, use_reentrant=False)
            else:
                value = self._chunk_ce(h, y)
            ce_sum = ce_sum + value
        if aux_targets is None:
            if aux_mask is not None:
                raise ValueError("aux_mask without auxiliary targets")
            selected_h = flat_h[:0].float()
            aux_sum = self.aux_head(selected_h).sum() * 0
            aux_rows = torch.zeros((), dtype=torch.long, device=hidden.device)
        else:
            if aux_targets.shape != (*labels.shape, self.aux_labels):
                raise ValueError("aux_targets must be [B,T,K]")
            if aux_mask is None or aux_mask.shape != labels.shape:
                raise ValueError("aux_mask must be [B,T]")
            selected = aux_mask.to(device=hidden.device, dtype=torch.bool)
            logits = self.aux_head(hidden[selected].float())
            targets = aux_targets[selected].float()
            aux_sum = F.binary_cross_entropy_with_logits(logits, targets, reduction="sum")
            aux_rows = selected.sum()
        aux_count = aux_rows * self.aux_labels
        return {"ce_sum": ce_sum, "ce_count": ce_count,
                "ce_mean": ce_sum / ce_count.clamp_min(1),
                "aux_sum": aux_sum, "aux_rows": aux_rows, "aux_count": aux_count,
                "aux_mean": aux_sum / aux_count.clamp_min(1)}

    @torch.no_grad()
    def token_scores(self, hidden, labels, chunk_size=64):
        """Per-position CE/top1 for evaluation; auxiliary head is never called."""
        if labels.shape != hidden.shape[:2] or chunk_size <= 0:
            raise ValueError("Invalid scoring shapes/chunk size")
        flat_h = hidden.reshape(-1, hidden.shape[-1])
        flat_y = labels.reshape(-1)
        indices = flat_y.ne(-100).nonzero(as_tuple=False).flatten()
        nll = torch.zeros(flat_y.shape, dtype=torch.float32, device=hidden.device)
        correct = torch.zeros(flat_y.shape, dtype=torch.bool, device=hidden.device)
        for start in range(0, indices.numel(), chunk_size):
            selected = indices[start:start + chunk_size]
            logits = self.output_layer(flat_h[selected])
            nll[selected] = F.cross_entropy(logits.float(), flat_y[selected], reduction="none")
            correct[selected] = logits.argmax(-1).eq(flat_y[selected])
        return {"nll": nll.reshape(labels.shape), "correct": correct.reshape(labels.shape),
                "valid": labels.ne(-100)}

    def trainable_state_dict(self):
        return {name: p.detach().cpu().clone()
                for name, p in self.named_parameters() if p.requires_grad}

    def load_trainable_state_dict(self, state):
        current = {name: p for name, p in self.named_parameters() if p.requires_grad}
        if set(current) != set(state):
            raise ValueError("Trainable checkpoint keys mismatch")
        with torch.no_grad():
            for name, parameter in current.items():
                if state[name].shape != parameter.shape or state[name].dtype != torch.float32:
                    raise ValueError(f"Trainable checkpoint shape/dtype mismatch: {name}")
                if not torch.isfinite(state[name]).all():
                    raise ValueError(f"Nonfinite trainable checkpoint: {name}")
                parameter.copy_(state[name].to(parameter.device))
        self.assert_parameter_contract()


def wrap_base(base, seed, aux_labels=90, gradient_checkpointing=True):
    """Attach identical q/v LoRA plus auxiliary head to a caller-owned base."""
    verify_versions()
    if base.config.model_type != "qwen3":
        raise ValueError("This controlled implementation supports Qwen3 only")
    torch.manual_seed(seed)
    base.config.use_cache = False
    base.requires_grad_(False)
    if gradient_checkpointing:
        base.gradient_checkpointing_enable(
            gradient_checkpointing_kwargs={"use_reentrant": False}
        )
    lora = LoraConfig(task_type=TaskType.CAUSAL_LM, r=8, lora_alpha=16,
                      lora_dropout=0.0, target_modules=["q_proj", "v_proj"],
                      bias="none", init_lora_weights=True)
    adapted = get_peft_model(base, lora, autocast_adapter_dtype=True)
    # Assert rather than rely solely on PEFT's current default promotion.
    for name, parameter in adapted.named_parameters():
        if parameter.requires_grad:
            parameter.data = parameter.data.float()
    return MorphTeacherLM(adapted, aux_labels, seed)


def load_pretrained(local_model_path, seed, aux_labels=90, device="cuda",
                    dtype=torch.bfloat16, gradient_checkpointing=True):
    """Load only a pre-downloaded local snapshot. Network/code execution disabled."""
    verify_versions()
    path = Path(local_model_path).resolve()
    if not path.is_dir() or not (path / "config.json").is_file():
        raise FileNotFoundError(path)
    if torch.device(device).type == "cuda" and dtype == torch.bfloat16:
        if not torch.cuda.is_bf16_supported():
            raise RuntimeError("Declared BF16 compute unavailable")
    base = AutoModelForCausalLM.from_pretrained(
        str(path), local_files_only=True, trust_remote_code=False,
        dtype=dtype, low_cpu_mem_usage=True,
        device_map={"": str(device)}, attn_implementation="sdpa",
    )
    result = wrap_base(base, seed, aux_labels, gradient_checkpointing)
    result.assert_parameter_contract()
    return result


def tiny_model(seed=12317, aux_labels=7, device="cpu", gradient_checkpointing=False):
    """Real HF Qwen3 architecture from a tiny random config; no downloads."""
    verify_versions()
    torch.manual_seed(seed)
    config = Qwen3Config(
        vocab_size=47, hidden_size=32, intermediate_size=64,
        num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2,
        head_dim=8, max_position_embeddings=32,
        bos_token_id=46, eos_token_id=46, pad_token_id=46,
        attention_dropout=0.0, tie_word_embeddings=True, use_cache=False,
    )
    config._attn_implementation = "sdpa"
    base = Qwen3ForCausalLM(config).to(device=device, dtype=torch.float32)
    return wrap_base(base, seed, aux_labels, gradient_checkpointing)
