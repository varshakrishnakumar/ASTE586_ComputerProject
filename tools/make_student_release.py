#!/usr/bin/env python3
"""Produce the student release: a copy of the repo with the hidden reference
backend (and run artifacts) stripped out.

    python tools/make_student_release.py [dest]

The student backend `src/aste586/dynamics/` -- the stubs -- is kept; only
`reference/` is removed, so students get a working harness with the equations
of motion left to implement. Before copying, ``grading/expected/`` is
regenerated from the reference backend so `aste586 grade` works in the
release without it.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Directories/files never shipped to students.
EXCLUDE = {"reference", "runs", ".git", "__pycache__", ".pytest_cache",
           "build", "dist", ".venv", "venv"}


def _ignore(_dir, names):
    return [n for n in names if n in EXCLUDE or n.endswith((".pyc", ".egg-info"))]


def _regenerate_expected() -> None:
    sys.path.insert(0, str(REPO / "tools"))
    import make_expected  # noqa: E402

    print("regenerating grading/expected/ from the reference backend ...")
    make_expected.main([])


def main() -> int:
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO.parent / "aste586_student"
    _regenerate_expected()
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(REPO, dest, ignore=_ignore)

    missing = [p.stem for p in (REPO / "configs").glob("*.yaml")
               if not (dest / "grading" / "expected" / f"{p.stem}.npz").is_file()]
    if missing:
        raise SystemExit(f"release is missing expected data for: {missing}")

    archive = shutil.make_archive(str(dest), "zip", root_dir=dest.parent,
                                  base_dir=dest.name)
    print(f"student release : {dest}")
    print(f"student zip      : {archive}")
    print("reference backend stripped; dynamics/ stubs retained.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
