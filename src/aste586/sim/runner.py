"""Run orchestration -- provided.

``run`` ties the pieces together: load the scenario, pick the backend,
integrate, compute the analysis time series, and store the result. It is what
``aste586 run`` calls.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from types import ModuleType

import numpy as np

from ..analysis import (
    angular_momentum_inertial,
    axisymmetric_omega,
    euler_angles_313,
    kinetic_energy,
    off_nadir_angle,
    quaternion_norm,
)
from ..conventions import enforce_sign_continuity, quat_to_matrix
from ..io import RunArtifact, load_config, save_run
from ..model import IDX_OMEGA_D, IDX_Q, IDX_THETA_D, IDX_W
from .integrator import integrate
from .scenario import Scenario, build_scenario


def load_backend(name: str) -> ModuleType:
    """Return the dynamics backend module for ``name``.

    ``"student"`` -> ``aste586.dynamics`` (the stubs you implement).
    ``"reference"`` -> ``aste586_reference`` (the hidden solution).
    """
    if name == "student":
        from aste586 import dynamics
        return dynamics
    if name == "reference":
        try:
            import aste586_reference
        except ImportError as exc:  # stripped from the student release
            raise RuntimeError(
                "the reference backend is not installed in this checkout"
            ) from exc
        return aste586_reference
    raise ValueError(f"unknown backend {name!r}; use 'student' or 'reference'")


def _backend_hash(backend: ModuleType) -> str:
    """Short content hash of the backend's source -- recorded in meta.json so a
    run can be traced to the exact code that produced it."""
    h = hashlib.sha256()
    pkg_dir = Path(backend.__path__[0])
    for path in sorted(pkg_dir.glob("*.py")):
        h.update(path.read_bytes())
    return h.hexdigest()[:12]


def _integrator_opts(scn: Scenario) -> dict:
    """Pull the keyword options that :func:`integrate` accepts from a config."""
    opts = {}
    for key in ("method", "rtol", "atol"):
        if key in scn.integrator:
            opts[key] = scn.integrator[key]
    return opts


def run(scenario: str, backend: str = "student") -> RunArtifact:
    """Propagate ``scenario`` with ``backend`` and persist the result."""
    cfg = load_config(scenario)
    scn = build_scenario(cfg)
    backend_mod = load_backend(backend)
    opts = _integrator_opts(scn)

    meta = {
        "scenario": scenario,
        "backend": backend,
        "part": scn.extras["part"],
        "model": scn.model,
        "integrator": {"method": "DOP853", "rtol": 1e-9, "atol": 1e-9, **opts},
        "geometry": scn.extras["geometry"],
        "backend_hash": _backend_hash(backend_mod),
    }

    if scn.model == "linear":
        series = _run_linear(scn, backend_mod, opts)
    else:
        series = _run_attitude(scn, backend_mod, opts)

    artifact = RunArtifact(scenario, backend, series, meta)
    save_run(artifact)
    return artifact


def _run_linear(scn: Scenario, backend, opts) -> dict:
    """Part 1: integrate the linear IVP and compare to the analytical form."""
    x = integrate(
        backend.linear_ivp_rhs, scn.x0, scn.t_eval, args=(scn.A,), **opts
    )
    x_exact = backend.analytical_solution(scn.t_eval)
    return {
        "time": scn.t_eval,
        "x": x,
        "x_analytical": x_exact,
        "error": np.abs(x - x_exact),
        # Part 1 asks to plot sum(x_i^2) - 2, which should stay near zero.
        "conserved": np.sum(x**2, axis=1) - 2.0,
    }


def _run_attitude(scn: Scenario, backend, opts) -> dict:
    """Parts 2-4: integrate the rotational state and derive analysis series."""
    params = scn.params
    z = integrate(
        backend.state_derivative, scn.z0, scn.t_eval, args=(params,), **opts
    )
    omega = z[:, IDX_W]
    q_raw = z[:, IDX_Q]
    q = enforce_sign_continuity(q_raw / np.linalg.norm(q_raw, axis=1, keepdims=True))

    Id = params.Id if scn.model == "damped" else 0.0
    K = params.K if scn.model == "damped" else 0.0
    theta_d = z[:, IDX_THETA_D] if scn.model == "damped" else None
    omega_d = z[:, IDX_OMEGA_D] if scn.model == "damped" else None

    ref_axis = int(scn.extras["analysis"].get("reference_axis", 3))
    psi, theta, phi = euler_angles_313(q, ref_axis)

    series = {
        "time": scn.t_eval,
        "omega": omega,
        "q": q,
        "q_norm": quaternion_norm(q_raw),
        "H_F": angular_momentum_inertial(omega, q, params.J, Id, omega_d),
        "T": kinetic_energy(omega, params.J, Id, K, theta_d, omega_d),
        "psi": psi,
        "theta": theta,
        "phi": phi,
    }
    if scn.model == "damped":
        series["theta_d"] = theta_d
        series["omega_d"] = omega_d

    # Analytical cross-check for axisymmetric (Part 2) bodies. The closed form
    # assumes torque-free rigid motion, so it does not apply to the damped
    # model even when the inertia happens to be axisymmetric.
    if scn.model == "rigid":
        omega_exact = axisymmetric_omega(scn.t_eval, omega[0], params.J)
        if omega_exact is not None:
            series["omega_analytical"] = omega_exact
            series["omega_error"] = np.abs(omega - omega_exact)

    # Part 3 dish: off-nadir angle of a body-fixed antenna.
    geom = scn.extras["geometry"]
    if "antenna_axis" in geom:
        antenna = np.array(geom["antenna_axis"], dtype=float)
        nadir = quat_to_matrix(q[0]) @ (antenna / np.linalg.norm(antenna))
        series["off_nadir"] = off_nadir_angle(q, antenna, nadir)

    return series
