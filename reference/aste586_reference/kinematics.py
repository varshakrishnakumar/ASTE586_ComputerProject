"""Reference solution — quaternion kinematics."""

from __future__ import annotations

import numpy as np

from aste586.conventions import quat_multiply


def quaternion_derivative(q: np.ndarray, omega: np.ndarray) -> np.ndarray:
    """``qdot = 1/2 * q (x) [omega, 0]``.

    For a scalar-last quaternion that rotates body vectors into the inertial
    frame, with ``omega`` expressed in the body frame, the kinematic equation
    is half the Hamilton product of ``q`` with the pure quaternion built from
    ``omega``.
    """
    omega_q = np.array([omega[0], omega[1], omega[2], 0.0])
    return 0.5 * quat_multiply(q, omega_q)
