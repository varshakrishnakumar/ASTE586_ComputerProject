"""Part 4 -- energy-dissipating damper (sprung, damped reaction wheel)

The damper wheel adds two state variables,
``theta_d`` (wheel angle) and ``omega_d`` (wheel rate), and modifies
the angular-acceleration equations. Implement equations from the
handout for Part 4.
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
    """Equations of motion for the damped rigid body (Part 4).

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
    """
    raise NotImplementedError(
        "Part 4: implement damper_eom in " "src/aste586/dynamics/damper.py"
    )
