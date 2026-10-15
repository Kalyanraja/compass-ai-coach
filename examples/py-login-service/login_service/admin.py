"""Admin maintenance helpers (SYNTHETIC FIXTURE)."""

import subprocess


def run_maintenance(command: str) -> int:
    """Run a maintenance command typed in by an operator and return its exit code."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.returncode
