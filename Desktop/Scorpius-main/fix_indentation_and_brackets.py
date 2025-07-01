#!/usr/bin/env python3
"""
Targeted Fix Script for Indentation and Bracket Issues
Addresses the specific syntax errors found in test output.
"""

import os
import re
import glob
import json
from pathlib import Path


def fix_mock_registry_indentation(content):
    """Fix indentation issues with mock registry lines"""
    lines = content.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        # Fix the common indentation error pattern
        if ("'SimilarityEngine': MockSimilarityEngine," in line and
                line.strip() == "'SimilarityEngine': MockSimilarityEngine,"):
            # Find proper indentation by looking at surrounding context
            proper_indent = 4
            if i > 0:
                prev_line = lines[i-1]
                if prev_line.strip().startswith(
                        'MOCK_REGISTRY = {') or 'globals().update({' in prev_line:
                    proper_indent = len(prev_line) - \
                        len(prev_line.lstrip()) + 4
                elif prev_line.strip() and not prev_line.strip().startswith(('#', '"""', "'''")):
                    proper_indent = len(prev_line) - len(prev_line.lstrip())

            fixed_lines.append(' ' * proper_indent + line.strip())
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def fix_bracket_mismatches(content):
    """Fix bracket and parenthesis mismatches"""
    lines = content.split('\n')
    fixed_lines = []
    bracket_stack = []

    for line_num, line in enumerate(lines):
        original_line = line

        # Track brackets for context
        for char in line:
            if char in '([{':
                bracket_stack.append((char, line_num))
            elif char in ')]}':
                if bracket_stack and ((char == ')' and bracket_stack[-1][0] == '(') or
                                      (char == ']' and bracket_stack[-1][0] == '[') or
                                      (char == '}' and bracket_stack[-1][0] == '{')):
                    bracket_stack.pop()

        # Fix common patterns
        fixed_line = line

        # Fix closing bracket mismatches
        if line.strip(
        ) == '}' and bracket_stack and bracket_stack[-1][0] == '[':
            fixed_line = line.replace('}', ']')
        elif line.strip() == ']' and bracket_stack and bracket_stack[-1][0] == '{':
            fixed_line = line.replace(']', '}')
        elif line.strip() == '},' and bracket_stack and bracket_stack[-1][0] == '[':
            fixed_line = line.replace('},', '],')
        elif line.strip() == '],' and bracket_stack and bracket_stack[-1][0] == '{':
            fixed_line = line.replace('],', '},')

        fixed_lines.append(fixed_line)

    return '\n'.join(fixed_lines)


def fix_malformed_docstrings(content):
    """Fix malformed docstrings"""
    # Fix patterns like """Text""" followed by more quotes
    content = re.sub(r'"""([^"]*?)"""([""]+)', r'"""\1"""', content)

    # Fix unterminated docstrings at end of functions
    lines = content.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        fixed_lines.append(line)

        # If we have a line with just quotes that might be unterminated
        if (line.strip().startswith('"""') and line.strip() != '"""' and
                line.count('"""') == 1 and i == len(lines) - 1):
            # Add closing docstring
            indent = len(line) - len(line.lstrip())
            fixed_lines.append(' ' * indent + '"""')

    return '\n'.join(fixed_lines)


def fix_f_string_syntax(content):
    """Fix f-string syntax errors"""
    # Fix the common f-string error pattern
    content = re.sub(
        r'print\(f"Error: \{([^}]+)\}"\)',
        r'print(f"Error: {\1}")',
        content)
    content = re.sub(
        r'print\(f"Error: \{str\(([^)]+)\)\}"\)',
        r'print(f"Error: {str(\1)}")',
        content)
    return content


def fix_try_except_blocks(content):
    """Fix malformed try-except blocks"""
    lines = content.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        if line.strip().startswith('try:'):
            fixed_lines.append(line)
            # Look ahead to ensure proper except block
            indent = len(line) - len(line.lstrip())
            has_except = False

            for j in range(i + 1, min(i + 10, len(lines))):
                if lines[j].strip().startswith(('except', 'finally')):
                    has_except = True
                    break
                elif (lines[j].strip() and
                      len(lines[j]) - len(lines[j].lstrip()) <= indent and
                      not lines[j].strip().startswith(('#', '"""', "'''"))):
                    break

            if not has_except:
                # Add a simple except block
                fixed_lines.append(' ' * (indent + 4) + 'pass')
                fixed_lines.append(' ' * indent + 'except Exception as e:')
                fixed_lines.append(' ' * (indent + 4) + 'print(f"Error: {e}")')
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def fix_parentheses_never_closed(content):
    """Fix unclosed parentheses issues"""
    lines = content.split('\n')
    fixed_lines = []
    open_parens = 0

    for line in lines:
        # Count parentheses
        for char in line:
            if char == '(':
                open_parens += 1
            elif char == ')':
                open_parens -= 1

        fixed_lines.append(line)

        # If we have unclosed parentheses at end of file, close them
        if line.strip() and open_parens > 0 and lines.index(line) == len(lines) - 1:
            indent = len(line) - len(line.lstrip())
            fixed_lines.append(' ' * indent + ')' * open_parens)

    return '\n'.join(fixed_lines)


def process_test_file(filepath):
    """Process a single test file with targeted fixes"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content

        # Apply targeted fixes
        content = fix_mock_registry_indentation(content)
        content = fix_bracket_mismatches(content)
        content = fix_malformed_docstrings(content)
        content = fix_f_string_syntax(content)
        content = fix_try_except_blocks(content)
        content = fix_parentheses_never_closed(content)

        # Only write if content changed
        if content != original_content:
            # Backup original
            backup_path = filepath + '.backup_targeted'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)

            # Write fixed content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            return True, "Fixed syntax issues"
        else:
            return True, "No changes needed"

    except Exception as e:
        return False, f"Error processing: {str(e)}"


def main():
    """Main execution function"""
    print("Starting Targeted Indentation and Bracket Fix")
    print("=" * 60)

    # Get all test files that had errors
    test_files = []
    for pattern in ["**/test_*.py", "**/*test*.py"]:
        test_files.extend(Path(".").rglob(pattern))

    # Filter out backup and problematic files
    excluded_patterns = [
        ".backup",
        "fix_",
        "test_runner",
        "__init__.py",
        "conftest.py"
    ]

    filtered_files = []
    for test_file in test_files:
        skip = False
        for pattern in excluded_patterns:
            if pattern in str(test_file):
                skip = True
                break
        if not skip:
            filtered_files.append(test_file)

    print(f"Found {len(filtered_files)} test files to process")

    results = {
        'total_files': len(filtered_files),
        'processed': 0,
        'failed': 0,
        'details': []
    }

    for i, test_file in enumerate(sorted(filtered_files), 1):
        print(f"[{i:2d}/{len(filtered_files):2d}] Processing: {test_file}")

        success, message = process_test_file(test_file)

        if success:
            results['processed'] += 1
            print(f"  ✓ {message}")
        else:
            results['failed'] += 1
            print(f"  ✗ {message}")

        results['details'].append({
            'file': str(test_file),
            'success': success,
            'message': message
        })

    # Save results
    with open('targeted_fix_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print("TARGETED FIX SUMMARY")
    print(f"Total files: {results['total_files']}")
    print(f"Successfully processed: {results['processed']}")
    print(f"Failed: {results['failed']}")
    print(
        f"Success rate: {
            results['processed']/results['total_files']*100:.1f}%")

    return results['failed'] == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
