#!/usr/bin/env python3
"""
Batch fix script for Python syntax errors in backend.
"""

import pathlib
import py_compile
import subprocess


def check_compilation_errors():
    """Find all Python files with compilation errors."""
    bad_files = []
    for p in pathlib.Path("backend").rglob("*.py"):
        try:
            py_compile.compile(p, doraise=True)
        except Exception:
            bad_files.append(str(p))
    return bad_files


def fix_common_issues(file_path):
    """Fix common issues in a Python file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix common issues
        lines = content.split("\n")
        fixed_lines = []
        imports_to_add = set()
        inside_function = False

        for i, line in enumerate(lines):
            # Check if we're inside a function/class
            if line.strip().startswith(("def ", "class ", "async def ")):
                inside_function = True
            elif line.strip() and not line.startswith((" ", "\t")):
                inside_function = False

            # If we find imports inside functions, move them to top and remove from here
            if inside_function and line.strip().startswith(("import ", "from ")):
                imports_to_add.add(line.strip())
                continue

            # Fix malformed raise statements
            if "raise HTTPException(" in line and "from e" in line:
                # Find the complete raise statement
                if not line.strip().endswith(")"):
                    # Multi-line raise statement
                    continue
                else:
                    # Single line - fix it
                    line = line.replace(" from e", "") + " from e"

            fixed_lines.append(line)

        # Add imports at the top if needed
        if imports_to_add:
            # Find where to insert imports
            insert_pos = 0
            for i, line in enumerate(fixed_lines):
                if (
                    line.strip().startswith("#")
                    or line.strip().startswith('"""')
                    or not line.strip()
                ):
                    continue
                if line.strip().startswith(("import ", "from ")):
                    insert_pos = i + 1
                else:
                    break

            # Insert imports
            for imp in sorted(imports_to_add):
                fixed_lines.insert(insert_pos, imp)
                insert_pos += 1

        new_content = "\n".join(fixed_lines)

        # Only write if content changed
        if new_content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ Fixed: {file_path}")
            return True
        else:
            print(f"⚪ No changes: {file_path}")
            return False

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def run_black_on_file(file_path):
    """Run Black formatter on a file."""
    try:
        subprocess.run(["black", file_path], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    print("🔧 Finding files with compilation errors...")
    bad_files = check_compilation_errors()

    print(f"Found {len(bad_files)} files with compilation errors")

    # Process files in batches
    batch_size = 10
    for i in range(0, len(bad_files), batch_size):
        batch = bad_files[i : i + batch_size]
        print(f"\n📦 Processing batch {i//batch_size + 1}: {len(batch)} files")

        for file_path in batch:
            print(f"🔨 Processing: {file_path}")

            # Try to fix common issues
            fixed = fix_common_issues(file_path)

            # Run Black to clean up formatting
            if fixed:
                run_black_on_file(file_path)

            # Check if it compiles now
            try:
                py_compile.compile(file_path, doraise=True)
                print(f"✅ {file_path} now compiles!")
            except Exception as e:
                print(f"❌ {file_path} still has errors: {e}")

    # Final check
    print("\n🏁 Final compilation check...")
    remaining_bad = check_compilation_errors()
    print(f"Remaining files with errors: {len(remaining_bad)}")

    if remaining_bad:
        print("Files still needing manual fixes:")
        for f in remaining_bad[:10]:  # Show first 10
            print(f"  - {f}")


if __name__ == "__main__":
    main()
