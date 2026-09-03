"""3-1-3 Euler-angle extraction -- provided.

The angles (precession psi, nutation theta, spin phi) are pulled from the
body->inertial rotation matrix. The body **reference axis** -- the axis that
plays the role of "body-3" in the 3-1-3 sequence -- is selectable, because
Parts 2-3 ask you to compare reference-axis choices.
"""

from __future__ import annotations

import numpy as np

from ..conventions import quat_to_matrix

# Right-handed (i, j, k) body triad for each choice of reference axis k. The
# permutation is cyclic so the permuted triad is still a proper right-handed
# frame and the standard 3-1-3 formulas apply to it unchanged.
_TRIAD = {1: (1, 2, 0), 2: (2, 0, 1), 3: (0, 1, 2)}


def euler_angles_313(
    q: np.ndarray, reference_axis: int = 3
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract unwrapped 3-1-3 Euler angles from a quaternion time series.

    The inertial "3" axis is always inertial z (the scenario builder aligns
    the angular momentum with it), so the nutation angle ``theta`` is the
    angle between the angular-momentum vector and the chosen body axis. For
    torque-free motion of an axisymmetric body about its symmetry axis,
    ``theta`` is therefore constant.

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
        # Columns of R are the body axes expressed in the inertial frame.
        # Permute the *body* columns so the reference axis plays "body 3";
        # the inertial rows stay put (row 2 is inertial z, the H direction).
        R = quat_to_matrix(q[idx])[:, (i, j, k)]
        theta[idx] = np.arccos(np.clip(R[2, 2], -1.0, 1.0))
        psi[idx] = np.arctan2(R[0, 2], -R[1, 2])
        phi[idx] = np.arctan2(R[2, 0], R[2, 1])

    return np.unwrap(psi), theta, np.unwrap(phi)
