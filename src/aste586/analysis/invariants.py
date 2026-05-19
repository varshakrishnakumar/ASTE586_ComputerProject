"""Physical invariants used to validate a simulation -- provided.

For torque-free motion the angular momentum is constant in the inertial
frame. Without a damper, kinetic energy is also constant; with a damper it
decreases monotonically. The quaternion must stay unit-norm. These functions
compute those quantities from a run's time series so the harness can check
them.
"""

from __future__ import annotations

import numpy as np

from ..conventions import quat_to_matrix


def quaternion_norm(q: np.ndarray) -> np.ndarray:
    """Norm of each quaternion in a ``(N, 4)`` time series."""
    return np.linalg.norm(q, axis=1)


def angular_momentum_body(
    omega: np.ndarray, J: np.ndarray, Id: float = 0.0,
    omega_d: np.ndarray | None = None,
) -> np.ndarray:
    """Angular momentum in body coordinates, ``(N, 3)``.

    With a damper (Part 4 Eq 15) the wheel momentum ``Id * omega_d`` adds to
    the body-2 component.
    """
    H = omega @ J.T
    if omega_d is not None and Id != 0.0:
        H = H.copy()
        H[:, 1] += Id * np.asarray(omega_d)
    return H


def angular_momentum_inertial(
    omega: np.ndarray, q: np.ndarray, J: np.ndarray, Id: float = 0.0,
    omega_d: np.ndarray | None = None,
) -> np.ndarray:
    """Angular momentum expressed in the inertial frame, ``(N, 3)``.

    For torque-free motion every component should be constant in time; the
    harness plots ``H(t) - H(0)`` to expose integration error.
    """
    H_body = angular_momentum_body(omega, J, Id, omega_d)
    H_F = np.empty_like(H_body)
    for i in range(len(q)):
        H_F[i] = quat_to_matrix(q[i]) @ H_body[i]
    return H_F


def kinetic_energy(
    omega: np.ndarray, J: np.ndarray, Id: float = 0.0, K: float = 0.0,
    theta_d: np.ndarray | None = None, omega_d: np.ndarray | None = None,
) -> np.ndarray:
    """Rotational kinetic energy ``(N,)``.

    Rigid body: ``T = 1/2 omega . J omega``. Damped body (Part 4 Eq 16) adds
    the wheel kinetic energy, the gyroscopic cross term, and the spring
    potential.
    """
    T = 0.5 * np.einsum("ni,ij,nj->n", omega, J, omega)
    if theta_d is not None and omega_d is not None and Id != 0.0:
        T = T + (0.5 * Id * omega_d**2
                 + Id * omega[:, 2] * omega_d
                 + 0.5 * K * theta_d**2)
    return T
