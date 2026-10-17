"""Unit tests for the quaternion/rotation conventions."""

import numpy as np

from aste586.conventions import (IDENTITY_Q, enforce_sign_continuity,
                                 matrix_to_quat, quat_multiply, quat_normalize,
                                 quat_to_matrix)


def test_identity_quaternion_is_identity_matrix():
    assert np.allclose(quat_to_matrix(IDENTITY_Q), np.eye(3))


def test_quat_to_matrix_is_a_rotation(quat):
    R = quat_to_matrix(quat)
    assert np.allclose(R @ R.T, np.eye(3), atol=1e-12)
    assert np.isclose(np.linalg.det(R), 1.0)


def test_matrix_quat_round_trip(quat):
    R = quat_to_matrix(quat)
    q2 = matrix_to_quat(R)
    # q and -q are the same attitude; compare matrices instead.
    assert np.allclose(quat_to_matrix(q2), R, atol=1e-10)


def test_quat_multiply_identity(quat):
    assert np.allclose(quat_multiply(quat, IDENTITY_Q), quat)


def test_quat_multiply_identity2(quat):
    assert np.allclose(quat_multiply(IDENTITY_Q, quat), quat)


def test_sign_continuity_removes_jumps(quat_jump_series):
    fixed = enforce_sign_continuity(quat_jump_series)
    dots = np.sum(fixed[1:] * fixed[:-1], axis=1)
    assert np.all(dots > 0.0)


def test_normalize_rejects_zero():
    try:
        quat_normalize(np.zeros(4))
    except ValueError:
        return
    raise AssertionError("expected ValueError for zero quaternion")
