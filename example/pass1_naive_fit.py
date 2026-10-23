#!/usr/bin/env python3
"""
example/pass1_naive_fit.py — Pass 1 Output of the Frontier Builder Agent.

WHAT THIS SCRIPT DOES (AND ITS DELIBERATE PASS 1 DEFECT):
  - Loads `example/data.csv` (12 specimens: 6 `head` points, 6 `body` points).
  - DEFECT: Fits a linear line `y = m*x + c` ONLY to the 6 `head` rows (`region == 'head'`)
    and projects that line onto the whole organism (`head` + `body`).
  - Because `body` follows a cubic scaling law (`y ~ x^3`), the head-fitted line
    catastrophically misses the body points (full-dataset R^2 = -0.3932, RMSE = 49.36 g)!
  - Writes `example/pass1_metrics.json` for Gate 2 (`gates/2_measure_sidecar.py`).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_CSV = ROOT / "example" / "data.csv"
OUT_JSON = ROOT / "example" / "pass1_metrics.json"


def load_rows() -> list[dict[str, float | str]]:
    with DATA_CSV.open(encoding="utf-8") as f:
        return [
            {
                "specimen_id": r["specimen_id"],
                "region": r["region"],
                "length_mm": float(r["length_mm"]),
                "mass_g": float(r["mass_g"]),
            }
            for r in csv.DictReader(f)
        ]


def fit_linear_least_squares(xs: list[float], ys: list[float]) -> tuple[float, float]:
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    m = num / den
    c = my - m * mx
    return m, c


def main() -> int:
    rows = load_rows()
    # PASS 1 FLAW: Builder fits ONLY on the `head` subset!
    head_rows = [r for r in rows if r["region"] == "head"]
    m, c = fit_linear_least_squares(
        [float(r["length_mm"]) for r in head_rows],
        [float(r["mass_g"]) for r in head_rows],
    )

    preds = [m * float(r["length_mm"]) + c for r in rows]
    actuals = [float(r["mass_g"]) for r in rows]
    mean_y = sum(actuals) / len(actuals)
    ss_res = sum((y - p) ** 2 for y, p in zip(actuals, preds))
    ss_tot = sum((y - mean_y) ** 2 for y in actuals)
    rmse_all = (ss_res / len(actuals)) ** 0.5
    r2_all = 1.0 - (ss_res / ss_tot)

    payload = {
        "pass": 1,
        "script": "example/pass1_naive_fit.py",
        "model_equation": "y = m * x + c (fitted to head subset only)",
        "fitted_params": {"m": round(m, 6), "c": round(c, 6)},
        "predictions": [round(p, 4) for p in preds],
        "reported_rmse_all": round(rmse_all, 4),
        "reported_r2_all": round(r2_all, 4),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"  [Pass 1 Builder] Wrote `{OUT_JSON.relative_to(ROOT)}`: RMSE={rmse_all:.4f} g, R^2={r2_all:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
