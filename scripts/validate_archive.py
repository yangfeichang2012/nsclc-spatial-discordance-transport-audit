#!/usr/bin/env python3
"""Validate locked values, manifest integrity, privacy and revision disclosures."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "Greek_primary_under_amended_G11": {
        "n": 61,
        "events": 45,
        "comparable_pairs": 1637,
        "C_B0": 0.6136224801466097,
        "C_B1": 0.5919364691508857,
        "delta_C": -0.02168601099572398,
        "interval": [-0.0640426761828849, 0.020918298917445496],
        "interval_key": "bootstrap_95_percentile_CI",
    },
    "UQ_descriptive_stress_test": {
        "n": 19,
        "events": 18,
        "comparable_pairs": 162,
        "C_B0": 0.6697530864197531,
        "C_B1": 0.6296296296296297,
        "delta_C": -0.04012345679012341,
        "interval": [-0.1558493258334023, 0.08824980650154793],
        "interval_key": "bootstrap_95_percentile_interval",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def close(left: object, right: object) -> bool:
    return math.isclose(float(left), float(right), rel_tol=0, abs_tol=1e-12)


def main() -> None:
    checks: dict[str, bool] = {}
    result_path = ROOT / "results" / "reproduced_results.json"
    checks["reproduced_results_present"] = result_path.is_file()
    results = json.loads(result_path.read_text(encoding="utf-8"))
    for cohort, expected in EXPECTED.items():
        observed = results[cohort]
        for key in ("n", "events", "comparable_pairs", "C_B0", "C_B1", "delta_C"):
            checks[f"{cohort}_{key}"] = close(observed[key], expected[key])
        interval = observed[expected["interval_key"]]
        checks[f"{cohort}_interval_lower"] = close(interval[0], expected["interval"][0])
        checks[f"{cohort}_interval_upper"] = close(interval[1], expected["interval"][1])

    checks["outcome_named_two_year_truncated"] = results["outcome"] == "two-year truncated PFS"
    checks["post_deviation_identity"] = "post-deviation" in results["study_identity"]
    checks["pipeline_not_claimed_fixed"] = "full pipeline not fixed" in results["preprocessing"]
    checks["candidate_counts"] = (
        results["candidate_universe"]["response_unique_n"] == 256
        and results["candidate_universe"]["resistance_unique_n"] == 644
    )
    checks["uq_half_margin_disclosed"] = results["M_value_counts"]["UQ"].get("0.5") == 1

    for filename in ("greek_bootstrap_delta_c.csv", "uq_descriptive_bootstrap_delta_c.csv"):
        lines = (ROOT / "results" / filename).read_text(encoding="utf-8").splitlines()
        checks[f"{filename}_2000_rows"] = len(lines) == 2001

    history = (ROOT / "PROTOCOL_HISTORY.md").read_text(encoding="utf-8")
    for token in ("G09", "G10", "G11", "at least 25", "two-year truncated", "full pipeline"):
        checks[f"history_{token}"] = token in history

    manifest = json.loads((ROOT / "SHA256SUMS.json").read_text(encoding="utf-8"))
    entries = manifest["files"]
    checks["manifest_version"] = manifest["format_version"] == "2.0"
    checks["manifest_nonempty"] = len(entries) >= 20
    for item in entries:
        path = ROOT / item["path"]
        checks[f"manifest_{item['path']}"] = (
            path.is_file()
            and path.stat().st_size == item["bytes"]
            and sha256(path) == item["sha256"]
        )

    archive_files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.relative_to(ROOT).parts
        and "inputs" not in path.relative_to(ROOT).parts
    ]
    text_suffixes = {".md", ".json", ".cff", ".txt", ".csv", ".py", ".yml", ".yaml", ".R"}
    joined_names = "\n".join(path.relative_to(ROOT).as_posix().lower() for path in archive_files)
    checks["privacy_filename_boundary"] = not any(
        token in joined_names
        for token in ("patient_level", "participant_level", "expression_matrix", "author_email")
    )
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    checks["exact_two_creators"] = citation.count("family-names:") == 2
    checks["no_personal_email"] = not any(
        re.search(r"[\w.+-]+@(?:qq|163|gmail|outlook)\.[A-Za-z]+", path.read_text(encoding="utf-8", errors="ignore"))
        for path in archive_files
        if path.suffix.lower() in text_suffixes and path.resolve() != Path(__file__).resolve()
    )
    checks["no_absolute_windows_path"] = not any(
        re.search(r"\b[A-Za-z]:\\", path.read_text(encoding="utf-8", errors="ignore"))
        for path in archive_files
        if path.suffix.lower() in text_suffixes and path.resolve() != Path(__file__).resolve()
    )

    failed = [name for name, passed in checks.items() if not passed]
    payload = {
        "status": "PASS" if not failed else "FAIL",
        "passed": sum(checks.values()),
        "total": len(checks),
        "failed": failed,
    }
    print(json.dumps(payload, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
