"""3-1-3 Euler-angle extraction must invert a known rotation for every choice
of body reference axis, with the inertial 3-axis fixed (the H direction)."""

import numpy as np
import pytest

from aste586.analysis import euler_angles_313
from aste586.analysis.euler_angles import _TRIAD
from aste586.conventions import matrix_to_quat


def _rot_313(psi, theta, phi):
    c, s = np.cos, np.sin
    Rz = lambda a: np.array([[c(a), -s(a), 0], [s(a), c(a), 0], [0, 0, 1]])  # noqa: E731
    Rx = lambda a: np.array([[1, 0, 0], [0, c(a), -s(a)], [0, s(a), c(a)]])  # noqa: E731
    return Rz(psi) @ Rx(theta) @ Rz(phi)


@pytest.mark.parametrize("axis", [1, 2, 3])
def test_round_trip(axis):
    psi, theta, phi = 0.4, 0.7, -1.1
    i, j, k = _TRIAD[axis]
    Rp = _rot_313(psi, theta, phi)      # columns: permuted body axes in inertial
    R = np.empty((3, 3))
    R[:, i], R[:, j], R[:, k] = Rp[:, 0], Rp[:, 1], Rp[:, 2]
    q = matrix_to_quat(R)
    ps, th, ph = euler_angles_313(q[None, :], axis)
    assert np.allclose([ps[0], th[0], ph[0]], [psi, theta, phi], atol=1e-9)


@pytest.mark.parametrize("axis", [1, 2, 3])
def test_pure_precession_keeps_nutation_constant(axis):
    """A body axis precessing about inertial z at fixed cone angle."""
    i, j, k = _TRIAD[axis]
    theta0 = np.radians(25.0)
    quats = []
    for psi in np.linspace(0, 4 * np.pi, 200):
        Rp = _rot_313(psi, theta0, 0.3 * psi)
        R = np.empty((3, 3))
        R[:, i], R[:, j], R[:, k] = Rp[:, 0], Rp[:, 1], Rp[:, 2]
        quats.append(matrix_to_quat(R))
    _, th, _ = euler_angles_313(np.array(quats), axis)
    assert np.allclose(th, theta0, atol=1e-9)
