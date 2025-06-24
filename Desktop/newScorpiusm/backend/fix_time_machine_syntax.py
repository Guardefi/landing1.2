#!/usr/bin/env python3
"""
Autofix malformed `raise HTTPException(` statements that accidentally put
`from e` **inside** the parentheses instead of after them.

  • Scans every *.py file (recursively) from the working directory downward.
  • Creates a <file>.bak copy before editing.
  • Handles the three most-common variants we've seen so far.
  • Prints a one-liner for each fix so you can commit or revert confidently.
"""



# ────────────────────────────────
# Regexes for the known patterns
# ────────────────────────────────
# 1) One-liner:   raise HTTPException() from e
PAT_ONE_LINE: Final = re.compile(
    r"raise\s+HTTPException\(\s*from\s+e(?!\w)", re.MULTILINE
)

# 2) Multi-line,   raise HTTPException() from e\n    status_code=...
PAT_MULTI_LINE_1: Final = re.compile(
    r"""raise\s+HTTPException\(\s*from\s+e\s*\n  # opener
        (?P<body>(?:[ \t]+\S.*\n)+?)             # arguments chunk
        [ \t]*\)                                # closing paren
    """,
    re.VERBOSE,
)

# 3) Same as #2 but with a trailing comma before the newline
PAT_MULTI_LINE_2: Final = re.compile(
    r"""raise\s+HTTPException\(\s*from\s+e,\s*\n
        (?P<body>(?:[ \t]+\S.*\n)+?)
        [ \t]*\)
    """,
    re.VERBOSE,
)

REPLACEMENTS = [
    # simple one-liner → just move `from e` outside
    (
        PAT_ONE_LINE,
        lambda _: "raise HTTPException() from e",  # we leave an empty arg list; black/ruff will flag if more args needed
    ),
    # multi-line (#1)
    (
        PAT_MULTI_LINE_1,
        lambda m: f"raise HTTPException(\n{m.group('body')}) from e",
    ),
    # multi-line + trailing comma (#2)
    (
        PAT_MULTI_LINE_2,
        lambda m: f"raise HTTPException(\n{m.group('body')}) from e",
    ),
]


def fix_file(path: Path) -> bool:
    """Return True if the file was modified."""
    txt = path.read_text(encoding="utf-8")
    original = txt
    for pattern, repl in REPLACEMENTS:
        txt = re.sub(pattern, repl, txt)

    if txt == original:
        return False
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path
from typing import Final

    # backup then write
    shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
    path.write_text(txt, encoding="utf-8")
    print(f"✔ fixed {path.relative_to(ROOT)}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fix malformed `raise HTTPException() from e` statements."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root to scan (default: current directory)",
    )
    args = parser.parse_args()

    global ROOT  # just for pretty printing inside fix_file
    ROOT = args.root.resolve()

    py_files = list(ROOT.rglob("*.py"))
    modified = sum(fix_file(p) for p in py_files)

    print(f"\n🧽  Done. {modified}/{len(py_files)} files updated.")


if __name__ == "__main__":
    main()
