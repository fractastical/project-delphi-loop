# Prompt 1 — Frontier Builder Agent (`prompts/01_builder_prompt.md`)

- **Role:** Primary Builder Agent (e.g., `claude-fable-5-1`, Anthropic)
- **Inputs Passed Into Prompt:**
  1. `example/data.csv` (verified by Gate 1 `gates/1_verify_inputs.py`, `SHA-256: 8cc91f52...`)
  2. `example/law.lean` (verified by Lean 4 kernel with `0 sorry`)
  3. `rubric.yaml` (the 7 weighted evaluation dimensions)
- **Output Required From Agent:**
  - Executable Python script (`example/pass1_naive_fit.py`) that writes `example/pass1_metrics.json` containing `"fitted_params"`, `"predictions"`, `"reported_rmse_all"`, and `"reported_r2_all"`.

---

## Exact Prompt Template Sent to the Builder Agent

```markdown
You are the Builder Agent in the Project Delphi closed-loop scientific pipeline.

## INPUT PAYLOADS PROVIDED IN WORKSPACE
1. Empirical dataset: `example/data.csv` (SHA-256 verified by `gates/1_verify_inputs.py`).
2. Formal mathematical law: `example/law.lean` (verified by Lean 4 with `0 sorry`).
3. Evaluation rubric: `rubric.yaml` (7 weighted dimensions on 0–100).

## TASK
Write a deterministic Python script `example/pass1_naive_fit.py` that loads `example/data.csv`, fits a mathematical model predicting `mass_g` from `length_mm`, and writes the structured output contract to `example/pass1_metrics.json`:
{
  "pass": 1,
  "script": "example/pass1_naive_fit.py",
  "model_equation": "<equation string>",
  "fitted_params": { ... },
  "predictions": [ <12 float predictions matching the 12 rows of example/data.csv> ],
  "reported_rmse_all": <float>,
  "reported_r2_all": <float>
}

Your output JSON will be hashed and independently re-verified by Gate 2 (`gates/2_measure_sidecar.py`) before being audited by a blinded referee model from a second AI provider.
```
