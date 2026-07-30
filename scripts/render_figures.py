#!/usr/bin/env python3
"""Regenerate aggregate figures from the locked result ledger."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "figure_source_data.csv"
OUT = ROOT / "reproduced_figures"


def main() -> None:
    rows = pd.read_csv(DATA)
    OUT.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    y = list(range(len(rows)))
    err_low = rows["delta_C"] - rows["interval_lower"]
    err_high = rows["interval_upper"] - rows["delta_C"]
    ax.errorbar(
        rows["delta_C"],
        y,
        xerr=[err_low, err_high],
        fmt="o",
        capsize=4,
        color="#1f4e79",
    )
    ax.axvline(0, color="#666666", linestyle="--", linewidth=1)
    ax.set_yticks(y, rows["cohort"])
    ax.set_xlabel("Change in Harrell C, B1 minus B0")
    ax.set_title("Fixed-coefficient incremental discrimination")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "delta_C_forest.png", dpi=300)
    fig.savefig(OUT / "delta_C_forest.svg")
    plt.close(fig)

    long = rows.melt(
        id_vars=["cohort"], value_vars=["C_B0", "C_B1"], var_name="model", value_name="C"
    )
    pivot = long.pivot(index="cohort", columns="model", values="C")
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    pivot.plot(kind="bar", ax=ax, color=["#4c78a8", "#f58518"], rot=0)
    ax.set_ylim(0.5, 0.75)
    ax.set_ylabel("Harrell C")
    ax.set_xlabel("")
    ax.set_title("Fixed-model concordance by center")
    ax.legend(["B0 baseline", "B1 augmented"], frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "fixed_C_values.png", dpi=300)
    fig.savefig(OUT / "fixed_C_values.svg")
    plt.close(fig)

    print(f"Wrote {len(list(OUT.glob('*')))} aggregate figure files to {OUT}")


if __name__ == "__main__":
    main()

