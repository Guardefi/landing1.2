#!/usr/bin/env python3
"""
Bulk fix B904 and F821 errors to massively reduce lint count.

B904: Add "from err" or "from None" to raise statements in except blocks
F821: Fix undefined variable "e" in except blocks (usually wrong variable name)
"""



def fix_b904_patterns(content: str) -> str:
    """Fix B904 - Add 'from err' or 'from None' to raise statements."""

    # Pattern 1: raise HTTPException(...) -> raise HTTPException(...) from e
    # Only if we're already in an except block with 'except Exception as e:'
    pattern1 = re.compile(
        r"""
        (except\s+Exception\s+as\s+e:.*?)           # except Exception as e: (capture group 1)
        (.*?)                                       # any content in between (capture group 2)
        (raise\s+HTTPException\(                    # raise HTTPException( (capture group 3)) from e
        (?:[^)]*?)                                  # arguments inside
        \))                                         # closing paren
        (?!\s+from\s+(?:e|None))                    # negative lookahead - not already followed by "from e" or "from None"
        """,
        re.VERBOSE | re.DOTALL,
    )

    def replace1(match):
        except_part = match.group(1)
        middle = match.group(2)
        raise_part = match.group(3)
        return f"{except_part}{middle}{raise_part}) from e"

    content = pattern1.sub(replace1, content)

    # Pattern 2: Other exceptions -> from None (for re-raises)
    pattern2 = re.compile(
        r"""
        (raise\s+(?:ValueError|RuntimeError|TypeError|Exception)\(
        [^)]*
        \))
        (?!\s+from\s+(?:e|None|err))
        """,
        re.VERBOSE | re.DOTALL,
    )

    content = pattern2.sub(r"\1 from None", content)

    return content


def fix_f821_patterns(content: str) -> str:
    """Fix F821 - undefined name 'e' by fixing variable names."""

    # Pattern: except Exception as err: ... some code referencing 'err'
    # Fix by changing 'err' references to 'err'

    # Find except blocks with wrong variable names
    pattern = re.compile(
        r"""
        (except\s+\w+\s+as\s+(err|ex|error|exception):.*?)  # except with variable name (capture groups 1,2)
        (.*?)                                                # content with potential 'e' references (capture group 3)
        (?=except|def\s|class\s|$)                          # until next except/def/class or end
        """,
        re.VERBOSE | re.DOTALL,
    )

    def fix_var_refs(match):
        except_line = match.group(1)
        var_name = match.group(2)  # err, ex, error, exception
        block_content = match.group(3)

        # Replace standalone 'e' with the correct variable name
        # Be careful not to replace 'e' in words like 'except', 'execute', etc.
        fixed_content = re.sub(r"\be\b(?!\w)", var_name, block_content)

        return except_line + fixed_content

    content = pattern.sub(fix_var_refs, content)

    # Also fix the common case: except Exception: (no 'as' clause) but code uses 'e'
    # Change to: except Exception as e:
    pattern_no_as = re.compile(
        r"except\s+(Exception|[A-Z]\w*Error)\s*:\s*\n(.*?)(?:\n\s*(?:logger|print).*?str\(e\))",
        re.DOTALL,
    )

    def add_as_clause(match):
        exception_type = match.group(1)
        return f'except {exception_type} as e:\n{match.group(2)}\n    logger.error(f"Error: {{e}}")'

    content = pattern_no_as.sub(add_as_clause, content)

    return content


def fix_e402_patterns(content: str) -> str:
    """Fix E402 - Move imports to top of file."""

    # Split content into lines
    lines = content.split("\n")

    # Find imports that are not at the top
    import_lines = []
    non_import_lines = []
    shebang = None
    docstring_start = None
    docstring_end = None

    in_docstring = False
    docstring_quotes = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Handle shebang
        if i == 0 and stripped.startswith("#!"):
            shebang = line
            continue

        # Handle docstrings
        if not in_docstring and (
            stripped.startswith('"""') or stripped.startswith("'''")
        ):
            docstring_quotes = stripped[:3]
            docstring_start = i
            if stripped.count(docstring_quotes) >= 2:  # Single line docstring
                docstring_end = i
            else:
                in_docstring = True
            non_import_lines.append(line)
            continue

        if in_docstring and docstring_quotes in stripped:
            docstring_end = i
            in_docstring = False
            non_import_lines.append(line)
            continue

        if in_docstring:
            non_import_lines.append(line)
            continue

        # Handle imports vs other code
        if stripped.startswith(("import ", "from ")) and "import" in stripped:
            # Only move imports that are after non-import code
            if any(
                non_import_lines[j].strip()
                and not non_import_lines[j].strip().startswith("#")
                and not non_import_lines[j].strip().startswith(('"""', "'''"))
                for j in range(len(non_import_lines))
            ):
                import_lines.append(line)
            else:
                non_import_lines.append(line)
        else:
            non_import_lines.append(line)

    # Reconstruct file
    result_lines = []
    if shebang:
        result_lines.append(shebang)

    # Add early non-import lines (docstring, etc.)
    for i, line in enumerate(non_import_lines):
        if docstring_end is not None and i <= docstring_end:
            result_lines.append(line)
        elif docstring_end is None and (
            line.strip().startswith(('"""', "'''")) or not line.strip()
        ):
            result_lines.append(line)
        else:
            break

    # Add moved imports
    for imp in import_lines:
        result_lines.append(imp)

    # Add remaining content
    start_idx = docstring_end + 1 if docstring_end is not None else 0
    for i, line in enumerate(non_import_lines[start_idx:], start_idx):
        if line not in import_lines:  # Don't duplicate imports
            result_lines.append(line)

    return "\n".join(result_lines)


def fix_file(file_path: Path) -> bool:
    """Fix a single file. Return True if modified."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        # Apply fixes
        content = fix_f821_patterns(content)
        content = fix_b904_patterns(content)
        content = fix_e402_patterns(content)

        if content != original:
            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + ".bak")
            shutil.copy2(file_path, backup_path)

            # Write fixed content
            file_path.write_text(content, encoding="utf-8")
            print(f"✅ Fixed {file_path.relative_to(Path.cwd())}")
            return True

        return False

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def main():
    """Fix B904 and F821 errors in all Python files."""

    # Focus on backend directory
    backend_dir = Path(".")
    py_files = list(backend_dir.rglob("*.py"))
import re
import shutil
from pathlib import Path

    print(f"🔧 Processing {len(py_files)} Python files...")

    fixed_count = 0
    for py_file in py_files:
        if fix_file(py_file):
            fixed_count += 1

    print(f"\n🎉 Fixed {fixed_count}/{len(py_files)} files")
    print("💡 Run 'ruff check . --fix' next to apply remaining auto-fixes")


if __name__ == "__main__":
    main()
