#!/usr/bin/env python3
"""Public, role-safe Git-blob verifier for TurkTokenizer corpus manifests.

The script contains no project-specific hashes or sealed-resource paths. Exact
blob identities must be supplied through a local manifest. By default, only
entries with the V4_TRAINING_POOL role are opened.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


DEFAULT_ROLE = "V4_TRAINING_POOL"
PLACEHOLDER = "FILL_FROM_AUTHORIZED_LOCKED_MANIFEST"


def git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--roles", default=DEFAULT_ROLE)
    parser.add_argument("--output")
    args = parser.parse_args()

    root = Path(args.directory)
    manifest_path = Path(args.manifest)
    selected_roles = {item.strip() for item in args.roles.split(",") if item.strip()}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    verified: list[str] = []
    missing: list[str] = []
    mismatched: list[str] = []
    unlocked: list[str] = []
    excluded_by_role: list[str] = []

    for name, spec in manifest.get("files", {}).items():
        if spec.get("role") not in selected_roles:
            excluded_by_role.append(name)
            continue
        expected = spec.get("blob_sha")
        if not expected or expected == PLACEHOLDER:
            unlocked.append(name)
            continue
        path = root / spec["file"]
        if not path.is_file():
            missing.append(name)
            continue
        if git_blob_sha(path) != expected:
            mismatched.append(name)
            continue
        verified.append(name)

    status = "PASS" if verified and not (missing or mismatched or unlocked) else "FAIL"
    result = {
        "status": status,
        "selected_roles": sorted(selected_roles),
        "verified": verified,
        "missing": missing,
        "mismatched": mismatched,
        "missing_locked_identity": unlocked,
        "excluded_by_role": excluded_by_role,
        "note": "Exact local hashes are compared but are not copied into this result.",
    }

    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
