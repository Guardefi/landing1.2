#!/usr/bin/env python3
"""
fix_syntax.py

Bulk-fix common Python syntax issues across a codebase:
  • Collapse runs of 4+ double-quotes into triple-quotes
  • Fix common mismatched brackets/parentheses: []→[], {}→{}, ()→(), ()→()
  • Insert `pass` into empty def/class bodies
  • Optionally re-format with autopep8 if installed, safely catching any errors

Usage:
  python -m pip install autopep8
  python fix_syntax.py [path]

Example:
  python fix_syntax.py .
"""

import re
import argparse
import sys
from pathlib import Path

# --- Regex-based fixes ---
REPLACEMENTS = {
    r'""{4,}': '"""',   # collapse 4+ quotes → exactly 3
    r'\[\)': '[]',
    r'\{\]': '{}',
    r'\(\]': '()',
    r'\(\}': '()',
}
DEF_CLASS_RE = re.compile(r'^(\s*)(def |class )(.+?:)\s*$')

# --- Try to import autopep8 once ---
try:
    import autopep8
except ImportError:
    autopep8 = None


def apply_regex_and_pass(text: str) -> str:
    # Apply simple replacements
    for patt, repl in REPLACEMENTS.items():
        text = re.sub(patt, repl, text)

    # Insert pass into empty defs/classes
    lines = text.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = DEF_CLASS_RE.match(line)
        if m:
            indent = m.group(1)
            # if next line isn't further indented, inject pass
            if i + \
                    1 >= len(lines) or not lines[i+1].startswith(indent + '    '):
                out.append(line)
                out.append(f"{indent}    pass\n")
                i += 1
                continue
        out.append(line)
        i += 1
    return ''.join(out)


def try_autopep8(text: str) -> str:
    if autopep8 is None:
        return text
    try:
        # aggressive=2 mimics two --aggressive flags
        return autopep8.fix_code(text, options={'aggressive': 2})
    except Exception as e:
        print(f"⚠️ autopep8 formatting skipped (error: {e})")
        return text


def fix_file(path: Path):
    content = path.read_text(encoding='utf-8')
    fixed = apply_regex_and_pass(content)
    fixed = try_autopep8(fixed)

    if fixed != content:
        path.write_text(fixed, encoding='utf-8')
        print(f"✔ Fixed: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Fix Python syntax issues project-wide")
    parser.add_argument(
        'root',
        nargs='?',
        default='.',
        help='Directory to scan')
    args = parser.parse_args()

    root = Path(args.root)
    for py in root.rglob("*.py"):
        # skip venvs, caches, hidden dirs
        if any(part.startswith(('.', 'venv', 'env', '__pycache__'))
               for part in py.parts):
            continue
        fix_file(py)

    print("\n✅ All done! Now re-run your tests with `pytest`.")


if __name__ == "__main__":
    main()
