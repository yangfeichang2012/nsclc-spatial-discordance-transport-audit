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
    checks["archive_version_v102"] = results["archive_version"] == "1.0.2"
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
    for token in (
        "G09",
        "G10",
        "G11",
        "at least 25",
        "two-year truncated",
        "full pipeline",
        "VALIDATED_COMPLETE",
        "publication supersession",
    ):
        checks[f"history_{token}"] = token in history

    historical_hashes = {
        "g11_protocol_contract_v1.0.json": "0c55d0e68811db73dc4c4be894472e3d37b805229fa4ccbb0a7ad6a40504f491",
        "g11_execution_authorization_historical_v1.0.json": "4dde3ff2fe87faa620521d4dc2f3331de17f846e2c872b3fb8be6948fad296c5",
        "g11_execution_state_historical_v1.0.json": "5d0a557d1375a7ab19486a0e2e0b33b7e4c950bee48bc3d523df64001846d607",
        "g12_result_and_claim_lock_v1.0.json": "8162e27aec0b8540015c1e19bea3bcb0e323a51395562082fedb28ca6059f161",
    }
    for filename, expected_hash in historical_hashes.items():
        path = ROOT / "protocol" / filename
        checks[f"historical_object_{filename}"] = path.is_file() and sha256(path) == expected_hash

    supersession_path = ROOT / "protocol" / "g11_state_transition_and_supersession_v1.0.json"
    checks["supersession_record_present"] = supersession_path.is_file()
    supersession = json.loads(supersession_path.read_text(encoding="utf-8"))
    checks["g11_current_state_complete"] = supersession["current_state"]["G11"] == "VALIDATED_COMPLETE"
    checks["g12_current_state_locked"] = supersession["current_state"]["G12"] == "RESULT_AND_CLAIM_LOCKED"
    checks["supersession_values_unchanged"] = supersession["current_state"]["scientific_values_changed"] is False
    checks["supersession_no_new_analysis"] = (
        supersession["current_state"]["new_analysis_performed_for_this_amendment"] is False
    )

    result_ledger = (ROOT / "data" / "result_ledger.csv").read_text(encoding="utf-8")
    figure_ledger = (ROOT / "data" / "figure_source_data.csv").read_text(encoding="utf-8")
    checks["result_ledger_current_greek_role"] = (
        "primary target cohort under amended G11 plan" in result_ledger
        and "sole confirmatory" not in result_ledger.lower()
    )
    checks["figure_ledger_current_greek_role"] = (
        "primary target cohort under amended G11 plan" in figure_ledger
        and "sole confirmatory" not in figure_ledger.lower()
    )

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
    checks["citation_version_v102"] = "version: 1.0.2" in citation
    checks["citation_v102_doi"] = "10.5281/zenodo.21715520" in citation
    zenodo_metadata = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    checks["zenodo_metadata_version_v102"] = zenodo_metadata["version"] == "1.0.2"
    checks["zenodo_metadata_v102_doi"] = zenodo_metadata["doi"] == "10.5281/zenodo.21715520"
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
