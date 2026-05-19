"""Reference solution — Euler's equations."""

from __future__ import annotations

import numpy as np


def euler_eqs(omega: np.ndarray, J: np.ndarray, torque: np.ndarray) -> np.ndarray:
    """Angular acceleration from Euler's equations, principal axes.

        I1 w1' = M1 - (I3 - I2) w2 w3
        I2 w2' = M2 - (I1 - I3) w3 w1
        I3 w3' = M3 - (I2 - I1) w1 w2
    """
    I1, I2, I3 = J[0, 0], J[1, 1], J[2, 2]
    w1, w2, w3 = omega
    return np.array([
        (torque[0] - (I3 - I2) * w2 * w3) / I1,
        (torque[1] - (I1 - I3) * w3 * w1) / I2,
        (torque[2] - (I2 - I1) * w1 * w2) / I3,
    ])
