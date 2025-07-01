#!/usr/bin/env python3
"""
Unicode Fix Wrapper for running tests on Windows
Handles Unicode encoding issues by setting proper environment variables
"""

import os
import sys
import subprocess


def setup_unicode_environment():
    """Set up proper Unicode environment for Windows"""
    # Set UTF-8 encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '1'

    # Enable Unicode in console
    if sys.platform == 'win32':
        try:
            import locale
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except BaseException:
            pass


def run_test_with_unicode_fix(test_file):
    """Run a test file with Unicode fixes"""
    setup_unicode_environment()

    try:
        # Run the test with proper encoding
        result = subprocess.run([
            sys.executable, test_file
        ], capture_output=True, text=True, encoding='utf-8', errors='replace')

        # Print results safely
        if result.stdout:
            print(result.stdout.encode('ascii', 'replace').decode('ascii'))
        if result.stderr:
            print(
                "STDERR:",
                result.stderr.encode(
                    'ascii',
                    'replace').decode('ascii'))

        return result.returncode == 0

    except Exception as e:
        print(f"Error running {test_file}: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python unicode_fix_wrapper.py <test_file>")
        sys.exit(1)

    test_file = sys.argv[1]
    success = run_test_with_unicode_fix(test_file)
    sys.exit(0 if success else 1)
