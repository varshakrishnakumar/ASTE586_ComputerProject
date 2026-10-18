"""Reference solution — the assembled state derivative."""

from __future__ import annotations

import numpy as np

from aste586.model import IDX_OMEGA_D, IDX_Q, IDX_THETA_D, IDX_W, Params

from .damper import damper_eom
from .kinematics import quaternion_derivative
from .rigid_body import euler_eqs


def state_derivative(t: float, z: np.ndarray, params: Params) -> np.ndarray:
    """Full ``dz/dt`` for the rigid or damped attitude model."""
    omega = z[IDX_W]
    q = z[IDX_Q]
    q_dot = quaternion_derivative(q, omega)

    if params.model == "rigid":
        alpha = euler_eqs(omega, params.J, params.torque)
        return np.concatenate([alpha, q_dot])

    elif params.model == "damped":
        theta_d = z[IDX_THETA_D]
        omega_d = z[IDX_OMEGA_D]
        alpha, theta_d_dot, omega_d_dot = damper_eom(
            omega, params.J, params.Id, params.D, params.K, theta_d, omega_d
        )
        return np.concatenate([alpha, q_dot, [theta_d_dot, omega_d_dot]])

    else:
        raise ValueError(f"unknown model {params.model!r}")
