"""Reference solution — Part 4
   the energy-dissipating damper (a sprung, damped reaction wheel)

The damper wheel spins about body axis 2. It adds two state variables,
``theta_d`` (wheel angle) and ``omega_d`` (wheel rate), and modifies the
angular-acceleration equations. Implement Eqs 1-5 of the Part 4 handout here.
"""

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
    """Equations of motion for the damped rigid body (Part 4, Eqs 1-5).

    The damper wheel spins about body axis 2.

    Parameters
    ----------
    omega : (3,) ndarray
        Body angular velocity (rad/s)
    J : (3, 3) ndarray
        Diagonal principal inertia matrix; ``I1, I2, I3 = diag(J)``
    Id : float
        Damper-wheel moment of inertia (kg-m^2)
    D : float
        Damping coefficient (N-m/(rad/s))
    K : float
        Spring coefficient (N-m/rad)
    theta_d : float
        Damper-wheel angle (rad)
    omega_d : float
        Damper-wheel rate (rad/s)

    Returns
    -------
    alpha : (3,) ndarray
        Body angular acceleration (rad/s^2) vector in body-fixed
        coordinates
    theta_d_dot : float
        Equals ``omega_d`` angular speed of the damper wheel
    omega_d_dot : float
        Angular acceleration of the damper wheel

    Notes
    -----
    Eq 5 uses the result of Eq 2 -- compute ``alpha2`` before ``omega_d_dot``.

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
