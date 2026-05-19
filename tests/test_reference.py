"""Integration tests for the reference backend.

These exercise the whole harness (scenario -> integrator -> analysis) and
confirm the reference dynamics are physically correct. They double as a
specification of what a correct student backend must reproduce.
"""

import numpy as np
import pytest

from aste586.sim import run

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


def test_part2_retrograde_precession_invariants():
    a = run("part2_retrograde_precession", backend="reference")
    H = a["H_F"]
    assert np.abs(H - H[0]).max() < 1e-3
    assert a["omega_error"].max() < 1e-4


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
