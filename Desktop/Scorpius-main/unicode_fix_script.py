#!/usr/bin/env python3
"""
Unicode Fix Script for Scorpius Test Files
Replaces problematic Unicode characters with ASCII equivalents
"""

import os
import sys
from pathlib import Path
import re


class UnicodeTestFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.fixes_applied = 0
        self.files_processed = 0

        # Comprehensive Unicode to ASCII mapping
        self.unicode_replacements = {
            # Emojis to ASCII
            '\U0001f389': '[CELEBRATION]',  # 🎉
            '\U0001f680': '[ROCKET]',       # 🚀
            '\U0001f50d': '[SEARCH]',       # 🔍
            '\U0001f9ea': '[TEST_TUBE]',    # 🧪
            '\U0001f52c': '[MICROSCOPE]',   # 🔬
            '\U0001f916': '[ROBOT]',        # 🤖
            '\U0001f4a5': '[EXPLOSION]',    # 💥
            '\U0001f6d1': '[STOP_SIGN]',    # 🛑
            '\u23f3': '[HOURGLASS]',        # ⏳
            '\u2705': '[CHECKMARK]',        # ✅
            '\u274c': '[X_MARK]',           # ❌
            '\u2713': '[CHECK]',            # ✓
            '\u2717': '[X]',                # ✗
            '\u269b\ufe0f': '[ATOM]',       # ⚛️
            '\u26a0\ufe0f': '[WARNING]',    # ⚠️
            '\u26a0': '[WARNING]',          # ⚠
            '\ufe0f': '',                   # Variation selector

            # Arrows and symbols
            '\u27a1': '->',                 # ➡️
            '\u2b05': '<-',                 # ⬅️
            '\u2b06': '^',                  # ⬆️
            '\u2b07': 'v',                  # ⬇️

            # Box drawing characters
            '\u2500': '-',                  # ─
            '\u2502': '|',                  # │
            '\u250c': '+',                  # ┌
            '\u2510': '+',                  # ┐
            '\u2514': '+',                  # └
            '\u2518': '+',                  # ┘
            '\u251c': '+',                  # ├
            '\u2524': '+',                  # ┤
            '\u252c': '+',                  # ┬
            '\u2534': '+',                  # ┴
            '\u253c': '+',                  # ┼

            # Mathematical symbols
            '\u2264': '<=',                 # ≤
            '\u2265': '>=',                 # ≥
            '\u2260': '!=',                 # ≠
            '\u00b1': '+/-',                # ±
            '\u00d7': 'x',                  # ×
            '\u00f7': '/',                  # ÷

            # Currency symbols
            '\u20ac': 'EUR',                # €
            '\u00a3': 'GBP',                # £
            '\u00a5': 'JPY',                # ¥

            # Other symbols
            '\u00ae': '(R)',                # ®
            '\u00a9': '(C)',                # ©
            '\u2122': '(TM)',               # ™
            '\u00b0': ' degrees',           # °
            '\u2026': '...',                # …

            # Smart quotes
            '\u201c': '"',                  # "
            '\u201d': '"',                  # "
            '\u2018': "'",                  # '
            '\u2019': "'",                  # '

            # Dashes
            '\u2013': '-',                  # –
            '\u2014': '--',                 # —
        }

    def find_test_files(self):
        """Find all test files in the project"""
        test_files = []
        for pattern in ["test_*.py", "*_test.py"]:
            test_files.extend(list(self.project_root.rglob(pattern)))
        return test_files

    def fix_unicode_in_file(self, file_path):
        """Fix Unicode characters in a single file"""
        try:
            # Read file with error handling
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            original_content = content

            # Apply Unicode replacements
            for unicode_char, replacement in self.unicode_replacements.items():
                if unicode_char in content:
                    content = content.replace(unicode_char, replacement)
                    self.fixes_applied += 1

            # Additional regex-based fixes for compound Unicode sequences
            # Fix Unicode escape sequences that might be causing issues
            content = re.sub(
                r'\\u[0-9a-fA-F]{4}',
                lambda m: self._fix_unicode_escape(
                    m.group(0)),
                content)
            content = re.sub(
                r'\\U[0-9a-fA-F]{8}',
                lambda m: self._fix_unicode_escape(
                    m.group(0)),
                content)

            # Only write if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(content)
                print(f"[FIXED] {file_path.relative_to(self.project_root)}")
                return True
            else:
                print(f"[OK] {file_path.relative_to(self.project_root)}")
                return False

        except Exception as e:
            print(f"[ERROR] Failed to fix {file_path}: {e}")
            return False

    def _fix_unicode_escape(self, escape_sequence):
        """Fix individual Unicode escape sequences"""
        try:
            # Convert escape sequence to actual Unicode character
            if escape_sequence.startswith('\\u'):
                unicode_char = escape_sequence.encode().decode('unicode_escape')
            elif escape_sequence.startswith('\\U'):
                unicode_char = escape_sequence.encode().decode('unicode_escape')
            else:
                return escape_sequence

            # Replace with ASCII equivalent if we have one
            return self.unicode_replacements.get(unicode_char, escape_sequence)
        except BaseException:
            return escape_sequence

    def fix_all_unicode_issues(self):
        """Fix Unicode issues in all test files"""
        print("=" * 80)
        print("UNICODE FIX SCRIPT FOR SCORPIUS TESTS")
        print("=" * 80)

        test_files = self.find_test_files()
        print(f"Found {len(test_files)} test files to process")

        # Filter out certain files
        skip_patterns = [
            "__pycache__",
            ".backup",
            "fix_all_tests.py",
            "test_runner.py",
            "unicode_fix_script.py"
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
        print("-" * 80)

        fixed_count = 0
        for test_file in filtered_files:
            self.files_processed += 1
            if self.fix_unicode_in_file(test_file):
                fixed_count += 1

        print("-" * 80)
        print("UNICODE FIX SUMMARY")
        print("-" * 80)
        print(f"Files processed: {self.files_processed}")
        print(f"Files fixed: {fixed_count}")
        print(f"Unicode replacements made: {self.fixes_applied}")
        print(
            f"Success rate: {(self.files_processed / len(filtered_files) * 100):.1f}%")

        if fixed_count > 0:
            print(
                "\n✅ Unicode issues fixed! Tests should now handle Windows encoding better.")
        else:
            print("\n✅ No Unicode issues found in test files.")


def main():
    fixer = UnicodeTestFixer()
    fixer.fix_all_unicode_issues()


if __name__ == "__main__":
    main()
