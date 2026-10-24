"""Generate a deterministic SHA-256 manifest for tracked-candidate repository files.
Run from anywhere: py scripts/maintenance/refresh_manifest.py
"""
from __future__ import annotations
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / 'docs' / 'provenance' / 'file_manifest.csv'
IGNORED_DIRS = {'.git', '.venv', '.vscode', '__pycache__', 'local-not-for-github', '.pytest_cache'}
IGNORED_FILES = {'.DS_Store', 'Thumbs.db', 'repository_inventory.txt'}


def include(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if path == TARGET or any(part in IGNORED_DIRS for part in rel.parts):
        return False
    if path.name in IGNORED_FILES or path.suffix.lower() in {'.pyc', '.log'}:
        return False
    if 'raw-runs' in rel.parts and 'results' in rel.parts:
        return False
    return True


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    rows = []
    for path in sorted(ROOT.rglob('*')):
        if path.is_file() and include(path):
            rows.append((path.relative_to(ROOT).as_posix(), path.stat().st_size, digest(path)))
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    with TARGET.open('w', encoding='utf-8-sig', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow(('path', 'size_bytes', 'sha256'))
        writer.writerows(rows)
    print(f'Wrote {len(rows)} file hashes to {TARGET}')

if __name__ == '__main__':
    main()
