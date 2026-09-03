"""Your dynamics functions, one check at a time.

This is the same set of checks as ``aste586 check``, exposed to pytest so
``pytest -q`` reports them too. A function that still raises
``NotImplementedError`` shows up as *skipped*, not failed.
"""

import pytest

from aste586.checks import run_checks
from aste586.report import FAIL, SKIP, TODO

_CHECKS = run_checks()


@pytest.mark.parametrize("check", _CHECKS, ids=[f"{c.group.split()[0]}::{c.name}" for c in _CHECKS])
def test_student_function(check):
    if check.status in (TODO, SKIP):
        pytest.skip(check.detail)
    assert check.status != FAIL, f"{check.detail}\n  hint: {check.hint}"
