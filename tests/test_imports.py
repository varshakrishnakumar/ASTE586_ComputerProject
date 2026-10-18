"""Smoke tests: verify that optional-but-required third-party modules import
correctly in the active environment.  These catch the common failure mode where
a dependency (e.g. numpy, matplotlib) is absent from the conda/venv environment
and Python silently falls back to an ABI-incompatible system installation.

Root cause of the failure pattern (issues #2 and #3): macOS users who have a
pre-existing Python 3.9 user-level site-packages directory cause `pip install`
inside the conda env to say "Requirement already satisfied" for numpy/matplotlib
while pointing at the Python 3.9 copies.  At runtime, Python 3.11 loads those
Python-3.9-compiled C extensions and fails.  Fix: `python -s -m pip install -e .`
"""

import importlib
import sys


def test_numpy_importable():
    """numpy C-extensions must load for the active interpreter.

    Fails with 'No module named numpy._core._multiarray_umath' when the conda
    env's Python 3.11 picks up a numpy that was compiled for Python 3.9 from
    the user-level site-packages (~/.local or ~/Library/Python/3.9/).
    """
    import numpy as np  # noqa: F401

    assert np.__version__


def test_matplotlib_importable():
    """matplotlib must import without a circular-import or C-extension error."""
    if "matplotlib" in sys.modules:
        import matplotlib  # noqa: F401

        return
    mod = importlib.import_module("matplotlib")
    assert mod is not None


def test_matplotlib_agg_backend():
    """The Agg (headless) backend must be selectable; this exercises the C
    extension layer that '_c_internal_utils' circular-import errors break."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: F401


def test_matplotlib_default_backend():
    """The default backend must be selectable for aste586 plot --show"""
    import matplotlib.pyplot as plt  # noqa: F401


def test_report_plots_importable():
    """The full plots module (which sets the Agg backend at import time) must
    load without error.  This mirrors exactly what `aste586 plot` does."""
    importlib.import_module("aste586.plots")
