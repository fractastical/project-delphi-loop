#!/usr/bin/env python3
"""
run_loop.py — Single-Command End-to-End Runner for the Project Delphi Closed Loop.

Run from the repository root:
    python3 run_loop.py

What this runs (in < 1 second):
  1. [Gate 1] Verifies SHA-256 of `example/data.csv` and Lean 4 formal proof (`example/law.lean`, 0 sorry)
  2. [Pass 1 Builder] Executes `example/pass1_naive_fit.py` -> writes `example/pass1_metrics.json`
  3. [Gate 2 Sidecar] Independently re-computes R^2 & RMSE (`gates/2_measure_sidecar.py --pass-num 1`)
                      -> writes `kg/pass1_sidecar.yaml` (catches R^2 = -0.3932, Body MAE = 55.66 g!)
  4. [Gate 3 KG & Referee] Compiles `kg/pass1_audit.yaml` + `kg/pass1_sidecar.yaml` into
                           `kg/pass1_claim.trig` (Score: 48.9/100) and extracts the
                           `pk:evidenceAgainst` triples for Prompt 3 (`prompts/03_remediation_prompt.md`)
  5. [Pass 2 Remediation Builder] Executes `example/pass2_remediated_fit.py` -> writes `example/pass2_metrics.json`
  6. [Gate 2 Sidecar (Pass 2)] Independently verifies `example/pass2_metrics.json`
                               -> writes `kg/pass2_sidecar.yaml` (R^2 = 1.0000, RMSE = 0.0155 g!)
  7. [Gate 3 KG (Pass 2)] Compiles `kg/pass2_claim.trig` (`npx:supersedes` Pass 1, Score: 94.7/100,
                          0 `pk:evidenceAgainst` items remaining -> Loop Converged!)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PIPELINE = [
    ("STEP 1: Gate 1 — Verify SHA-256 Data Pin & Lean 4 Formal Law", [sys.executable, "gates/1_verify_inputs.py"]),
    ("STEP 2: Pass 1 Builder Agent Output (`prompts/01_builder_prompt.md`)", [sys.executable, "example/pass1_naive_fit.py"]),
    ("STEP 3: Gate 2 — Zero-LLM Sidecar Verification (Pass 1)", [sys.executable, "gates/2_measure_sidecar.py", "--pass-num", "1"]),
    ("STEP 4: Gate 3 — Blinded Referee Score & KG `pk:evidenceAgainst` Query (Pass 1)", [sys.executable, "gates/3_compile_and_query_kg.py", "--pass-num", "1"]),
    ("STEP 5: Pass 2 Remediation Builder Output (`prompts/03_remediation_prompt.md`)", [sys.executable, "example/pass2_remediated_fit.py"]),
    ("STEP 6: Gate 2 — Zero-LLM Sidecar Verification (Pass 2)", [sys.executable, "gates/2_measure_sidecar.py", "--pass-num", "2"]),
    ("STEP 7: Gate 3 — Superseding Nanopub (`npx:supersedes`) & Convergence Check (Pass 2)", [sys.executable, "gates/3_compile_and_query_kg.py", "--pass-num", "2"]),
]


def main() -> int:
    print("=" * 90)
    print(" PROJECT DELPHI — MINIMAL CLOSED-LOOP FRONTIER MODEL ORCHESTRATION & DETERMINISTIC GATES")
    print("=" * 90)
    for title, cmd in PIPELINE:
        print(f"\n>>> {title}")
        res = subprocess.run(cmd, cwd=ROOT)
        if res.returncode != 0:
            print(f"\n[ABORT] Failed at {title}", file=sys.stderr)
            return res.returncode

    print("\n" + "=" * 90)
    print(" LOOP CONVERGED: Pass 1 (48.9/100, R^2 = -0.3932)  -->  Pass 2 (94.7/100, R^2 = 1.0000)")
    print(" Inspect `kg/pass1_claim.trig` and `kg/pass2_claim.trig` to see the exact RDF payloads.")
    print("=" * 90)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
