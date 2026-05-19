"""Unit tests for the quaternion/rotation conventions."""

import numpy as np

from aste586.conventions import (
    enforce_sign_continuity,
    matrix_to_quat,
    quat_multiply,
    quat_normalize,
    quat_to_matrix,
)

IDENTITY_Q = np.array([0.0, 0.0, 0.0, 1.0])


def _random_quats(n, seed=0):
    rng = np.random.default_rng(seed)
    q = rng.normal(size=(n, 4))
    return q / np.linalg.norm(q, axis=1, keepdims=True)


def test_identity_quaternion_is_identity_matrix():
    assert np.allclose(quat_to_matrix(IDENTITY_Q), np.eye(3))


def test_quat_to_matrix_is_a_rotation():
    for q in _random_quats(20):
        R = quat_to_matrix(q)
        assert np.allclose(R @ R.T, np.eye(3), atol=1e-12)
        assert np.isclose(np.linalg.det(R), 1.0)


def test_matrix_quat_round_trip():
    for q in _random_quats(20, seed=1):
        R = quat_to_matrix(q)
        q2 = matrix_to_quat(R)
        # q and -q are the same attitude; compare matrices instead.
        assert np.allclose(quat_to_matrix(q2), R, atol=1e-10)


def test_quat_multiply_identity():
    for q in _random_quats(10, seed=2):
        assert np.allclose(quat_multiply(q, IDENTITY_Q), q)
        assert np.allclose(quat_multiply(IDENTITY_Q, q), q)


def test_sign_continuity_removes_jumps():
    base = _random_quats(1, seed=3)[0]
    series = np.array([base, base, -base, base, -base])
    fixed = enforce_sign_continuity(series)
    dots = np.sum(fixed[1:] * fixed[:-1], axis=1)
    assert np.all(dots > 0.0)


def test_normalize_rejects_zero():
    try:
        quat_normalize(np.zeros(4))
    except ValueError:
        return
    raise AssertionError("expected ValueError for zero quaternion")
