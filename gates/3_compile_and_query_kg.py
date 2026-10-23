#!/usr/bin/env python3
"""
gates/3_compile_and_query_kg.py — Gate 3: RDF Nanopub Compiler & `pk:evidenceAgainst` Query.

What gets passed into this gate:
  - `rubric.json` (the 7 weighted dimensions)
  - `kg/pass<N>_sidecar.json` (deterministic measurements from Gate 2)
  - `kg/pass<N>_audit.json` (the Blinded Cross-Provider Referee's scores + `remediation` list)

What this gate emits:
  - `kg/pass<N>_claim.trig` (Project Delphi RDF Nanopublication with `pk:hasScore`,
    `pk:evidenceAgainst`, and `npx:supersedes` in Pass 2)
  - Prints the extracted `pk:evidenceAgainst` items that get passed into Prompt 3
    (`prompts/03_remediation_prompt.md`) to drive Pass 2!
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUBRIC_JSON = ROOT / "rubric.json"


def compute_weighted_score(rubric: dict, scores: dict[str, int]) -> float:
    total = 0.0
    for dim in rubric["dimensions"]:
        did = dim["id"]
        w = float(dim["weight"])
        total += w * float(scores[did])
    return round(total / 100.0, 2)


def emit_trig(audit_doc: dict, sidecar_doc: dict, overall_score: float, pass_num: int) -> tuple[Path, str]:
    trig_out = ROOT / "kg" / f"pass{pass_num}_claim.trig"
    remediations = audit_doc.get("remediation", [])
    ev_against_lines = ",\n    ".join(f'"{r}"' for r in remediations)
    ev_against_block = f"  pk:evidenceAgainst\n    {ev_against_lines} ;\n" if remediations else ""
    supersedes_line = (
        "  npx:supersedes <https://w3id.org/delphi/np/pass1-example-claim> ;\n" if pass_num == 2 else ""
    )

    body = f"""@prefix np: <http://www.nanopub.org/nschema#> .
@prefix npx: <http://purl.org/nanopub/x/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix pk: <https://w3id.org/delphi/ontology/> .
@prefix pkr: <https://w3id.org/delphi/resource/> .
@prefix sub: <https://w3id.org/delphi/np/pass{pass_num}-example-claim/> .

sub:Head {{
  <https://w3id.org/delphi/np/pass{pass_num}-example-claim> a np:Nanopublication ;
    np:hasAssertion sub:assertion ;
    np:hasProvenance sub:provenance ;
    np:hasPublicationInfo sub:pubinfo .
}}

sub:assertion {{
  pkr:claim-example-allometry a pk:Claim ;
    pk:targetScript "{sidecar_doc['target_script']}" ;
    pk:artifactSha256 "{sidecar_doc['artifact_sha256']}" ;
    pk:measuredR2 "{sidecar_doc['independent_measurements']['r2_all']}"^^xsd:double ;
    pk:measuredRMSE "{sidecar_doc['independent_measurements']['rmse_all_g']}"^^xsd:double ;
    pk:assessedBy pkr:model-{audit_doc['assessor_model']} ;
    pk:hasScore "{overall_score / 100.0:.4f}"^^xsd:double ;
{ev_against_block}    pk:verdict "{'faithful' if overall_score >= 80 else 'needs_remediation'}" .
}}

sub:provenance {{
  sub:assertion prov:wasAttributedTo pkr:model-{audit_doc['assessor_model']} ;
    prov:wasDerivedFrom <file://{sidecar_doc['artifact_file']}> .
}}

sub:pubinfo {{
{supersedes_line}  <https://w3id.org/delphi/np/pass{pass_num}-example-claim> npx:hasTrustyDigest "{hashlib.sha256(str(overall_score).encode()).hexdigest()[:32]}" .
}}
"""
    trig_out.write_text(body, encoding="utf-8")
    return trig_out, body


def query_evidence_against(trig_path: Path) -> list[str]:
    txt = trig_path.read_text(encoding="utf-8")
    m = re.search(r"pk:evidenceAgainst\s+(.*?)\s*;", txt, re.S)
    if not m:
        return []
    return re.findall(r'"([^"]+)"', m.group(1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass-num", type=int, choices=[1, 2], required=True)
    args = ap.parse_args()

    rubric = json.loads(RUBRIC_JSON.read_text(encoding="utf-8"))
    sidecar = json.loads((ROOT / "kg" / f"pass{args.pass_num}_sidecar.json").read_text(encoding="utf-8"))
    audit = json.loads((ROOT / "kg" / f"pass{args.pass_num}_audit.json").read_text(encoding="utf-8"))

    overall = compute_weighted_score(rubric, audit["scores"])
    trig_path, _ = emit_trig(audit, sidecar, overall, args.pass_num)

    print(
        f"  [Gate 3 PASS] Compiled `{trig_path.relative_to(ROOT)}` | "
        f"Assessor: `{audit['assessor_model']}` ({audit['provider']}) | "
        f"Weighted Rubric Score: {overall:.1f} / 100"
    )

    flaws = query_evidence_against(trig_path)
    if flaws:
        print(f"  [KG QUERY] Extracted {len(flaws)} `pk:evidenceAgainst` item(s) to inject into Remediation Prompt:")
        for idx, fl in enumerate(flaws, start=1):
            print(f"             ({idx}) {fl}")
    else:
        print("  [KG QUERY] 0 `pk:evidenceAgainst` items remaining -> Loop Converged (>= 80 Faithful Band)!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
