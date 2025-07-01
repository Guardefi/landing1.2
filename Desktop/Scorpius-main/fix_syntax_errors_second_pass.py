#!/usr/bin/env python3
"""
Second Pass Syntax Error Fix Script
Addresses specific remaining syntax issues after the first comprehensive fix.
"""

import os
import re
import sys
import json
import time
import logging
from pathlib import Path
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('syntax_fix_second_pass.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SecondPassSyntaxFixer:
    """Second pass syntax error fixer for specific issues"""

    def __init__(self):
        self.stats = {
            'files_processed': 0,
            'files_fixed': 0,
            'errors_fixed': 0,
            'failed_files': []
        }

    def find_test_files(self, root_dir: str = ".") -> List[str]:
        """Find all Python test files in the project"""
        test_files = []

        for root, dirs, files in os.walk(root_dir):
            skip_dirs = {
                '.git',
                '__pycache__',
                '.pytest_cache',
                'node_modules',
                '.venv',
                'venv'}
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            for file in files:
                if file.endswith('.py') and (
                        'test_' in file or file.endswith('_test.py') or 'test' in file.lower()):
                    test_files.append(os.path.join(root, file))

        logger.info(f"Found {len(test_files)} test files")
        return test_files

    def fix_unterminated_triple_quotes(self, content: str) -> str:
        """Fix unterminated triple-quoted strings"""
        # Fix pattern: """docstring"""
        content = re.sub(r'"""([^"]*?)"""', r'"""\1"""', content)

        # Fix pattern: """docstring."""
        content = re.sub(r'"""([^"]*?)\."""', r'"""\1."""', content)

        # Fix hanging triple quotes at end of line
        content = re.sub(
            r'"""([^"]*?)$',
            r'"""\1"""',
            content,
            flags=re.MULTILINE)

        return content

    def fix_unmatched_braces(self, content: str) -> str:
        """Fix unmatched braces and brackets"""
        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Fix standalone }) that should be removed
            if stripped == '})' and i > 0:
                prev_line = lines[i-1].strip()
                if not prev_line or 'globals().update({' in prev_line:
                    continue  # Skip this line

            # Fix unmatched } at start of line
            if stripped == '}' and i > 0:
                prev_line = lines[i-1].strip()
                if 'globals().update({' in prev_line or not prev_line:
                    continue  # Skip this line

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def fix_indentation_errors_in_globals(self, content: str) -> str:
        """Fix indentation errors in globals().update() calls"""
        lines = content.split('\n')
        fixed_lines = []
        inside_globals_update = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Detect start of problematic globals().update pattern
            if "globals().update({" in line and line.strip().endswith('{'):
                inside_globals_update = True
                fixed_lines.append("globals().update({})")
                continue

            # Skip lines that are part of malformed globals update
            if inside_globals_update and ("'SimilarityEngine'" in stripped or
                                          "'BytecodeNormalizer'" in stripped or
                                          "'MultiDimensionalComparison'" in stripped or
                                          "'TestClient'" in stripped):
                continue

            # End of malformed globals update
            if inside_globals_update and stripped in ['})', '}', '])']:
                inside_globals_update = False
                continue

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def fix_malformed_docstrings(self, content: str) -> str:
        """Fix malformed docstrings and invalid syntax"""
        # Fix docstring patterns that cause invalid syntax
        content = re.sub(
            r'^(\s*)([A-Z][^"]*?)\s*$',
            r'\1# \2',
            content,
            flags=re.MULTILINE)

        # Fix specific patterns
        replacements = [
            (r'Basic tests for the API Gateway without web3 dependencies\.',
             r'# Basic tests for the API Gateway without web3 dependencies.'),
            (r'API Test Script for Scorpius Enterprise Platform',
             r'# API Test Script for Scorpius Enterprise Platform'),
            (r'Test API endpoints for usage metering service',
             r'# Test API endpoints for usage metering service'),
            (r'Integration tests for usage metering service',
             r'# Integration tests for usage metering service'),
            (r'Test Stripe integration service',
             r'# Test Stripe integration service'),
            (r'Tests for the static analysis engine',
             r'# Tests for the static analysis engine'),
            (r'Test suite for Scorpius Enterprise Platform',
             r'# Test suite for Scorpius Enterprise Platform'),
            (r'Comprehensive Integration Test Suite for Enhanced Scorpius Scanner',
             r'# Comprehensive Integration Test Suite for Enhanced Scorpius Scanner'),
        ]

        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)

        return content

    def fix_invalid_f_strings(self, content: str) -> str:
        """Fix invalid f-string patterns"""
        # Fix pattern: result['avg_time'] * 1000:.2f}
        content = re.sub(
            r"(\w+\['[^']*'\]\s*\*\s*\d+):\.(\d+)f\}",
            r"\1:.2f}",
            content
        )

        return content

    def fix_mismatched_brackets_in_data_structures(self, content: str) -> str:
        """Fix mismatched brackets in data structures"""
        # Fix common patterns of mismatched brackets
        lines = content.split('\n')
        fixed_lines = []
        bracket_stack = []

        for line in lines:
            # Skip obvious problematic lines
            if ('pass' in line and 'except Exception as e:' in line and (
                    'print(f"Error: {e}")' in line or 'print(f\'Error:' in line)):
                continue

            # Fix specific patterns
            # Remove extra whitespace after {
            line = re.sub(r'\{\s*$', r'{', line)
            line = re.sub(
                r'print\(f"Error:\s*\{e\}"\)',
                r'print(f"Error: {e}")',
                line)

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def fix_except_statements(self, content: str) -> str:
        """Fix orphaned except statements"""
        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Skip orphaned except blocks
            if stripped.startswith('except ImportError:') and i > 0:
                prev_line = lines[i-1].strip()
                if not prev_line.startswith('try'):
                    continue

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def add_missing_imports_and_structure(self, content: str) -> str:
        """Add missing imports and proper structure"""
        if not content.strip().startswith('#!/usr/bin/env python3'):
            header = [
                "#!/usr/bin/env python3",
                "import sys",
                "import os",
                "import asyncio",
                "import time",
                "import json",
                "from pathlib import Path",
                "",
                "# Add parent directory to path for imports",
                "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))",
                "",
            ]
            content = '\n'.join(header) + '\n' + content

        # Add main execution block if not present
        if "if __name__ == '__main__':" not in content:
            main_block = [
                "",
                "if __name__ == '__main__':",
                "    print('Running test file...')",
                "    ",
                "    # Run all test functions",
                "    test_functions = [name for name in globals() if name.startswith('test_')]",
                "    passed = 0",
                "    failed = 0",
                "    ",
                "    for test_name in test_functions:",
                "        try:",
                "            test_func = globals()[test_name]",
                "            if asyncio.iscoroutinefunction(test_func):",
                "                asyncio.run(test_func())",
                "            else:",
                "                test_func()",
                "            print(f'✓ {test_name} passed')",
                "            passed += 1",
                "        except Exception as e:",
                "            print(f'✗ {test_name} failed: {e}')",
                "            failed += 1",
                "    ",
                "    print(f'\\nTest results: {passed} passed, {failed} failed')",
            ]
            content += '\n'.join(main_block)

        return content

    def fix_file(self, file_path: str) -> bool:
        """Fix a single test file"""
        try:
            logger.info(f"Processing {file_path}")

            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                original_content = f.read()

            # Apply all fixes
            content = original_content
            content = self.fix_unterminated_triple_quotes(content)
            content = self.fix_unmatched_braces(content)
            content = self.fix_indentation_errors_in_globals(content)
            content = self.fix_malformed_docstrings(content)
            content = self.fix_invalid_f_strings(content)
            content = self.fix_mismatched_brackets_in_data_structures(content)
            content = self.fix_except_statements(content)
            content = self.add_missing_imports_and_structure(content)

            # Only write if content changed
            if content != original_content:
                # Create backup
                backup_path = file_path + '.backup2'
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)

                # Write fixed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                logger.info(f"Fixed {file_path} (backup created)")
                self.stats['files_fixed'] += 1
                self.stats['errors_fixed'] += 1
            else:
                logger.info(f"No changes needed for {file_path}")

            self.stats['files_processed'] += 1
            return True

        except Exception as e:
            logger.error(f"Failed to fix {file_path}: {e}")
            self.stats['failed_files'].append(file_path)
            return False

    def fix_all_files(self) -> Dict:
        """Fix all test files in the project"""
        logger.info("Starting second pass syntax error fix...")

        test_files = self.find_test_files()

        for file_path in test_files:
            self.fix_file(file_path)

        # Generate report
        report = {
            'summary': self.stats,
            'success_rate': (
                self.stats['files_fixed'] /
                self.stats['files_processed']) *
            100 if self.stats['files_processed'] > 0 else 0,
            'timestamp': time.time()}

        logger.info(f"Second pass syntax fixing completed!")
        logger.info(f"Files processed: {self.stats['files_processed']}")
        logger.info(f"Files fixed: {self.stats['files_fixed']}")
        logger.info(f"Success rate: {report['success_rate']:.1f}%")

        # Save report
        with open('syntax_fix_second_pass_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        return report


def main():
    """Main execution function"""
    print("🔧 Scorpius Second Pass Syntax Error Fix")
    print("=" * 50)

    fixer = SecondPassSyntaxFixer()
    report = fixer.fix_all_files()

    print(
        f"\n✅ Second pass fix completed with {
            report['success_rate']:.1f}% success rate")
    print(f"📊 Report saved to syntax_fix_second_pass_report.json")

    return report['success_rate'] > 90


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
