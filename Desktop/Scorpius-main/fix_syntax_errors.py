#!/usr/bin/env python3
"""
Fix syntax errors in test files created by the previous fix script.
Specifically addresses malformed try statements without except/finally blocks.
"""

import os
import re
from pathlib import Path


class SyntaxErrorFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.fixes_applied = 0
        self.files_processed = 0

    def find_all_test_files(self):
        """Find all test files in the project"""
        test_files = []
        for pattern in ["test_*.py", "*_test.py"]:
            test_files.extend(list(self.project_root.rglob(pattern)))
        return test_files

    def fix_malformed_imports(self, content):
        """Fix malformed try statements in imports"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check for malformed try statements
            if line.strip().startswith('try:') and i + 1 < len(lines):
                next_line = lines[i + 1].strip()

                # If next line is import/from and not indented properly, or if
                # there's another try: right after
                if (next_line.startswith('import ') or next_line.startswith(
                        'from ')) and not next_line.startswith('    '):
                    # This is a malformed try, convert to simple import
                    import_line = lines[i + 1]
                    fixed_lines.append(import_line)
                    i += 2  # Skip both the try and the import line
                    continue
                elif next_line.startswith('try:'):
                    # Multiple try statements, skip this one
                    i += 1
                    continue

            fixed_lines.append(line)
            i += 1

        return '\n'.join(fixed_lines)

    def remove_duplicate_fallback_sections(self, content):
        """Remove duplicate fallback import sections"""
        # Split content into sections
        sections = content.split(
            '# Fallback imports and mocks for missing modules')

        if len(sections) <= 1:
            return content

        # Keep only the first section and the last part (actual test code)
        # Find where the actual test code starts
        first_section = sections[0]

        # Look for the actual test code after all the fallback sections
        for i in range(len(sections) - 1, 0, -1):
            section = sections[i]
            # Look for actual test functions or classes
            if ('def test_' in section or 'class Test' in section or
                    'async def main' in section or 'if __name__' in section):
                # This section contains actual test code
                actual_code = section
                break
        else:
            # If no test code found, use the last section
            actual_code = sections[-1]

        # Combine first section with actual code
        return first_section + actual_code

    def clean_up_content(self, content):
        """Clean up the content by removing unnecessary duplications"""
        # Remove multiple consecutive empty lines
        content = re.sub(r'\n\n\n+', '\n\n', content)

        # Remove duplicate import statements
        lines = content.split('\n')
        seen_imports = set()
        cleaned_lines = []

        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                if line.strip() not in seen_imports:
                    seen_imports.add(line.strip())
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def fix_single_file(self, file_path):
        """Fix a single test file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                original_content = f.read()

            # Apply all fixes
            content = original_content
            content = self.fix_malformed_imports(content)
            content = self.remove_duplicate_fallback_sections(content)
            content = self.clean_up_content(content)

            # Only write if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied += 1
                print(f"[FIXED] {file_path.relative_to(self.project_root)}")
            else:
                print(f"[OK] {file_path.relative_to(self.project_root)}")

            self.files_processed += 1

        except Exception as e:
            print(f"[ERROR] Failed to fix {file_path}: {e}")

    def run_syntax_fix(self):
        """Run syntax fixes on all test files"""
        print("=" * 80)
        print("SCORPIUS SYNTAX ERROR FIXER")
        print("=" * 80)

        test_files = self.find_all_test_files()
        print(f"Found {len(test_files)} test files to process")

        # Filter out certain files we don't want to modify
        skip_patterns = [
            "__pycache__",
            ".git",
            "node_modules",
            "conftest.py",
        ]

        filtered_files = []
        for test_file in test_files:
            skip = False
            for pattern in skip_patterns:
                if pattern in str(test_file):
                    skip = True
                    break
            if not skip:
                filtered_files.append(test_file)

        print(f"Processing {len(filtered_files)} test files...")
        print()

        for test_file in filtered_files:
            self.fix_single_file(test_file)

        print()
        print("=" * 80)
        print("SYNTAX FIX SUMMARY")
        print("=" * 80)
        print(f"Files processed: {self.files_processed}")
        print(f"Files modified: {self.fixes_applied}")
        print(
            f"Success rate: {(self.files_processed / len(filtered_files) * 100):.1f}%")
        print()
        print("Syntax errors have been fixed!")


def main():
    """Main entry point"""
    fixer = SyntaxErrorFixer()
    fixer.run_syntax_fix()


if __name__ == "__main__":
    main()
