#!/usr/bin/env python3
"""Regenerate ``grading/expected/`` from the hidden reference backend.

    python tools/make_expected.py [scenario ...]

Instructor tool. The expected files are what ``aste586 grade`` compares a
student run against, so they must be regenerated whenever the reference
backend or a scenario config changes. ``tools/make_student_release.py`` runs
this automatically. With no arguments every scenario is regenerated.
"""

from __future__ import annotations

import sys
import time

from aste586.grading import save_expected
from aste586.io import list_configs
from aste586.sim import run


def main(argv: list[str]) -> int:
    names = argv or list_configs()
    for name in names:
        t0 = time.perf_counter()
        artifact = run(name, backend="reference")
        path = save_expected(artifact)
        print(f"{name:30s} -> {path.relative_to(path.parents[2])}  "
              f"({time.perf_counter() - t0:.1f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
