#!/usr/bin/env python3
"""
import_rewriter.py – auto-patch absolute imports after repo_detox
----------------------------------------------------------------
Fixes previous bug: now rewrites **every** line, not just the first, by
using the `re.MULTILINE` flag so `^` matches the start of *any* line.

Run (dry-run):
    python import_rewriter.py . --old-prefixes "scanner,mempool" --dry-run
Run (apply):
    python import_rewriter.py . --old-prefixes "scanner,mempool" --write
"""
from __future__ import annotations
import argparse, difflib, os, re, sys
from pathlib import Path
from typing import Iterable, List

IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+([\w\.]+)", re.MULTILINE)

def detect_prefixes(root: Path) -> List[str]:
    return [d.name.replace("-","_") for d in root.iterdir() if d.is_dir() and d.name not in {"packages",".git","__pycache__"}]

def rewrite(text: str, olds: Iterable[str], core: str) -> str:
    def _sub(match: re.Match[str]) -> str:
        mod = match.group(1)
        for old in olds:
            if mod == old or mod.startswith(f"{old}."):
                suffix = mod[len(old):].lstrip('.')
                return match.group(0).replace(mod, f"{core}.{suffix}" if suffix else core)
        return match.group(0)
    return IMPORT_RE.sub(_sub, text)

def patch_files(root: Path, olds: List[str], core: str, write: bool):
    changed = 0
    for p in root.rglob("*.py"):
        if "packages" in p.parts:
            continue
        txt = p.read_text(encoding="utf-8")
        new = rewrite(txt, olds, core)
        if txt != new:
            changed += 1
            if write:
                p.write_text(new, encoding="utf-8")
            print(f"✔ Patched {p.relative_to(root)}")
    if not changed:
        print("No matching imports found – nothing changed.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    ap.add_argument("--old-prefixes", default="", help="comma list of legacy prefixes")
    ap.add_argument("--core-prefix", default="packages.core")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    root = args.path.resolve()
    olds = [x.strip() for x in (args.old_prefixes.split(",") if args.old_prefixes else detect_prefixes(root)) if x]
    print(f"✦ Rewriting imports in {root} …")
    patch_files(root, olds, args.core_prefix, args.write)