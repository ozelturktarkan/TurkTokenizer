#!/usr/bin/env python3
"""TurkTokenizer v6.0 R2: source-first contextual filtering over locked A1.

R2 starts from a fresh random initialization and retains A1's contextual
top-20 morphology posterior.  It adds a separately supervised source-token
filter for the three direct relation families, numerically safe masked
posteriors/evidence summaries, and source-level hard-negative penalties.

Only TRAIN and CALIB are available to this screen.  INTERNAL_VAL, external
holdouts, and official test splits are never opened by this program.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F


BASE = Path(__file__).resolve().parent
A1_SOURCE = BASE / "TurkTokenizer_v5_11_v4_1_A1_train.py"
VARIANT = "R2_A1_source_first_contextual_filter"
DIRECT_FAMILIES = ("POSS_HEAD", "OBJECT", "PARTICIPLE_HEAD")
SOURCE_FAMILY_WEIGHTS = {
    "POSS_HEAD": 1.15,
    "OBJECT": 1.40,
    "PARTICIPLE_HEAD": 1.15,
}
HARDNEG_SOURCE_WEIGHTS = {
    "POSS_HEAD": 1.25,
    "OBJECT": 1.50,
    "PARTICIPLE_HEAD": 1.25,
}


def load_a1():
    spec = importlib.util.spec_from_file_location("v511_v4_1_a1_for_v6_r2", A1_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import locked A1 source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


a1 = load_a1()
v4 = a1.v4


@dataclass(frozen=True)
class R2Config(a1.A1Config):
    # Patience is a lower bound of five for every stage.  Epoch budgets are
    # extended so the five-epoch window remains meaningful near old maxima.
    syntax_epochs: int = 20
    relation_epochs: int = 30
    hardnegative_epochs: int = 10
    patience_syntax: int = 5
    patience_relation: int = 5
    patience_hardnegative: int = 5
    early_stop_min_delta: float = 1e-4
    source_filter_projection_dim: int = 32
    source_filter_hidden: int = 192
    source_filter_loss_weight: float = 0.35
    source_filter_gate_initial_logit: float = -2.0
    source_hardnegative_penalty: float = 0.25
    safe_probability_epsilon: float = 1e-8


CFG = R2Config()
a1.CFG = CFG
v4.CFG = CFG

R2_MODEL_DIR = BASE / "v600_R2_models"
R2_MODEL_DIR.mkdir(exist_ok=True)
v4.MODEL_DIR = R2_MODEL_DIR
v4.BEST_SYNTAX = R2_MODEL_DIR / "v600_R2_best_syntax.pt"
v4.BEST_RELATION = R2_MODEL_DIR / "v600_R2_best_relation.pt"
v4.BEST_HARDNEG = R2_MODEL_DIR / "v600_R2_best_hardnegative.pt"
v4.FROZEN_CHECKPOINT = R2_MODEL_DIR / "v600_R2_frozen.pt"
v4.CALIBRATION_FILE = R2_MODEL_DIR / "v600_R2_calibration.json"
v4.CALIB_AUDIT = BASE / "TurkTokenizer_v6_0_R2_CALIB_Audit.json"
v4.CALIB_GATE = BASE / "TurkTokenizer_v6_0_R2_CALIB_Gate.json"
v4.TRAIN_LOG = BASE / "TurkTokenizer_v6_0_R2_train.log"
R2_SCREEN_RESULT = BASE / "TurkTokenizer_v6_0_R2_Screen_Result.json"
R2_SMOKE_REPORT = BASE / "TurkTokenizer_v6_0_R2_Smoke_Report.json"

A1_BASELINE = {
    "macro_relation_f1": 0.8107563337851816,
    "minimum_family_f1": 0.7174066243833686,
    "UAS": 0.8785155899002606,
    "LAS": 0.7599065504537694,
    "families": {
        "POSS_HEAD": 0.8189910979228486,
        "OBJECT": 0.7174066243833686,
        "PARTICIPLE_HEAD": 0.8374384236453202,
        "CASE_GOVERNOR": 0.8691891891891892,
    },
}
R1_BASELINE = {
    "macro_relation_f1": 0.8078271460408145,
    "minimum_family_f1": 0.7137834036568215,
    "UAS": 0.883053284212418,
    "LAS": 0.7643094617665559,
    "families": {
        "POSS_HEAD": 0.8123138033763654,
        "OBJECT": 0.7137834036568215,
        "PARTICIPLE_HEAD": 0.8231827111984283,
        "CASE_GOVERNOR": 0.8820286659316428,
    },
}


def safe_masked_softmax(scores: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """Softmax with exact zero mass for invalid or entirely empty rows."""
    work = scores.float()
    valid_row = mask.any(-1, keepdim=True)
    masked = work.masked_fill(~mask, -torch.inf)
    masked = torch.where(valid_row, masked, torch.zeros_like(masked))
    probability = F.softmax(masked, -1) * mask.float()
    denominator = probability.sum(-1, keepdim=True).clamp_min(
        CFG.safe_probability_epsilon
    )
    probability = torch.where(
        valid_row, probability / denominator, torch.zeros_like(probability)
    )
    return probability.to(scores.dtype)


def safe_evidence_summary(
    logits: torch.Tensor, pair_mask: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return max and log-mean-exp over valid heads without mask sentinels."""
    work = logits.float().masked_fill(~pair_mask, -torch.inf)
    valid_count = pair_mask.sum(-1)
    has_head = valid_count > 0
    maximum = work.amax(-1)
    logmean = torch.logsumexp(work, -1) - valid_count.clamp_min(1).float().log()
    maximum = torch.where(has_head, maximum, torch.zeros_like(maximum))
    logmean = torch.where(has_head, logmean, torch.zeros_like(logmean))
    return maximum.to(logits.dtype), logmean.to(logits.dtype)


class R2Model(a1.A1Model):
    """A1 plus a direct-family source candidate filter."""

    def __init__(self, resources):
        super().__init__(resources)
        projection = CFG.source_filter_projection_dim
        self.source_upos_projection = nn.Linear(len(resources.upos), projection)
        self.source_deprel_projection = nn.Linear(len(resources.deprel), projection)
        self.source_udfeat_projection = nn.Linear(len(resources.udfeat), projection)
        source_input = 3 * CFG.hidden + 3 * projection
        self.source_filter = nn.ModuleDict({
            family: nn.Sequential(
                nn.LayerNorm(source_input),
                nn.Linear(source_input, CFG.source_filter_hidden),
                nn.GELU(),
                nn.Dropout(CFG.dropout),
                nn.Linear(CFG.source_filter_hidden, 1),
            )
            for family in DIRECT_FAMILIES
        })
        self.source_filter_gate = nn.ParameterDict({
            family: nn.Parameter(torch.tensor(CFG.source_filter_gate_initial_logit))
            for family in DIRECT_FAMILIES
        })

    @staticmethod
    def posterior(scores, mask):
        return safe_masked_softmax(scores, mask)

    def forward(self, batch):
        output = super().forward(batch)
        mask = batch["mask"]
        tokens = mask.shape[1]
        eye = torch.eye(tokens, dtype=torch.bool, device=mask.device).unsqueeze(0)
        pair_mask = mask.unsqueeze(2) & mask.unsqueeze(1) & ~eye

        # Reconstruct the contextual morphology state exposed to the source
        # filter.  This does not alter A1's syntax or head-scoring paths.
        candidates = self.candidate_representations(batch)
        refined_morph = (
            output["morph_context_attention"].unsqueeze(-1) * candidates
        ).sum(2)
        morph_hidden = self.morph_to_hidden(refined_morph) * mask.unsqueeze(-1)
        upos = F.gelu(self.source_upos_projection(F.softmax(output["upos"], -1)))
        deprel = F.gelu(
            self.source_deprel_projection(F.softmax(output["deprel_parent"], -1))
        )
        udfeat = F.gelu(self.source_udfeat_projection(torch.sigmoid(output["udfeat"])))
        source_context = torch.cat([
            output["relation_encoded"], output["graph"], morph_hidden,
            upos, deprel, udfeat,
        ], -1)

        output["a1_source_logits"] = {
            family: output["source_logits"][family].clone()
            for family in DIRECT_FAMILIES
        }
        output["source_base_logits"] = {}
        output["source_filter_logits"] = {}
        output["source_filter_gates"] = {}
        for family in DIRECT_FAMILIES:
            maximum, logmean = safe_evidence_summary(
                output["head_logits"][family], pair_mask
            )
            base_source = self.source_joint[family](torch.cat([
                output["graph"], maximum.unsqueeze(-1), logmean.unsqueeze(-1)
            ], -1)).squeeze(-1)
            filter_logit = self.source_filter[family](source_context).squeeze(-1)
            gate = torch.sigmoid(self.source_filter_gate[family])
            combined = base_source + gate * filter_logit
            output["source_base_logits"][family] = torch.where(
                mask, base_source, torch.zeros_like(base_source)
            )
            output["source_filter_logits"][family] = torch.where(
                mask, filter_logit, torch.zeros_like(filter_logit)
            )
            output["source_filter_gates"][family] = gate
            output["source_logits"][family] = torch.where(
                mask, combined, torch.zeros_like(combined)
            )

        # No downstream loss or metric consumes the retained 4-expert stack.
        # Releasing it here reduces persistent forward-output memory without
        # changing any fused logits or fusion diagnostics.
        output["experts"].clear()
        return output


BASE_RELATION_LOSS = a1.a1_relation_loss


def r2_relation_loss(output, batch, consensus, train_mode, hardneg=None):
    total = BASE_RELATION_LOSS(output, batch, consensus, train_mode, hardneg)
    if not train_mode:
        return total

    mask = batch["mask"]
    source, uncertainty, _, _ = v4.relation_targets(
        batch, consensus, train_mode, output["encoded"].device
    )
    weighted_auxiliary = output["encoded"].sum() * 0.0
    weight_total = 0.0
    for family in DIRECT_FAMILIES:
        family_weight = SOURCE_FAMILY_WEIGHTS[family]
        weighted_auxiliary = weighted_auxiliary + family_weight * v4.balanced_focal(
            output["source_filter_logits"][family], source[family], mask,
            uncertainty[family], CFG.source_gamma, CFG.source_pos_share,
        )
        weight_total += family_weight
    total = total + CFG.source_filter_loss_weight * weighted_auxiliary / weight_total

    # Edge hard negatives with a genuinely negative source teach the prefilter
    # to reject the token.  Wrong-head negatives from a gold source are not
    # allowed to suppress the correct source token.
    if hardneg:
        penalties = []
        for batch_index, sid in enumerate(batch["sids"]):
            for family, source_index, _ in hardneg.get(sid, ()):
                if (family in DIRECT_FAMILIES
                        and source_index < mask.shape[1]
                        and source[family][batch_index, source_index] < 0.5):
                    penalties.append(
                        HARDNEG_SOURCE_WEIGHTS[family]
                        * F.softplus(output["source_filter_logits"][family][
                            batch_index, source_index
                        ])
                    )
        if penalties:
            total = total + CFG.source_hardnegative_penalty * torch.stack(penalties).mean()
    return total


v4.V4Model = R2Model
v4.relation_loss = r2_relation_loss
a1.A1Model = R2Model


def screen_decision(relation_metrics, syntax_metrics):
    gains = {
        "macro_relation_f1": (
            relation_metrics["macro_f1"] - A1_BASELINE["macro_relation_f1"]
        ),
        "minimum_family_f1": (
            relation_metrics["min_family_f1"] - A1_BASELINE["minimum_family_f1"]
        ),
    }
    family_deltas = {
        family: (
            relation_metrics["families"][family]["f1"]
            - A1_BASELINE["families"][family]
        )
        for family in v4.FAMILIES
    }
    syntax_regressions = {
        "UAS": A1_BASELINE["UAS"] - syntax_metrics["UAS"],
        "LAS": A1_BASELINE["LAS"] - syntax_metrics["LAS"],
    }
    checks = {
        "macro_gain_at_least_0_01": gains["macro_relation_f1"] >= 0.01,
        "no_family_regression": all(delta >= 0.0 for delta in family_deltas.values()),
        "syntax_regression_within_0_005": all(
            regression <= 0.005 for regression in syntax_regressions.values()
        ),
    }
    keep = all(checks.values())
    return {
        "status": "KEEP_FOR_MULTI_SEED_FINALIST" if keep else "DROP_AFTER_SCREEN",
        "keep": keep,
        "requirements": {
            "macro_gain_minimum": 0.01,
            "family_regression_allowed": False,
            "maximum_UAS_or_LAS_regression": 0.005,
        },
        "gains_against_A1": gains,
        "family_deltas_against_A1": family_deltas,
        "syntax_regressions_against_A1": syntax_regressions,
        "checks": checks,
    }


@torch.no_grad()
def collect_auxiliary_metrics(model, loader, device):
    model.eval()
    morph_top1 = morph_static_top1 = supervised = 0
    compatible_mass = 0.0
    source_counts = {family: Counter() for family in DIRECT_FAMILIES}
    for batch in loader:
        v4.to_device(batch, device)
        output = model(batch)
        valid_morph = batch["mask"] & batch["morph_supervised"]
        if valid_morph.any():
            contextual_index = output["morph_context_attention"].argmax(-1)
            static_index = output["morph_static_attention"].argmax(-1)
            contextual_hit = batch["morph_compatible"].gather(
                -1, contextual_index.unsqueeze(-1)
            ).squeeze(-1)
            static_hit = batch["morph_compatible"].gather(
                -1, static_index.unsqueeze(-1)
            ).squeeze(-1)
            mass = (
                output["morph_context_attention"]
                * batch["morph_compatible"].float()
            ).sum(-1)
            count = int(valid_morph.sum())
            supervised += count
            morph_top1 += int(contextual_hit[valid_morph].sum())
            morph_static_top1 += int(static_hit[valid_morph].sum())
            compatible_mass += float(mass[valid_morph].sum())

        for batch_index, gold in enumerate(batch["goldrels"]):
            tokens = len(batch["rows"][batch_index]["tokens"])
            for family in DIRECT_FAMILIES:
                probability = torch.sigmoid(
                    output["source_filter_logits"][family][batch_index, :tokens]
                )
                for source_index, heads in enumerate(gold[family]):
                    predicted = bool(probability[source_index] >= 0.5)
                    expected = bool(heads)
                    source_counts[family][
                        "tp" if predicted and expected else
                        "fp" if predicted else
                        "fn" if expected else "tn"
                    ] += 1
    return {
        "morphology": {
            "supervised_tokens": supervised,
            "contextual_top1_compatible_recall": morph_top1 / max(1, supervised),
            "static_top1_compatible_recall": morph_static_top1 / max(1, supervised),
            "mean_contextual_compatible_mass": compatible_mass / max(1, supervised),
        },
        "source_filter_at_0_5": {
            family: v4.prf(source_counts[family]) for family in DIRECT_FAMILIES
        },
        "learned_filter_gates": {
            family: float(torch.sigmoid(model.source_filter_gate[family]).cpu())
            for family in DIRECT_FAMILIES
        },
    }


def comparison_against(baseline, relation_metrics, syntax_metrics):
    return {
        "macro_relation_f1_delta": relation_metrics["macro_f1"] - baseline["macro_relation_f1"],
        "minimum_family_f1_delta": relation_metrics["min_family_f1"] - baseline["minimum_family_f1"],
        "UAS_delta": syntax_metrics["UAS"] - baseline["UAS"],
        "LAS_delta": syntax_metrics["LAS"] - baseline["LAS"],
        "family_deltas": {
            family: relation_metrics["families"][family]["f1"] - baseline["families"][family]
            for family in v4.FAMILIES
        },
    }


def run_smoke():
    _, train_rows, _, lattice, syntax_consensus, relation_consensus, resources = (
        v4.load_train_material()
    )
    device = torch.device("cpu")
    collate = a1.a1_collate_builder(resources, lattice)
    sample = [train_rows[0], train_rows[len(train_rows) // 3], train_rows[-1]]
    batch = v4.to_device(collate(sample), device)
    model = R2Model(resources).to(device)
    output = model(batch)
    syntax = a1.a1_syntax_loss(output, batch, resources, syntax_consensus, True)
    relation = r2_relation_loss(output, batch, relation_consensus, True)
    total = syntax + relation
    total.backward()

    all_invalid_scores = torch.tensor([[1.0, -1.0]], dtype=torch.bfloat16)
    all_invalid_mask = torch.zeros_like(all_invalid_scores, dtype=torch.bool)
    all_invalid_posterior = safe_masked_softmax(all_invalid_scores, all_invalid_mask)
    finite_gradients = all(
        parameter.grad is None or torch.isfinite(parameter.grad).all()
        for parameter in model.parameters()
    )
    checks = {
        "finite_losses": bool(torch.isfinite(total).item()),
        "finite_gradients": bool(finite_gradients),
        "all_invalid_posterior_finite": bool(torch.isfinite(all_invalid_posterior).all()),
        "all_invalid_posterior_exact_zero": float(all_invalid_posterior.abs().max()) == 0.0,
        "valid_morph_posteriors_sum_to_one": bool(torch.allclose(
            output["morph_context_attention"].sum(-1)[batch["mask"]],
            torch.ones_like(output["morph_context_attention"].sum(-1)[batch["mask"]]),
            atol=1e-6, rtol=0.0,
        )),
        "direct_source_logits_finite": all(
            bool(torch.isfinite(output["source_logits"][family][batch["mask"]]).all())
            for family in DIRECT_FAMILIES
        ),
        "retained_expert_stacks_released": not output["experts"],
        "patience_minimum_five_all_stages": min(
            CFG.patience_syntax, CFG.patience_relation, CFG.patience_hardnegative
        ) >= 5,
        "internal_val_loaded": False,
        "external_holdouts_loaded": False,
    }
    status_checks = [
        value for key, value in checks.items() if not key.endswith("_loaded")
    ]
    report = {
        "status": "PASS_V6_0_R2_SMOKE" if all(status_checks) else "FAIL_V6_0_R2_SMOKE",
        "variant": VARIANT,
        "syntax_loss": float(syntax.detach()),
        "relation_loss": float(relation.detach()),
        "parameters": sum(parameter.numel() for parameter in model.parameters()),
        "config": asdict(CFG),
        "source_filter_initial_gates": {
            family: float(output["source_filter_gates"][family].detach())
            for family in DIRECT_FAMILIES
        },
        "checks": checks,
    }
    R2_SMOKE_REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] != "PASS_V6_0_R2_SMOKE":
        raise RuntimeError("R2 smoke invariants failed")


def run_screen():
    if v4.INTERNAL_SENTINEL.exists():
        raise RuntimeError(f"internal validation sentinel already exists: {v4.INTERNAL_SENTINEL}")
    audit, train_rows, calib_rows, lattice, syntax_consensus, relation_consensus, resources = (
        v4.load_train_material()
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader, train_eval_loader, calib_loader = v4.build_loaders(
        train_rows, calib_rows, resources, lattice
    )
    model = R2Model(resources).to(device)
    train_supervision = a1.supervision_audit(train_rows, lattice)
    v4.log(json.dumps({
        "event": "v6_0_R2_screen_start",
        "variant": VARIANT,
        "device": str(device),
        "seed": CFG.seed,
        "train": len(train_rows),
        "calib": len(calib_rows),
        "internal_val_sealed": audit["split_sentences"]["internal_val"],
        "a1_script_sha256": v4.sha256(A1_SOURCE),
        "r2_script_sha256": v4.sha256(Path(__file__)),
        "config": asdict(CFG),
        "train_morph_supervision": train_supervision,
    }, sort_keys=True))

    v4.train_syntax(model, train_loader, calib_loader, resources, syntax_consensus, device)
    relation_checkpoint = v4.train_relations(
        model, train_loader, calib_loader, resources, syntax_consensus,
        relation_consensus, device,
    )
    hardneg, hardneg_counts = v4.mine_hard_negatives(
        model, train_eval_loader, device, relation_checkpoint["extra"]["thresholds"]
    )
    v4.log("R2 HARDNEG mined " + json.dumps(hardneg_counts, sort_keys=True))
    final_checkpoint = v4.train_relations(
        model, train_loader, calib_loader, resources, syntax_consensus,
        relation_consensus, device, hardneg=hardneg,
    )

    records, syntax_metrics, fusion = v4.collect_predictions(model, calib_loader, device)
    thresholds, calibration_selection = v4.calibrate(records)
    relation_metrics = v4.evaluate(records, thresholds)
    auxiliary_metrics = collect_auxiliary_metrics(model, calib_loader, device)
    torch.save(final_checkpoint, v4.FROZEN_CHECKPOINT)
    calibration = {
        "variant": VARIANT,
        "thresholds": thresholds,
        "checkpoint_sha256": v4.sha256(v4.FROZEN_CHECKPOINT),
        "script_sha256": v4.sha256(Path(__file__)),
        "a1_source_sha256": v4.sha256(A1_SOURCE),
        "selected_on": "CALIB_ONLY",
        "checkpoint_stage": final_checkpoint["stage"],
        "checkpoint_epoch": final_checkpoint["epoch"],
        "internal_val_consumed": False,
    }
    v4.CALIBRATION_FILE.write_text(
        json.dumps(calibration, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    legacy_gates = {
        "macro_relation_f1": {"value": relation_metrics["macro_f1"], "minimum": 0.90},
        "minimum_family_f1": {"value": relation_metrics["min_family_f1"], "minimum": 0.87},
        "UAS": {"value": syntax_metrics["UAS"], "minimum": 0.88},
        "LAS": {"value": syntax_metrics["LAS"], "minimum": 0.80},
    }
    effective_v6_production_gates = {
        "macro_relation_f1": {"value": relation_metrics["macro_f1"], "minimum": 0.90},
        "minimum_family_f1": {"value": relation_metrics["min_family_f1"], "minimum": 0.87},
        "UAS": {"value": syntax_metrics["UAS"], "minimum": 0.93},
        "LAS": {"value": syntax_metrics["LAS"], "minimum": 0.85},
    }
    decision = screen_decision(relation_metrics, syntax_metrics)
    calib_audit = {
        "status": "R2_CALIB_SCREEN_COMPLETE_INTERNAL_VAL_UNTOUCHED",
        "variant": VARIANT,
        "relation": relation_metrics,
        "syntax": syntax_metrics,
        "auxiliary": auxiliary_metrics,
        "thresholds": thresholds,
        "threshold_selection": calibration_selection,
        "fusion_mean": fusion,
        "hardnegative_counts": hardneg_counts,
        "train_morph_supervision": train_supervision,
        "checkpoint_sha256": calibration["checkpoint_sha256"],
        "screen_decision": decision,
        "comparison_against_A1": comparison_against(
            A1_BASELINE, relation_metrics, syntax_metrics
        ),
        "comparison_against_R1": comparison_against(
            R1_BASELINE, relation_metrics, syntax_metrics
        ),
        "internal_val_consumed": False,
        "external_holdouts_consumed": False,
        "official_test_splits_consumed": False,
    }
    v4.CALIB_AUDIT.write_text(
        json.dumps(calib_audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    legacy_pass = all(item["value"] >= item["minimum"] for item in legacy_gates.values())
    production_pass = all(
        item["value"] >= item["minimum"]
        for item in effective_v6_production_gates.values()
    )
    gate_result = {
        "status": (
            "PASS_V6_PRODUCTION_CALIB_ELIGIBLE_INTERNAL_STILL_SEALED"
            if production_pass else "FAIL_V6_PRODUCTION_CALIB_INTERNAL_STILL_SEALED"
        ),
        "legacy_absolute_gates": legacy_gates,
        "legacy_absolute_pass": legacy_pass,
        "effective_v6_production_gates": effective_v6_production_gates,
        "effective_v6_production_pass": production_pass,
        "stretch_target_all_metrics": 0.95,
        "screen_decision": decision,
        "internal_val_consumed": False,
        "checkpoint_sha256": calibration["checkpoint_sha256"],
    }
    v4.CALIB_GATE.write_text(
        json.dumps(gate_result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    result = {
        "status": decision["status"],
        "variant": VARIANT,
        "selected_checkpoint": {
            "stage": final_checkpoint["stage"],
            "epoch": final_checkpoint["epoch"],
            "selection_score": final_checkpoint["score"],
            "sha256": calibration["checkpoint_sha256"],
        },
        "relation": relation_metrics,
        "syntax": syntax_metrics,
        "auxiliary": auxiliary_metrics,
        "screen_decision": decision,
        "comparison_against_A1": calib_audit["comparison_against_A1"],
        "comparison_against_R1": calib_audit["comparison_against_R1"],
        "absolute_gate": gate_result,
        "internal_val_consumed": False,
        "external_holdouts_consumed": False,
    }
    R2_SCREEN_RESULT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    v4.log("R2 CALIB SCREEN " + json.dumps({
        "decision": decision["status"],
        "macro": relation_metrics["macro_f1"],
        "min": relation_metrics["min_family_f1"],
        "UAS": syntax_metrics["UAS"],
        "LAS": syntax_metrics["LAS"],
        "internal_val_consumed": False,
    }, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--screen", action="store_true")
    args = parser.parse_args()
    if args.smoke == args.screen:
        parser.error("choose exactly one of --smoke or --screen")
    v4.seed_all(CFG.seed)
    if args.smoke:
        run_smoke()
    else:
        run_screen()


if __name__ == "__main__":
    main()
