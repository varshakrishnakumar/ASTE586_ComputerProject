"""The assembled state derivative -- the one function the integrator calls.

``state_derivative`` unpacks the state vector ``z``, calls the equations of
motion you implemented in the other modules, and packs the result back into a
single derivative vector ``dz``.
"""

from __future__ import annotations

import numpy as np

from ..model import IDX_OMEGA_D, IDX_Q, IDX_THETA_D, IDX_W, Params
from .damper import damper_eom
from .kinematics import quaternion_derivative
from .rigid_body import euler_eqs


def state_derivative(t: float, z: np.ndarray, params: Params) -> np.ndarray:
    """Full time derivative ``dz/dt`` of the simulation state.

    The state layout depends on ``params.model`` (see docs/conventions.md):

    - ``"rigid"``  -> ``z = [omega(3), q(4)]``                length 7
    - ``"damped"`` -> ``z = [omega(3), q(4), theta_d, omega_d]`` length 9

    Use the index constants ``IDX_W``, ``IDX_Q``, ``IDX_THETA_D``,
    ``IDX_OMEGA_D`` to slice ``z`` rather than hard-coding numbers.

    Parameters
    ----------
    t : float
        Time (s). Unused -- the dynamics are autonomous -- but the integrator
        passes it.
    z : ndarray
        Current state vector.
    params : Params
        Physical parameters (inertia, model selector, damper coefficients).

    Returns
    -------
    ndarray
        ``dz/dt``, the same length as ``z``.
    """
    raise NotImplementedError(
        "Part 2: implement state_derivative -- unpack z, call euler_eqs and "
        "quaternion_derivative, pack dz. Extend it for params.model == "
        "'damped' in Part 4 using damper_eom."
    )
