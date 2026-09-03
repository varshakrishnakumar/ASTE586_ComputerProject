"""Attitude kinematics -- how the orientation quaternion evolves."""

from __future__ import annotations

import numpy as np


def quaternion_derivative(q: np.ndarray, omega: np.ndarray) -> np.ndarray:
    """Time derivative of the attitude quaternion.

    ``q`` is scalar-last ``[x, y, z, w]`` and rotates body vectors into the
    inertial frame (see docs/conventions.md). ``omega`` is the body angular
    velocity expressed in body coordinates.

    Parameters
    ----------
    q : (4,) ndarray
        Current attitude quaternion ``[x, y, z, w]``.
    omega : (3,) ndarray
        Body angular velocity (rad/s).

    Returns
    -------
    (4,) ndarray
        ``dq/dt``.
    """
    raise NotImplementedError(
        "Part 2: implement quaternion_derivative in "
        "src/aste586/dynamics/kinematics.py -- the quaternion kinematic equation"
    )
