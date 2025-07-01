# backend/Bytecode/tests/conftest.py - Configuration for Bytecode tests
import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).parent.parent.parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Add backend and other directories to sys.path
directories_to_add = [
    "backend",
    "backend/Bytecode",
    "packages", 
    "services",
    "monitoring",
    "reporting"
]

for directory in directories_to_add:
    path = project_root / directory
    if path.exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))
