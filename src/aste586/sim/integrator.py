"""Numerical integration -- provided.

A thin wrapper over ``scipy.integrate.solve_ivp``. The project rules say to
use a library integrator rather than rolling your own, so this is harness
code: students supply only the right-hand side.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.integrate import solve_ivp


def integrate(
    rhs: Callable,
    z0: np.ndarray,
    t_eval: np.ndarray,
    *,
    method: str = "DOP853",
    rtol: float = 1e-9,
    atol: float = 1e-9,
    args: tuple = (),
) -> np.ndarray:
    """Integrate ``dz/dt = rhs(t, z, *args)`` and sample it at ``t_eval``.

    Parameters
    ----------
    rhs : callable
        Right-hand side ``rhs(t, z, *args) -> dz``.
    z0 : ndarray
        Initial state.
    t_eval : ndarray
        Strictly increasing output times; ``t_eval[0]`` is the initial time.
    method, rtol, atol : see ``scipy.integrate.solve_ivp``.
    args : tuple
        Extra positional arguments forwarded to ``rhs``.

    Returns
    -------
    (N, dim) ndarray
        The state sampled at each time in ``t_eval``.
    """
    sol = solve_ivp(
        rhs,
        (t_eval[0], t_eval[-1]),
        np.asarray(z0, dtype=float),
        method=method,
        t_eval=t_eval,
        rtol=rtol,
        atol=atol,
        args=args,
        dense_output=False,
    )
    if not sol.success:
        raise RuntimeError(f"integration failed: {sol.message}")
    return sol.y.T
