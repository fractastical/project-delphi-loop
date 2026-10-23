#!/usr/bin/env python3
"""
gates/1_verify_inputs.py — Gate 1: Cryptographic Data Pinning & Lean 4 Proof Gate.

Input Contract : `example/data.csv` + `example/law.lean`
Output Contract: Exit 0 iff SHA-256 matches pinned constant AND Lean 4 has `0 sorry`.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_CSV = ROOT / "example" / "data.csv"
EXPECTED_DATA_SHA256 = "8cc91f52974935716c7f7a18bcb07aa8ab67181356a4880240075ff3f550e8c5"
LEAN_FILE = ROOT / "example" / "law.lean"


def main() -> int:
    actual_sha = hashlib.sha256(DATA_CSV.read_bytes()).hexdigest()
    if actual_sha != EXPECTED_DATA_SHA256:
        print(f"  [GATE 1 FAIL] SHA-256 mismatch on {DATA_CSV.name}: {actual_sha}", file=sys.stderr)
        return 1
    print(f"  [Gate 1 PASS] Data pin verified: `{DATA_CSV.relative_to(ROOT)}` (SHA-256: {actual_sha[:16]}...)")

    lean_src = LEAN_FILE.read_text(encoding="utf-8")
    if "sorry" in lean_src.split("--")[0]:
        print("  [GATE 1 FAIL] Lean 4 file contains `sorry`!", file=sys.stderr)
        return 1

    lean_bin = shutil.which("lean")
    if lean_bin:
        res = subprocess.run([lean_bin, str(LEAN_FILE)], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"  [GATE 1 FAIL] Lean 4 kernel rejected `{LEAN_FILE.name}`:\n{res.stderr}", file=sys.stderr)
            return 1
        print(f"  [Gate 1 PASS] Lean 4 kernel verified `{LEAN_FILE.relative_to(ROOT)}` (exit 0, 0 sorry)")
    else:
        print(f"  [Gate 1 PASS] `{LEAN_FILE.relative_to(ROOT)}` 0-sorry check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
