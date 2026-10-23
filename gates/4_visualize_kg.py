#!/usr/bin/env python3
"""
gates/4_visualize_kg.py — Render the Project Delphi RDF Knowledge Graph &
generate a self-contained interactive HTML Knowledge Graph Explorer.

Outputs:
  1. `media/delphi_knowledge_graph_network.png` — High-res dark-mode visual map
     of the RDF Knowledge Graph showing the 4 named graphs per Nanopub
     (`sub:Head`, `sub:assertion`, `sub:provenance`, `sub:pubinfo`), the
     `pk:Claim` node, the 7 dimension score nodes (`pk:hasScore`), the
     `pk:evidenceAgainst` remediation nodes, and the `npx:supersedes` edge
     from Pass 2 (`94.7/100`) to Pass 1 (`49.4/100`).
  2. `kg/explore_kg.html` — Interactive zero-dependency HTML/SVG Knowledge Graph
     Explorer where any reviewer can click every RDF node/edge and inspect its
     exact `.trig` triples, SHA-256 digests, and scores.
"""

from __future__ import annotations

import json
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT_PNG = ROOT / "media" / "delphi_knowledge_graph_network.png"
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
    # Type pill
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
        col = "#3fb950" if "0.9470" in ln or "faithful" in ln or "1.000" in ln else (
            "#f85149" if "evidenceAgainst" in ln or "-0.2461" in ln or "needs_remediation" in ln else "#c9d1d9"
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

    # Outer border
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

    # Header
    ax.text(
        2.2,
        96.2,
        "Project Delphi RDF Knowledge Graph Topology & Nanopublication Contents (`kg/*.trig`)",
        color="#f0f6fc",
        fontsize=14.0,
        fontweight="bold",
        va="center",
    )
    ax.text(
        2.2,
        92.3,
        "Every Nanopublication contains 4 Named RDF Graphs (`sub:Head`, `sub:assertion`, `sub:provenance`, `sub:pubinfo`). "
        "Pass 2 (`94.7/100`) links to Pass 1 (`49.4/100`) via `npx:supersedes` after resolving `pk:evidenceAgainst`.",
        color=BLUE,
        fontsize=8.6,
        fontweight="bold",
        va="center",
    )

    # -------------------------------------------------------------------------
    # LEFT CONTAINER: Pass 1 Nanopublication (`kg/pass1_claim.trig`, 49.4/100)
    # -------------------------------------------------------------------------
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
        " NANOPUB #1 — Pass 1 Checkpoint (`kg/pass1_claim.trig` · Score: 49.4/100 · Replaced)",
        color=AMBER,
        fontsize=8.8,
        fontweight="bold",
        family="monospace",
        va="center",
    )

    # Node P1 Head & Pubinfo
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
            "npx:hasTrustyDigest 'b883f259...'",
        ],
        AMBER,
        "#7c2d12",
    )

    # Node P1 Provenance & Sidecar
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

    # Node P1 Assertion (`pk:Claim` + `pk:LLMClaimAssessment`)
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
            'pk:measuredR2 "-0.246056"^^xsd:double ; pk:measuredRMSE "44.2323"^^xsd:double ;',
            'pk:hasScore "0.4940"^^xsd:double ; pk:verdict "needs_remediation" ;',
            "Dimension Scores: fidelity=35, match=20, param=40, quant=50, data=95, code=70, repro=90",
        ],
        AMBER,
        "#9a3412",
    )

    # Node P1 `pk:evidenceAgainst` (The Trigger!)
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

    # Internal edges in Pass 1
    draw_predicate_edge(ax, (13.7, 66.0), (13.7, 63.5), "np:hasAssertion", AMBER, ly=0.2)
    draw_predicate_edge(ax, (35.0, 66.0), (35.0, 63.5), "prov:wasDerivedFrom", BLUE, ly=0.2)
    draw_predicate_edge(ax, (24.4, 47.0), (24.4, 45.0), "pk:evidenceAgainst", RED, ly=0.1)

    # -------------------------------------------------------------------------
    # RIGHT CONTAINER: Pass 2 Nanopublication (`kg/pass2_claim.trig`, 94.7/100)
    # -------------------------------------------------------------------------
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
        " NANOPUB #2 — Pass 2 Active Head (`kg/pass2_claim.trig` · Score: 94.7/100 · Faithful)",
        color=GREEN,
        fontsize=8.8,
        fontweight="bold",
        family="monospace",
        va="center",
    )

    # Node P2 Head & Pubinfo
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
            "npx:hasTrustyDigest 'f192da5e...'",
        ],
        GREEN,
        "#14532d",
    )

    # Node P2 Provenance & Sidecar
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

    # Node P2 Assertion
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
            'pk:hasScore "0.9470"^^xsd:double ; pk:verdict "faithful" ;',
            "Dimension Scores: fidelity=95, match=96, param=92, quant=95, data=95, code=92, repro=95",
        ],
        GREEN,
        "#15803d",
    )

    # Node P2 Convergence Verification
    draw_kg_node(
        ax,
        55.2,
        31.8,
        40.8,
        13.2,
        "Gate 1 + Gate 2 + Gate 3 Verification Summary",
        "0 `pk:evidenceAgainst` Triples Remaining -> Loop Converged",
        [
            "• Lean 4 Theorem: `ProjectDelphi.Example.unit_length_recovers_prefactor` (0 sorry)",
            "• Fitted Exponents: b_head = 1.9954 (area) | b_body = 3.0005 (volume)",
            "• Version Chain: Nanopub #2 supersedes Nanopub #1 (Pass 1 remains immutable on record)",
        ],
        PURPLE,
        "#581c87",
    )

    # Internal edges in Pass 2
    draw_predicate_edge(ax, (64.9, 66.0), (64.9, 63.5), "np:hasAssertion", GREEN, ly=0.2)
    draw_predicate_edge(ax, (86.2, 66.0), (86.2, 63.5), "prov:wasDerivedFrom", BLUE, ly=0.2)
    draw_predicate_edge(ax, (75.6, 47.0), (75.6, 45.0), "pk:verifiedBy", PURPLE, ly=0.1)

    # Cross-Nanopub edges:
    # 1. `npx:supersedes` from Pass 2 Head -> Pass 1 Head
    draw_predicate_edge(
        ax,
        (55.2, 74.2),
        (23.5, 74.2),
        "npx:supersedes (Immutable Version Chain)",
        GREEN,
        rad=-0.16,
        ly=4.2,
    )

    # 2. `pk:evidenceAgainst` -> Prompt 3 -> Pass 2 Script
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

    # -------------------------------------------------------------------------
    # BOTTOM BAND: Real-World Production Scale in Thompson 1917 Study (80 Nanopubs)
    # -------------------------------------------------------------------------
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
        "HOW THIS EXACT RDF GRAPH SCALES IN THE FULL D'ARCY THOMPSON (1917) PRODUCTION GRAPH (80 SIGNED NANOPUBLICATIONS)",
        color="#f0f6fc",
        fontsize=8.9,
        fontweight="bold",
        va="center",
    )

    prod_batches = [
        (
            "Batch 1: MorphoEval Audits",
            "17 Signed Nanopubs",
            "RAYFKAfyOnqIKXWzdEzCN...",
            "• 9 Primary (`claude-fable-5-1`: 76.6)\n• 8 Blinded (`gemini-4-argon`: 90.8)\n• `pk:evidenceAgainst` sparked 600-pt fit",
            BLUE,
        ),
        (
            "Batch 2: Ancestral & Fossil Claims",
            "68 Signed Nanopubs",
            "np_thompson_pred-*",
            "• 36 Crown-Family Ancestral States\n• 6 MRCA Pairs (1917 Classics)\n• 15 Monte Bolca (50 Ma) + 10 Fossils",
            PURPLE,
        ),
        (
            "Batch 3: Blind Preregistration Lock",
            "1 Signed Nanopub (Locked)",
            "RAilN4nbRHp3e3ZHqlbIge...",
            "• Locks 10,888 species predictions\n• SHA-256 `1d50205ffc2e...` pinned\n  BEFORE FishShapes v1 download",
            AMBER,
        ),
        (
            "Batch 4: Unblinded Test & Portfolio",
            "2 Signed Nanopubs",
            "RAJancw... & RA9ZKlSD...",
            "• Links to `RAilN4nb` (`prov:wasDerivedFrom`)\n• 5,180 blind species (`p = 10^-103`)\n• 14-Dataset Weekly CI Portfolio",
            GREEN,
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
        ax.text(bx + 0.8, 18.2, bcount, color=bcol, fontsize=7.3, fontweight="bold", va="center", zorder=4)
        ax.text(bx + 0.8, 15.9, buri, color=BLUE, fontsize=6.6, family="monospace", va="center", zorder=4)
        ax.text(bx + 0.8, 10.2, bdesc, color="#c9d1d9", fontsize=6.6, linespacing=1.28, va="center", zorder=4)

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, facecolor=BG)
    plt.close(fig)
    print(f"Saved Knowledge Graph visual map to {out_png}")


def build_interactive_html(out_html: Path):
    p1_trig = (ROOT / "kg" / "pass1_claim.trig").read_text(encoding="utf-8")
    p2_trig = (ROOT / "kg" / "pass2_claim.trig").read_text(encoding="utf-8")
    p1_sidecar = (ROOT / "kg" / "pass1_sidecar.json").read_text(encoding="utf-8")
    p2_sidecar = (ROOT / "kg" / "pass2_sidecar.json").read_text(encoding="utf-8")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Project Delphi — Interactive RDF Knowledge Graph & Nanopub Explorer</title>
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
  .badge {{
    display: inline-block;
    padding: 3px 8px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    font-family: monospace;
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
  <h1>Project Delphi — Interactive RDF Knowledge Graph & Nanopub Explorer</h1>
  <div class="subtitle">
    Click any RDF node in the graph below to inspect its exact triples, cryptographic SHA-256 locks, and how
    <code>pk:evidenceAgainst</code> drives the closed remediation loop from Pass 1 (49.4/100) to Pass 2 (94.7/100).
  </div>

  <div class="layout">
    <div class="panel">
      <svg viewBox="0 0 820 500" width="100%" style="background:#090d13;border-radius:8px;border:1px solid #30363d;">
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
        </defs>

        <!-- Edges -->
        <path d="M 520 75 Q 395 25 270 75" fill="none" stroke="#3fb950" stroke-width="2.5" marker-end="url(#arrow-green)"/>
        <text x="395" y="38" fill="#3fb950" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle">npx:supersedes</text>

        <line x1="155" y1="115" x2="155" y2="180" stroke="#d29922" stroke-width="2" marker-end="url(#arrow-blue)"/>
        <text x="155" y="152" fill="#8b949e" font-size="10" font-family="monospace" text-anchor="middle">np:hasAssertion</text>

        <line x1="155" y1="265" x2="155" y2="345" stroke="#f85149" stroke-width="2.2" marker-end="url(#arrow-red)"/>
        <text x="155" y="310" fill="#f85149" font-size="10" font-family="monospace" font-weight="bold" text-anchor="middle">pk:evidenceAgainst (2)</text>

        <path d="M 290 385 Q 410 385 520 235" fill="none" stroke="#f85149" stroke-width="2.2" stroke-dasharray="6,4" marker-end="url(#arrow-red)"/>
        <text x="415" y="340" fill="#f85149" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle">Prompt 3 resolves</text>

        <line x1="645" y1="115" x2="645" y2="180" stroke="#3fb950" stroke-width="2" marker-end="url(#arrow-green)"/>
        <text x="645" y="152" fill="#8b949e" font-size="10" font-family="monospace" text-anchor="middle">np:hasAssertion</text>

        <line x1="645" y1="265" x2="645" y2="345" stroke="#58a6ff" stroke-width="2" marker-end="url(#arrow-blue)"/>
        <text x="645" y="310" fill="#58a6ff" font-size="10" font-family="monospace" text-anchor="middle">prov:wasDerivedFrom</text>

        <!-- Node 1: Pass 1 Head -->
        <g class="node-btn" onclick="selectNode('p1_head')">
          <rect x="40" y="45" width="230" height="70" rx="8" fill="#161b22" stroke="#d29922" stroke-width="2"/>
          <text x="155" y="70" fill="#d29922" font-size="12" font-family="monospace" font-weight="bold" text-anchor="middle">np:Nanopublication (Pass 1)</text>
          <text x="155" y="92" fill="#f0f6fc" font-size="11" font-family="monospace" text-anchor="middle">delphi:np/pass1-example-claim</text>
        </g>

        <!-- Node 2: Pass 1 Assertion -->
        <g class="node-btn" onclick="selectNode('p1_assertion')">
          <rect x="40" y="180" width="230" height="85" rx="8" fill="#161b22" stroke="#d29922" stroke-width="2"/>
          <text x="155" y="205" fill="#f0f6fc" font-size="12" font-family="monospace" font-weight="bold" text-anchor="middle">pk:Claim (Pass 1 v1)</text>
          <text x="155" y="226" fill="#f85149" font-size="11" font-family="monospace" text-anchor="middle">pk:hasScore "0.4940" (49.4/100)</text>
          <text x="155" y="246" fill="#8b949e" font-size="11" font-family="monospace" text-anchor="middle">R² = -0.2461 | RMSE = 44.23g</text>
        </g>

        <!-- Node 3: Pass 1 evidenceAgainst -->
        <g class="node-btn" onclick="selectNode('p1_remediation')">
          <rect x="25" y="345" width="265" height="90" rx="8" fill="#2a1215" stroke="#f85149" stroke-width="2.2"/>
          <text x="157" y="370" fill="#f85149" font-size="12" font-family="monospace" font-weight="bold" text-anchor="middle">pk:evidenceAgainst (Trigger)</text>
          <text x="157" y="392" fill="#f0f6fc" font-size="10.5" font-family="monospace" text-anchor="middle">1. Fit power law y=a*x^b on all 12 rows</text>
          <text x="157" y="412" fill="#f0f6fc" font-size="10.5" font-family="monospace" text-anchor="middle">2. Report b_head &amp; b_body (R² &gt; 0.99)</text>
        </g>

        <!-- Node 4: Pass 2 Head -->
        <g class="node-btn" onclick="selectNode('p2_head')">
          <rect x="520" y="45" width="250" height="70" rx="8" fill="#161b22" stroke="#3fb950" stroke-width="2.2"/>
          <text x="645" y="70" fill="#3fb950" font-size="12" font-family="monospace" font-weight="bold" text-anchor="middle">np:Nanopublication (Pass 2 Head)</text>
          <text x="645" y="92" fill="#f0f6fc" font-size="11" font-family="monospace" text-anchor="middle">delphi:np/pass2-example-claim</text>
        </g>

        <!-- Node 5: Pass 2 Assertion -->
        <g class="node-btn" onclick="selectNode('p2_assertion')">
          <rect x="520" y="180" width="250" height="85" rx="8" fill="#12261e" stroke="#3fb950" stroke-width="2.2"/>
          <text x="645" y="205" fill="#f0f6fc" font-size="12" font-family="monospace" font-weight="bold" text-anchor="middle">pk:Claim (Pass 2 Remediated)</text>
          <text x="645" y="226" fill="#3fb950" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle">pk:hasScore "0.9470" (94.7/100)</text>
          <text x="645" y="246" fill="#c9d1d9" font-size="11" font-family="monospace" text-anchor="middle">R² = 1.0000 | RMSE = 0.0227g</text>
        </g>

        <!-- Node 6: Pass 2 Sidecar & Provenance -->
        <g class="node-btn" onclick="selectNode('p2_sidecar')">
          <rect x="520" y="345" width="250" height="90" rx="8" fill="#161b22" stroke="#58a6ff" stroke-width="2"/>
          <text x="645" y="370" fill="#58a6ff" font-size="12" font-family="monospace" font-weight="bold" text-anchor="middle">sub:provenance &amp; Sidecar Gate 2</text>
          <text x="645" y="392" fill="#c9d1d9" font-size="10.5" font-family="monospace" text-anchor="middle">SHA-256: ddb638b2e99b...</text>
          <text x="645" y="412" fill="#3fb950" font-size="10.5" font-family="monospace" text-anchor="middle">0 pk:evidenceAgainst remaining</text>
        </g>
      </svg>
    </div>

    <div class="panel">
      <div id="node-title" style="font-size:16px;font-weight:700;color:var(--blue);">
        Click any node in the RDF graph to inspect its contents
      </div>
      <div id="node-desc" style="font-size:13px;color:var(--muted);margin-top:6px;">
        Showing exact RDF TriG (`kg/pass1_claim.trig` & `kg/pass2_claim.trig`) and Gate 2 sidecar JSON payloads.
      </div>
      <div class="tabs">
        <button class="tab active" onclick="selectNode('p1_remediation')">pk:evidenceAgainst (Loop Trigger)</button>
        <button class="tab" onclick="selectNode('p1_head')">Pass 1 Nanopub (.trig)</button>
        <button class="tab" onclick="selectNode('p2_head')">Pass 2 Nanopub (.trig)</button>
        <button class="tab" onclick="selectNode('p1_assertion')">Pass 1 Sidecar (.json)</button>
        <button class="tab" onclick="selectNode('p2_sidecar')">Pass 2 Sidecar (.json)</button>
      </div>
      <pre id="code-box"></pre>
    </div>
  </div>

<script>
const PAYLOADS = {{
  p1_remediation: {{
    title: "pk:evidenceAgainst Triples (Extracted by Gate 3 -> Injected into Prompt 3)",
    desc: "When Pass 1 scores 49.4/100 (< 80), `gates/3_compile_and_query_kg.py` queries `kg/pass1_claim.trig` for `pk:evidenceAgainst` and passes these exact lines into `prompts/03_remediation_prompt.md`:",
    code: `pk:evidenceAgainst
  "remediation needed: Fit the power law y = a * x^b across the full organism (all 12 rows of example/data.csv, accounting for both head and body modules) instead of fitting a linear line only to the 6 head rows (line 49)." ,
  "remediation needed: Report the fitted power-law exponents b_head and b_body and verify that full-dataset R^2 exceeds 0.99." ;`
  }},
  p1_head: {{
    title: "Pass 1 RDF Nanopublication (kg/pass1_claim.trig — 49.4/100)",
    desc: "Full TriG file emitted by Gate 3 (`gates/3_compile_and_query_kg.py --pass-num 1`) with 4 named graphs (`Head`, `assertion`, `provenance`, `pubinfo`):",
    code: {json.dumps(p1_trig)}
  }},
  p2_head: {{
    title: "Pass 2 RDF Nanopublication (kg/pass2_claim.trig — 94.7/100, npx:supersedes Pass 1)",
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
    desc: "Converged claim with 0 `pk:evidenceAgainst` items remaining (`pk:hasScore = 0.9470`):",
    code: {json.dumps(p2_trig)}
  }}
}};

function selectNode(key) {{
  const item = PAYLOADS[key] || PAYLOADS.p1_remediation;
  document.getElementById("node-title").textContent = item.title;
  document.getElementById("node-desc").textContent = item.desc;
  document.getElementById("code-box").textContent = item.code;
}}
selectNode("p1_remediation");
</script>
</body>
</html>
"""
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html, encoding="utf-8")
    print(f"Saved interactive HTML Knowledge Graph Explorer to {out_html}")


def main() -> int:
    render_kg_png(OUT_PNG)
    build_interactive_html(OUT_HTML)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
