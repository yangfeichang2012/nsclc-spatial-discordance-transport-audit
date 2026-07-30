#!/usr/bin/env python3
"""Render true-vector main and supplementary figures from locked aggregates."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "reproduced_results.json"
OUT = ROOT / "figures"


def save(fig: plt.Figure, stem: str) -> None:
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.tif", dpi=300, bbox_inches="tight")


def timeline() -> None:
    fig, ax = plt.subplots(figsize=(12.4, 4.8))
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 5)
    ax.axis("off")
    items = [
        (
            0.2,
            "#dbeafe",
            "G09 — original estimand",
            "Weighted UQ + Greek transport\nUQ anticipated n=27\nHard gate n≥25\nInvalid author key → STOP",
        ),
        (
            4.2,
            "#fef3c7",
            "G10 — public recovery",
            "Public GEO/source-table crosswalk\n21 predictor-paired patients\n19 outcome-complete patients\nOriginal G09 gate not met",
        ),
        (
            8.2,
            "#dcfce7",
            "G11 — amended plan",
            "Frozen before outcome-linked execution\nGreek cohort primary\nUQ descriptive stress test\nG09 never resumed or reweighted",
        ),
    ]
    for left, color, title, body in items:
        box = FancyBboxPatch(
            (left, 1.25),
            3.55,
            2.35,
            boxstyle="round,pad=0.08,rounding_size=0.08",
            linewidth=1.4,
            edgecolor="#334155",
            facecolor=color,
        )
        ax.add_patch(box)
        ax.text(left + 0.18, 3.18, title, fontsize=10.5, fontweight="bold", va="top")
        ax.text(left + 0.18, 2.78, body, fontsize=8.7, va="top", linespacing=1.45)
    for left, right in ((3.75, 4.2), (7.75, 8.2)):
        ax.add_patch(
            FancyArrowPatch(
                (left, 2.42),
                (right, 2.42),
                arrowstyle="-|>",
                mutation_scale=14,
                linewidth=1.4,
                color="#475569",
            )
        )
    ax.text(
        6.2,
        4.55,
        "Protocol and analysis-plan chronology",
        ha="center",
        fontsize=15,
        fontweight="bold",
    )
    ax.text(
        6.2,
        0.55,
        "Study identity: analysis-plan-locked post-deviation secondary transport audit",
        ha="center",
        fontsize=10.5,
        color="#334155",
    )
    save(fig, "Figure_1_protocol_timeline")
    plt.close(fig)


def forest(results: dict) -> None:
    rows = [
        (
            "Greek\nprimary under amended G11",
            results["Greek_primary_under_amended_G11"]["delta_C"],
            results["Greek_primary_under_amended_G11"]["bootstrap_95_percentile_CI"],
        ),
        (
            "UQ\ndescriptive stress test",
            results["UQ_descriptive_stress_test"]["delta_C"],
            results["UQ_descriptive_stress_test"]["bootstrap_95_percentile_interval"],
        ),
    ]
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    y_positions = [1, 0]
    for y, (label, estimate, interval) in zip(y_positions, rows):
        ax.errorbar(
            estimate,
            y,
            xerr=[[estimate - interval[0]], [interval[1] - estimate]],
            fmt="o",
            markersize=7,
            capsize=5,
            linewidth=1.8,
            color="#0f4c81" if y else "#b45309",
        )
        ax.text(
            0.095,
            y,
            f"{estimate:+.3f} [{interval[0]:+.3f}, {interval[1]:+.3f}]",
            va="center",
            fontsize=9.5,
        )
    ax.axvline(0, color="#64748b", linestyle="--", linewidth=1.2)
    ax.set_yticks(y_positions, [row[0] for row in rows])
    ax.set_xlim(-0.18, 0.13)
    ax.set_ylim(-0.65, 1.65)
    ax.set_xlabel("Change in Harrell C (B1 − B0)")
    ax.set_title("Incremental discrimination for two-year truncated PFS", fontweight="bold")
    ax.grid(axis="x", color="#cbd5e1", linewidth=0.7, alpha=0.7)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.text(
        0.0,
        -0.5,
        "Patient-level percentile intervals; conditional on Yale coefficients and target preprocessing",
        ha="center",
        fontsize=8.8,
        color="#475569",
    )
    save(fig, "Figure_2_delta_C_forest")
    plt.close(fig)


def paired_c(results: dict) -> None:
    rows = [
        ("Greek", results["Greek_primary_under_amended_G11"]),
        ("UQ", results["UQ_descriptive_stress_test"]),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for index, (name, row) in enumerate(rows):
        y = 1 - index
        ax.plot([row["C_B0"], row["C_B1"]], [y, y], color="#94a3b8", linewidth=2)
        ax.scatter(row["C_B0"], y, s=70, color="#2563eb", label="B0" if index == 0 else None, zorder=3)
        ax.scatter(row["C_B1"], y, s=70, color="#ea580c", label="B1" if index == 0 else None, zorder=3)
    ax.set_yticks([1, 0], ["Greek", "UQ"])
    ax.set_xlim(0.56, 0.70)
    ax.set_xlabel("Harrell C")
    ax.set_title("Fixed-coefficient concordance by target cohort", fontweight="bold")
    ax.grid(axis="x", color="#cbd5e1", linewidth=0.7)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.legend(frameon=False, ncol=2, loc="lower right")
    save(fig, "Supplementary_Figure_S1_paired_C")
    plt.close(fig)


def main() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
        }
    )
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    timeline()
    forest(results)
    paired_c(results)
    print("Wrote 3 figure sets (SVG, PDF, PNG and TIFF) to figures/")


if __name__ == "__main__":
    main()
