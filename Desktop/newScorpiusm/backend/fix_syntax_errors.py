#!/usr/bin/env python3
"""
Autofix B904 (“raise ... without `from`”) across the code-base.

Strategy
========
1. Walk every *.py file under the repo.
2. Parse each with `ast`.
3. For every `raise` inside an `except … as <var>` block that lacks a
   `from`, append  `from <var>`.
4. Write the patched file back.

Why AST?
--------
Regex fails on multi-line statements and comments.  The AST guarantees
we only touch real `raise` nodes and keeps formatting intact.
"""




# ───────────────────────────────────────────────────────────── helpers ──────
def iter_py_files(root: Path) -> Iterator[Path]:
    for path in root.rglob("*.py"):
        if any(part in {".venv", "venv", "site-packages", "__pycache__"} for part in path.parts):
            continue
        yield path


class B904Collector(ast.NodeVisitor):
    """Collect (lineno, except_var) tuples where `raise` is missing a cause."""

    def __init__(self) -> None:
        self.todo: list[tuple[int, str]] = []
        self._stack: list[str | None] = []

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self._stack.append(node.name)  # may be None
        self.generic_visit(node)
        self._stack.pop()

    def visit_Raise(self, node: ast.Raise) -> None:
        if self._stack and self._stack[-1] and node.cause is None:
            self.todo.append((node.lineno, self._stack[-1]))
        self.generic_visit(node)


def patch_file(path: Path) -> bool:
    """Return True if the file was modified."""
    try:
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except SyntaxError:
        return False  # skip broken files
from __future__ import annotations

import ast
from collections.abc import Iterator
from pathlib import Path

    collector = B904Collector()
    collector.visit(tree)
    if not collector.todo:
        return False

    lines = src.splitlines(keepends=True)

    # Edit bottom-up so line numbers stay valid
    for lineno, var in sorted(collector.todo, reverse=True):
        code, *comment = lines[lineno - 1].rstrip("\n").split("#", maxsplit=1)
        if f" from {var}" not in code:
            code = code.rstrip() + f" from {var}"
        lines[lineno - 1] = code + (" #" + comment[0] if comment else "") + "\n"

    path.write_text("".join(lines), encoding="utf-8")
    return True


# ────────────────────────────────────────────────────────────── main ───────
def main() -> None:
    repo_root = Path(__file__).resolve().parent
    changed = 0

    for py in iter_py_files(repo_root):
        if patch_file(py):
            changed += 1
            print(f"Patched {py}")

    print(f"\n✅ Added `from <err>` to {changed} file(s)")


if __name__ == "__main__":
    main()
