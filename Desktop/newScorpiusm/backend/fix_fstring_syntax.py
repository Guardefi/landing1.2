#!/usr/bin/env python3
"""
Fix f-string syntax errors where 'from e' is inside the f-string brackets.
Converts: f"text: {str(e)}" -> f"text: {str(e)}"
The 'from e' is already handled by the raise statement.
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


def fix_fstring_syntax(content: str) -> tuple[str, bool]:
    """Fix f-string syntax errors where 'from e' is inside the f-string.

    Returns:
        tuple[str, bool]: (fixed_content, was_modified)
    """
    # Pattern to match f-strings with "from e" inside the brackets
    # Matches: f"...{str(e)}..." or similar patterns
    pattern = r'f"([^"]*)\{([^}]*)\s+from\s+([^}]+)\}([^"]*)"'

    def replace_func(match):
        prefix = match.group(1)
        expr_part = match.group(2).strip()
        var_name = match.group(3).strip()
        suffix = match.group(4)

        # Remove "from var" from the expression and clean it up
        # If the expression was "str(e)", make it just "str(e)"
        if f" from {var_name}" in expr_part:
            expr_part = expr_part.replace(f" from {var_name}", "").strip()

        return f'f"{prefix}{{{expr_part}}}{suffix}"'

    original_content = content
    content = re.sub(pattern, replace_func, content)

    # Also handle single-quoted f-strings
    pattern_single = r"f'([^']*)\\{([^}]*)\\s+from\\s+([^}]+)\\}([^']*)'"
    content = re.sub(pattern_single, replace_func, content)

    return content, content != original_content


def fix_file(file_path: Path) -> bool:
    """Fix f-string syntax errors in a single file.

    Returns:
        bool: True if the file was modified
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        fixed_content, was_modified = fix_fstring_syntax(content)

        if was_modified:
            file_path.write_text(fixed_content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to fix f-string syntax errors."""
    repo_root = Path(__file__).resolve().parent
    fixed_count = 0

    print("🔧 Fixing f-string syntax errors...")
import re
from collections.abc import Iterator
from pathlib import Path

    for py_file in iter_py_files(repo_root):
        if fix_file(py_file):
            print(f"📦 Fixed f-string syntax → {py_file}")
            fixed_count += 1

    print(f"\n✅ Fixed f-string syntax errors in {fixed_count} file(s)")


if __name__ == "__main__":
    main()
