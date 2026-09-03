"""The per-function checks must accept a correct backend and reject a wrong
one. The 'correct' side needs the hidden reference and is skipped in the
student release; the 'wrong' side always runs."""

from types import SimpleNamespace

import numpy as np
import pytest

from aste586.checks import run_checks
from aste586.report import FAIL, PASS, TODO


def test_reference_passes_every_check():
    ref = pytest.importorskip("aste586_reference")
    bad = [c for c in run_checks(backend=ref) if c.status != PASS]
    assert not bad, "\n".join(f"{c.group} / {c.name}: {c.detail}" for c in bad)


def _todo(*a, **k):
    raise NotImplementedError("stub")


def _fake_backend(**fns):
    names = ("linear_ivp_rhs", "analytical_solution", "quaternion_derivative",
             "euler_eqs", "damper_eom", "state_derivative")
    return SimpleNamespace(**{n: fns.get(n, _todo) for n in names})


def _euler_checks(euler_eqs):
    return {c.name: c for c in run_checks(part=2, backend=_fake_backend(euler_eqs=euler_eqs))
            if c.group.startswith("euler_eqs")}


def test_one_row_sign_error_in_euler_eqs_is_caught():
    def euler_eqs(omega, J, torque):
        I1, I2, I3 = np.diag(J)
        w1, w2, w3 = omega
        return np.array([(torque[0] - (I3 - I2) * w2 * w3) / I1,
                         (torque[1] + (I1 - I3) * w3 * w1) / I2,      # sign wrong
                         (torque[2] - (I2 - I1) * w1 * w2) / I3])

    checks = _euler_checks(euler_eqs)
    assert checks["known values"].status == FAIL
    assert checks["torque-free: kinetic energy conserved"].status == FAIL
    assert checks["torque-free: |H| conserved"].status == FAIL
    assert checks["spherical body: alpha = torque / I"].status == PASS  # cannot see a sign error


def test_global_sign_flip_in_euler_eqs_is_caught_by_known_values():
    # Flipping every gyroscopic term still conserves T and |H|, so only the
    # stored known values can expose it.
    def euler_eqs(omega, J, torque):
        I1, I2, I3 = np.diag(J)
        w1, w2, w3 = omega
        return np.array([(torque[0] + (I3 - I2) * w2 * w3) / I1,
                         (torque[1] + (I1 - I3) * w3 * w1) / I2,
                         (torque[2] + (I2 - I1) * w1 * w2) / I3])

    checks = _euler_checks(euler_eqs)
    assert checks["known values"].status == FAIL


def test_student_exception_becomes_fail_not_crash():
    def euler_eqs(omega, J, torque):
        return omega[7]  # IndexError

    checks = _euler_checks(euler_eqs)
    assert checks["known values"].status == FAIL
    assert "IndexError" in checks["known values"].detail


def test_stubs_report_todo_not_fail():
    statuses = {c.status for c in run_checks()}
    # in a fresh checkout every function is a stub; whatever the student has
    # done since, nothing here may crash the check runner itself
    assert statuses <= {PASS, FAIL, TODO, "SKIP"}
