import re

test_files = [
    "tests/test_api.py",
    "tests/test_comprehensive.py",
    "tests/test_production_readiness.py",
    "tests/test_focused.py",
    "tests/test_strategic.py",
    "tests/test_final_coverage.py",
]

for file_path in test_files:
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        content = re.sub(
            r"from simple_server import app", "from main import app", content
        )
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed {file_path}")
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
