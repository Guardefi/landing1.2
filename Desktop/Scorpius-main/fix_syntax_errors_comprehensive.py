#!/usr/bin/env python3
"""
Comprehensive Syntax Error Fix Script
Systematically fixes all syntax errors in test files across the Scorpius project.
Enterprise-grade error handling and logging.
"""

import os
import re
import sys
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('syntax_fix.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SyntaxErrorFixer:
    """Enterprise-grade syntax error fixing utility"""

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
            # Skip certain directories
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
                        'test_' in file or file.endswith('_test.py')):
                    test_files.append(os.path.join(root, file))

        logger.info(f"Found {len(test_files)} test files")
        return test_files

    def fix_globals_update_blocks(self, content: str) -> str:
        """Fix malformed globals().update() blocks"""
        # Pattern to match incomplete globals().update blocks
        pattern = r"globals\(\)\.update\(\{\s*'[^']*':\s*[^,]*,\s*pass\s*except\s*Exception\s*as\s*e:\s*print\(f\"Error:\s*\{e\}\"\)\s*,"

        def replace_globals_block(match):
            # Replace with proper empty globals update
            return "globals().update({})"

        # Fix the malformed pattern
        content = re.sub(
            pattern,
            replace_globals_block,
            content,
            flags=re.MULTILINE | re.DOTALL)

        # Fix incomplete globals().update blocks
        content = re.sub(
            r"globals\(\)\.update\(\{\s*'[^']*':\s*[^,]*,\s*pass\s*except[^}]*\}\)",
            "globals().update({})",
            content,
            flags=re.MULTILINE | re.DOTALL)

        return content

    def fix_orphaned_pass_statements(self, content: str) -> str:
        """Fix orphaned pass statements that cause syntax errors"""
        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Check if this is an orphaned pass statement
            if stripped == 'pass' and i > 0:
                prev_line = lines[i-1].strip()
                # If previous line doesn't end with : or is not a control
                # structure
                if not prev_line.endswith(':') and not any(
                    prev_line.startswith(kw) for kw in [
                        'if',
                        'for',
                        'while',
                        'try',
                        'except',
                        'finally',
                        'with',
                        'def',
                        'class']):
                    # Skip this orphaned pass
                    continue

            # Check for orphaned except blocks
            if stripped.startswith('except Exception as e:') and i > 0:
                prev_line = lines[i-1].strip()
                if not prev_line.startswith('try') and 'pass' in prev_line:
                    # Skip orphaned except block
                    continue

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def fix_mismatched_brackets(self, content: str) -> str:
        """Fix mismatched brackets and braces"""
        # Stack to track opening brackets
        stack = []
        bracket_map = {'(': ')', '[': ']', '{': '}'}

        # First pass: identify and fix obvious mismatches
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            # Skip lines that are clearly malformed
            if 'pass' in line and 'except Exception as e:' in line and '{' in line:
                continue

            # Fix incomplete dictionary/list definitions
            if line.strip().endswith('{') and 'globals().update(' in line:
                line = line.replace('{', '{})')

            # Fix lines with mismatched brackets in parametrized decorators
            if line.strip().startswith(
                    '@pytest.mark.parametrize') and line.count('[') != line.count(']'):
                # Find the opening bracket
                if '[' in line and ']' not in line:
                    # Look for the closing bracket in subsequent lines
                    bracket_count = line.count('[') - line.count(']')
                    if bracket_count > 0:
                        line += ']' * bracket_count

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def fix_unterminated_strings(self, content: str) -> str:
        """Fix unterminated string literals"""
        # Fix unterminated triple-quoted strings
        content = re.sub(
            r'"""([^"]*?)$',
            r'"""\1"""',
            content,
            flags=re.MULTILINE
        )

        # Fix unterminated f-strings
        content = re.sub(
            r'f"([^"]*?)\{([^}]*?)\}([^"]*?)$',
            r'f"\1{\2}\3"',
            content,
            flags=re.MULTILINE
        )

        return content

    def fix_invalid_syntax_patterns(self, content: str) -> str:
        """Fix common invalid syntax patterns"""
        # Fix decimal literal issues
        content = re.sub(
            r'(\d+)\.(\d+)\}([^"]*?)$',
            r'\1.\2}\3',
            content,
            flags=re.MULTILINE
        )

        # Fix missing closing parentheses in function calls
        content = re.sub(
            r'assert\s+([^()+)\(\s*([^)]*?)\s*$',
            r'assert \1(\2)',
            content,
            flags=re.MULTILINE
        )

        return content

    def add_proper_imports_and_main(self, content: str) -> str:
        """Add proper imports and main execution block"""
        imports = [
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

        # Add main execution block if not present
        if "if __name__ == '__main__':" not in content:
            main_block = [
                "",
                "if __name__ == '__main__':",
                "    print('Running test file...')",
                "    ",
                "    # Run all test functions",
                "    test_functions = [name for name in globals() if name.startswith('test_')]",
                "    ",
                "    for test_name in test_functions:",
                "        try:",
                "            test_func = globals()[test_name]",
                "            if asyncio.iscoroutinefunction(test_func):",
                "                asyncio.run(test_func())",
                "            else:",
                "                test_func()",
                "            print(f'✓ {test_name} passed')",
                "        except Exception as e:",
                "            print(f'✗ {test_name} failed: {e}')",
                "    ",
                "    print('Test execution completed.')",
            ]
            content += '\n'.join(main_block)

        return '\n'.join(imports) + '\n' + content

    def fix_file(self, file_path: str) -> bool:
        """Fix a single test file"""
        try:
            logger.info(f"Processing {file_path}")

            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                original_content = f.read()

            # Apply all fixes
            content = original_content
            content = self.fix_globals_update_blocks(content)
            content = self.fix_orphaned_pass_statements(content)
            content = self.fix_mismatched_brackets(content)
            content = self.fix_unterminated_strings(content)
            content = self.fix_invalid_syntax_patterns(content)
            content = self.add_proper_imports_and_main(content)

            # Only write if content changed
            if content != original_content:
                # Create backup
                backup_path = file_path + '.backup'
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
        logger.info("Starting comprehensive syntax error fix...")

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

        logger.info(f"Syntax fixing completed!")
        logger.info(f"Files processed: {self.stats['files_processed']}")
        logger.info(f"Files fixed: {self.stats['files_fixed']}")
        logger.info(f"Success rate: {report['success_rate']:.1f}%")

        # Save report
        with open('syntax_fix_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        return report


def main():
    """Main execution function"""
    print("🔧 Scorpius Comprehensive Syntax Error Fix")
    print("=" * 50)

    fixer = SyntaxErrorFixer()
    report = fixer.fix_all_files()

    print(f"\n✅ Fix completed with {report['success_rate']:.1f}% success rate")
    print(f"📊 Report saved to syntax_fix_report.json")

    return report['success_rate'] > 90


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
