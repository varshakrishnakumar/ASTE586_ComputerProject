"""Integration tests for the hidden reference backend (instructor checkout).

These exercise the whole harness (scenario -> integrator -> analysis) and
confirm the reference dynamics are physically correct. They double as a
specification of what a correct student backend must reproduce. They are
skipped automatically in the student release, where ``reference/`` is absent.
"""

import numpy as np
import pytest

pytest.importorskip("aste586_reference",
                    reason="reference backend not present (student release)")

from aste586.sim import run  # noqa: E402

pytestmark = pytest.mark.filterwarnings("ignore")


def test_part1_matches_analytical():
    a = run("part1_ivp", backend="reference")
    assert a["error"].max() < 1e-3            # handout target at t = 10
    assert np.abs(a["conserved"]).max() < 1e-3


def test_part2_direct_precession_invariants():
    a = run("part2_direct_precession", backend="reference")
    # unit quaternion
    assert np.abs(a["q_norm"] - 1.0).max() < 1e-5
    # angular momentum constant in the inertial frame
    H = a["H_F"]
    assert np.abs(H - H[0]).max() < 1e-3
    # kinetic energy conserved (no damper)
    assert a["T"].max() - a["T"].min() < 1e-4
    # matches the analytical axisymmetric solution
    assert a["omega_error"].max() < 1e-4
    # nutation is constant at 10 deg and precession/spin have the same sign
    nut = np.degrees(a["theta"])
    assert np.allclose(nut, 10.0, atol=0.05)
    psi_rate = np.polyfit(a["time"], a["psi"], 1)[0]
    phi_rate = np.polyfit(a["time"], a["phi"], 1)[0]
    assert psi_rate > 0 and phi_rate > 0                     # direct


def test_part2_retrograde_precession_invariants():
    a = run("part2_retrograde_precession", backend="reference")
    H = a["H_F"]
    assert np.abs(H - H[0]).max() < 1e-3
    assert a["omega_error"].max() < 1e-4
    nut = np.degrees(a["theta"])
    assert np.allclose(nut, 45.0, atol=0.05)
    psi_rate = np.polyfit(a["time"], a["psi"], 1)[0]
    phi_rate = np.polyfit(a["time"], a["phi"], 1)[0]
    assert psi_rate * phi_rate < 0                           # retrograde


def test_part4_intelsat_dissipates_energy():
    a = run("part4_intelsat", backend="reference")
    T = a["T"]
    # handout spot-check: T starts ~1.529e6 J and decreases to ~1.518e6 J
    assert 1.52e6 < T[0] < 1.54e6
    assert 1.51e6 < T[-1] < 1.52e6
    assert T[-1] < T[0]
    # the slow trend (block-averaged) must be non-increasing
    blocks = np.array_split(T, 16)
    means = np.array([b.mean() for b in blocks])
    assert np.diff(means).max() < 1.0
    # angular momentum still conserved with a damper
    H = a["H_F"]
    assert np.abs(H - H[0]).max() < 1e-1
    # handout spot-check: nutation falls from ~4 deg to ~2.7 deg
    nut = np.degrees(a["theta"])
    assert 3.9 < nut[0] < 4.1
    assert 2.6 < nut[-1] < 2.9
