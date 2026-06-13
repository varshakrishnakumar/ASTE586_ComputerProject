"""Pytest configuration: add src/ to sys.path so tests run without needing
PYTHONPATH=src in the shell."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
