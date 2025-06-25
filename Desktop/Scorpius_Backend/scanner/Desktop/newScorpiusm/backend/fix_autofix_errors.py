#!/usr/bin/env python3
"""
Script to fix the syntax errors introduced by automated lint fixes.
Focuses on the most common patterns:
1. Malformed f-strings: {str(e)}" -> {str(e)}"
2. Broken try/except/finally blocks
3. Indentation issues
"""

import os
import re
from pathlib import Path


def fix_malformed_fstrings(content):
    """Fix malformed f-strings caused by auto-fix attempts."""
    # Pattern: {str(e)}" should be {str(e)}"
    pattern1 = r'\{str\(e\)\) from e\}"'
    content = re.sub(pattern1, '{str(e)}"', content)

    # Pattern: {e}" should be {e}"
    pattern2 = r'\{e\)\) from e\}"'
    content = re.sub(pattern2, '{e}"', content)

    # Pattern: {str(ex)}" should be {str(ex)}"
    pattern3 = r'\{str\((\w+)\)\) from \1\}"'
    content = re.sub(pattern3, r'{str(\1)}"', content)

    # Pattern: {ex}" should be {ex}"
    pattern4 = r'\{(\w+)\)\) from \1\}"'
    content = re.sub(pattern4, r'{\1}"', content)

    return content


def fix_indentation_errors(content):
    """Fix basic indentation errors."""
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        # Check for unexpected indentation at the start of a line that should not be indented
        if line.strip() and not line[0].isspace():
            # Look for patterns that indicate this should be indented
            if any(
                keyword in line for keyword in ["except ", "finally:", "elif ", "else:"]
            ):
                if i > 0 and lines[i - 1].strip().endswith(":"):
                    line = "    " + line

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_broken_statements(content):
    """Fix broken statements and missing colons."""
    # Fix missing colons after try/except/finally
    content = re.sub(
        r"^(\s*)(try|except|finally|else|elif)\s*$",
        r"\1\2:",
        content,
        flags=re.MULTILINE,
    )

    # Fix broken except clauses
    content = re.sub(
        r"^(\s*)except\s+Exception\s+as\s+(\w+)\s*$",
        r"\1except Exception as \2:",
        content,
        flags=re.MULTILINE,
    )

    return content


def process_file(file_path):
    """Process a single Python file to fix syntax errors."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply fixes
        content = fix_malformed_fstrings(content)
        content = fix_broken_statements(content)
        content = fix_indentation_errors(content)

        # Only write if changes were made
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to process all Python files."""
    backend_dir = Path(__file__).parent

    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    print(f"Found {len(python_files)} Python files to process")

    fixed_count = 0
    for file_path in python_files:
        if process_file(file_path):
            fixed_count += 1

    print(f"\nProcessed {len(python_files)} files")
    print(f"Fixed {fixed_count} files")


if __name__ == "__main__":
    main()
