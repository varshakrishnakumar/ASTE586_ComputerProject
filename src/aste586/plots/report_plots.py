"""Report figures -- provided.

Given a stored run, produce the figures the assignment asks for and save them
as PNGs alongside the run. Nothing here is student code; it only visualizes
whatever the dynamics backend produced.

Figures written by ``aste586 plot``:

* Part 1: ``components.png`` (numerical vs analytical) and ``accuracy.png``.
* Parts 2-4: ``time_histories.png`` (omega, nutation, precession/spin, |q|-1,
  H drift, energy), ``polhode.png`` (omega traced in body coordinates) and,
  when applicable, ``case_quantities.png`` (analytical error, off-nadir
  angle, damper angle).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: write files, never pop a window
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from ..io import RunArtifact, run_dir  # noqa: E402

_DEG = 180.0 / np.pi


def plot_run(artifact: RunArtifact) -> list[Path]:
    """Render every applicable figure for ``artifact``; return the PNG paths."""
    out_dir = run_dir(artifact.scenario, artifact.backend)
    if artifact.meta["model"] == "linear":
        figs = _plot_linear(artifact)
    else:
        figs = _plot_attitude(artifact)

    paths = []
    for name, fig in figs:
        path = out_dir / f"{name}.png"
        fig.savefig(path, dpi=130, bbox_inches="tight")
        plt.close(fig)
        paths.append(path)
    return paths


def _plot_linear(a: RunArtifact) -> list[tuple[str, plt.Figure]]:
    t = a["time"]
    x, x_a, err = a["x"], a["x_analytical"], a["error"]

    fig1, axes = plt.subplots(2, 2, figsize=(10, 6), sharex=True,
                              constrained_layout=True)
    for k, ax in enumerate(axes.flat):
        ax.plot(t, x[:, k], label="numerical")
        ax.plot(t, x_a[:, k], "--", label="analytical")
        ax.set_title(f"x{k + 1}")
        ax.grid(alpha=0.3)
    axes[0, 0].legend()
    for ax in axes[1, :]:
        ax.set_xlabel("time (s)")
    fig1.suptitle(f"{a.scenario}: numerical vs analytical")

    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    ax1.semilogy(t, np.maximum(err.max(axis=1), 1e-300))
    ax1.set(title="max component error", xlabel="time (s)", ylabel="|num - ana|")
    ax1.grid(alpha=0.3)
    ax2.plot(t, a["conserved"])
    ax2.set(title=r"$\sum x_i^2 - 2$", xlabel="time (s)")
    ax2.grid(alpha=0.3)

    return [("components", fig1), ("accuracy", fig2)]


def _plot_attitude(a: RunArtifact) -> list[tuple[str, plt.Figure]]:
    t = a["time"]
    axis = a.meta.get("analysis", {}).get("reference_axis", 3)
    damped = a.meta["model"] == "damped"
    figs: list[tuple[str, plt.Figure]] = []

    # --- Time histories ---------------------------------------------------
    fig, axes = plt.subplots(2, 3, figsize=(15, 7.5), constrained_layout=True)

    ax = axes[0, 0]
    for k, lbl in enumerate(("w1", "w2", "w3")):
        ax.plot(t, a["omega"][:, k], label=lbl)
    ax.set(title="angular velocity, body coords (rad/s)", xlabel="time (s)")
    ax.legend(); ax.grid(alpha=0.3)

    ax = axes[0, 1]
    th = a["theta"] * _DEG
    ax.plot(t, th, color="C1")
    if th.max() - th.min() < 1e-3:
        # Constant to numerical precision (axisymmetric torque-free case):
        # show it as a flat line, not integrator noise on a 1e-8 scale.
        ax.set_ylim(th.mean() - 1.0, th.mean() + 1.0)
    ax.set(title=f"nutation angle, H vs body axis {axis} (deg)", xlabel="time (s)")
    ax.grid(alpha=0.3)

    ax = axes[0, 2]
    ax.plot(t, a["psi"] * _DEG, label="precession psi")
    ax.plot(t, a["phi"] * _DEG, label="spin phi")
    ax.set(title="3-1-3 precession and spin, unwrapped (deg)", xlabel="time (s)")
    ax.legend(); ax.grid(alpha=0.3)

    ax = axes[1, 0]
    ax.plot(t, a["q_norm"] - 1.0)
    ax.set(title="quaternion norm error (|q| - 1)", xlabel="time (s)")
    ax.grid(alpha=0.3)

    ax = axes[1, 1]
    H = a["H_F"]
    for k, lbl in enumerate(("Hx", "Hy", "Hz")):
        ax.plot(t, H[:, k] - H[0, k], label=lbl)
    ax.set(title="angular momentum drift, inertial frame (kg m^2/s)", xlabel="time (s)")
    ax.legend(); ax.grid(alpha=0.3)

    ax = axes[1, 2]
    T = a["T"]
    if damped:
        ax.plot(t, T)
        ax.set(title="kinetic + spring energy T (J), should decrease", xlabel="time (s)")
    else:
        ax.plot(t, T - T[0])
        ax.set(title=f"kinetic energy drift T - T(0) (J), T(0) = {T[0]:.4g} J",
               xlabel="time (s)")
    ax.grid(alpha=0.3)
    fig.suptitle(f"{a.scenario} [{a.backend}]: time histories")
    figs.append(("time_histories", fig))

    # --- Polhode: omega traced in body coordinates ------------------------
    fig = plt.figure(figsize=(6.5, 6))
    ax = fig.add_subplot(111, projection="3d")
    w = a["omega"]
    ax.plot(w[:, 0], w[:, 1], w[:, 2], lw=0.8)
    ax.scatter(*w[0], color="C3", s=25, label="t = 0")
    # Equal aspect so a circular polhode looks circular.
    centre = (w.max(axis=0) + w.min(axis=0)) / 2
    half = max((w.max(axis=0) - w.min(axis=0)).max() / 2, 1e-9) * 1.1
    ax.set_xlim(centre[0] - half, centre[0] + half)
    ax.set_ylim(centre[1] - half, centre[1] + half)
    ax.set_zlim(centre[2] - half, centre[2] + half)
    ax.set_box_aspect((1, 1, 1))
    ax.set(xlabel="w1 (rad/s)", ylabel="w2 (rad/s)", zlabel="w3 (rad/s)",
           title=f"{a.scenario}: polhode (omega in body coords)")
    ax.legend(loc="upper left")
    figs.append(("polhode", fig))

    # --- Optional panels ---------------------------------------------------
    extra = []
    if "omega_error" in a:
        extra.append(("|omega - analytical| (rad/s)",
                      np.maximum(a["omega_error"].max(axis=1), 1e-300), True))
    if "off_nadir" in a:
        extra.append(("off-nadir angle (deg)", a["off_nadir"] * _DEG, False))
    if "theta_d" in a:
        extra.append(("damper wheel angle theta_d (rad)", a["theta_d"], False))
    if "omega_d" in a:
        extra.append(("damper wheel rate omega_d (rad/s)", a["omega_d"], False))

    if extra:
        fig, axes = plt.subplots(1, len(extra), figsize=(5 * len(extra), 4),
                                 squeeze=False, constrained_layout=True)
        for ax, (title, data, logy) in zip(axes[0], extra):
            (ax.semilogy if logy else ax.plot)(t, data)
            ax.set(title=title, xlabel="time (s)")
            ax.grid(alpha=0.3)
        fig.suptitle(f"{a.scenario} [{a.backend}]: case quantities")
        figs.append(("case_quantities", fig))

    return figs
