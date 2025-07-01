#!/usr/bin/env python3
"""
Scorpius Enterprise-Grade Smart Contract Vulnerability Scanner
Main entry point for the Scorpius application
"""
import sys

from cli.scanner_cli import main

if __name__ == "__main__":
    sys.exit(main())
