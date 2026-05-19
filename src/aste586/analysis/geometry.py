"""Geometry helpers -- provided.

Off-nadir angle for the Part 3 dish/Earth-line problem, and the closed-form
inertia of a uniform cylinder.
"""

from __future__ import annotations

import numpy as np

from ..conventions import quat_to_matrix


def cylinder_inertia(mass: float, height: float, radius: float) -> tuple[float, float, float]:
    """Principal moments of a uniform solid cylinder.

    The symmetry axis is axis 3.

        I1 = I2 = m/12 * h^2 + m/4 * R^2
        I3 = m/2 * R^2
    """
    I_lat = mass / 12.0 * height**2 + mass / 4.0 * radius**2
    I_sym = mass / 2.0 * radius**2
    return I_lat, I_lat, I_sym


def off_nadir_angle(
    q: np.ndarray, antenna_axis_body: np.ndarray, nadir_inertial: np.ndarray
) -> np.ndarray:
    """Angle (radians) between the antenna axis and the Earth line.

    The antenna axis is body-fixed; rotated into the inertial frame at each
    instant it is compared with the fixed nadir direction (the inertial
    direction the antenna pointed at t = 0).

    Parameters
    ----------
    q : (N, 4) ndarray
        Attitude time series.
    antenna_axis_body : (3,) array
        Antenna boresight in body coordinates (need not be unit).
    nadir_inertial : (3,) array
        Earth-line direction in inertial coordinates (need not be unit).

    Returns
    -------
    (N,) ndarray
        Off-nadir angle in radians.
    """
    a_body = np.asarray(antenna_axis_body, float)
    a_body = a_body / np.linalg.norm(a_body)
    nadir = np.asarray(nadir_inertial, float)
    nadir = nadir / np.linalg.norm(nadir)

    ang = np.empty(len(q))
    for idx in range(len(q)):
        a_F = quat_to_matrix(q[idx]) @ a_body
        ang[idx] = np.arccos(np.clip(np.dot(a_F, nadir), -1.0, 1.0))
    return ang
