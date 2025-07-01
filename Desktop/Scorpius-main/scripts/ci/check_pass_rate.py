#!/usr/bin/env python3
"""Check that pytest JUnit XML results meet a minimum pass-rate threshold.

Usage:
  python check_pass_rate.py <junit-xml-path> [<threshold>]

<junit-xml-path> – Path to pytest JUnit XML file.
<threshold>       – Optional float between 0 and 1 representing minimum
                    pass ratio required (defaults to 0.75).

The script exits with code 0 if the pass-rate is >= threshold, otherwise 1.
It prints a short summary to stdout for CI logs.
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python check_pass_rate.py <junit-xml-path> [<threshold>]",
            file=sys.stderr,
        )
        sys.exit(2)

    junit_path = Path(sys.argv[1])
    if not junit_path.is_file():
        print(f"JUnit XML file not found: {junit_path}", file=sys.stderr)
        sys.exit(2)

    try:
        threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.75
    except ValueError:
        print("Threshold must be a float between 0 and 1", file=sys.stderr)
        sys.exit(2)

    if not 0.0 <= threshold <= 1.0:
        print("Threshold must be between 0 and 1", file=sys.stderr)
        sys.exit(2)

    tree = ET.parse(junit_path)
    root = tree.getroot()

    total = int(root.attrib.get("tests", 0))
    failures = int(root.attrib.get("failures", 0))
    errors = int(root.attrib.get("errors", 0))
    skipped = int(root.attrib.get("skipped", 0))

    passed = total - failures - errors - skipped
    executed = total - skipped
    pass_ratio = passed / executed if executed else 0.0

    print(
        f"Test summary – executed: {executed}, passed: {passed}, "
        f"failures: {failures}, errors: {errors}, pass-rate: {pass_ratio:.2%}"
    )

    if pass_ratio < threshold:
        print(
            f"❌ Pass-rate {pass_ratio:.2%} is below required threshold {threshold:.0%}",
            file=sys.stderr,
        )
        sys.exit(1)

    print("✅ Pass-rate requirement met → continuing…")


if __name__ == "__main__":
    main()
