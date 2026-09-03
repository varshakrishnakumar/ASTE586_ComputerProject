"""PyBullet replay of a stored run -- provided.

Replays the attitude time series in 3-D. The spacecraft body is a primitive
sized from the config's ``viz``/``geometry`` block; overlays show the
body-fixed axes, the (body-fixed) angular velocity and the (inertially fixed)
angular momentum so the precession/nutation/spin geometry is visible.
PyBullet is imported lazily so the rest of the toolkit works without it.
"""

from __future__ import annotations

import time

import numpy as np

from ..conventions import quat_to_matrix
from ..io import RunArtifact
from .overlays import Overlay

_DEG = 180.0 / np.pi

_BODY_AXIS_COLORS = ([0.9, 0.5, 0.5], [0.5, 0.9, 0.5], [0.5, 0.5, 0.9])


def _import_pybullet():
    try:
        import pybullet as p
    except ImportError as exc:
        raise RuntimeError(
            "pybullet is not installed, so `aste586 view` cannot open a window.\n"
            "  Install it with `conda install -c conda-forge pybullet` (see "
            "environment.yml).\n  Everything else (run/plot/check/grade) works "
            "without it."
        ) from exc
    return p


def make_body(p, geom: dict):
    """Create the spacecraft visual body from the geometry/viz config."""
    shape = geom.get("shape", "box")
    color = [0.5, 0.6, 0.85, 1.0]
    if shape == "cylinder":
        radius = float(geom.get("radius", 0.36))
        height = float(geom.get("height", 0.59))
        vis = p.createVisualShape(p.GEOM_CYLINDER, radius=radius, length=height,
                                  rgbaColor=color)
    else:
        he = [float(x) for x in geom.get("half_extents", [0.35, 0.22, 0.45])]
        vis = p.createVisualShape(p.GEOM_BOX, halfExtents=he, rgbaColor=color)
    return p.createMultiBody(baseMass=0.0, baseVisualShapeIndex=vis)


def body_geometry(artifact: RunArtifact) -> dict:
    """Merged ``geometry`` + ``viz`` blocks from the run's metadata."""
    return {**(artifact.meta.get("geometry") or {}), **(artifact.meta.get("viz") or {})}


def view(artifact: RunArtifact, speed: float = 1.0) -> None:
    """Open a PyBullet window and replay ``artifact``.

    Parameters
    ----------
    artifact : RunArtifact
        A run produced by ``aste586 run`` (must be an attitude run).
    speed : float
        Playback rate multiplier (1.0 = real time).
    """
    if artifact.meta["model"] == "linear":
        raise ValueError("Part 1 is a linear IVP -- there is nothing to view")

    p = _import_pybullet()

    t = artifact["time"]
    q = artifact["q"]
    omega = artifact["omega"]
    theta = artifact["theta"] * _DEG
    H_world = artifact["H_F"][0]              # constant for torque-free motion
    H_dir = H_world / max(np.linalg.norm(H_world), 1e-12)

    p.connect(p.GUI)
    p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
    p.resetDebugVisualizerCamera(3.0, 45, -30, [0, 0, 0])
    body = make_body(p, body_geometry(artifact))

    overlay = Overlay(p)
    # Inertial reference axes (faint), drawn once.
    for axis, color in zip(np.eye(3), ([1, 0, 0], [0, 1, 0], [0, 0, 1])):
        p.addUserDebugLine([0, 0, 0], 1.6 * axis, lineColorRGB=color,
                           lineWidth=1.0)

    duration = (t[-1] - t[0]) / max(speed, 1e-6)
    print(f"Replaying {artifact.scenario} [{artifact.backend}] at {speed:g}x "
          f"({duration:.0f} s of wall time) -- close the window to stop.")
    print("  red = angular momentum H (fixed)   orange = angular velocity omega\n"
          "  pastel red/green/blue = body axes 1/2/3")
    wall0 = time.time()
    try:
        for i in range(len(t)):
            if not p.isConnected():
                break
            R = quat_to_matrix(q[i])
            p.resetBasePositionAndOrientation(body, [0, 0, 0], q[i])

            for k in range(3):
                overlay.vector(f"b{k + 1}", [0, 0, 0], R[:, k],
                               color=_BODY_AXIS_COLORS[k], scale=1.0)
            omega_world = R @ omega[i]
            overlay.vector("omega", [0, 0, 0], omega_world,
                           color=[1.0, 0.6, 0.0],
                           scale=1.2 / max(np.linalg.norm(omega_world), 1e-6))
            overlay.vector("H", [0, 0, 0], H_dir, color=[0.9, 0.1, 0.1], scale=1.8)
            overlay.hud(
                f"t = {t[i]:7.2f} s   |omega| = {np.linalg.norm(omega[i]):.3f} rad/s"
                f"   nutation = {theta[i]:6.2f} deg"
            )

            target = wall0 + (t[i] - t[0]) / max(speed, 1e-6)
            time.sleep(max(0.0, target - time.time()))
    except p.error:
        pass  # window closed mid-replay
    finally:
        if p.isConnected():
            p.disconnect()
    print("Replay finished.")
