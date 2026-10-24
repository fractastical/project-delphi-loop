#!/usr/bin/env python3
"""
discovery/2_preregister_blind_predictions.py — Frontier Discovery Agent Step 2:
Cryptographic Pre-Registration of Out-of-Sample Predictions BEFORE Unblinding.

Driven by: `prompts/05_blind_preregistration_prompt.md`
CRITICAL BLINDING INVARIANT:
  This script NEVER opens or reads `discovery/heldout_blind_species.csv`!
  It generates out-of-sample predictions across a fixed grid of phylogenetic divergence
  horizons `tau` using ONLY `discovery/ablation_and_hypotheses.json`, locks the prediction
  CSV by SHA-256, and emits Nanopub #3 (`kg/discovery_preregistration.trig`) into the
  Knowledge Graph before Gate 4b (`gates/6_score_blind_discovery.py`) unblinds the data.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HYP_JSON = ROOT / "discovery" / "ablation_and_hypotheses.json"
LOCKED_CSV = ROOT / "discovery" / "blind_predictions_locked.csv"
MANIFEST_JSON = ROOT / "kg" / "discovery_preregistration_manifest.json"
PREREG_TRIG = ROOT / "kg" / "discovery_preregistration.trig"

# Fixed phylogenetic divergence horizons (Myr) for the 16 held-out test slots
HELDOUT_HORIZONS = [
    ("ho_01", 7.8, "sympatric"),
    ("ho_02", 11.4, "sympatric"),
    ("ho_03", 14.2, "allopatric"),
    ("ho_04", 18.6, "sympatric"),
    ("ho_05", 24.5, "sympatric"),
    ("ho_06", 31.2, "sympatric"),
    ("ho_07", 38.4, "allopatric"),
    ("ho_08", 44.8, "sympatric"),
    ("ho_09", 52.4, "allopatric"),
    ("ho_10", 64.0, "allopatric"),
    ("ho_11", 76.5, "allopatric"),
    ("ho_12", 82.0, "allopatric"),
    ("ho_13", 91.5, "sympatric"),
    ("ho_14", 101.8, "allopatric"),
    ("ho_15", 109.4, "sympatric"),
    ("ho_16", 116.2, "sympatric"),
]


def main() -> int:
    hyp = json.loads(HYP_JSON.read_text(encoding="utf-8"))
    cal = hyp["calibrated_prediction_parameters"]
    slope = float(cal["outline_iou_slope_per_myr"])
    intercept = float(cal["outline_iou_intercept"])
    pi_hw = float(cal["pi95_halfwidth_iou"])
    tau_star = float(cal["estimated_modularity_horizon_tau_star_myr"])

    with LOCKED_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "heldout_id",
            "divergence_myr",
            "ecological_overlap",
            "pred_iou_600pt_outline",
            "pi95_low",
            "pi95_high",
            "pred_outline_beats_17dot",
            "pred_h4_unbounded_17dot_within_floor",
        ])
        for hid, tau, eco in HELDOUT_HORIZONS:
            pred_iou = intercept + slope * tau
            writer.writerow([
                hid,
                f"{tau:.1f}",
                eco,
                f"{pred_iou:.4f}",
                f"{pred_iou - pi_hw:.4f}",
                f"{pred_iou + pi_hw:.4f}",
                1,
                1,  # H4 null claim predicts 17-dot stays within genus floor everywhere
            ])

    locked_sha256 = hashlib.sha256(LOCKED_CSV.read_bytes()).hexdigest()

    manifest = {
        "preregistration_id": "https://w3id.org/delphi/np/discovery-preregistration",
        "derived_from_kg_claim": "https://w3id.org/delphi/np/pass2-example-claim",
        "locked_predictions_file": str(LOCKED_CSV.relative_to(ROOT)),
        "locked_predictions_sha256": locked_sha256,
        "n_locked_predictions": len(HELDOUT_HORIZONS),
        "estimated_modularity_horizon_tau_star_myr": tau_star,
        "heldout_data_touched_during_preregistration": False,
        "registered_hypotheses": [h["id"] for h in hyp["synthesized_hypotheses"]],
    }
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    trig_body = f"""@prefix np: <http://www.nanopub.org/nschema#> .
@prefix npx: <http://purl.org/nanopub/x/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix pk: <https://w3id.org/delphi/ontology/> .
@prefix pkr: <https://w3id.org/delphi/resource/> .
@prefix sub: <https://w3id.org/delphi/np/discovery-preregistration/> .

sub:Head {{
  <https://w3id.org/delphi/np/discovery-preregistration> a np:Nanopublication ;
    np:hasAssertion sub:assertion ;
    np:hasProvenance sub:provenance ;
    np:hasPublicationInfo sub:pubinfo .
}}

sub:assertion {{
  pkr:prereg-modular-allometry-horizon a pk:PreRegisteredPrediction ;
    pk:lockedPredictionsFile "{LOCKED_CSV.relative_to(ROOT)}" ;
    pk:lockedPredictionsSha256 "{locked_sha256}" ;
    pk:predictedHorizonMyr "{tau_star}"^^xsd:double ;
    pk:registersHypothesis "H1_head_bias_seesaw", "H2_horizon_error_scaling", "H3_sympatric_head_acceleration", "H4_unbounded_17dot_null" ;
    pk:blindedStatus "locked_prior_to_heldout_access" .
}}

sub:provenance {{
  sub:assertion prov:wasAttributedTo pkr:model-claude-fable-5-1 ;
    prov:wasDerivedFrom <https://w3id.org/delphi/np/pass2-example-claim> ;
    prov:wasDerivedFrom <file://discovery/ablation_and_hypotheses.json> .
}}

sub:pubinfo {{
  <https://w3id.org/delphi/np/discovery-preregistration> npx:hasTrustyDigest "{locked_sha256[:32]}" .
}}
"""
    PREREG_TRIG.write_text(trig_body, encoding="utf-8")
    print(
        f"  [Pre-Registration Lock] Compiled `{PREREG_TRIG.relative_to(ROOT)}` BEFORE touching held-out data!\n"
        f"                          Locked `{LOCKED_CSV.relative_to(ROOT)}` (SHA-256: {locked_sha256[:16]}...)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
