#!/usr/bin/env python3
"""Validate locked values, manifest integrity, and archive privacy boundaries."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    "Greek": {
        "n": 61,
        "events": 45,
        "comparable_pairs": 1637,
        "C_B0": 0.6136224801466097,
        "C_B1": 0.5919364691508857,
        "delta_C": -0.02168601099572398,
        "interval_lower": -0.0640426761828849,
        "interval_upper": 0.020918298917445496,
    },
    "UQ": {
        "n": 19,
        "events": 18,
        "comparable_pairs": 162,
        "C_B0": 0.6697530864197531,
        "C_B1": 0.6296296296296297,
        "delta_C": -0.04012345679012341,
        "interval_lower": -0.1558493258334023,
        "interval_upper": 0.08824980650154793,
    },
}

FORBIDDEN_NAMES = (
    "patient_level",
    "participant_level",
    "expression_matrix",
    "bootstrap_draw",
    "author_email",
    "submission",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    rows = pd.read_csv(ROOT / "data" / "figure_source_data.csv").set_index("cohort")
    checks = {}
    for cohort, expected in EXPECTED.items():
        for key, value in expected.items():
            observed = rows.loc[cohort, key]
            checks[f"{cohort}_{key}"] = abs(float(observed) - float(value)) < 1e-12

    manifest = json.loads((ROOT / "SHA256SUMS.json").read_text(encoding="utf-8-sig"))
    for item in manifest:
        path = ROOT / item["path"]
        checks[f"manifest_{item['path']}"] = (
            path.exists()
            and path.stat().st_size == item["bytes"]
            and sha256(path) == item["sha256"]
        )

    file_names = [p.relative_to(ROOT).as_posix().lower() for p in ROOT.rglob("*") if p.is_file()]
    checks["privacy_filename_boundary"] = not any(
        token in name for token in FORBIDDEN_NAMES for name in file_names
    )
    checks["exact_two_creators"] = (
        (ROOT / "CITATION.cff").read_text(encoding="utf-8").count("family-names:") == 2
    )
    checks["no_author_email"] = not any(
        "@qq.com" in p.read_text(encoding="utf-8", errors="ignore")
        or "@163.com" in p.read_text(encoding="utf-8", errors="ignore")
        for p in ROOT.rglob("*")
        if p.is_file()
        and p.resolve() != Path(__file__).resolve()
        and p.suffix.lower() in {".md", ".json", ".cff", ".txt", ".csv", ".py"}
    )

    failed = [name for name, ok in checks.items() if not ok]
    print(
        json.dumps(
            {
                "status": "PASS" if not failed else "FAIL",
                "passed": sum(checks.values()),
                "total": len(checks),
                "failed": failed,
            },
            indent=2,
        )
    )
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
