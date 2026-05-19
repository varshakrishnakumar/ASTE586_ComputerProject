"""Report figures -- provided.

Given a stored run, produce the figures the assignment asks for and save them
as PNGs alongside the run. Nothing here is student code; it only visualizes
whatever the dynamics backend produced.
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

    fig1, axes = plt.subplots(2, 2, figsize=(10, 6), sharex=True)
    for k, ax in enumerate(axes.flat):
        ax.plot(t, x[:, k], label="numerical")
        ax.plot(t, x_a[:, k], "--", label="analytical")
        ax.set_title(f"x{k + 1}")
        ax.grid(alpha=0.3)
    axes[0, 0].legend()
    for ax in axes[1, :]:
        ax.set_xlabel("time (s)")
    fig1.suptitle(f"{a.scenario}: numerical vs analytical")

    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    ax1.semilogy(t, err.max(axis=1))
    ax1.set(title="max component error", xlabel="time (s)", ylabel="|num - ana|")
    ax1.grid(alpha=0.3)
    ax2.plot(t, a["conserved"])
    ax2.set(title=r"$\sum x_i^2 - 2$", xlabel="time (s)")
    ax2.grid(alpha=0.3)

    return [("components", fig1), ("accuracy", fig2)]


def _plot_attitude(a: RunArtifact) -> list[tuple[str, plt.Figure]]:
    t = a["time"]
    figs: list[tuple[str, plt.Figure]] = []

    # --- Time histories: omega, Euler angles, |q| error, H drift ----------
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    ax = axes[0, 0]
    for k, lbl in enumerate(("w1", "w2", "w3")):
        ax.plot(t, a["omega"][:, k], label=lbl)
    ax.set(title="angular velocity (rad/s)", xlabel="time (s)")
    ax.legend(); ax.grid(alpha=0.3)

    ax = axes[0, 1]
    ax.plot(t, a["psi"] * _DEG, label="precession")
    ax.plot(t, a["theta"] * _DEG, label="nutation")
    ax.plot(t, a["phi"] * _DEG, label="spin")
    ax.set(title="3-1-3 Euler angles (deg)", xlabel="time (s)")
    ax.legend(); ax.grid(alpha=0.3)

    ax = axes[1, 0]
    ax.plot(t, a["q_norm"] - 1.0)
    ax.set(title="quaternion norm error (|q| - 1)", xlabel="time (s)")
    ax.grid(alpha=0.3)

    ax = axes[1, 1]
    H = a["H_F"]
    for k, lbl in enumerate(("Hx", "Hy", "Hz")):
        ax.plot(t, H[:, k] - H[0, k], label=lbl)
    ax.set(title="angular momentum drift, inertial frame", xlabel="time (s)")
    ax.legend(); ax.grid(alpha=0.3)
    fig.suptitle(f"{a.scenario}: time histories")
    figs.append(("time_histories", fig))

    # --- Polhode: omega traced in body coordinates ------------------------
    fig = plt.figure(figsize=(6, 5))
    ax = fig.add_subplot(111, projection="3d")
    w = a["omega"]
    ax.plot(w[:, 0], w[:, 1], w[:, 2], lw=0.8)
    ax.set(xlabel="w1", ylabel="w2", zlabel="w3",
           title=f"{a.scenario}: polhode")
    figs.append(("polhode", fig))

    # --- Optional panels ---------------------------------------------------
    extra = []
    if "omega_error" in a:
        extra.append(("omega error vs analytical (rad/s)",
                       a["omega_error"].max(axis=1), True))
    if "off_nadir" in a:
        extra.append(("off-nadir angle (deg)", a["off_nadir"] * _DEG, False))
    if "T" in a and a.meta["model"] == "damped":
        extra.append(("kinetic energy (J)", a["T"], False))
    if "theta_d" in a:
        extra.append(("damper angle (rad)", a["theta_d"], False))

    if extra:
        fig, axes = plt.subplots(1, len(extra), figsize=(5 * len(extra), 4),
                                 squeeze=False)
        for ax, (title, data, logy) in zip(axes[0], extra):
            (ax.semilogy if logy else ax.plot)(t, data)
            ax.set(title=title, xlabel="time (s)")
            ax.grid(alpha=0.3)
        fig.suptitle(f"{a.scenario}: case quantities")
        figs.append(("case_quantities", fig))

    return figs
