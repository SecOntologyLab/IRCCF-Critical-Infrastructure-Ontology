"""Generate a deterministic SHA-256 manifest of Git-tracked files.

Usage:
    py scripts/maintenance/refresh_manifest.py

The manifest excludes itself to avoid a circular hash dependency.
Hashes represent the bytes of files in the local working directory.
"""

from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "docs" / "provenance" / "file_manifest.csv"


def digest(path: Path) -> str:
    """Calculate the SHA-256 hash of a file."""
    hasher = hashlib.sha256()

    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def tracked_files() -> list[Path]:
    """Return files tracked by Git, excluding the manifest itself."""
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    paths = []

    for name in result.stdout.split(b"\0"):
        if not name:
            continue

        relative_path = name.decode("utf-8", errors="surrogateescape")
        path = ROOT / relative_path

        if path == TARGET:
            continue

        if path.is_file():
            paths.append(path)

    return sorted(paths, key=lambda p: p.relative_to(ROOT).as_posix())


def main() -> None:
    rows = []

    for path in tracked_files():
        rows.append(
            (
                path.relative_to(ROOT).as_posix(),
                path.stat().st_size,
                digest(path),
            )
        )

    TARGET.parent.mkdir(parents=True, exist_ok=True)

    with TARGET.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("path", "size_bytes", "sha256"))
        writer.writerows(rows)

    print(f"Manifest updated: {len(rows)} Git-tracked files")


if __name__ == "__main__":
    main()