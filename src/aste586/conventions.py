"""Quaternion and rotation helpers — provided.

All quaternions are **scalar-last** ``[x, y, z, w]`` and rotate body-frame
vectors into the inertial frame (see docs/conventions.md). These helpers are
used by the harness; the reference backend uses them too. Students may use
them but do not need to.
"""

from __future__ import annotations

import numpy as np


def quat_normalize(q: np.ndarray) -> np.ndarray:
    """Return ``q`` rescaled to unit norm."""
    q = np.asarray(q, dtype=float)
    n = np.linalg.norm(q)
    if n == 0.0:
        raise ValueError("cannot normalize a zero quaternion")
    return q / n


def quat_multiply(p: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Hamilton product ``p (x) r`` for scalar-last quaternions."""
    px, py, pz, pw = p
    rx, ry, rz, rw = r
    return np.array(
        [
            pw * rx + px * rw + py * rz - pz * ry,
            pw * ry - px * rz + py * rw + pz * rx,
            pw * rz + px * ry - py * rx + pz * rw,
            pw * rw - px * rx - py * ry - pz * rz,
        ]
    )


def quat_to_matrix(q: np.ndarray) -> np.ndarray:
    """Body->inertial rotation matrix ``C^FC`` from a scalar-last quaternion."""
    x, y, z, w = quat_normalize(q)
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]
    )


def matrix_to_quat(R: np.ndarray) -> np.ndarray:
    """Scalar-last quaternion from a 3x3 rotation matrix (Shepperd's method)."""
    R = np.asarray(R, dtype=float)
    t = np.trace(R)
    if t > 0.0:
        s = 0.5 / np.sqrt(t + 1.0)
        w = 0.25 / s
        x = (R[2, 1] - R[1, 2]) * s
        y = (R[0, 2] - R[2, 0]) * s
        z = (R[1, 0] - R[0, 1]) * s
    elif R[0, 0] >= R[1, 1] and R[0, 0] >= R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2])
        w = (R[2, 1] - R[1, 2]) / s
        x = 0.25 * s
        y = (R[0, 1] + R[1, 0]) / s
        z = (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] >= R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2])
        w = (R[0, 2] - R[2, 0]) / s
        x = (R[0, 1] + R[1, 0]) / s
        y = 0.25 * s
        z = (R[1, 2] + R[2, 1]) / s
    else:
        s = 2.0 * np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])
        w = (R[1, 0] - R[0, 1]) / s
        x = (R[0, 2] + R[2, 0]) / s
        y = (R[1, 2] + R[2, 1]) / s
        z = 0.25 * s
    return quat_normalize(np.array([x, y, z, w]))


def enforce_sign_continuity(quats: np.ndarray) -> np.ndarray:
    """Flip signs along a quaternion time series so it never jumps to ``-q``.

    ``q`` and ``-q`` are the same attitude; a numerical solution can hop
    between them. Plots and the viewer want a continuous track.
    """
    quats = np.array(quats, dtype=float)
    for i in range(1, len(quats)):
        if np.dot(quats[i], quats[i - 1]) < 0.0:
            quats[i] = -quats[i]
    return quats
