"""One-screen physical summary of a run -- provided.

Printed by ``aste586 run`` so you see, without opening a figure, whether the
motion you just produced conserves what it should and how large the nutation
angle is.
"""

from __future__ import annotations

import numpy as np

from .io import RunArtifact

_DEG = 180.0 / np.pi


def summarize(a: RunArtifact) -> list[str]:
    """Human-readable lines describing the physics of run ``a``."""
    t = a["time"]
    lines = [f"t = 0 .. {t[-1]:g} s  ({len(t)} samples)"]
    if a.meta["model"] == "linear":
        lines.append(f"max |numerical - analytical| = {a['error'].max():.2e}")
        lines.append(f"max |sum x_i^2 - 2|          = {np.abs(a['conserved']).max():.2e}")
        return lines

    qn = np.abs(a["q_norm"] - 1.0).max()
    H = a["H_F"]
    drift = np.abs(H - H[0]).max()
    lines.append(f"max | |q| - 1 |          = {qn:.2e}")
    lines.append(f"|H| = {np.linalg.norm(H[0]):.6g} kg m^2/s, max drift in inertial frame = {drift:.2e}")

    T = a["T"]
    if a.meta["model"] == "damped":
        lines.append(f"T = {T[0]:.6g} -> {T[-1]:.6g} J  (change {T[-1] - T[0]:+.4g})")
    else:
        lines.append(f"T = {T[0]:.6g} J, spread = {T.max() - T.min():.2e}")

    axis = a.meta.get("analysis", {}).get("reference_axis", 3)
    th = a["theta"] * _DEG
    lines.append(f"nutation about body axis {axis}: {th[0]:.3f} deg at t=0, "
                 f"range [{th.min():.3f}, {th.max():.3f}] deg, {th[-1]:.3f} deg at the end")
    psi_rate = np.polyfit(t, a["psi"], 1)[0]
    phi_rate = np.polyfit(t, a["phi"], 1)[0]
    lines.append(f"mean precession rate {psi_rate:+.5f} rad/s, mean spin rate {phi_rate:+.5f} rad/s")
    if "omega_error" in a:
        lines.append(f"max |omega - analytical (axisymmetric)| = {a['omega_error'].max():.2e} rad/s")
    if "off_nadir" in a:
        od = a["off_nadir"] * _DEG
        lines.append(f"off-nadir angle: max {od.max():.3f} deg")
    return lines
