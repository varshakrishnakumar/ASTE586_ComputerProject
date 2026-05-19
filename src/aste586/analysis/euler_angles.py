"""3-1-3 Euler-angle extraction -- provided.

The angles (precession psi, nutation theta, spin phi) are pulled from the
body->inertial rotation matrix. The body **reference axis** -- the axis that
plays the role of "body-3" in the 3-1-3 sequence -- is selectable, because
Parts 2-3 ask you to compare reference-axis choices.
"""

from __future__ import annotations

import numpy as np

from ..conventions import quat_to_matrix

# Right-handed (i, j, k) triad for each choice of reference axis k.
# Mirrors the axisloop logic in the Part 2 reference report.
_TRIAD = {1: (1, 2, 0), 2: (2, 0, 1), 3: (0, 1, 2)}


def euler_angles_313(
    q: np.ndarray, reference_axis: int = 3
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract unwrapped 3-1-3 Euler angles from a quaternion time series.

    Parameters
    ----------
    q : (N, 4) ndarray
        Attitude quaternions, scalar-last.
    reference_axis : {1, 2, 3}
        Which body axis is the spin/reference axis.

    Returns
    -------
    psi, theta, phi : (N,) ndarrays
        Precession, nutation, spin in **radians**. ``psi`` and ``phi`` are
        unwrapped so revolutions accumulate; ``theta`` is in ``[0, pi]``.
    """
    if reference_axis not in _TRIAD:
        raise ValueError("reference_axis must be 1, 2 or 3")
    i, j, k = _TRIAD[reference_axis]

    n = len(q)
    psi = np.empty(n)
    theta = np.empty(n)
    phi = np.empty(n)
    for idx in range(n):
        R = quat_to_matrix(q[idx])
        # Permute body axes so the reference axis acts as column 3, then apply
        # the standard 3-1-3 formula (class-notes convention).
        theta[idx] = np.arccos(np.clip(R[k, k], -1.0, 1.0))
        psi[idx] = np.arctan2(R[i, k], -R[j, k])
        phi[idx] = np.arctan2(R[k, i], R[k, j])

    return np.unwrap(psi), theta, np.unwrap(phi)
