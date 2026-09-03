"""Part 4 -- the energy-dissipating damper (a sprung, damped reaction wheel).

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

    Parameters
    ----------
    omega : (3,) ndarray
        Body angular velocity (rad/s).
    J : (3, 3) ndarray
        Diagonal principal inertia matrix; ``I1, I2, I3 = diag(J)``.
    Id : float
        Damper-wheel moment of inertia (kg-m^2).
    D : float
        Damping coefficient (N-m/(rad/s)).
    K : float
        Spring coefficient (N-m/rad).
    theta_d : float
        Damper-wheel angle (rad).
    omega_d : float
        Damper-wheel rate (rad/s).

    Returns
    -------
    alpha : (3,) ndarray
        Body angular acceleration (rad/s^2).
    theta_d_dot : float
        Equals ``omega_d`` (Eq 4).
    omega_d_dot : float
        Damper-wheel angular acceleration (Eq 5).

    Notes
    -----
    Eq 5 uses the result of Eq 2 -- compute ``alpha2`` before ``omega_d_dot``.
    """
    raise NotImplementedError(
        "Part 4: implement damper_eom in src/aste586/dynamics/damper.py -- "
        "Eqs 1-5 of the handout"
    )
