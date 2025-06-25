#!/usr/bin/env python3
"""
Fix all remaining syntax errors in the codebase.
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


def fix_syntax_errors(content: str) -> tuple[str, bool]:
    """Fix various syntax errors in the content.

    Returns:
        tuple[str, bool]: (fixed_content, was_modified)
    """
    original_content = content

    # Fix 1: "raise e" -> "raise e"
    content = re.sub(r"\braise\s+from\s+(\w+)", r"raise \1 from \1", content)

    # Fix 2: "str(e)" in function calls -> "str(e)"
    content = re.sub(r"str\((\w+)\)\s+from\s+\1", r"str(\1)", content)

    # Fix 3: HTTPException with malformed from clause
    content = re.sub(
        r"HTTPException\([^)]*detail=([^)]*)\s+from\s+(\w+)\)",
        r"HTTPException(status_code=500, detail=\1)",
        content,
    )

    # Fix 4: Other function calls with "from e" pattern
    content = re.sub(r"([a-zA-Z_]\w*\([^)]*)\s+from\s+(\w+)\)", r"\1)", content)

    return content, content != original_content


def fix_file(file_path: Path) -> bool:
    """Fix syntax errors in a single file.

    Returns:
        bool: True if the file was modified
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        fixed_content, was_modified = fix_syntax_errors(content)

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

    print("🔧 Fixing remaining syntax errors...")
import re
from collections.abc import Iterator
from pathlib import Path

    for py_file in iter_py_files(repo_root):
        if fix_file(py_file):
            print(f"📦 Fixed syntax errors → {py_file}")
            fixed_count += 1

    print(f"\n✅ Fixed syntax errors in {fixed_count} file(s)")


if __name__ == "__main__":
    main()
