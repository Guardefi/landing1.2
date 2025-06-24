#!/usr/bin/env python3
"""
Fix malformed raise HTTPException patterns in time_machine.py
The patterns look like:
    raise HTTPException() from e
        status_code=...,
        detail=...,
    )
"""



def fix_malformed_raises(content: str) -> str:
    """Fix the specific malformed pattern."""
    # Pattern: raise HTTPException() from e\n    status_code=...\n    detail=...\n)
    pattern = re.compile(
        r"raise HTTPException\(\s*from\s+e\s*\n"
import re
from pathlib import Path

        r"(\s+)(status_code=[^,\n]+),?\s*\n"
        r"(\s+)(detail=[^,\n)]+),?\s*\n"
        r"\s*\)",
        re.MULTILINE,
    )

    def replacement(match):
        indent = match.group(1)
        status_code = match.group(2)
        detail = match.group(4)
        return f"raise HTTPException(\n{indent}{status_code},\n{indent}{detail},\n{indent}) from e"

    return pattern.sub(replacement, content)


def main():
    file_path = Path("time_machine/time_machine.py")

    if not file_path.exists():
        print(f"File {file_path} not found")
        return

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    original_content = content
    fixed_content = fix_malformed_raises(content)

    if fixed_content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_content)
        print(f"✔ Fixed malformed raise patterns in {file_path}")

        # Count how many we fixed
        count = len(re.findall(r"raise HTTPException\(\s*from\s+e", original_content))
        print(f"  Fixed {count} malformed raise statements")
    else:
        print(f"No malformed patterns found in {file_path}")


if __name__ == "__main__":
    main()
