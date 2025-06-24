#!/usr/bin/env python3
"""
Scorpius / GUARDEFI Repository Cleanup Utility
============================================
Flatten "Russian‑doll" directory nests, deduplicate identical files, fence off
secrets, and re‑home docs + configs into a sane monorepo skeleton.

Usage
-----
Dry‑run analysis (no changes written):
    python repo_cleanup.py /path/to/repo

Execute full cleanup after review:
    python repo_cleanup.py /path/to/repo --execute
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
from collections import defaultdict
from fnmatch import fnmatch
from pathlib import Path

# ---------------------------------------------------------------------------
# Helper configuration
# ---------------------------------------------------------------------------

# Anything matching these glob patterns is ignored for hashing & moving
IGNORE_PATTERNS: list[str] = [
    ".git",
    "*/.git/*",  # repo internals
    "**/__pycache__/**",
    "**/node_modules/**",
    "*.pyc",
    "*.pyo",
    "*.so",
    "*.log",
    "*.log.*",
    "yarn.lock",
    "package-lock.json",
]

# Files that almost certainly contain secrets
SECRET_FILENAMES = [
    ".env",
    ".env.*",
    "*.env",
    "*.key",
    "*.pem",
]

# Filenames worth outright deleting / quarantining
DEAD_PATTERNS = [
    "Dockerfile.simple",
    "Dockerfile.backend",
    "Dockerfile.frontend",
    "*.zip",
    "*.bak",
    "*.bat",
    "*.ps1",
    "package-electron.json",
    "fix-*.js",
    "fix-*.cjs",
]

# Target clean layout
CLEAN_DIRS = [
    "backend_clean",
    "frontend_clean",
    "docker_clean",
    "scripts_clean",
    "docs",
    "configs",
]


class RepoCleanup:
    """Main cleanup orchestration class."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.duplicates: dict[str, list[Path]] = defaultdict(list)
        self.secrets_found: list[Path] = []

    # ------------------------------------------------------------------
    # File‑system helpers
    # ------------------------------------------------------------------
    def _is_ignored(self, path: Path) -> bool:
        return any(fnmatch(str(path), pat) for pat in IGNORE_PATTERNS)

    def _hash_file(self, path: Path) -> str | None:
        """SHA‑256 hash for small/medium files; skip huge binaries."""
        try:
            if path.stat().st_size > 20 * 1024 * 1024:  # 20 MB guardrail
                return None
            h = hashlib.sha256()
            with path.open("rb") as fh:
                for chunk in iter(lambda: fh.read(4096), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Analysis passes
    # ------------------------------------------------------------------
    def find_duplicates(self) -> None:
        hashes: dict[str, list[Path]] = defaultdict(list)
        for fp in self.root.rglob("*"):
            if fp.is_file() and not self._is_ignored(fp):
                if h := self._hash_file(fp):
                    hashes[h].append(fp)
        self.duplicates = {k: v for k, v in hashes.items() if len(v) > 1}

    def detect_russian_dolls(self) -> list[Path]:
        dolls: list[Path] = []
        for d in self.root.rglob("*"):
            if d.is_dir() and d.parent.name == d.name:
                dolls.append(d)
        return dolls

    def find_secrets(self) -> None:
        for pat in SECRET_FILENAMES:
            for fp in self.root.rglob(pat):
                if fp.is_file() and not self._is_ignored(fp):
                    self.secrets_found.append(fp)

    def find_dead_weight(self) -> list[Path]:
        dead: list[Path] = []
        for pat in DEAD_PATTERNS:
            for fp in self.root.rglob(pat):
                if fp.is_file():
                    dead.append(fp)
        return dead

    # ------------------------------------------------------------------
    # Mutating passes (executed only when --execute flag is on)
    # ------------------------------------------------------------------
    def _ensure_layout(self) -> None:
        for d in CLEAN_DIRS:
            (self.root / d).mkdir(exist_ok=True)

    def flatten_backend(self) -> None:
        """Locate deepest `backend` dir and copy unique files out."""
        backend_target = self.root / "backend_clean"
        backend_dirs = sorted(
            {p for p in self.root.rglob("backend") if p.is_dir()},
            key=lambda p: len(p.parts),
            reverse=True,
        )
        seen: set[str] = set()
        for bdir in backend_dirs:
            for fp in bdir.rglob("*"):
                if fp.is_file() and not self._is_ignored(fp):
                    rel = fp.relative_to(bdir)
                    if rel.as_posix() in seen:
                        continue
                    seen.add(rel.as_posix())
                    dest = backend_target / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(fp, dest)

    def copy_frontend(self) -> None:
        src = self.root / "frontend"
        tgt = self.root / "frontend_clean"
        if src.exists():
            shutil.copytree(src, tgt, dirs_exist_ok=True)

    def move_docs_configs(self) -> None:
        docs = self.root / "docs"
        cfgs = self.root / "configs"
        for fp in self.root.rglob("*.md"):
            if fp.is_file() and fp.parent != docs:
                shutil.move(str(fp), docs / fp.name)
        for fp in self.root.rglob("*.yml"):
            if fp.is_file() and "package" not in fp.name:
                shutil.move(str(fp), cfgs / fp.name)
        for name in ("docker-compose.yml",):
            fp = self.root / name
            if fp.exists():
                shutil.move(str(fp), cfgs / fp.name)

    def create_env_examples(self) -> None:
        for env_fp in self.secrets_found:
            ex_file = env_fp.with_name(env_fp.name + ".example")
            lines: list[str] = []
            try:
                with env_fp.open() as fh:
                    for line in fh:
                        if "=" in line and not line.strip().startswith("#"):
                            key = line.split("=", 1)[0]
                            lines.append(f"{key}=YOUR_VALUE_HERE\n")
                        else:
                            lines.append(line)
                with ex_file.open("w") as out:
                    out.writelines(lines)
            except Exception:
                pass

    def write_gitignore(self) -> None:
        gitignore = self.root / ".gitignore"
        content = (
            "# Auto-generated by repo_cleanup.py\n"
            "# Secrets\n.env*\n!.env.example\n\n"
            "# Python\n__pycache__/\n*.py[cod]\nenv/\nvenv/\n\n"
            "# Node\nnode_modules/\n*.log\n\n"
            "# Build\ndist/\nbuild/\n*.zip\n*.tar.gz\n"
        )
        gitignore.write_text(content, encoding="utf-8")

    # ------------------------------------------------------------------
    # Entry points
    # ------------------------------------------------------------------
    def report(self) -> str:
        dolls = self.detect_russian_dolls()
        dead = self.find_dead_weight()
        dupe_count = sum(len(v) - 1 for v in self.duplicates.values())

        out = [
            "\n🧹  REPO CLEANUP REPORT",
            "====================================",
            f"Root: {self.root}\n",
            f"Russian‑doll directories: {len(dolls)}",
            f"Duplicate extra files:   {dupe_count}",
            f"Potential secrets:       {len(self.secrets_found)}",
            f"Dead‑weight files:       {len(dead)}",
        ]
        return "\n".join(out)

    def execute(self) -> None:
        self._ensure_layout()
        self.flatten_backend()
        self.copy_frontend()
        self.create_env_examples()
        self.move_docs_configs()
        self.write_gitignore()


# ---------------------------------------------------------------------------
# CLI glue
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Flatten + sanitize a Scorpius repo")
    p.add_argument("root", help="Path to repo root, e.g. ./GUARDEFI-main")
    p.add_argument(
        "--execute", action="store_true", help="Perform changes instead of dry run"
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    cleanup = RepoCleanup(Path(args.root))

    # Analysis phase
    cleanup.find_duplicates()
    cleanup.find_secrets()

    print(cleanup.report())

    if args.execute:
        confirm = (
            input("\nContinue with destructive cleanup? [y/N] ").lower().startswith("y")
        )
        if confirm:
            cleanup.execute()
            print(
                "\n✅  Cleanup completed. Review *_clean directories before swapping in."
            )
        else:
            print("Aborted.")
    else:
        print("\n(Dry‑run only — no files changed. Re‑run with --execute to apply.)")


if __name__ == "__main__":
    main()
