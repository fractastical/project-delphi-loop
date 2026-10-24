# Project Delphi — Two Coupled Closed Loops: (1) Making the Knowledge Graph & (2) Scientific Discovery

> **Zero-dependency reference repository** showing how Project Delphi integrates frontier models (`claude-fable-5-1`, `gemini-4-argon`, `gpt-5.6-sol`) with **deterministic verification gates**, **Lean 4 (`0 sorry`) formal proofs**, **blinded cross-provider refereeing**, and **RDF Nanopublication (`pk:evidenceAgainst` & `pk:PreRegisteredPrediction`) feedback** across **two coupled closed loops**:
> 1. **Loop 1 — Making & Remediating the Knowledge Graph (`python3 run_loop.py`):** Builds a mathematical reproduction from a SHA-256-locked dataset and Lean 4 law, audits it in an isolated worktree with a second-provider referee, compiles defects into `pk:evidenceAgainst` RDF triples (`kg/pass1_claim.trig`, `49.4 / 100`), and remediates the code in Pass 2 (`kg/pass2_claim.trig`, `94.7 / 100`, linked via `npx:supersedes`).
> 2. **Loop 2 — Scientific Discovery from the Knowledge Graph (`python3 run_discovery_loop.py`):** Queries the signed Loop 1 Knowledge Graph for structural anomalies ($b_{\text{head}} = 2.00$ vs. $b_{\text{body}} = 3.00$), synthesizes falsifiable hypotheses with a 4-way deconfounding ablation matrix and Lean 4 proofs (`discovery/discovery_law.lean`), **cryptographically pre-registers out-of-sample predictions (`kg/discovery_preregistration.trig`) BEFORE unblinding**, and scores held-out data via a zero-LLM gate (`kg/discovery_outcome.trig`, `+58.7 dB` Bayesian weight of evidence).

---

## Quick Start (Runs in `< 1 Second`, Python 3 Stdlib Only)

```bash
# 1. Loop 1: Build, audit, and remediate the Knowledge Graph (Pass 1: 49.4/100 -> Pass 2: 94.7/100)
python3 run_loop.py

# 2. Loop 2: Run KG-driven discovery & cryptographic blind pre-registration (+58.7 dB)
python3 run_discovery_loop.py

# 3. Query the Knowledge Graph across all 4 Nanopubs, Lean 4 theorems, and MorphoSwarm Studio (SPEC-074)
python3 query_kg_solver.py --mode solve
python3 query_kg_solver.py --mode morphoswarm
```

---

## Diagram 1 — Loop 1: How the Knowledge Graph Is Made & Remediated (`run_loop.py`)

![Diagram 1 — Loop 1: 12-Step Closed-Loop Knowledge Graph Construction & Remediation](./media/delphi_12step_closed_loop.gif)

| Edge | Producer $\to$ Consumer | Payload Passed | Verification Gate |
| :-: | :--- | :--- | :--- |
| **`E1`** | **Gate 1** (`gates/1_verify_inputs.py`) $\to$ **Builder Agent** (`prompts/01_builder_prompt.md`) | `example/data.csv`, `example/law.lean`, `rubric.json` | SHA-256 equals `8cc91f52...`; `lean example/law.lean` exits `0` (`0 sorry`) |
| **`E2`** | **Builder Pass 1** (`example/pass1_naive_fit.py`) $\to$ **Gate 2** (`gates/2_measure_sidecar.py`) | `example/pass1_metrics.json` | Hashes output (`26455f9f...`) and checks all 12 predictions |
| **`E3`** | **Gate 2 Sidecar** $\to$ **Blinded Referee** (`prompts/02_referee_prompt.md`) | `kg/pass1_sidecar.json` | Zero-LLM verifier re-derives $R^2 = -0.2461$, Head MAE $= 0.09\text{ g}$, Body MAE $= 51.70\text{ g}$ |
| **`E4`** | **Blinded Referee** (`gemini-4-argon`) $\to$ **Gate 3** (`gates/3_compile_and_query_kg.py`) | `kg/pass1_audit.json` | Isolated worktree without prior audits; checks 7 rubric weights sum to `100` |
| **`E5`** | **Gate 3 KG Compiler** $\to$ **Remediation Agent** (`prompts/03_remediation_prompt.md`) | **Nanopub #1** (`kg/pass1_claim.trig`) | Extracts `pk:evidenceAgainst` RDF triples (`Score: 49.4 / 100 < 80`) |
| **`E6`** | **Pass 2 Builder** (`example/pass2_remediated_fit.py`) $\to$ **Gates 2 & 3** | **Nanopub #2** (`kg/pass2_claim.trig`) | $R^2 = 1.0000$, $\text{RMSE} = 0.0227\text{ g}$, `0` `pk:evidenceAgainst`, `npx:supersedes` Pass 1 (`94.7 / 100`) |

---

## Diagram 2 — Loop 2: How We Do Discovery from the Knowledge Graph (`run_discovery_loop.py`)

![Diagram 2 — Loop 2: Scientific Discovery & Cryptographic Blind Pre-Registration](./media/delphi_discovery_loop.gif)

| Edge | Producer $\to$ Consumer | Payload Passed | Verification Gate |
| :-: | :--- | :--- | :--- |
| **`E7`** | **Gate 4a** (`gates/5_query_kg_for_discovery.py`) $\to$ **Discovery Agent** (`prompts/04_discovery_hypothesis_prompt.md`) | `kg/discovery_anomaly_query.json`, `discovery/discovery_law.lean` | Queries Loop 1 KG ($b_{\text{head}}=2.00$ vs. $b_{\text{body}}=3.00$) & runs `lean discovery/discovery_law.lean` (`0 sorry`) |
| **`E8`** | **Discovery Step 1** (`discovery/1_synthesize_hypotheses.py`) $\to$ **Pre-Reg Step 2** (`prompts/05_blind_preregistration_prompt.md`) | `discovery/ablation_and_hypotheses.json` | 4-way interfamily ablation (`Unwarped 0.616` $\to$ `17-Dot Seesaw 0.572` $\to$ `4p Box 0.370` $\to$ `600-pt Outline 0.767`) |
| **`E9`** | **Pre-Reg Step 2** (`discovery/2_preregister_blind_predictions.py`) $\to$ **Gate 4b** (`gates/6_score_blind_discovery.py`) | `discovery/blind_predictions_locked.csv` + **Nanopub #3** (`kg/discovery_preregistration.trig`) | **Strict Pre-Unblinding Lock:** Commits SHA-256 `fd123b73f8058320...` *before* `heldout_blind_species.csv` is opened |
| **`E10`** | **Gate 4b Blind Scorer** $\to$ **Gate 5** (`gates/7_compile_discovery_kg.py`) | `kg/discovery_blind_sidecar.json` | Verifies locked SHA-256 commitment; scores `H1–H3 CONFIRMED` (`+58.7 dB`) and `H4 FALSIFIED` ($\tau^* = 48.6\text{ Myr}$) |
| **`E11`** | **Gate 5 KG Compiler** $\to$ **Gate 6 MorphoSwarm Bridge** (`gates/8_bridge_morphoswarm_register.py`) | **Nanopub #4** (`kg/discovery_outcome.trig`) + `kg/morphoswarm_register_bridge.json` | Emits `npx:evaluatesPreRegistration` Nanopub #4 and passes all 6 `SPEC-014` detectors (`D1–D5, D8`), `SPEC-060` (`reconstructed`), & `SPEC-074` |

---

## Diagram 3 — The 4-Nanopublication Knowledge Graph Topology (`kg/*.trig`)

![Diagram 3 — Project Delphi RDF Knowledge Graph Topology](./media/delphi_knowledge_graph_network.png)

Every checkpoint across Loop 1 and Loop 2 is a self-contained **RDF Nanopublication** (`.trig`) with 4 named graphs (`sub:Head`, `sub:assertion`, `sub:provenance`, `sub:pubinfo`):
1. **Nanopub #1 (`kg/pass1_claim.trig`):** Pass 1 claim (`49.4 / 100`, $R^2 = -0.2461$) with 2 `pk:evidenceAgainst` remediation triples.
2. **Nanopub #2 (`kg/pass2_claim.trig`):** Remediated Pass 2 head (`94.7 / 100`, $R^2 = 1.0000$), linked via `npx:supersedes` to Nanopub #1.
3. **Nanopub #3 (`kg/discovery_preregistration.trig`):** Cryptographic pre-registration (`a pk:PreRegisteredPrediction`), locking the out-of-sample prediction SHA-256 digest before unblinding.
4. **Nanopub #4 (`kg/discovery_outcome.trig`):** Blind discovery evaluation (`a pk:DiscoveryClaim`, `+58.7 dB`), recording both the 3 confirmed laws (`H1–H3`) and the falsified domain boundary (`H4` above $\tau^* = 48.6\text{ Myr}$), bridged to [MorphoSwarm Studio (`studio.morphoswarm.ai/problems`)](https://studio.morphoswarm.ai/problems) via `kg/morphoswarm_register_bridge.json` (open [`kg/explore_kg.html`](./kg/explore_kg.html) to inspect interactively).

---

## Repository File Map

```text
project-delphi-loop/
├── README.md                                   # Documentation with 3 canonical diagrams (Loop 1, Loop 2, KG Topology)
├── run_loop.py                                 # Loop 1 Runner: Making & Remediating the Knowledge Graph
├── run_discovery_loop.py                       # Loop 2 Runner: KG-Driven Discovery & Blind Pre-Registration
├── query_kg_solver.py                          # Multi-mode KG query solver (`solve`, `defects`, `boundaries`, `theorems`, `morphoswarm`)
├── rubric.json                                 # 7 weighted evaluation dimensions (weights sum to 100)
├── media/
│   ├── delphi_12step_closed_loop.gif           # Diagram 1: Loop 1 (Making & Remediating the Knowledge Graph)
│   ├── delphi_discovery_loop.gif               # Diagram 2: Loop 2 (Scientific Discovery & Blind Pre-Registration)
│   └── delphi_knowledge_graph_network.png      # Diagram 3: 4-Nanopublication RDF Knowledge Graph Topology
├── prompts/                                    # Verbatim agent prompts (01_builder .. 06_discovery_synthesis)
├── gates/                                      # Deterministic zero-LLM verification gates (1_verify .. 8_bridge_morphoswarm)
├── example/                                    # Loop 1 data (`data.csv`), Lean 4 (`law.lean`), Pass 1 & Pass 2 scripts
├── discovery/                                  # Loop 2 Lean 4 (`discovery_law.lean`), datasets, ablation & pre-reg scripts
└── kg/                                         # Emitted `.trig` Nanopublications (#1–#4), sidecars, & `explore_kg.html`
```
