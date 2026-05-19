"""Reference solution — Part 1 linear IVP."""

from __future__ import annotations

import numpy as np


def linear_ivp_rhs(t: float, x: np.ndarray, A: np.ndarray) -> np.ndarray:
    """``xdot = A x`` -- the system is linear and autonomous."""
    return A @ x


def analytical_solution(t: np.ndarray) -> np.ndarray:
    """Closed form of the Part 1 system.

    The 4x4 matrix is block-diagonal: components (1,2) form a 2 rad/s rotation
    and components (3,4) a 200 rad/s rotation. With x(0) = [1, 0, 1, 0]:

        x1 =  cos(2 t)      x3 =  cos(200 t)
        x2 = -sin(2 t)      x4 = -sin(200 t)
    """
    t = np.atleast_1d(np.asarray(t, dtype=float))
    return np.column_stack([
        np.cos(2.0 * t),
        -np.sin(2.0 * t),
        np.cos(200.0 * t),
        -np.sin(200.0 * t),
    ])
