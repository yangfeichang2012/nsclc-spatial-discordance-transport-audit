#!/usr/bin/env python3
"""Build a self-validating release ZIP and test it after extraction."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", "inputs", "__pycache__", ".pytest_cache"}
EXCLUDED_NAMES = {"SHA256SUMS.json"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def release_files() -> list[Path]:
    return sorted(
        (
            path
            for path in ROOT.rglob("*")
            if path.is_file()
            and not EXCLUDED_PARTS.intersection(path.relative_to(ROOT).parts)
            and path.name not in EXCLUDED_NAMES
            and not path.name.endswith(".zip")
        ),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


def main() -> int:
    output_dir = ROOT.parent / "releases"
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "format_version": "2.0",
        "archive_version": "1.0.1",
        "files": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in release_files()
        ],
    }
    (ROOT / "SHA256SUMS.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_archive.py")], check=True)

    zip_path = output_dir / "nsclc-spatial-discordance-transport-audit-v1.0.1.zip"
    if zip_path.exists():
        zip_path.unlink()
    package_root = "nsclc-spatial-discordance-transport-audit-v1.0.1"
    files_with_manifest = release_files() + [ROOT / "SHA256SUMS.json"]
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(files_with_manifest, key=lambda item: item.relative_to(ROOT).as_posix()):
            archive.write(path, f"{package_root}/{path.relative_to(ROOT).as_posix()}")

    with tempfile.TemporaryDirectory(prefix="prj015_release_check_") as temporary:
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(temporary)
        extracted = Path(temporary) / package_root
        subprocess.run(
            [sys.executable, str(extracted / "scripts" / "validate_archive.py")],
            cwd=extracted,
            check=True,
        )
    payload = {"zip": str(zip_path), "bytes": zip_path.stat().st_size, "sha256": sha256(zip_path)}
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
