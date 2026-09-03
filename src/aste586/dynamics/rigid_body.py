"""Euler's equations for a torque-free (or torque-driven) rigid body."""

from __future__ import annotations

import numpy as np


def euler_eqs(omega: np.ndarray, J: np.ndarray, torque: np.ndarray) -> np.ndarray:
    """Angular acceleration from Euler's rotational equations of motion.

    For a body with principal inertia ``J = diag(I1, I2, I3)``, angular
    velocity ``omega`` in body coordinates, and external ``torque`` in body
    coordinates, return ``d(omega)/dt``.

    Parameters
    ----------
    omega : (3,) ndarray
        Body angular velocity (rad/s).
    J : (3, 3) ndarray
        Diagonal principal inertia matrix (kg-m^2).
    torque : (3,) ndarray
        External torque, body coordinates (N-m). Zero for this project.

    Returns
    -------
    (3,) ndarray
        Angular acceleration ``alpha`` (rad/s^2).
    """
    raise NotImplementedError(
        "Part 2: implement euler_eqs in src/aste586/dynamics/rigid_body.py -- "
        "Euler's equations for a rigid body"
    )
