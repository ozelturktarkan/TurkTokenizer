#!/usr/bin/env python3
"""Interruption-safe runner for the precommitted TurkTokenizer v6.0 R2 screen.

The wrapper changes no model, loss, optimizer, seed, data split, selection
score, threshold grid, or gate. It replaces only the three training loops with
epoch-boundary state snapshots containing model, optimizer, RNG, patience,
best-score, and balanced-sampler state.  Every epoch logs the exact patience
transition and may mirror state to TURKTOKENIZER_DURABLE_DIR.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import random
import shutil
import sys
from dataclasses import asdict
from pathlib import Path

import torch


BASE = Path(__file__).resolve().parent
ORIGINAL = BASE / "TurkTokenizer_v6_0_R2_train.py"
STATE_DIR = BASE / "v600_R2_resume_state"
STATE_DIR.mkdir(exist_ok=True)
HARDNEG_CACHE = STATE_DIR / "hardnegative_cache.pt"
DURABLE_DIR = Path(os.environ.get(
    "TURKTOKENIZER_DURABLE_DIR", str(BASE / "v600_R2_durable")
)).resolve()
DURABLE_DIR.mkdir(parents=True, exist_ok=True)


def load_original():
    spec = importlib.util.spec_from_file_location("v600_r2_resumable_source", ORIGINAL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import precommitted v6.0 R2 source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


r2 = load_original()
v4 = r2.v4
CFG = r2.CFG
ORIGINAL_MINE_HARD_NEGATIVES = v4.mine_hard_negatives

FINGERPRINT = {
    "original_r2_sha256": v4.sha256(ORIGINAL),
    "a1_source_sha256": v4.sha256(r2.A1_SOURCE),
    "locked_trainer_sha256": v4.sha256(r2.a1.LOCKED),
    "seed": CFG.seed,
    "config": asdict(CFG),
}


def atomic_torch_save(payload, path: Path) -> None:
    temporary = path.with_name(path.name + ".tmp")
    torch.save(payload, temporary)
    temporary.replace(path)


def atomic_json_write(payload, path: Path) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def mirror_durable(path: Path) -> None:
    destination = DURABLE_DIR / path.name
    temporary = destination.with_name(destination.name + ".tmp")
    shutil.copy2(path, temporary)
    temporary.replace(destination)


def stage_paths(stage: str) -> tuple[Path, Path]:
    return STATE_DIR / f"{stage}_state.pt", STATE_DIR / f"{stage}_done.json"


def sampler_epoch(loader) -> int:
    return int(getattr(loader.batch_sampler, "epoch", 0))


def set_sampler_epoch(loader, value: int) -> None:
    if hasattr(loader.batch_sampler, "epoch"):
        loader.batch_sampler.epoch = int(value)


def optimizer_to(optimizer, device) -> None:
    for state in optimizer.state.values():
        for key, value in state.items():
            if torch.is_tensor(value):
                state[key] = value.to(device)


def save_best(path, model, resources, stage, epoch, score, extra) -> None:
    payload = {
        "model": model.state_dict(),
        "config": asdict(CFG),
        "vocabs": resources.state(),
        "stage": stage,
        "epoch": epoch,
        "score": score,
        "extra": extra,
    }
    atomic_torch_save(payload, path)
    mirror_durable(path)


def save_state(path, stage, epoch, model, optimizer, best, bad, loader) -> None:
    atomic_torch_save(
        {
            "fingerprint": FINGERPRINT,
            "stage": stage,
            "completed_epoch": epoch,
            "next_epoch": epoch + 1,
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "best": best,
            "bad": bad,
            "python_rng_state": random.getstate(),
            "torch_rng_state": torch.get_rng_state(),
            "sampler_epoch": sampler_epoch(loader),
        },
        path,
    )
    mirror_durable(path)


def restore_state(path, stage, model, optimizer, loader, device):
    payload = torch.load(path, map_location=device, weights_only=False)
    if payload.get("fingerprint") != FINGERPRINT or payload.get("stage") != stage:
        raise RuntimeError(f"incompatible resumable state: {path}")
    model.load_state_dict(payload["model"])
    optimizer.load_state_dict(payload["optimizer"])
    optimizer_to(optimizer, device)
    random.setstate(payload["python_rng_state"])
    torch.set_rng_state(payload["torch_rng_state"].cpu())
    set_sampler_epoch(loader, payload["sampler_epoch"])
    return payload["next_epoch"], payload["best"], payload["bad"]


def finish_stage(done_path, stage, best_path, loader) -> None:
    atomic_json_write(
        {
            "status": "COMPLETE",
            "stage": stage,
            "best_checkpoint": best_path.name,
            "best_checkpoint_sha256": v4.sha256(best_path),
            "sampler_epoch": sampler_epoch(loader),
            "fingerprint": FINGERPRINT,
        },
        done_path,
    )
    mirror_durable(done_path)


def restore_completed(done_path, best_path, model, loader):
    done = json.loads(done_path.read_text(encoding="utf-8"))
    if done.get("fingerprint") != FINGERPRINT:
        raise RuntimeError(f"incompatible completed-stage marker: {done_path}")
    if v4.sha256(best_path) != done.get("best_checkpoint_sha256"):
        raise RuntimeError(f"completed-stage checkpoint changed: {best_path}")
    set_sampler_epoch(loader, done["sampler_epoch"])
    return v4.load_checkpoint(best_path, model)


def train_syntax_resumable(
    model, train_loader, calib_loader, resources, syntax_consensus, device
):
    stage = "syntax"
    state_path, done_path = stage_paths(stage)
    if done_path.exists() and v4.BEST_SYNTAX.exists():
        v4.log("RESUME syntax already complete; restoring selected checkpoint")
        return restore_completed(done_path, v4.BEST_SYNTAX, model, train_loader)

    optimizer = torch.optim.AdamW(
        model.parameters(), lr=CFG.lr_syntax, weight_decay=CFG.weight_decay
    )
    start_epoch, best, bad = 1, -1.0, 0
    if state_path.exists():
        start_epoch, best, bad = restore_state(
            state_path, stage, model, optimizer, train_loader, device
        )
        v4.log(f"RESUME syntax from E{start_epoch:02d}")

    for epoch in range(start_epoch, CFG.syntax_epochs + 1):
        model.train()
        total_loss = batches = 0
        for batch in train_loader:
            v4.to_device(batch, device)
            optimizer.zero_grad(set_to_none=True)
            output = model(batch)
            loss = v4.syntax_loss(output, batch, resources, syntax_consensus, True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), CFG.grad_clip)
            optimizer.step()
            total_loss += float(loss.detach())
            batches += 1
        _, syntax, _ = v4.collect_predictions(model, calib_loader, device)
        score = 0.60 * syntax["LAS"] + 0.30 * syntax["UAS"] + 0.10 * syntax["UPOS"]
        v4.log(
            f"SYNTAX E{epoch:02d} loss={total_loss/max(1,batches):.4f} "
            f"UAS={syntax['UAS']:.4f} LAS={syntax['LAS']:.4f} UPOS={syntax['UPOS']:.4f}"
        )
        improved = score > best + CFG.early_stop_min_delta
        if improved:
            best, bad = score, 0
            save_best(
                v4.BEST_SYNTAX, model, resources, stage, epoch, score,
                {"calib_syntax": syntax},
            )
        else:
            bad += 1
        save_state(state_path, stage, epoch, model, optimizer, best, bad, train_loader)
        v4.log(
            f"PATIENCE {stage} E{epoch:02d} score={score:.8f} "
            f"improved={str(improved).lower()} patience={bad}/{CFG.patience_syntax}"
        )
        v4.log(f"RESUME_STATE {stage} E{epoch:02d} durable_local_and_mirror")
        if bad >= CFG.patience_syntax:
            break

    checkpoint = v4.load_checkpoint(v4.BEST_SYNTAX, model)
    finish_stage(done_path, stage, v4.BEST_SYNTAX, train_loader)
    return checkpoint


def train_relations_resumable(
    model, train_loader, calib_loader, resources, syntax_consensus,
    relation_consensus, device, hardneg=None,
):
    stage = "hardnegative" if hardneg else "relation"
    epochs = CFG.hardnegative_epochs if hardneg else CFG.relation_epochs
    patience = CFG.patience_hardnegative if hardneg else CFG.patience_relation
    learning_rate = CFG.lr_hardnegative if hardneg else CFG.lr_relation
    best_path = v4.BEST_HARDNEG if hardneg else v4.BEST_RELATION
    state_path, done_path = stage_paths(stage)

    if done_path.exists() and best_path.exists():
        v4.log(f"RESUME {stage} already complete; restoring selected checkpoint")
        return restore_completed(done_path, best_path, model, train_loader)

    optimizer = torch.optim.AdamW(
        model.parameters(), lr=learning_rate, weight_decay=CFG.weight_decay
    )
    start_epoch, best, bad = 1, -1.0, 0
    if state_path.exists():
        start_epoch, best, bad = restore_state(
            state_path, stage, model, optimizer, train_loader, device
        )
        v4.log(f"RESUME {stage} from E{start_epoch:02d}")

    for epoch in range(start_epoch, epochs + 1):
        model.train()
        total_loss = batches = 0
        for batch in train_loader:
            v4.to_device(batch, device)
            optimizer.zero_grad(set_to_none=True)
            output = model(batch)
            relation = v4.relation_loss(output, batch, relation_consensus, True, hardneg)
            syntax = v4.syntax_loss(output, batch, resources, syntax_consensus, True)
            loss = relation + CFG.syntax_retention * syntax
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), CFG.grad_clip)
            optimizer.step()
            total_loss += float(loss.detach())
            batches += 1

        records, syntax_metrics, fusion = v4.collect_predictions(model, calib_loader, device)
        thresholds, _ = v4.calibrate(records)
        relation_metrics = v4.evaluate(records, thresholds)
        score = v4.relation_selection_score(relation_metrics, syntax_metrics)
        family_text = " ".join(
            f"{family}:{relation_metrics['families'][family]['f1']:.3f}"
            for family in v4.FAMILIES
        )
        v4.log(
            f"{stage.upper()} E{epoch:02d} loss={total_loss/max(1,batches):.4f} "
            f"macro={relation_metrics['macro_f1']:.4f} "
            f"min={relation_metrics['min_family_f1']:.4f} {family_text} "
            f"UAS={syntax_metrics['UAS']:.4f} LAS={syntax_metrics['LAS']:.4f}"
        )
        improved = score > best + CFG.early_stop_min_delta
        if improved:
            best, bad = score, 0
            save_best(
                best_path, model, resources, stage, epoch, score,
                {
                    "calib_metrics": relation_metrics,
                    "calib_syntax": syntax_metrics,
                    "thresholds": thresholds,
                    "fusion_mean": fusion,
                },
            )
        else:
            bad += 1
        save_state(state_path, stage, epoch, model, optimizer, best, bad, train_loader)
        v4.log(
            f"PATIENCE {stage} E{epoch:02d} score={score:.8f} "
            f"improved={str(improved).lower()} patience={bad}/{patience}"
        )
        v4.log(f"RESUME_STATE {stage} E{epoch:02d} durable_local_and_mirror")
        if bad >= patience:
            break

    checkpoint = v4.load_checkpoint(best_path, model)
    finish_stage(done_path, stage, best_path, train_loader)
    return checkpoint


def mine_hard_negatives_resumable(model, train_eval_loader, device, thresholds):
    relation_sha = v4.sha256(v4.BEST_RELATION)
    if HARDNEG_CACHE.exists():
        payload = torch.load(HARDNEG_CACHE, map_location="cpu", weights_only=False)
        if payload.get("fingerprint") == FINGERPRINT and payload.get("relation_sha256") == relation_sha:
            v4.log("RESUME hard-negative cache restored")
            return payload["hardneg"], payload["counts"]

    hardneg, counts = ORIGINAL_MINE_HARD_NEGATIVES(
        model, train_eval_loader, device, thresholds
    )
    atomic_torch_save(
        {
            "fingerprint": FINGERPRINT,
            "relation_sha256": relation_sha,
            "hardneg": hardneg,
            "counts": counts,
        },
        HARDNEG_CACHE,
    )
    mirror_durable(HARDNEG_CACHE)
    v4.log("RESUME_STATE hard-negative cache durable_local_and_mirror")
    return hardneg, counts


def run_screen() -> None:
    v4.train_syntax = train_syntax_resumable
    v4.train_relations = train_relations_resumable
    v4.mine_hard_negatives = mine_hard_negatives_resumable
    r2.run_screen()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--screen", action="store_true")
    args = parser.parse_args()
    if args.smoke == args.screen:
        parser.error("choose exactly one of --smoke or --screen")
    v4.seed_all(CFG.seed)
    if args.smoke:
        r2.run_smoke()
    else:
        run_screen()


if __name__ == "__main__":
    main()
