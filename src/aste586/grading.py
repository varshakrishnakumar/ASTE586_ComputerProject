"""Grading -- provided.

``aste586 grade <scenario>`` propagates the scenario with **your** backend and
then

1. checks your run against the physical invariants (unit quaternion, angular
   momentum constant in the inertial frame, energy conserved or dissipated);
2. compares your time series component-wise with the reference series.

The reference series come from ``grading/expected/<scenario>.npz``, which
ships with the project, so grading works without the hidden reference
backend. Tolerances live in ``grading/rubric.yaml``.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import yaml

from .io import RunArtifact, list_configs
from .io.config import _repo_root
from .report import FAIL, PASS, TODO, Check, describe_exception, print_report
from .sim import run
from .summary import summarize

_MATCH_KEYS = {"linear": ("x",), "rigid": ("omega", "q"), "damped": ("omega", "q")}


# ---------------------------------------------------------------------------
# Rubric and expected data
# ---------------------------------------------------------------------------

def _rubric(scenario: str) -> dict:
    """Per-scenario tolerances, falling back to the ``default`` block."""
    path = _repo_root() / "grading" / "rubric.yaml"
    rubric = yaml.safe_load(path.read_text()) if path.is_file() else {}
    merged = dict(rubric.get("default", {}))
    merged.update(rubric.get(scenario, {}))
    return merged


def expected_dir() -> Path:
    return _repo_root() / "grading" / "expected"


def expected_path(scenario: str) -> Path:
    return expected_dir() / f"{scenario}.npz"


def save_expected(artifact: RunArtifact) -> Path:
    """Store the series ``grade`` compares against (instructor tool)."""
    if artifact.backend != "reference":
        raise ValueError("expected data must come from the reference backend")
    keys = ("time",) + _MATCH_KEYS[artifact.meta["model"]]
    path = expected_path(artifact.scenario)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, meta=json.dumps(artifact.meta),
                        **{k: artifact.series[k] for k in keys})
    return path


def load_expected(scenario: str) -> RunArtifact | None:
    """The shipped reference series for ``scenario``, or ``None`` if absent."""
    path = expected_path(scenario)
    if not path.is_file():
        return None
    with np.load(path) as data:
        series = {k: data[k] for k in data.files if k != "meta"}
        meta = json.loads(str(data["meta"]))
    return RunArtifact(scenario, "expected", series, meta)


def reference_series(scenario: str) -> RunArtifact:
    """Shipped expected data if present, else a fresh reference run."""
    expected = load_expected(scenario)
    if expected is not None:
        return expected
    try:
        return run(scenario, backend="reference")
    except RuntimeError as exc:
        raise RuntimeError(
            f"no reference data for {scenario!r}: grading/expected/{scenario}.npz "
            "is missing and the reference backend is not installed. Ask the "
            "instructor to regenerate it with `python tools/make_expected.py`."
        ) from exc


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def _energy_envelope_increase(T: np.ndarray, n_windows: int = 16) -> float:
    """Largest increase between consecutive block-averaged values of ``T``.

    Block-averaging removes the precession-frequency ripple so the check sees
    the slow energy trend, which dissipation forces to be non-increasing.
    """
    blocks = np.array_split(np.asarray(T), min(n_windows, len(T)))
    means = np.array([b.mean() for b in blocks])
    return float(np.diff(means).max()) if len(means) > 1 else 0.0


def _check(name, passed, detail, hint="") -> Check:
    return Check(name, PASS if passed else FAIL, detail, hint=hint, group="physical invariants")


def _invariant_checks(a: RunArtifact, tol: dict) -> list[Check]:
    """Physics checks on a run. On the student run these are diagnostics: a
    failure points at a specific kind of mistake."""
    if a.meta["model"] == "linear":
        max_err = float(a["error"].max())
        return [_check(
            "numerical matches your analytical solution", max_err <= tol["linear_error"],
            f"max|num - ana| = {max_err:.2e} (<= {tol['linear_error']:.0e})",
            hint="one of linear_ivp_rhs / analytical_solution is wrong; `aste586 check --part 1` tells you which.")]

    checks = []
    qn = float(np.abs(a["q_norm"] - 1.0).max())
    checks.append(_check(
        "quaternion stays unit-norm", qn <= tol["quat_norm"],
        f"max||q|-1| = {qn:.2e} (<= {tol['quat_norm']:.0e})",
        hint="quaternion_derivative is not norm-preserving (q . dq/dt must be 0)."))

    H = a["H_F"]
    drift = float(np.abs(H - H[0]).max())
    checks.append(_check(
        "angular momentum conserved (inertial)", drift <= tol["H_drift"],
        f"max drift = {drift:.2e} kg m^2/s (<= {tol['H_drift']:.0e})",
        hint="H is only constant if the rotation (quaternion_derivative) and the "
             "gyroscopic terms (euler_eqs / damper_eom) agree; run `aste586 check`."))

    T = a["T"]
    if a.meta["model"] == "damped":
        rise = _energy_envelope_increase(T)
        checks.append(_check(
            "kinetic energy decreases (envelope)", rise <= tol["energy_rise"],
            f"max window-mean increase = {rise:.2e} J (<= {tol['energy_rise']:.0e})",
            hint="the dashpot must only remove energy: check the signs of the D and K "
                 "terms in damper_eom (Eq 2 vs Eq 5)."))
    else:
        spread = float(T.max() - T.min())
        checks.append(_check(
            "kinetic energy conserved", spread <= tol["energy_spread"],
            f"T spread = {spread:.2e} J (<= {tol['energy_spread']:.0e})",
            hint="omega . J alpha must be zero for torque-free motion: a sign in euler_eqs is wrong."))
    return checks


def _match_checks(student: RunArtifact, ref: RunArtifact, tol: dict) -> list[Check]:
    """Component-wise comparison of the student run against the reference."""
    checks = []
    for key in _MATCH_KEYS[ref.meta["model"]]:
        if key not in student or key not in ref:
            continue
        if student[key].shape != ref[key].shape:
            checks.append(Check(f"{key} matches reference", FAIL,
                                f"shape {student[key].shape} vs expected {ref[key].shape}",
                                group="comparison with reference"))
            continue
        err = float(np.abs(student[key] - ref[key]).max())
        checks.append(Check(
            f"{key} matches reference", PASS if err <= tol["match"] else FAIL,
            f"max abs diff = {err:.2e} (<= {tol['match']:.0e})",
            hint="invariants may all hold and this still fail: a convention differs "
                 "from docs/conventions.md (frame of omega, quaternion order, sign of a term).",
            group="comparison with reference"))
    return checks


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def grade_checks(scenario: str) -> tuple[list[Check], RunArtifact | None]:
    """Compute the grading checks for ``scenario`` without printing."""
    tol = _rubric(scenario)
    try:
        student = run(scenario, backend="student")
    except NotImplementedError as exc:
        return [Check("student backend runs", TODO, str(exc), group="student run")], None
    except Exception as exc:  # noqa: BLE001 -- student code can raise anything
        return [Check("student backend runs", FAIL, describe_exception(exc),
                      hint="fix the error above, then re-run.", group="student run")], None
    ref = reference_series(scenario)
    checks = _invariant_checks(student, tol) + _match_checks(student, ref, tol)
    return checks, student


def grade(scenario: str) -> bool:
    """Grade one scenario and print the report. ``True`` if everything passed."""
    t0 = time.perf_counter()
    checks, student = grade_checks(scenario)
    elapsed = time.perf_counter() - t0
    ok = print_report(f"Grading: {scenario}  ({elapsed:.1f} s)", checks)
    if student is not None:
        for line in summarize(student):
            print(f"    {line}")
        print()
    return ok


def grade_many(scenarios: list[str]) -> bool:
    """Grade several scenarios; print each report and a final summary."""
    results = {}
    for name in scenarios:
        try:
            results[name] = "PASS" if grade(name) else "FAIL"
        except RuntimeError as exc:
            print(f"  error: {exc}\n")
            results[name] = "ERROR"
    print("  Summary")
    print("  " + "-" * 40)
    for name, status in results.items():
        print(f"  [{status}] {name}")
    print()
    return all(s == "PASS" for s in results.values())


def scenarios_for_part(part: int) -> list[str]:
    from .io import load_config
    return [n for n in list_configs() if int(load_config(n)["part"]) == part]
