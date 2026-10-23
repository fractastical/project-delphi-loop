# Prompt 3 — Knowledge-Graph-Driven Remediation Agent (`prompts/03_remediation_prompt.md`)

- **Role:** Builder Agent in Pass 2 (`claude-fable-5-1` or `gemini-4-argon`)
- **Inputs Passed Into Prompt:**
  1. `example/pass1_naive_fit.py` (the Pass 1 script that scored `48.9 / 100`)
  2. `kg/pass1_sidecar.yaml` (showing `r2_all: -0.3932`, `mae_head_subset_g: 0.0567`, `mae_body_subset_g: 55.6611`)
  3. The `pk:evidenceAgainst` RDF triples extracted by Gate 3 (`gates/3_compile_and_query_kg.py`) from `kg/pass1_claim.trig`:
     - `"remediation needed: Fit the power law y = a * x^b across the full organism (all 12 rows of example/data.csv, accounting for both head and body modules) instead of fitting a linear line only to the 6 head rows (line 49)."`
     - `"remediation needed: Report the fitted power-law exponents b_head and b_body and verify that full-dataset R^2 exceeds 0.99."`
- **Output Required From Agent:**
  - `example/pass2_remediated_fit.py` + `example/pass2_metrics.json` (which is then re-verified by Gate 2 and re-scored by the Blinded Referee in Pass 2, raising the score from **`48.9 / 100` $\to$ `94.7 / 100`** and minting `npx:supersedes` in `kg/pass2_claim.trig`).

---

## Exact Prompt Template Sent to the Remediation Agent

```markdown
You are executing Pass 2 (Closed-Loop Remediation) of the Project Delphi pipeline.

## WHY PASS 1 FAILED (SCORE: 48.9 / 100)
Querying the signed Pass 1 RDF Nanopublication (`kg/pass1_claim.trig`) returned the following `pk:evidenceAgainst` triples recorded by the Blinded Referee and verified by `kg/pass1_sidecar.yaml` (`r2_all = -0.3932`, `mae_head_subset_g = 0.0567 g`, `mae_body_subset_g = 55.6611 g`):

1. "remediation needed: Fit the power law y = a * x^b across the full organism (all 12 rows of example/data.csv, accounting for both head and body modules) instead of fitting a linear line only to the 6 head rows (line 49)."
2. "remediation needed: Report the fitted power-law exponents b_head and b_body and verify that full-dataset R^2 exceeds 0.99."

## TASK
Write `example/pass2_remediated_fit.py` fixing every `pk:evidenceAgainst` item above, and emit `example/pass2_metrics.json`. Your new output will be re-checked by `gates/2_measure_sidecar.py --pass-num 2` and `gates/3_compile_and_query_kg.py --pass-num 2` (which will mint `kg/pass2_claim.trig` with `npx:supersedes <https://w3id.org/delphi/np/pass1-example-claim>`).
```
