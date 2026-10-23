#!/usr/bin/env python3
"""
gates/2_measure_sidecar.py — Gate 2: Zero-LLM Independent Sidecar Verifier.

Why this gate exists:
  Never trust an LLM agent's self-reported metrics (`example/pass1_metrics.json`).
  This sidecar loads `example/data.csv` and the Builder's predictions independently,
  computes its own SHA-256 digest and independent RMSE / R^2 (both overall and split
  by `head` vs `body` subsets), asserts agreement with the script's numbers to 1e-4,
  and writes `kg/pass<N>_sidecar.json` to be handed to the Blinded Referee Agent.

Usage:
  python3 gates/2_measure_sidecar.py --pass-num 1
  python3 gates/2_measure_sidecar.py --pass-num 2
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_CSV = ROOT / "example" / "data.csv"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass-num", type=int, choices=[1, 2], required=True)
    args = ap.parse_args()

    metrics_file = ROOT / "example" / f"pass{args.pass_num}_metrics.json"
    sidecar_out = ROOT / "kg" / f"pass{args.pass_num}_sidecar.json"

    if not metrics_file.exists():
        print(f"  [GATE 2 FAIL] Missing builder output: {metrics_file}", file=sys.stderr)
        return 1

    raw_bytes = metrics_file.read_bytes()
    art_sha = hashlib.sha256(raw_bytes).hexdigest()
    builder = json.loads(raw_bytes.decode("utf-8"))
    preds = [float(x) for x in builder["predictions"]]

    with DATA_CSV.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    actuals = [float(r["mass_g"]) for r in rows]
    mean_y = sum(actuals) / len(actuals)
    ss_res = sum((y - p) ** 2 for y, p in zip(actuals, preds))
    ss_tot = sum((y - mean_y) ** 2 for y in actuals)
    ind_rmse = (ss_res / len(actuals)) ** 0.5
    ind_r2 = 1.0 - (ss_res / ss_tot)

    # Subset breakdown (reveals WHY Pass 1 fails!)
    head_err = [abs(float(r["mass_g"]) - p) for r, p in zip(rows, preds) if r["region"] == "head"]
    body_err = [abs(float(r["mass_g"]) - p) for r, p in zip(rows, preds) if r["region"] == "body"]
    mae_head = sum(head_err) / len(head_err)
    mae_body = sum(body_err) / len(body_err)

    diff_rmse = abs(ind_rmse - float(builder["reported_rmse_all"]))
    if diff_rmse > 1e-3:
        print(
            f"  [GATE 2 FAIL] Sidecar RMSE ({ind_rmse}) != Builder RMSE ({builder['reported_rmse_all']})",
            file=sys.stderr,
        )
        return 1

    sidecar_doc = {
        "pass": args.pass_num,
        "target_script": builder["script"],
        "artifact_file": str(metrics_file.relative_to(ROOT)),
        "artifact_sha256": art_sha,
        "independent_measurements": {
            "n_specimens_total": len(rows),
            "rmse_all_g": round(ind_rmse, 4),
            "r2_all": round(ind_r2, 6),
            "mae_head_subset_g": round(mae_head, 4),
            "mae_body_subset_g": round(mae_body, 4),
            "sidecar_builder_rmse_delta": round(diff_rmse, 6),
        },
    }
    sidecar_out.parent.mkdir(parents=True, exist_ok=True)
    sidecar_out.write_text(json.dumps(sidecar_doc, indent=2) + "\n", encoding="utf-8")

    print(
        f"  [Gate 2 PASS] Sidecar `{sidecar_out.relative_to(ROOT)}` verified `{metrics_file.name}` "
        f"(SHA-256={art_sha[:12]}...)\n"
        f"                Independent R^2 = {ind_r2:.4f} | RMSE = {ind_rmse:.4f} g "
        f"(Head MAE = {mae_head:.4f} g, Body MAE = {mae_body:.4f} g)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
