#!/usr/bin/env python3
"""
gates/4_visualize_kg.py — Render the Project Delphi RDF Knowledge Graph,
the Loop 2 Scientific Discovery Architecture (PNG + animated GIF), and the
self-contained interactive HTML Knowledge Graph Explorer (`kg/explore_kg.html`).

Outputs:
  1. `media/delphi_knowledge_graph_network.png` — High-res dark-mode visual map
     of the RDF Knowledge Graph showing the 4 named graphs per Nanopub
     (`sub:Head`, `sub:assertion`, `sub:provenance`, `sub:pubinfo`), the
     `pk:Claim` node, the `pk:evidenceAgainst` remediation nodes, the
     `npx:supersedes` edge from Pass 2 (`94.7/100`) to Pass 1 (`49.4/100`), and
     the Loop 2 Discovery Nanopubs (`discovery_preregistration.trig` ->
     `discovery_outcome.trig`).
  2. `media/delphi_discovery_loop.png` & `media/delphi_discovery_loop.gif` —
     High-res dark-mode visual diagram and animated step-by-step GIF of Loop 2
     ("How We Do Discovery from the Knowledge Graph").
  3. `kg/explore_kg.html` — Interactive zero-dependency HTML/SVG Knowledge Graph
     Explorer covering both Loop 1 (Making the KG) and Loop 2 (Discovery).
"""

from __future__ import annotations

import io
import json
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT_PNG = ROOT / "media" / "delphi_knowledge_graph_network.png"
OUT_DISC_PNG = ROOT / "media" / "delphi_discovery_loop.png"
OUT_DISC_GIF = ROOT / "media" / "delphi_discovery_loop.gif"
OUT_HTML = ROOT / "kg" / "explore_kg.html"


def draw_kg_node(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    rdf_type: str,
    iri_short: str,
    lines: list[str],
    border_col: str,
    badge_col: str,
    bg_col: str = "#161b22",
):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.18,rounding_size=0.8",
            fc=bg_col,
            ec=border_col,
            lw=1.6,
            zorder=3,
        )
    )
    ax.add_patch(
        FancyBboxPatch(
            (x + 0.5, y + h - 3.1),
            w - 1.0,
            2.4,
            boxstyle="round,pad=0.06,rounding_size=0.4",
            fc=badge_col,
            ec="none",
            zorder=4,
        )
    )
    ax.text(
        x + w / 2,
        y + h - 1.9,
        rdf_type,
        color="#f0f6fc",
        fontsize=7.3,
        fontweight="bold",
        family="monospace",
        ha="center",
        va="center",
        zorder=5,
    )
    ax.text(
        x + w / 2,
        y + h - 4.7,
        iri_short,
        color="#58a6ff",
        fontsize=7.8,
        fontweight="bold",
        family="monospace",
        ha="center",
        va="center",
        zorder=5,
    )
    for idx, ln in enumerate(lines):
        col = (
            "#3fb950"
            if ("0.947" in ln or "faithful" in ln or "1.000" in ln or "CONFIRMED" in ln or "+58.7" in ln)
            else (
                "#f85149"
                if ("evidenceAgainst" in ln or "-0.2461" in ln or "needs_remediation" in ln or "FALSIFIED" in ln)
                else "#c9d1d9"
            )
        )
        ax.text(
            x + 0.7,
            y + h - 7.3 - idx * 2.35,
            ln,
            color=col,
            fontsize=6.9,
            family="monospace",
            ha="left",
            va="center",
            zorder=5,
        )


def draw_predicate_edge(
    ax,
    p1: tuple[float, float],
    p2: tuple[float, float],
    predicate: str,
    color: str,
    rad: float = 0.0,
    ls: str = "-",
    lx: float = 0.0,
    ly: float = 0.0,
):
    ax.add_patch(
        FancyArrowPatch(
            p1,
            p2,
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>,head_length=8,head_width=5",
            color=color,
            lw=1.7,
            ls=ls,
            zorder=6,
        )
    )
    mx = (p1[0] + p2[0]) / 2 + lx
    my = (p1[1] + p2[1]) / 2 + ly
    ax.text(
        mx,
        my,
        predicate,
        color="#f0f6fc",
        fontsize=6.9,
        fontweight="bold",
        family="monospace",
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=0.22,rounding_size=0.35", fc="#0d1117", ec=color, lw=1.1),
        zorder=7,
    )


def render_kg_png(out_png: Path):
    BG = "#0d1117"
    STROKE = "#30363d"
    BLUE = "#58a6ff"
    GREEN = "#3fb950"
    AMBER = "#d29922"
    RED = "#f85149"
    PURPLE = "#bc8cff"

    fig, ax = plt.subplots(figsize=(15.0, 9.4), dpi=150, facecolor=BG)
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.add_patch(
        FancyBboxPatch(
            (1.2, 1.8),
            97.6,
            88.5,
            boxstyle="round,pad=0.3,rounding_size=1.4",
            fc=BG,
            ec=STROKE,
            lw=1.2,
            zorder=1,
        )
    )

    ax.text(
        2.2,
        96.2,
        "Project Delphi RDF Knowledge Graph Topology — Loop 1 (Making the KG) & Loop 2 (Discovery)",
        color="#f0f6fc",
        fontsize=13.8,
        fontweight="bold",
        va="center",
    )
    ax.text(
        2.2,
        92.3,
        "Loop 1 (`pass1_claim.trig` -> `pass2_claim.trig`) builds & remediates the KG via `pk:evidenceAgainst`; "
        "Loop 2 (`discovery_preregistration.trig` -> `discovery_outcome.trig`) pre-registers & tests new laws.",
        color=BLUE,
        fontsize=8.5,
        fontweight="bold",
        va="center",
    )

    # LEFT CONTAINER: Pass 1 Nanopublication (`kg/pass1_claim.trig`, 49.4/100)
    ax.add_patch(
        FancyBboxPatch(
            (2.4, 30.0),
            44.0,
            57.5,
            boxstyle="round,pad=0.25,rounding_size=1.1",
            fc="#11161d",
            ec=AMBER,
            lw=1.4,
            ls="--",
            zorder=2,
        )
    )
    ax.text(
        4.0,
        85.0,
        " NANOPUB #1 — Loop 1 Pass 1 (`kg/pass1_claim.trig` · Score: 49.4/100 · Superseded)",
        color=AMBER,
        fontsize=8.6,
        fontweight="bold",
        family="monospace",
        va="center",
    )

    draw_kg_node(
        ax,
        4.0,
        66.0,
        19.5,
        16.5,
        "np:Nanopublication (Head)",
        "delphi:np/pass1-example-claim",
        [
            "np:hasAssertion sub:assertion",
            "np:hasProvenance sub:provenance",
            "np:hasPublicationInfo sub:pubinfo",
            "npx:hasTrustyDigest 'abd43982...'",
        ],
        AMBER,
        "#7c2d12",
    )

    draw_kg_node(
        ax,
        25.2,
        66.0,
        19.6,
        16.5,
        "sub:provenance (Gate 2 Pin)",
        "kg/pass1_sidecar.json",
        [
            "prov:wasAttributedTo pkr:gemini-4-argon",
            "prov:wasDerivedFrom pass1_metrics.json",
            "pk:artifactSha256 '26455f9f9c24...'",
            "Head MAE: 0.09g | Body MAE: 51.70g",
        ],
        BLUE,
        "#1e3a8a",
    )

    draw_kg_node(
        ax,
        4.0,
        47.0,
        40.8,
        16.5,
        "sub:assertion (pk:Claim + pk:LLMClaimAssessment)",
        "pkr:claim-example-allometry (Pass 1 v1)",
        [
            'pk:targetScript "example/pass1_naive_fit.py" ;',
            'pk:measuredR2 "-0.246106"^^xsd:double ; pk:measuredRMSE "44.2323"^^xsd:double ;',
            'pk:hasScore "0.4940"^^xsd:double ; pk:verdict "needs_remediation" ;',
            "Dimension Scores: fidelity=35, match=20, param=40, quant=50, data=95, code=70, repro=90",
        ],
        AMBER,
        "#9a3412",
    )

    draw_kg_node(
        ax,
        4.0,
        31.8,
        40.8,
        13.2,
        "pk:evidenceAgainst (2 Remediation Triples Extracted by Gate 3)",
        "Queried by `gates/3_compile_and_query_kg.py` -> Prompt 3",
        [
            '1. "remediation needed: Fit power law y = a*x^b across all 12 rows (head + body)"',
            '2. "remediation needed: Report exponents b_head & b_body and verify R^2 > 0.99"',
            "--> Injected verbatim into `prompts/03_remediation_prompt.md`!",
        ],
        RED,
        "#991b1b",
    )

    draw_predicate_edge(ax, (13.7, 66.0), (13.7, 63.5), "np:hasAssertion", AMBER, ly=0.2)
    draw_predicate_edge(ax, (35.0, 66.0), (35.0, 63.5), "prov:wasDerivedFrom", BLUE, ly=0.2)
    draw_predicate_edge(ax, (24.4, 47.0), (24.4, 45.0), "pk:evidenceAgainst", RED, ly=0.1)

    # RIGHT CONTAINER: Pass 2 Nanopublication (`kg/pass2_claim.trig`, 94.7/100)
    ax.add_patch(
        FancyBboxPatch(
            (53.6, 30.0),
            44.0,
            57.5,
            boxstyle="round,pad=0.25,rounding_size=1.1",
            fc="#11161d",
            ec=GREEN,
            lw=1.8,
            zorder=2,
        )
    )
    ax.text(
        55.2,
        85.0,
        " NANOPUB #2 — Loop 1 Pass 2 Head (`kg/pass2_claim.trig` · Score: 94.7/100 · Faithful)",
        color=GREEN,
        fontsize=8.6,
        fontweight="bold",
        family="monospace",
        va="center",
    )

    draw_kg_node(
        ax,
        55.2,
        66.0,
        19.5,
        16.5,
        "np:Nanopublication (Head)",
        "delphi:np/pass2-example-claim",
        [
            "npx:supersedes pass1-example-claim",
            "np:hasAssertion sub:assertion",
            "np:hasProvenance sub:provenance",
            "npx:hasTrustyDigest '6bae1985...'",
        ],
        GREEN,
        "#14532d",
    )

    draw_kg_node(
        ax,
        76.4,
        66.0,
        19.6,
        16.5,
        "sub:provenance (Gate 2 Pin)",
        "kg/pass2_sidecar.json",
        [
            "prov:wasAttributedTo pkr:gemini-4-argon",
            "prov:wasDerivedFrom pass2_metrics.json",
            "pk:artifactSha256 'ddb638b2e99b...'",
            "Head MAE: 0.005g | Body MAE: 0.029g",
        ],
        BLUE,
        "#1e3a8a",
    )

    draw_kg_node(
        ax,
        55.2,
        47.0,
        40.8,
        16.5,
        "sub:assertion (pk:Claim + pk:LLMClaimAssessment)",
        "pkr:claim-example-allometry (Pass 2 v2)",
        [
            'pk:targetScript "example/pass2_remediated_fit.py" ;',
            'pk:measuredR2 "1.000000"^^xsd:double ; pk:measuredRMSE "0.0227"^^xsd:double ;',
            'pk:hasScore "0.9471"^^xsd:double ; pk:verdict "faithful" ;',
            "Dimension Scores: fidelity=95, match=96, param=92, quant=95, data=95, code=92, repro=95",
        ],
        GREEN,
        "#15803d",
    )

    draw_kg_node(
        ax,
        55.2,
        31.8,
        40.8,
        13.2,
        "Gate 4a Anomaly Seed -> Triggers Loop 2 (`run_discovery_loop.py`)",
        "Exponent Gap Discovered in KG: b_head = 1.995 vs. b_body = 3.001",
        [
            "• Why does fitting head-heavy landmarks degrade whole-body outlines?",
            "• Seeds `discovery/discovery_law.lean` (0 sorry) + 4-way deconfounding ablation",
            "• Links directly to Nanopub #3 (`discovery_preregistration.trig`) & #4 (`discovery_outcome.trig`)",
        ],
        PURPLE,
        "#581c87",
    )

    draw_predicate_edge(ax, (64.9, 66.0), (64.9, 63.5), "np:hasAssertion", GREEN, ly=0.2)
    draw_predicate_edge(ax, (86.2, 66.0), (86.2, 63.5), "prov:wasDerivedFrom", BLUE, ly=0.2)
    draw_predicate_edge(ax, (75.6, 47.0), (75.6, 45.0), "gates/5_query_kg", PURPLE, ly=0.1)

    draw_predicate_edge(
        ax,
        (55.2, 74.2),
        (23.5, 74.2),
        "npx:supersedes (Immutable Version Chain)",
        GREEN,
        rad=-0.16,
        ly=4.2,
    )

    draw_predicate_edge(
        ax,
        (44.8, 38.4),
        (55.2, 54.0),
        "Prompt 3 resolves\npk:evidenceAgainst",
        RED,
        rad=0.12,
        ls="--",
        lx=0.0,
        ly=-2.2,
    )

    # BOTTOM BAND: Loop 2 Nanopubs (#3 Pre-Registration & #4 Discovery Outcome) + Production Scale
    ax.add_patch(
        FancyBboxPatch(
            (2.4, 3.6),
            95.2,
            23.8,
            boxstyle="round,pad=0.25,rounding_size=1.0",
            fc="#161b22",
            ec=PURPLE,
            lw=1.4,
            zorder=2,
        )
    )
    ax.text(
        4.0,
        25.0,
        "LOOP 2 DISCOVERY NANOPUBLICATIONS (`kg/discovery_*.trig`) & REAL-WORLD PRODUCTION SCALE (80 SIGNED NANOPUBS)",
        color="#f0f6fc",
        fontsize=8.8,
        fontweight="bold",
        va="center",
    )

    prod_batches = [
        (
            "Nanopub #3: Blind Preregistration",
            "kg/discovery_preregistration.trig",
            "delphi:np/discovery-preregistration",
            "• Locks 16 out-of-sample predictions\n• SHA-256 `fd123b73f805...` pinned\n  BEFORE unblinding `heldout_blind_species.csv`",
            AMBER,
        ),
        (
            "Nanopub #4: Discovery Outcome",
            "kg/discovery_outcome.trig",
            "delphi:np/discovery-outcome-claim",
            "• `npx:evaluatesPreRegistration` -> #3\n• CONFIRMED: H1, H2, H3 (+58.7 dB)\n• FALSIFIED: H4 > 48.6 Myr Horizon",
            GREEN,
        ),
        (
            "Thompson 1917 Production Audit",
            "17 Signed Audit Nanopubs",
            "RAYFKAfyOnqIKXWzdEzCN...",
            "• 9 Primary (`claude-fable-5-1`: 76.6)\n• 8 Blinded (`gemini-4-argon`: 90.8)\n• `pk:evidenceAgainst` sparked 600-pt fit",
            BLUE,
        ),
        (
            "FishShapes v1 + 15-Clade Portfolio",
            "90+ Production Nanopubs",
            "RAilN4nb... -> RAJancw...",
            "• 10,888 species locked before download\n• 5,180 blind species (`p = 10^-103`)\n• 15-Clade Cross-Kingdom GM Portfolio",
            PURPLE,
        ),
    ]

    bx_coords = [4.0, 27.6, 51.2, 74.8]
    bw = 21.8
    for (btitle, bcount, buri, bdesc, bcol), bx in zip(prod_batches, bx_coords):
        ax.add_patch(
            FancyBboxPatch(
                (bx, 5.2),
                bw,
                17.4,
                boxstyle="round,pad=0.15,rounding_size=0.7",
                fc="#0d1117",
                ec=bcol,
                lw=1.2,
                zorder=3,
            )
        )
        ax.text(bx + 0.8, 20.6, btitle, color="#f0f6fc", fontsize=7.6, fontweight="bold", va="center", zorder=4)
        ax.text(bx + 0.8, 18.2, bcount, color=bcol, fontsize=7.2, fontweight="bold", va="center", zorder=4)
        ax.text(bx + 0.8, 15.9, buri, color=BLUE, fontsize=6.5, family="monospace", va="center", zorder=4)
        ax.text(bx + 0.8, 10.2, bdesc, color="#c9d1d9", fontsize=6.6, linespacing=1.28, va="center", zorder=4)

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, facecolor=BG)
    plt.close(fig)
    print(f"Saved Knowledge Graph visual map to {out_png}")


def render_discovery_loop_diagram(out_png: Path, out_gif: Path):
    BG = "#0d1117"
    CARD = "#161b22"
    ACTIVE_BG = "#1e293b"
    STROKE = "#30363d"
    BLUE = "#58a6ff"
    GREEN = "#3fb950"
    AMBER = "#d29922"
    RED = "#f85149"
    PURPLE = "#bc8cff"

    STEPS = [
        (
            1,
            "STEP D1 — Query Loop 1 KG & Pin Lean 4 Laws",
            "Gate 4a: `gates/5_query_kg_for_discovery.py`",
            BLUE,
            (4.0, 56.0, 28.0, 27.0),
            [
                "• Reads `kg/pass1_claim.trig` & `kg/pass2_claim.trig`",
                "• Extracts exponent gap: b_head=2.0 vs b_body=3.0",
                "• Verifies `discovery/discovery_law.lean` (0 sorry)",
                "• Verifies `landmark_vs_outline_data.csv` SHA-256",
                "• Emits `kg/discovery_anomaly_query.json`",
            ],
        ),
        (
            2,
            "STEP D2 — 4-Way Ablation & Hypothesis Synthesis",
            "Agent: `discovery/1_synthesize_hypotheses.py` (Prompt 4)",
            PURPLE,
            (36.0, 56.0, 28.0, 27.0),
            [
                "• Ablation 1: 17-Dot Head Seesaw degrades IoU",
                "  (0.616 -> 0.572) vs 600-pt Outline (0.767)",
                "• Ablation 2: 4p Box (0.370) vs True Warp (+0.396)",
                "• Ablation 3: Sympatric Head/Body Rate = 4.78x",
                "• Synthesizes falsifiable H1, H2, H3, and null H4",
            ],
        ),
        (
            3,
            "STEP D3 — Cryptographic Blind Pre-Registration",
            "Agent: `discovery/2_preregister_blind_predictions.py` (Prompt 5)",
            AMBER,
            (68.0, 56.0, 28.0, 27.0),
            [
                "• STRICT BLINDING: Never touches held-out data!",
                "• Writes `discovery/blind_predictions_locked.csv`",
                "• Computes SHA-256 lock `fd123b73f8058320...`",
                "• Emits Nanopub #3: `discovery_preregistration.trig`",
                "• Linked via `prov:wasDerivedFrom` -> Pass 2 KG",
            ],
        ),
        (
            4,
            "STEP D4 — Zero-LLM Blind Unblinding & Falsification",
            "Gate 4b: `gates/6_score_blind_discovery.py`",
            RED,
            (18.0, 12.0, 31.0, 29.0),
            [
                "• Verifies SHA-256 of locked predictions BEFORE",
                "  unblinding `discovery/heldout_blind_species.csv`",
                "• H1 (Outline Recovery 8/8): CONFIRMED (+24.1 dB)",
                "• H2 (Error vs tau r=0.979): CONFIRMED (+18.4 dB)",
                "• H3 (Sympatric 4.75x Jaw): CONFIRMED (+16.2 dB)",
                "• H4 (>50 Myr 17-Dot Grid): FALSIFIED (tau*=48.6 Myr)",
            ],
        ),
        (
            5,
            "STEP D5 — Discovery Outcome Nanopub & KG Update",
            "Gate 5: `gates/7_compile_discovery_kg.py` (Prompt 6)",
            GREEN,
            (54.0, 12.0, 34.0, 29.0),
            [
                "• Emits Nanopub #4: `kg/discovery_outcome.trig`",
                "• Predicate `npx:evaluatesPreRegistration` -> #3",
                "• Records 3 Confirmed Laws (`+58.7 dB` combined)",
                "• Records Honest Falsification of H4 (`tau* = 48.6 Myr`)",
                "• Updates Knowledge Graph with domain boundary!",
            ],
        ),
    ]

    def draw_disc_frame(active_step: int | None = None) -> Image.Image:
        fig, ax = plt.subplots(figsize=(14.5, 8.6), dpi=140, facecolor=BG)
        fig.subplots_adjust(0, 0, 1, 1)
        ax.set_facecolor(BG)
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis("off")

        ax.add_patch(
            FancyBboxPatch(
                (1.2, 2.0),
                97.6,
                87.0,
                boxstyle="round,pad=0.3,rounding_size=1.4",
                fc=BG,
                ec=STROKE,
                lw=1.2,
                zorder=1,
            )
        )

        ax.text(
            2.2,
            95.5,
            "Project Delphi Loop 2 — Knowledge-Graph-Driven Scientific Discovery & Blind Pre-Registration",
            color="#f0f6fc",
            fontsize=13.5,
            fontweight="bold",
            va="center",
        )
        ax.text(
            2.2,
            91.4,
            "Starts from Loop 1 KG (`kg/pass2_claim.trig`) -> Synthesizes Deconfounded Hypotheses + Lean 4 Proofs -> "
            "Locks Pre-Registration SHA-256 BEFORE Unblinding -> Scores Held-Out Data (+58.7 dB)",
            color=GREEN if active_step in (None, 5) else BLUE,
            fontsize=8.5,
            fontweight="bold",
            va="center",
        )

        for snum, stitle, sgate, scol, (x, y, w, h), lines in STEPS:
            is_act = active_step == snum
            ax.add_patch(
                FancyBboxPatch(
                    (x, y),
                    w,
                    h,
                    boxstyle="round,pad=0.22,rounding_size=1.0",
                    fc=ACTIVE_BG if is_act else CARD,
                    ec=scol if (is_act or active_step is None) else STROKE,
                    lw=2.5 if is_act else 1.5,
                    zorder=3,
                )
            )
            ax.add_patch(
                FancyBboxPatch(
                    (x + 0.6, y + h - 3.6),
                    w - 1.2,
                    2.8,
                    boxstyle="round,pad=0.08,rounding_size=0.45",
                    fc=scol,
                    ec="none",
                    zorder=4,
                )
            )
            ax.text(
                x + w / 2,
                y + h - 2.2,
                stitle,
                color="#0d1117" if scol in (GREEN, AMBER, BLUE) else "#f0f6fc",
                fontsize=8.0,
                fontweight="bold",
                family="monospace",
                ha="center",
                va="center",
                zorder=5,
            )
            ax.text(
                x + 0.8,
                y + h - 6.0,
                sgate,
                color=scol,
                fontsize=7.3,
                fontweight="bold",
                family="monospace",
                va="center",
                zorder=5,
            )
            for idx, ln in enumerate(lines):
                lcol = (
                    GREEN
                    if ("CONFIRMED" in ln or "+58.7" in ln or "0 sorry" in ln)
                    else (RED if "FALSIFIED" in ln or "degrades" in ln else "#c9d1d9")
                )
                ax.text(
                    x + 0.8,
                    y + h - 9.4 - idx * 3.1,
                    ln,
                    color=lcol,
                    fontsize=7.1,
                    family="monospace",
                    va="center",
                    zorder=5,
                )

        # Arrows connecting the 5 steps + closed feedback to KG
        draw_predicate_edge(ax, (32.0, 69.5), (36.0, 69.5), "E7: Anomaly\n+ Lean 4", BLUE, ly=3.5)
        draw_predicate_edge(ax, (64.0, 69.5), (68.0, 69.5), "E8: H1..H4\nAblations", PURPLE, ly=3.5)
        draw_predicate_edge(
            ax,
            (82.0, 56.0),
            (33.5, 41.0),
            "E9: SHA-256 Locked Nanopub #3 (`discovery_preregistration.trig`)",
            AMBER,
            rad=-0.12,
            ly=2.2,
        )
        draw_predicate_edge(ax, (49.0, 26.5), (54.0, 26.5), "E10: Blind\nSidecar", RED, ly=3.8)
        draw_predicate_edge(
            ax,
            (54.0, 16.0),
            (12.0, 56.0),
            "E11: Updates KG with Confirmed Laws (+58.7 dB) & Honest Domain Boundary (tau* = 48.6 Myr)",
            GREEN,
            rad=-0.22,
            ls="--",
            ly=-4.2,
        )

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=140, facecolor=BG)
        plt.close(fig)
        buf.seek(0)
        return Image.open(buf).convert("RGB")

    summary_img = draw_disc_frame(None)
    frames = [draw_disc_frame(s) for s in (1, 2, 3, 4, 5)] + [summary_img, summary_img]
    frames[0].save(
        out_gif,
        save_all=True,
        append_images=frames[1:],
        duration=[900, 900, 900, 900, 900, 1400, 1400],
        loop=0,
    )
    print(f"Saved Loop 2 Discovery animated GIF to {out_gif}")


def build_interactive_html(out_html: Path):
    p1_trig = (ROOT / "kg" / "pass1_claim.trig").read_text(encoding="utf-8")
    p2_trig = (ROOT / "kg" / "pass2_claim.trig").read_text(encoding="utf-8")
    p1_sidecar = (ROOT / "kg" / "pass1_sidecar.json").read_text(encoding="utf-8")
    p2_sidecar = (ROOT / "kg" / "pass2_sidecar.json").read_text(encoding="utf-8")
    prereg_trig = (ROOT / "kg" / "discovery_preregistration.trig").read_text(encoding="utf-8")
    disc_trig = (ROOT / "kg" / "discovery_outcome.trig").read_text(encoding="utf-8")
    disc_sidecar = (ROOT / "kg" / "discovery_blind_sidecar.json").read_text(encoding="utf-8")
    ms_bridge_path = ROOT / "kg" / "morphoswarm_register_bridge.json"
    ms_bridge = ms_bridge_path.read_text(encoding="utf-8") if ms_bridge_path.exists() else "{}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Project Delphi — Interactive RDF Knowledge Graph & Discovery Explorer</title>
<style>
  :root {{
    --bg: #0d1117;
    --card: #161b22;
    --elev: #1f2937;
    --border: #30363d;
    --text: #f0f6fc;
    --muted: #8b949e;
    --blue: #58a6ff;
    --green: #3fb950;
    --amber: #d29922;
    --red: #f85149;
    --purple: #bc8cff;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 24px;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }}
  h1 {{ margin: 0 0 6px 0; font-size: 22px; }}
  .subtitle {{ color: var(--muted); font-size: 14px; margin-bottom: 20px; }}
  .layout {{
    display: grid;
    grid-template-columns: 1.35fr 1fr;
    gap: 20px;
    align-items: start;
  }}
  .panel {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
  }}
  .node-btn {{
    cursor: pointer;
    transition: opacity 0.15s;
  }}
  .node-btn:hover {{ opacity: 0.88; }}
  pre {{
    background: #090d13;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px;
    overflow-x: auto;
    font-size: 12px;
    line-height: 1.45;
    color: #e6edf3;
    margin: 8px 0 0 0;
  }}
  .tabs {{ display: flex; gap: 8px; margin-top: 14px; flex-wrap: wrap; }}
  .tab {{
    background: var(--elev);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
    cursor: pointer;
  }}
  .tab.active {{ border-color: var(--blue); background: #1e293b; color: var(--blue); font-weight: 600; }}
</style>
</head>
<body>
  <h1>Project Delphi — Interactive RDF Knowledge Graph & Discovery Explorer</h1>
  <div class="subtitle">
    Click any RDF Nanopublication node across <b>Loop 1 (Making the Knowledge Graph)</b> and
    <b>Loop 2 (Scientific Discovery &amp; Blind Pre-Registration)</b> to inspect its exact <code>.trig</code> triples and sidecar JSON payloads.
  </div>

  <div class="layout">
    <div class="panel">
      <svg viewBox="0 0 820 740" width="100%" style="background:#090d13;border-radius:8px;border:1px solid #30363d;">
        <defs>
          <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#3fb950"/>
          </marker>
          <marker id="arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#f85149"/>
          </marker>
          <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#58a6ff"/>
          </marker>
          <marker id="arrow-amber" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#d29922"/>
          </marker>
        </defs>

        <!-- Loop 1 Header -->
        <text x="25" y="26" fill="#58a6ff" font-size="12" font-family="monospace" font-weight="bold">LOOP 1: MAKING &amp; REMEDIATING THE KNOWLEDGE GRAPH (`python3 run_loop.py`)</text>

        <!-- Edges Loop 1 -->
        <path d="M 520 75 Q 395 30 270 75" fill="none" stroke="#3fb950" stroke-width="2.5" marker-end="url(#arrow-green)"/>
        <text x="395" y="42" fill="#3fb950" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle">npx:supersedes</text>

        <line x1="155" y1="115" x2="155" y2="170" stroke="#d29922" stroke-width="2" marker-end="url(#arrow-blue)"/>
        <line x1="155" y1="255" x2="155" y2="315" stroke="#f85149" stroke-width="2.2" marker-end="url(#arrow-red)"/>
        <text x="155" y="290" fill="#f85149" font-size="10" font-family="monospace" font-weight="bold" text-anchor="middle">pk:evidenceAgainst (2)</text>

        <path d="M 290 355 Q 410 355 520 215" fill="none" stroke="#f85149" stroke-width="2.2" stroke-dasharray="6,4" marker-end="url(#arrow-red)"/>
        <text x="415" y="315" fill="#f85149" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle">Prompt 3 resolves</text>

        <line x1="645" y1="115" x2="645" y2="170" stroke="#3fb950" stroke-width="2" marker-end="url(#arrow-green)"/>
        <line x1="645" y1="255" x2="645" y2="315" stroke="#58a6ff" stroke-width="2" marker-end="url(#arrow-blue)"/>

        <!-- Node 1: Pass 1 Head -->
        <g class="node-btn" onclick="selectNode('p1_head')">
          <rect x="40" y="45" width="230" height="70" rx="8" fill="#161b22" stroke="#d29922" stroke-width="2"/>
          <text x="155" y="70" fill="#d29922" font-size="12" font-family="monospace" font-weight="bold" text-anchor="middle">Nanopub #1 (Pass 1)</text>
          <text x="155" y="92" fill="#f0f6fc" font-size="11" font-family="monospace" text-anchor="middle">delphi:np/pass1-example-claim</text>
        </g>

        <!-- Node 2: Pass 1 Assertion -->
        <g class="node-btn" onclick="selectNode('p1_assertion')">
          <rect x="40" y="170" width="230" height="85" rx="8" fill="#161b22" stroke="#d29922" stroke-width="2"/>
          <text x="155" y="195" fill="#f0f6fc" font-size="12" font-family="monospace" font-weight="bold" text-anchor="middle">pk:Claim (Pass 1 v1)</text>
          <text x="155" y="216" fill="#f85149" font-size="11" font-family="monospace" text-anchor="middle">pk:hasScore "0.4940" (49.4/100)</text>
          <text x="155" y="236" fill="#8b949e" font-size="11" font-family="monospace" text-anchor="middle">R² = -0.2461 | RMSE = 44.23g</text>
        </g>

        <!-- Node 3: Pass 1 evidenceAgainst -->
        <g class="node-btn" onclick="selectNode('p1_remediation')">
          <rect x="25" y="315" width="265" height="80" rx="8" fill="#2a1215" stroke="#f85149" stroke-width="2.2"/>
          <text x="157" y="340" fill="#f85149" font-size="12" font-family="monospace" font-weight="bold" text-anchor="middle">pk:evidenceAgainst (Trigger)</text>
          <text x="157" y="362" fill="#f0f6fc" font-size="10.5" font-family="monospace" text-anchor="middle">1. Fit power law y=a*x^b on all 12 rows</text>
          <text x="157" y="380" fill="#f0f6fc" font-size="10.5" font-family="monospace" text-anchor="middle">2. Report b_head &amp; b_body (R² &gt; 0.99)</text>
        </g>

        <!-- Node 4: Pass 2 Head -->
        <g class="node-btn" onclick="selectNode('p2_head')">
          <rect x="520" y="45" width="250" height="70" rx="8" fill="#161b22" stroke="#3fb950" stroke-width="2.2"/>
          <text x="645" y="70" fill="#3fb950" font-size="12" font-family="monospace" font-weight="bold" text-anchor="middle">Nanopub #2 (Pass 2 Head)</text>
          <text x="645" y="92" fill="#f0f6fc" font-size="11" font-family="monospace" text-anchor="middle">delphi:np/pass2-example-claim</text>
        </g>

        <!-- Node 5: Pass 2 Assertion -->
        <g class="node-btn" onclick="selectNode('p2_assertion')">
          <rect x="520" y="170" width="250" height="85" rx="8" fill="#12261e" stroke="#3fb950" stroke-width="2.2"/>
          <text x="645" y="195" fill="#f0f6fc" font-size="12" font-family="monospace" font-weight="bold" text-anchor="middle">pk:Claim (Pass 2 Remediated)</text>
          <text x="645" y="216" fill="#3fb950" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle">pk:hasScore "0.9471" (94.7/100)</text>
          <text x="645" y="236" fill="#c9d1d9" font-size="11" font-family="monospace" text-anchor="middle">R² = 1.0000 | RMSE = 0.0227g</text>
        </g>

        <!-- Node 6: Pass 2 Sidecar -->
        <g class="node-btn" onclick="selectNode('p2_sidecar')">
          <rect x="520" y="315" width="250" height="80" rx="8" fill="#161b22" stroke="#58a6ff" stroke-width="2"/>
          <text x="645" y="340" fill="#58a6ff" font-size="12" font-family="monospace" font-weight="bold" text-anchor="middle">Gate 2 Sidecar &amp; Anomaly Seed</text>
          <text x="645" y="362" fill="#c9d1d9" font-size="10.5" font-family="monospace" text-anchor="middle">b_head = 2.00 vs b_body = 3.00</text>
          <text x="645" y="380" fill="#bc8cff" font-size="10.5" font-family="monospace" text-anchor="middle">Seeds Loop 2 Discovery Query!</text>
        </g>

        <!-- Divider -->
        <line x1="20" y1="420" x2="800" y2="420" stroke="#30363d" stroke-width="1.5" stroke-dasharray="4,4"/>
        <text x="25" y="445" fill="#bc8cff" font-size="12" font-family="monospace" font-weight="bold">LOOP 2: SCIENTIFIC DISCOVERY &amp; BLIND PRE-REGISTRATION (`python3 run_discovery_loop.py`)</text>

        <!-- Edge from Pass 2 to Nanopub #3 -->
        <path d="M 520 385 Q 340 435 200 470" fill="none" stroke="#d29922" stroke-width="2.2" marker-end="url(#arrow-amber)"/>
        <text x="360" y="460" fill="#d29922" font-size="10.5" font-family="monospace" font-weight="bold" text-anchor="middle">prov:wasDerivedFrom + SHA-256 Lock</text>

        <!-- Node 7: Nanopub #3 Pre-Registration -->
        <g class="node-btn" onclick="selectNode('disc_prereg')">
          <rect x="25" y="470" width="330" height="125" rx="8" fill="#1f1a10" stroke="#d29922" stroke-width="2.2"/>
          <text x="190" y="495" fill="#d29922" font-size="12" font-family="monospace" font-weight="bold" text-anchor="middle">Nanopub #3: pk:PreRegisteredPrediction</text>
          <text x="190" y="516" fill="#f0f6fc" font-size="11" font-family="monospace" text-anchor="middle">delphi:np/discovery-preregistration</text>
          <text x="190" y="538" fill="#c9d1d9" font-size="10.5" font-family="monospace" text-anchor="middle">SHA-256: fd123b73f8058320... (Locked BEFORE unblinding)</text>
          <text x="190" y="558" fill="#3fb950" font-size="10.5" font-family="monospace" text-anchor="middle">Registers H1, H2, H3, H4 + tau* = 48.8 Myr</text>
          <text x="190" y="578" fill="#58a6ff" font-size="10.5" font-family="monospace" text-anchor="middle">Lean 4: discovery/discovery_law.lean (0 sorry)</text>
        </g>

        <!-- Edge from Nanopub #3 to Nanopub #4 -->
        <line x1="355" y1="532" x2="465" y2="532" stroke="#3fb950" stroke-width="2.5" marker-end="url(#arrow-green)"/>
        <text x="410" y="518" fill="#3fb950" font-size="10" font-family="monospace" font-weight="bold" text-anchor="middle">Gate 4b Unblinds</text>

        <!-- Node 8: Nanopub #4 Discovery Outcome -->
        <g class="node-btn" onclick="selectNode('disc_outcome')">
          <rect x="465" y="470" width="330" height="125" rx="8" fill="#12261e" stroke="#3fb950" stroke-width="2.2"/>
          <text x="630" y="495" fill="#3fb950" font-size="12" font-family="monospace" font-weight="bold" text-anchor="middle">Nanopub #4: pk:DiscoveryClaim (+58.7 dB)</text>
          <text x="630" y="516" fill="#f0f6fc" font-size="11" font-family="monospace" text-anchor="middle">delphi:np/discovery-outcome-claim</text>
          <text x="630" y="538" fill="#3fb950" font-size="10.5" font-family="monospace" text-anchor="middle">CONFIRMED: H1 (8/8), H2 (r=0.979), H3 (4.75x Jaw)</text>
          <text x="630" y="558" fill="#f85149" font-size="10.5" font-family="monospace" text-anchor="middle">FALSIFIED: H4 &gt; 50 Myr (Horizon tau* = 48.6 Myr)</text>
          <text x="630" y="578" fill="#c9d1d9" font-size="10.5" font-family="monospace" text-anchor="middle">npx:evaluatesPreRegistration -&gt; Nanopub #3</text>
        </g>

        <!-- Edge from Nanopub #4 to MorphoSwarm Bridge -->
        <line x1="630" y1="595" x2="630" y2="628" stroke="#58a6ff" stroke-width="2.2" marker-end="url(#arrow-blue)"/>
        <path d="M 190 595 Q 190 620 260 628" fill="none" stroke="#58a6ff" stroke-width="2.0" marker-end="url(#arrow-blue)"/>

        <!-- Node 9: MorphoSwarm Studio Bridge -->
        <g class="node-btn" onclick="selectNode('ms_bridge')">
          <rect x="25" y="630" width="770" height="90" rx="8" fill="#111b27" stroke="#58a6ff" stroke-width="2.2"/>
          <text x="410" y="654" fill="#58a6ff" font-size="12" font-family="monospace" font-weight="bold" text-anchor="middle">Gate 6: MorphoSwarm Studio Bridge (`kg/morphoswarm_register_bridge.json` -&gt; `studio.morphoswarm.ai/problems`)</text>
          <text x="410" y="676" fill="#3fb950" font-size="10.5" font-family="monospace" text-anchor="middle">SPEC-014 Detectors: 6/6 PASSED (D1, D2, D3, D4, D5, D8) | SPEC-060 Pack: `fit-only` -&gt; `reconstructed` (R1-R6)</text>
          <text x="410" y="698" fill="#f0f6fc" font-size="10.5" font-family="monospace" text-anchor="middle">SPEC-074 Tab 2 (`inferred-gap`): 0 -&gt; 2 Populated | Tab 1: 3 Open Problems Bound (`0 impl -&gt; 1 impl`) | Tab 3: 6 Specs Resolved</text>
        </g>
      </svg>
    </div>

    <div class="panel">
      <div id="node-title" style="font-size:16px;font-weight:700;color:var(--blue);">
        Click any node in the RDF graph to inspect its contents
      </div>
      <div id="node-desc" style="font-size:13px;color:var(--muted);margin-top:6px;">
        Inspect exact RDF TriG and zero-LLM sidecar JSON payloads across Loop 1 and Loop 2.
      </div>
      <div class="tabs">
        <button class="tab active" onclick="selectNode('p1_remediation')">Loop 1: pk:evidenceAgainst</button>
        <button class="tab" onclick="selectNode('p1_head')">Nanopub #1 (Pass 1 .trig)</button>
        <button class="tab" onclick="selectNode('p2_head')">Nanopub #2 (Pass 2 .trig)</button>
        <button class="tab" onclick="selectNode('disc_prereg')">Nanopub #3 (Pre-Reg .trig)</button>
        <button class="tab" onclick="selectNode('disc_outcome')">Nanopub #4 (Discovery .trig)</button>
        <button class="tab" onclick="selectNode('disc_sidecar')">Loop 2 Blind Sidecar (.json)</button>
        <button class="tab" onclick="selectNode('ms_bridge')">MorphoSwarm Bridge (.json)</button>
      </div>
      <pre id="code-box"></pre>
    </div>
  </div>

<script>
const PAYLOADS = {{
  p1_remediation: {{
    title: "Loop 1 Trigger — pk:evidenceAgainst Triples (Gate 3 -> Prompt 3)",
    desc: "When Pass 1 scores 49.4/100 (< 80), `gates/3_compile_and_query_kg.py` queries `kg/pass1_claim.trig` for `pk:evidenceAgainst` and passes these exact lines into `prompts/03_remediation_prompt.md`:",
    code: `pk:evidenceAgainst
  "remediation needed: Fit the power law y = a * x^b across the full organism (all 12 rows of example/data.csv, accounting for both head and body modules) instead of fitting a linear line only to the 6 head rows (line 49)." ,
  "remediation needed: Report the fitted power-law exponents b_head and b_body and verify that full-dataset R^2 exceeds 0.99." ;`
  }},
  p1_head: {{
    title: "Nanopub #1 — Pass 1 RDF Nanopublication (kg/pass1_claim.trig — 49.4/100)",
    desc: "Full TriG file emitted by Gate 3 (`gates/3_compile_and_query_kg.py --pass-num 1`) with 4 named graphs (`Head`, `assertion`, `provenance`, `pubinfo`):",
    code: {json.dumps(p1_trig)}
  }},
  p2_head: {{
    title: "Nanopub #2 — Pass 2 RDF Nanopublication (kg/pass2_claim.trig — 94.7/100, npx:supersedes #1)",
    desc: "Full TriG file emitted after Pass 2 remediation (`gates/3_compile_and_query_kg.py --pass-num 2`), superseding Pass 1:",
    code: {json.dumps(p2_trig)}
  }},
  p1_assertion: {{
    title: "Gate 2 Deterministic Sidecar — Pass 1 (kg/pass1_sidecar.json)",
    desc: "Zero-LLM sidecar verification showing why Pass 1 failed (`r2_all = -0.2461`, `mae_body_subset_g = 51.7015 g`):",
    code: {json.dumps(p1_sidecar)}
  }},
  p2_sidecar: {{
    title: "Gate 2 Deterministic Sidecar — Pass 2 (kg/pass2_sidecar.json)",
    desc: "Zero-LLM sidecar verification after Pass 2 remediation (`r2_all = 1.0000`, `rmse_all_g = 0.0227 g`):",
    code: {json.dumps(p2_sidecar)}
  }},
  p2_assertion: {{
    title: "Pass 2 Assertion Graph (pkr:claim-example-allometry)",
    desc: "Converged claim with 0 `pk:evidenceAgainst` items remaining (`pk:hasScore = 0.9471`):",
    code: {json.dumps(p2_trig)}
  }},
  disc_prereg: {{
    title: "Nanopub #3 — Cryptographic Pre-Registration (kg/discovery_preregistration.trig)",
    desc: "Minted by `discovery/2_preregister_blind_predictions.py` BEFORE `discovery/heldout_blind_species.csv` is ever read, locking the prediction CSV SHA-256 hash into the Knowledge Graph:",
    code: {json.dumps(prereg_trig)}
  }},
  disc_outcome: {{
    title: "Nanopub #4 — Blind Discovery Outcome (kg/discovery_outcome.trig — +58.7 dB)",
    desc: "Minted by `gates/7_compile_discovery_kg.py` after Gate 4b verifies the pre-registration SHA-256 lock and scores all 4 hypotheses on held-out species (confirming H1, H2, H3 and falsifying H4 above tau* = 48.6 Myr):",
    code: {json.dumps(disc_trig)}
  }},
  disc_sidecar: {{
    title: "Gate 4b Zero-LLM Blind Discovery Sidecar (kg/discovery_blind_sidecar.json)",
    desc: "Deterministic out-of-sample evaluation report with Bayesian Weight of Evidence in decibans (+58.7 dB) and the discovered modularity horizon tau* = 48.6 Myr:",
    code: {json.dumps(disc_sidecar)}
  }},
  ms_bridge: {{
    title: "Gate 6 MorphoSwarm Studio Bridge (kg/morphoswarm_register_bridge.json)",
    desc: "Bridges the signed Knowledge Graph (Nanopubs #1-#4 + Lean 4) to studio.morphoswarm.ai/problems (SPEC-074 Tab 1/Tab 2/Tab 3, SPEC-060 R1-R6 reconstruction, and SPEC-014 D1-D8 integrity detectors):",
    code: {json.dumps(ms_bridge)}
  }}
}};

function selectNode(key) {{
  const item = PAYLOADS[key] || PAYLOADS.p1_remediation;
  document.getElementById("node-title").textContent = item.title;
  document.getElementById("node-desc").textContent = item.desc;
  document.getElementById("code-box").textContent = item.code;
}}
selectNode("disc_outcome");
</script>
</body>
</html>
"""
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html, encoding="utf-8")
    print(f"Saved interactive HTML Knowledge Graph Explorer to {out_html}")


def main() -> int:
    render_kg_png(OUT_PNG)
    render_discovery_loop_diagram(OUT_DISC_PNG, OUT_DISC_GIF)
    build_interactive_html(OUT_HTML)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
