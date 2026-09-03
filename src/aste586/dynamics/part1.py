"""Part 1 -- the linear initial-value-problem warm-up.

Two functions to implement. Neither uses the attitude state layout; Part 1 is
a standalone exercise to confirm your integration tooling works.
"""

from __future__ import annotations

import numpy as np


def linear_ivp_rhs(t: float, x: np.ndarray, A: np.ndarray) -> np.ndarray:
    """Right-hand side of the linear system ``xdot = A x``.

    Parameters
    ----------
    t : float
        Time (unused -- the system is autonomous, but the integrator passes it).
    x : (4,) ndarray
        Current state.
    A : (4, 4) ndarray
        The system matrix from the Part 1 handout.

    Returns
    -------
    (4,) ndarray
        ``dx/dt``.
    """
    raise NotImplementedError(
        "Part 1: implement linear_ivp_rhs in src/aste586/dynamics/part1.py -- "
        "return dx/dt = A x"
    )


def analytical_solution(t: np.ndarray) -> np.ndarray:
    """Closed-form solution ``x(t)`` of the Part 1 system.

    Derive this **by hand** (no symbolic solver). The system decouples into two
    independent planar rotations; expect sinusoids.

    Parameters
    ----------
    t : (N,) ndarray
        Times at which to evaluate the solution.

    Returns
    -------
    (N, 4) ndarray
        The exact state at each time.
    """
    raise NotImplementedError(
        "Part 1: implement analytical_solution in src/aste586/dynamics/part1.py "
        "-- return the closed form x(t) you derived by hand"
    )
