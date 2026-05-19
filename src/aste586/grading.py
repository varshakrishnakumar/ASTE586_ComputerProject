"""Grading -- provided.

Compares a student run against the hidden reference run for the same scenario
and checks physical invariants. Tolerances live in ``grading/rubric.yaml``.
``aste586 grade <scenario>`` calls :func:`grade`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import yaml

from .io import RunArtifact
from .io.config import _repo_root
from .sim import run


@dataclass
class Check:
    """One graded line item."""

    name: str
    passed: bool
    detail: str


def _rubric(scenario: str) -> dict:
    """Per-scenario tolerances, falling back to the ``default`` block."""
    path = _repo_root() / "grading" / "rubric.yaml"
    rubric = yaml.safe_load(path.read_text()) if path.is_file() else {}
    merged = dict(rubric.get("default", {}))
    merged.update(rubric.get(scenario, {}))
    return merged


def _energy_envelope_increase(T: np.ndarray, n_windows: int = 16) -> float:
    """Largest increase between consecutive block-averaged values of ``T``.

    Block-averaging removes the precession-frequency ripple so the check sees
    the slow energy trend, which dissipation forces to be non-increasing.
    """
    blocks = np.array_split(np.asarray(T), min(n_windows, len(T)))
    means = np.array([b.mean() for b in blocks])
    return float(np.diff(means).max()) if len(means) > 1 else 0.0


def _invariant_checks(ref: RunArtifact, tol: dict) -> list[Check]:
    """Checks on the reference run -- these validate the scenario itself."""
    checks = []
    if ref.meta["model"] == "linear":
        max_err = float(ref["error"].max())
        checks.append(Check(
            "analytical accuracy", max_err <= tol["linear_error"],
            f"max|num-ana| = {max_err:.2e} (<= {tol['linear_error']:.0e})"))
        return checks

    qn = float(np.abs(ref["q_norm"] - 1.0).max())
    checks.append(Check(
        "quaternion stays unit-norm", qn <= tol["quat_norm"],
        f"max||q|-1| = {qn:.2e}"))

    H = ref["H_F"]
    drift = float(np.abs(H - H[0]).max())
    checks.append(Check(
        "angular momentum conserved (inertial)", drift <= tol["H_drift"],
        f"max drift = {drift:.2e} kg m^2/s"))

    T = ref["T"]
    if ref.meta["model"] == "damped":
        # The dashpot dissipates energy, but precession puts a small ripple on
        # T(t); check the *envelope* (block-averaged) is non-increasing rather
        # than every single step.
        rise = _energy_envelope_increase(T)
        checks.append(Check(
            "kinetic energy decreases (envelope)", rise <= tol["energy_rise"],
            f"max window-mean increase = {rise:.2e} J"))
    else:
        spread = float(T.max() - T.min())
        checks.append(Check(
            "kinetic energy conserved", spread <= tol["energy_spread"],
            f"T spread = {spread:.2e} J"))
    return checks


def _match_checks(student: RunArtifact, ref: RunArtifact, tol: dict) -> list[Check]:
    """Component-wise comparison of the student run against the reference."""
    checks = []
    keys = ("x",) if ref.meta["model"] == "linear" else ("omega", "q")
    for key in keys:
        if key not in student or key not in ref:
            continue
        err = float(np.abs(student[key] - ref[key]).max())
        checks.append(Check(
            f"{key} matches reference", err <= tol["match"],
            f"max abs diff = {err:.2e} (<= {tol['match']:.0e})"))
    return checks


def grade(scenario: str) -> bool:
    """Grade ``scenario``: run both backends, check, print a report.

    Returns ``True`` if every check passed.
    """
    tol = _rubric(scenario)
    ref = run(scenario, backend="reference")
    student = run(scenario, backend="student")

    checks = _invariant_checks(ref, tol) + _match_checks(student, ref, tol)

    print(f"\n  Grading: {scenario}\n  " + "-" * 50)
    for c in checks:
        mark = "PASS" if c.passed else "FAIL"
        print(f"  [{mark}] {c.name:42s} {c.detail}")
    ok = all(c.passed for c in checks)
    print("  " + "-" * 50)
    print(f"  {'ALL CHECKS PASSED' if ok else 'SOME CHECKS FAILED'}\n")
    return ok
