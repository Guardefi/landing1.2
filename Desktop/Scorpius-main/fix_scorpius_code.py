#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path

# chunk sizes
ISORT_CHUNK_SIZE = 20
AUTOFLAKE_CHUNK_SIZE = 20
AUTOPEP8_CHUNK_SIZE = 5


def run_module(module_name, args):
    """Run a stdlib module via subprocess and fail-fast on error."""
    cmd = [sys.executable, "-m", module_name] + args
    print(f">>> Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def safe_autopep8(files):
    """
    Try autopep8 in chunks; if a chunk blows up, rerun file-by-file
    so we skip only the broken ones.
    """
    base_args = ["--in-place", "--aggressive", "--aggressive"]
    for i in range(0, len(files), AUTOPEP8_CHUNK_SIZE):
        chunk = files[i: i + AUTOPEP8_CHUNK_SIZE]
        try:
            run_module("autopep8", base_args + chunk)
        except subprocess.CalledProcessError:
            print(
                f"✋  Chunk failed— retrying individually: {chunk}",
                file=sys.stderr)
            for f in chunk:
                try:
                    run_module("autopep8", base_args + [f])
                except subprocess.CalledProcessError as e:
                    print(f"✋  Skipping autopep8 on {f}: {e}", file=sys.stderr)


def run_in_chunks(module_name, base_args, files, chunk_size):
    """Strict (fail-fast) runner for isort and autoflake."""
    for i in range(0, len(files), chunk_size):
        run_module(module_name, base_args + files[i: i + chunk_size])


def main():
    base = Path(__file__).parent
    all_py = [str(p) for p in base.rglob("*.py")]

    # 1) isort — strict
    run_in_chunks("isort", ["--profile", "black"], all_py, ISORT_CHUNK_SIZE)

    # 2) autoflake — strict
    run_in_chunks(
        "autoflake",
        ["--in-place", "--remove-all-unused-imports", "--remove-unused-variables"],
        all_py,
        AUTOFLAKE_CHUNK_SIZE,
    )

    # 3) autopep8 — safe, skip only truly broken files
    safe_autopep8(all_py)


if __name__ == "__main__":
    main()
