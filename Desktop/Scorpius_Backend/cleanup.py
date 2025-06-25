#!/usr/bin/env python3
"""
repo_detox.py – Scorpius / generic mono‑repo cleanup tool
=========================================================

▪ Nukes heavyweight dev artifacts (node_modules, .idea, .vscode, __pycache__, *.log)
▪ De‑duplicates identical files by SHA‑256 (optionally hard‑links them)
▪ Generates an audit report of everything it touched

Usage (dry‑run first!):
    python repo_detox.py /path/to/repo --dry-run

Then execute the real cleanup:
    python repo_detox.py /path/to/repo --link-duplicates

Options:
    --core-dir DIR     Move the first copy of each duplicate into DIR (default: packages/core) and
                       replace the rest with hard‑links.
    --link-duplicates  Instead of deleting dupes, replace them with hard‑links pointing to the kept copy.
    --delete-duplicates  Delete duplicate files outright (mutually exclusive with --link-duplicates).
    --dry-run          Show what *would* happen without changing anything.
    --ignore PATTERN   Extra glob pattern(s) to ignore (can repeat).

Recommended workflow: dry‑run → commit → real run → commit.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from pprint import pformat

# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

DEFAULT_NUKE_DIRS = {
    "node_modules",
    "__pycache__",
    ".idea",
    ".vscode",
    ".pytest_cache",
}

DEFAULT_IGNORE_PATTERNS = {
    "*.log",
    "*.log.*",
    "*.pyc",
    "*.pyo",
    "*.so",
}

HASH_CHUNK = 1024 * 1024  # 1 MiB

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def sha256(path: Path) -> str:
    """Streaming SHA‑256 hash for large files."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(HASH_CHUNK):
            h.update(chunk)
    return h.hexdigest()


def nuke_dirs(root: Path, dry: bool) -> list[Path]:
    """Remove heavyweight directories like node_modules. Returns list removed."""
    removed: list[Path] = []
    for dirpath, dirnames, _ in os.walk(root):
        basename_set = set(dirnames)
        for target in basename_set & DEFAULT_NUKE_DIRS:
            victim = Path(dirpath) / target
            removed.append(victim)
            if not dry:
                shutil.rmtree(victim, ignore_errors=True)
            # prevent descending into it further
            dirnames.remove(target)
    return removed


def collect_hashes(root: Path, ignore_patterns: set[str]) -> dict[str, list[Path]]:
    """Return mapping hash -> list of file Paths (duplicates)."""
    hashes: dict[str, list[Path]] = defaultdict(list)
    for path in root.rglob("*"):
        if path.is_file():
            if any(path.match(pat) for pat in ignore_patterns):
                continue
            try:
                h = sha256(path)
            except (OSError, PermissionError):
                continue
            hashes[h].append(path)
    return hashes


def dedupe(hashes: dict[str, list[Path]], *, core_dir: Path, link: bool, delete: bool, dry: bool) -> dict[str, list[Path]]:
    """Deduplicate files. Returns mapping kept_hash -> [dupes_removed]."""
    actions: dict[str, list[Path]] = {}
    core_dir.mkdir(parents=True, exist_ok=True)

    for h, paths in hashes.items():
        if len(paths) <= 1:
            continue  # unique
        # Choose the first path (shortest path len prefer) as canonical
        canonical = min(paths, key=lambda p: (len(str(p)), str(p)))
        if core_dir not in canonical.parents:
            target = core_dir / canonical.name
            if not dry:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(canonical, target)
            canonical = target
        removed = []
        for dupe in paths:
            if dupe == canonical:
                continue
            removed.append(dupe)
            if not dry:
                dupe.unlink(missing_ok=True)
                if link:
                    # Hard‑link back to canonical
                    os.link(canonical, dupe)
        if removed:
            actions[canonical.as_posix()] = removed
    return actions


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Repo detox & dedupe utility")
    p.add_argument("path", type=Path, help="Root directory of repo to clean")
    p.add_argument("--core-dir", type=Path, default=Path("packages/core"), help="Directory to store canonical copies of duplicates (default: packages/core)")

    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--link-duplicates", action="store_true", help="Replace duplicates with hard‑links to the kept copy (default)")
    mode.add_argument("--delete-duplicates", action="store_true", help="Delete duplicate files outright")

    p.add_argument("--dry-run", action="store_true", help="Print actions without modifying files")
    p.add_argument("--ignore", action="append", default=[], help="Additional glob pattern to ignore (can repeat)")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()
    root: Path = args.path.resolve()
    if not root.exists():
        sys.exit(f"✖ Path not found: {root}")

    ignore_patterns = DEFAULT_IGNORE_PATTERNS | set(args.ignore)

    # Phase 1 – nuke heavy dirs
    nuked = nuke_dirs(root, args.dry_run)

    # Phase 2 – dedupe
    hashes = collect_hashes(root, ignore_patterns)
    actions = dedupe(
        hashes,
        core_dir=args.core_dir.resolve(),
        link=args.link_duplicates or not args.delete_duplicates,
        delete=args.delete_duplicates,
        dry=args.dry_run,
    )

    # Phase 3 – report
    summary = {
        "root": str(root),
        "dry_run": args.dry_run,
        "dirs_nuked": [str(p) for p in nuked],
        "files_deduped": {k: [str(p) for p in v] for k, v in actions.items()},
    }
    print("\n=== DETOX SUMMARY ===")
    print(pformat(summary, compact=True, width=120))


if __name__ == "__main__":
    main()
