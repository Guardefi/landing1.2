#!/usr/bin/env python3
"""
Scorpius Time Machine - Main Application Entry Point

This is the primary entry point for the Time Machine application.
It provides both CLI and server functionality in a unified interface.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Import after path setup
from time_machine_app import main

if __name__ == "__main__":
    main()
