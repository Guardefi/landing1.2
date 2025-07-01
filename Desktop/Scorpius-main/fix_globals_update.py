#!/usr/bin/env python3
"""
Fix globals().update() calls that were malformed by previous syntax fixes
"""

import re
from pathlib import Path


def fix_globals_update(content):
    """Fix malformed globals().update() patterns"""

    # Pattern 1: globals().update({}) followed by orphaned dictionary entries
    pattern1 = r'globals\(\)\.update\(\{\}\)\s*\n((?:\s*[\'"][^\'\"]+[\'"]:\s*[^,]+,?\s*\n)+)\s*\}\)'

    def replace_pattern1(match):
        orphaned_entries = match.group(1)
        return f'globals().update({{\n{orphaned_entries}}})'

    content = re.sub(pattern1, replace_pattern1, content, flags=re.MULTILINE)

    # Pattern 2: Fix indentation issues in dictionary entries
    lines = content.split('\n')
    fixed_lines = []
    in_globals_update = False

    for i, line in enumerate(lines):
        if 'globals().update({' in line and not line.strip().endswith('})'):
            in_globals_update = True
            fixed_lines.append(line)
        elif in_globals_update and line.strip() == '})':
            in_globals_update = False
            fixed_lines.append(line)
        elif in_globals_update and line.strip().startswith(("'", '"')) and ':' in line:
            # Fix indentation for dictionary entries
            if not line.startswith('    '):
                indent = '    '
                fixed_lines.append(indent + line.strip())
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def fix_bracket_indentation(content):
    """Fix specific bracket indentation issues"""

    # Fix 'SimilarityEngine': MockSimilarityEngine, indentation
    lines = content.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        # Check if this line is a dictionary entry that should be indented
        if (line.strip().startswith(("'SimilarityEngine':", '"SimilarityEngine":'))
                and 'MockSimilarityEngine' in line and not line.startswith('    ')):
            # Add proper indentation
            fixed_lines.append('    ' + line.strip())
        elif (line.strip().endswith(': MockSimilarityEngine,') and
              not line.startswith('    ')):
            # Add proper indentation for any mock entries
            fixed_lines.append('    ' + line.strip())
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def fix_f_string_errors(content):
    """Fix f-string syntax errors"""
    # Fix the pattern: print(f"Error: {str(e)}")
    content = re.sub(
        r'print\(f"Error: \{str\(e\)\}"\)',
        r'print(f"Error: {str(e)}")',
        content)
    return content


def process_file(file_path):
    """Process a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content

        # Apply fixes
        content = fix_globals_update(content)
        content = fix_bracket_indentation(content)
        content = fix_f_string_errors(content)

        # Only write if content changed
        if content != original_content:
            # Backup original
            backup_path = str(file_path) + '.backup_globals'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)

            # Write fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True, "Fixed globals().update() and indentation"
        else:
            return True, "No changes needed"

    except Exception as e:
        return False, f"Error: {e}"


def main():
    """Main execution"""
    print("Fixing globals().update() calls and indentation issues...")
    print("=" * 60)

    # Get all Python test files
    test_files = list(Path('.').rglob('*test*.py'))

    # Filter out backup files
    test_files = [f for f in test_files if '.backup' not in str(f)]

    processed = 0
    failed = 0

    for test_file in test_files:
        print(f"Processing: {test_file}")
        success, message = process_file(test_file)

        if success:
            processed += 1
            print(f"  ✓ {message}")
        else:
            failed += 1
            print(f"  ✗ {message}")

    print("\n" + "=" * 60)
    print(f"GLOBALS FIX SUMMARY")
    print(f"Total files: {len(test_files)}")
    print(f"Successfully processed: {processed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {processed/len(test_files)*100:.1f}%")


if __name__ == "__main__":
    main()
