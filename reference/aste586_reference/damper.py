"""Reference solution — Part 4 damper equations of motion."""

from __future__ import annotations

import numpy as np


def damper_eom(
    omega: np.ndarray,
    J: np.ndarray,
    Id: float,
    D: float,
    K: float,
    theta_d: float,
    omega_d: float,
) -> tuple[np.ndarray, float, float]:
    """Part 4 Eqs 1-5. The damper wheel spins about body axis 2.

        a1 = -[ w2 w3 (I3 - I2) - Id w3 Omega_d ] / I1
        a2 = -[ w1 w3 (I1 - I3) - D Omega_d - K Theta_d ] / (I2 - Id)
        a3 = -[ w1 w2 (I2 - I1) + Id w1 Omega_d ] / I3
        Theta_d' = Omega_d
        Omega_d' = (-D Omega_d - K Theta_d) / Id - a2

    Eq 5 reuses ``a2``, so a2 is computed before ``omega_d_dot``.
    """
    I1, I2, I3 = J[0, 0], J[1, 1], J[2, 2]
    w1, w2, w3 = omega

    a1 = -(w2 * w3 * (I3 - I2) - Id * w3 * omega_d) / I1
    a2 = -(w1 * w3 * (I1 - I3) - D * omega_d - K * theta_d) / (I2 - Id)
    a3 = -(w1 * w2 * (I2 - I1) + Id * w1 * omega_d) / I3

    theta_d_dot = omega_d
    omega_d_dot = (-D * omega_d - K * theta_d) / Id - a2

    return np.array([a1, a2, a3]), theta_d_dot, omega_d_dot
