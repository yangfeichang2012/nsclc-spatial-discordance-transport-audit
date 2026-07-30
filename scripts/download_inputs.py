#!/usr/bin/env python3
"""Download and verify the public inputs used by the reproduction workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "inputs")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data" / "source_manifest.json")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    for item in manifest["sources"]:
        target = args.output / item["filename"]
        if not target.exists() or target.stat().st_size != item["bytes"] or sha256(target) != item["sha256"]:
            temporary = target.with_suffix(target.suffix + ".part")
            if temporary.exists():
                temporary.unlink()
            print(f"downloading {item['id']} -> {target}")
            urllib.request.urlretrieve(item["url"], temporary)
            temporary.replace(target)
        observed_bytes = target.stat().st_size
        observed_hash = sha256(target)
        if observed_bytes != item["bytes"] or observed_hash != item["sha256"]:
            raise RuntimeError(
                f"{item['id']} verification failed: bytes={observed_bytes}, sha256={observed_hash}"
            )
        print(f"PASS {item['id']} {observed_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
