"""Shared pass/fail reporting -- provided.

``aste586 check`` and ``aste586 grade`` both produce a list of :class:`Check`
line items and print them with :func:`print_report`. A check has one of four
statuses:

* ``PASS`` -- the check passed;
* ``FAIL`` -- it ran and the result was wrong (a ``hint`` says what to look at);
* ``TODO`` -- the function under test still raises ``NotImplementedError``;
* ``SKIP`` -- the check could not run because something it depends on is
  still ``TODO`` (nothing is wrong yet).
"""

from __future__ import annotations

import traceback
from dataclasses import dataclass
from pathlib import Path

PASS, FAIL, TODO, SKIP = "PASS", "FAIL", "TODO", "SKIP"


@dataclass
class Check:
    """One line item of a report."""

    name: str
    status: str
    detail: str = ""
    hint: str = ""
    group: str = ""

    @property
    def passed(self) -> bool:
        return self.status == PASS


def locate_student_frame(exc: BaseException) -> str | None:
    """``"src/aste586/dynamics/<file>.py:<line> (in <function>)"`` for the
    innermost traceback frame inside the student backend, or ``None`` if the
    exception did not pass through student code."""
    frames = traceback.extract_tb(exc.__traceback__)
    for fr in reversed(frames):
        parts = Path(fr.filename).parts
        if "dynamics" in parts and "aste586" in parts:
            idx = parts.index("aste586")
            rel = Path(*parts[max(idx - 1, 0):])   # src/aste586/dynamics/x.py
            return f"{rel}:{fr.lineno} (in {fr.name})"
    return None


def describe_exception(exc: BaseException) -> str:
    """One-line ``TypeName: message`` plus, if applicable, where in the
    student code it was raised."""
    text = f"{type(exc).__name__}: {exc}"
    loc = locate_student_frame(exc)
    return f"{text}  [at {loc}]" if loc else text


def print_report(title: str, checks: list[Check], *, width: int = 66) -> bool:
    """Print ``checks`` as a table; return ``True`` if none is FAIL or TODO."""
    print(f"\n  {title}")
    print("  " + "-" * width)
    group = None
    for c in checks:
        if c.group and c.group != group:
            group = c.group
            print(f"  {group}")
        indent = "    " if c.group else "  "
        print(f"{indent}[{c.status}] {c.name:40s} {c.detail}")
        if c.status == FAIL and c.hint:
            print(f"{indent}       hint: {c.hint}")
    print("  " + "-" * width)
    n = {s: sum(c.status == s for c in checks) for s in (PASS, FAIL, TODO, SKIP)}
    summary = ", ".join(f"{v} {k.lower()}" for k, v in n.items() if v)
    ok = n[FAIL] == 0 and n[TODO] == 0
    verdict = "ALL CHECKS PASSED" if ok else (
        "NOT YET IMPLEMENTED" if n[FAIL] == 0 else "SOME CHECKS FAILED")
    print(f"  {verdict}  ({summary})\n")
    return ok
