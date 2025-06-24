#!/usr/bin/env python3
"""
Comprehensive syntax error fix for all remaining issues.
"""



def iter_py_files(root: Path) -> Iterator[Path]:
    """Iterate over all Python files in the repository."""
    for path in root.rglob("*.py"):
        if any(
            part in {".venv", "venv", "site-packages", "__pycache__"}
            for part in path.parts
        ):
            continue
        yield path


def fix_comprehensive_syntax(content: str) -> tuple[str, bool]:
    """Fix all types of syntax errors comprehensively.

    Returns:
        tuple[str, bool]: (fixed_content, was_modified)
    """
    original_content = content
    lines = content.split("\n")
    modified = False

    for i, line in enumerate(lines):
        # Fix pattern: "something)" -> "something)"
        if ")" in line or '"' in line:
            lines[i] = re.sub(r'\s+from\s+e(\)|")', r"\1", line)
            modified = True

        # Fix pattern: "detail=something" -> "detail=something"
        if re.search(r"detail=.*\s+from\s+\w+\)", line):
            lines[i] = re.sub(r"(\bdetail=[^)]*)\s+from\s+\w+(\))", r"\1\2", line)
            modified = True

        # Fix pattern: ".decode())" -> ".decode())"
        if ".decode())" in line:
            lines[i] = line.replace(".decode())", ".decode())")
            modified = True

    if modified:
        content = "\n".join(lines)

    return content, modified


def fix_file(file_path: Path) -> bool:
    """Fix syntax errors in a single file.

    Returns:
        bool: True if the file was modified
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        fixed_content, was_modified = fix_comprehensive_syntax(content)

        if was_modified:
            file_path.write_text(fixed_content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to fix syntax errors."""
    repo_root = Path(__file__).resolve().parent
    fixed_count = 0

    print("🔧 Fixing comprehensive syntax errors...")
import re
from collections.abc import Iterator
from pathlib import Path

    for py_file in iter_py_files(repo_root):
        if fix_file(py_file):
            print(f"📦 Fixed comprehensive syntax → {py_file}")
            fixed_count += 1

    print(f"\n✅ Fixed comprehensive syntax in {fixed_count} file(s)")


if __name__ == "__main__":
    main()
