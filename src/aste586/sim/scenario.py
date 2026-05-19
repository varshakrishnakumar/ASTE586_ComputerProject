"""Scenario builder -- provided.

Turns a parsed config dict into the concrete numbers the runner needs: the
initial state vector, the ``Params`` object, and the output time grid. It
also constructs the initial quaternion so the angular momentum starts aligned
with the inertial z-axis (which makes the extracted Euler angles meaningful).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ..conventions import matrix_to_quat
from ..model import Params


@dataclass
class Scenario:
    """Everything the runner needs to propagate one scenario."""

    cfg: dict
    model: str
    t_eval: np.ndarray
    integrator: dict
    params: Params | None = None       # rigid / damped
    z0: np.ndarray | None = None       # rigid / damped initial state
    A: np.ndarray | None = None        # linear (Part 1)
    x0: np.ndarray | None = None       # linear (Part 1)
    extras: dict = field(default_factory=dict)


def _initial_quaternion(omega0: np.ndarray, J: np.ndarray) -> np.ndarray:
    """Quaternion placing the angular-momentum vector along inertial z.

    Builds an orthonormal body triad whose third member is the (body-frame)
    angular-momentum direction, then reads off the body->inertial quaternion.
    """
    h_body = J @ omega0
    norm = np.linalg.norm(h_body)
    if norm < 1e-12:
        return np.array([0.0, 0.0, 0.0, 1.0])  # no spin: identity attitude
    k = h_body / norm
    seed = np.array([1.0, 0.0, 0.0]) if abs(k[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    i = np.cross(seed, k)
    i /= np.linalg.norm(i)
    j = np.cross(k, i)
    C_CF = np.column_stack([i, j, k])   # world -> body
    return matrix_to_quat(C_CF.T)       # body -> world quaternion


def build_scenario(cfg: dict) -> Scenario:
    """Construct a :class:`Scenario` from a parsed config dict."""
    model = cfg["model"]
    t_eval = np.linspace(0.0, float(cfg["tf"]), int(cfg["n_points"]))
    integ = dict(cfg.get("integrator", {}))

    extras = {
        "analysis": cfg.get("analysis", {}),
        "geometry": cfg.get("geometry", {}),
        "viz": cfg.get("viz", {}),
        "part": cfg["part"],
    }

    if model == "linear":
        lin = cfg["linear"]
        return Scenario(
            cfg=cfg, model=model, t_eval=t_eval, integrator=integ,
            A=np.array(lin["A"], dtype=float),
            x0=np.array(lin["x0"], dtype=float),
            extras=extras,
        )

    J = np.diag(np.array(cfg["inertia"], dtype=float))
    omega0 = np.array(cfg["initial"]["omega"], dtype=float)

    q_cfg = cfg["initial"].get("quaternion")
    q0 = np.array(q_cfg, dtype=float) if q_cfg else _initial_quaternion(omega0, J)
    q0 = q0 / np.linalg.norm(q0)

    if model == "rigid":
        params = Params(J=J, model="rigid")
        z0 = np.concatenate([omega0, q0])
    elif model == "damped":
        d = cfg["damper"]
        params = Params(
            J=J, model="damped",
            Id=float(d["Id"]), D=float(d["D"]), K=float(d["K"]),
        )
        z0 = np.concatenate([
            omega0, q0,
            [float(d.get("theta_d", 0.0)), float(d.get("omega_d", 0.0))],
        ])
    else:
        raise ValueError(f"unknown model {model!r}")

    return Scenario(
        cfg=cfg, model=model, t_eval=t_eval, integrator=integ,
        params=params, z0=z0, extras=extras,
    )
