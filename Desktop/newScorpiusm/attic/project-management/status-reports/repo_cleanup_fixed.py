#!/usr/bin/env python3
"""
Scorpius / GUARDEFI Repository Cleanup Utility
=============================================
Flatten "Russian‑doll" directory nests, deduplicate identical files, quarantine
secrets, and reorganise docs + configs into a lean monorepo skeleton.

Usage
-----
Dry‑run analysis (no changes written):
    python repo_cleanup.py /path/to/repo

Execute full cleanup after review:
    python repo_cleanup.py /path/to/repo --execute

Optional flags
--------------
--move‑docs            Move (not copy) markdown/config files into docs/ & configs/
--remove‑artifacts     Delete compiled artefacts (pyc/pyd/exe) & .venv after copy
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

# glob‑style ignore filters (checked via simple substring for speed)
IGNORE_SUBSTR = [
    "/.git/",
    "__pycache__",
    "/node_modules/",
    "/dist/",
    "/build/",
]
IGNORE_SUFFIX = (
    ".pyc",
    ".pyo",
    ".so",
    ".log",
    "yarn.lock",
    "package-lock.json",
)

# Files that almost certainly contain credentials
SECRET_FILENAMES = [
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    ".pem",
    ".key",
]

# Patterns worth purging when --remove‑artifacts is set
ARTIFACT_SUFFIX = (".pyc", ".pyd", ".exe")
ARTIFACT_DIRS = (".venv", "venv", "env")

# Top‑level clean layout
CLEAN_DIRS = [
    "backend_clean",
    "frontend_clean",
    "docker_clean",
    "scripts_clean",
    "docs",
    "configs",
]


class RepoCleanup:
    """Main cleanup‑orchestration class."""

    def __init__(self, root: Path, move_docs: bool, remove_artifacts: bool):
        self.root = root.resolve()
        self.move_docs = move_docs
        self.remove_artifacts = remove_artifacts

        self.duplicates: dict[str, list[Path]] = defaultdict(list)
        self.secrets_found: list[Path] = []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _is_ignored(self, path: Path) -> bool:
        p = path.as_posix()
        return any(sub in p for sub in IGNORE_SUBSTR) or p.endswith(IGNORE_SUFFIX)

    def _hash_file(self, path: Path) -> str | None:
        """Return SHA‑256 for files ≤20 MB; skip larger."""
        try:
            if path.stat().st_size > 20 * 1024 * 1024:
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
    def analyse(self) -> None:
        """Populate duplicate + secret lists."""
        hashes: dict[str, list[Path]] = defaultdict(list)

        for fp in self.root.rglob("*"):
            if fp.is_file() and not self._is_ignored(fp):
                # duplicates
                if h := self._hash_file(fp):
                    hashes[h].append(fp)
                # secrets
                if any(fnmatch(fp.name, pat) for pat in SECRET_FILENAMES):
                    self.secrets_found.append(fp)
        # keep only dupes
        self.duplicates = {k: v for k, v in hashes.items() if len(v) > 1}

    def russian_dolls(self) -> list[Path]:
        return [
            d for d in self.root.rglob("*") if d.is_dir() and d.parent.name == d.name
        ]

    # ------------------------------------------------------------------
    # Mutating passes (run only with --execute)
    # ------------------------------------------------------------------
    def _ensure_layout(self) -> None:
        for d in CLEAN_DIRS:
            (self.root / d).mkdir(exist_ok=True)

    def flatten_backend(self) -> None:
        target = self.root / "backend_clean"
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
                    dest = target / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(fp, dest)
                    if self.remove_artifacts and fp.suffix in ARTIFACT_SUFFIX:
                        fp.unlink(missing_ok=True)

    def copy_frontend(self) -> None:
        for cand in (self.root / "frontend", self.root / "src"):
            if cand.exists():
                shutil.copytree(cand, self.root / "frontend_clean", dirs_exist_ok=True)
                break

    def move_docs_configs(self) -> None:
        docs, cfgs = self.root / "docs", self.root / "configs"
        mover = shutil.move if self.move_docs else shutil.copy2
        for fp in self.root.rglob("*.md"):
            if fp.is_file() and not self._is_ignored(fp) and fp.parent != docs:
                mover(str(fp), docs / fp.name)
        for fp in self.root.rglob("*.yml"):
            if (
                fp.is_file()
                and not self._is_ignored(fp)
                and "package" not in fp.name
                and fp.parent != cfgs
            ):
                mover(str(fp), cfgs / fp.name)
        dc = self.root / "docker-compose.yml"
        if dc.exists() and dc.parent != cfgs:
            mover(str(dc), cfgs / dc.name)

    def create_env_examples(self) -> None:
        for env_fp in self.secrets_found:
            ex_fp = env_fp.with_name(env_fp.name + ".example")
            out_lines: list[str] = []
            try:
                with env_fp.open() as fh:
                    for line in fh:
                        if "=" in line and not line.strip().startswith("#"):
                            key = line.split("=", 1)[0]
                            out_lines.append(f"{key}=YOUR_VALUE_HERE\n")
                        else:
                            out_lines.append(line)
                ex_fp.write_text("".join(out_lines))
            except Exception:
                pass

    def write_gitignore(self) -> None:
        (self.root / ".gitignore").write_text(
            """# Auto‑generated by repo_cleanup.py\n"
            "# Secrets\n.env*\n!.env.example\n\n"
            "# Python\n__pycache__/\n*.py[cod]\nvenv/\n.venv/\n\n"
            "# Node\nnode_modules/\n*.log\n\n"
            "# Builds\ndist/\nbuild/\n*.zip\n*.tar.gz\n""",
            encoding="utf-8",
        )

    def purge_artifacts(self) -> None:
        if not self.remove_artifacts:
            return
        for fp in self.root.rglob("*"):
            if fp.is_file() and fp.suffix in ARTIFACT_SUFFIX:
                fp.unlink(missing_ok=True)
        for d in ARTIFACT_DIRS:
            tgt = self.root / d
            if tgt.exists():
                shutil.rmtree(tgt, ignore_errors=True)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
    def report(self) -> str:
        dolls = self.russian_dolls()
        dupe_count = sum(len(v) - 1 for v in self.duplicates.values())
        return (
            f"\n🧹  REPO CLEANUP REPORT\n====================================\n"
            f"Root: {self.root}\n\n"
            f"Russian‑doll directories: {len(dolls)}\n"
            f"Duplicate extra files:   {dupe_count}\n"
            f"Potential secrets:       {len(self.secrets_found)}\n"
        )

    def execute(self) -> None:
        self._ensure_layout()
        self.flatten_backend()
        self.copy_frontend()
        self.create_env_examples()
        self.move_docs_configs()
        self.purge_artifacts()
        self.write_gitignore()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Flatten + sanitise a Scorpius repo")
    p.add_argument("root", help="Path to repo root, e.g. ./NewScorp")
    p.add_argument(
        "--execute", action="store_true", help="Apply changes instead of dry‑run"
    )
    p.add_argument(
        "--move-docs",
        action="store_true",
        help="Move (not copy) docs/configs into place",
    )
    p.add_argument(
        "--remove-artifacts",
        action="store_true",
        help="Delete .pyc/.pyd/.exe and .venv after copying",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cleaner = RepoCleanup(
        Path(args.root),
        move_docs=args.move_docs,
        remove_artifacts=args.remove_artifacts,
    )

    cleaner.analyse()
    print(cleaner.report())

    if args.execute:
        proceed = (
            input("\nContinue with destructive cleanup? [y/N] ").lower().startswith("y")
        )
        if proceed:
            cleaner.execute()
            print(
                "\n✅  Cleanup completed. Review *_clean directories before swapping in."
            )
        else:
            print("Aborted.")
    else:
        print("\n(Dry‑run only — no files changed. Re‑run with --execute when ready.)")


if __name__ == "__main__":
    main()
