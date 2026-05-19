"""Analytical solutions used to check a simulation -- provided.

The torque-free motion of an **axisymmetric** rigid body has a closed-form
angular velocity: the component along the symmetry axis is constant and the
two lateral components rotate at a fixed rate. Parts 2's test cases are
axisymmetric so the simulation can be checked against this directly.
"""

from __future__ import annotations

import numpy as np


def _symmetry_axis(J: np.ndarray, tol: float = 1e-9) -> int | None:
    """Index (0,1,2) of the symmetry axis, or None if the body is not
    axisymmetric. The symmetry axis is the one whose two *other* moments of
    inertia are equal.
    """
    I = np.diag(J)
    for k in range(3):
        i, j = [m for m in range(3) if m != k]
        if abs(I[i] - I[j]) <= tol * max(1.0, abs(I[i])):
            return k
    return None


def axisymmetric_omega(
    t: np.ndarray, omega0: np.ndarray, J: np.ndarray
) -> np.ndarray | None:
    """Analytical body angular velocity ``omega(t)`` for an axisymmetric body.

    Returns ``(N, 3)`` array, or ``None`` if ``J`` is not axisymmetric (in
    which case there is no elementary closed form and the harness skips the
    analytical comparison).

    With symmetry axis ``k`` and lateral axes ``i, j``:

        lambda    = omega_k * (I_k - I_lat) / I_lat
        omega_i(t) = omega_i0 cos(lambda t) - omega_j0 sin(lambda t)
        omega_j(t) = omega_i0 sin(lambda t) + omega_j0 cos(lambda t)
        omega_k(t) = omega_k0
    """
    k = _symmetry_axis(J)
    if k is None:
        return None
    # Euler's equations are cyclic: the lateral pair must be the cyclic
    # continuation (k+1, k+2) of the symmetry axis, not just "the other two".
    i, j = (k + 1) % 3, (k + 2) % 3
    I = np.diag(J)
    lam = omega0[k] * (I[k] - I[i]) / I[i]

    t = np.asarray(t, float)
    out = np.empty((len(t), 3))
    c, s = np.cos(lam * t), np.sin(lam * t)
    out[:, i] = omega0[i] * c - omega0[j] * s
    out[:, j] = omega0[i] * s + omega0[j] * c
    out[:, k] = omega0[k]
    return out
