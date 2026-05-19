"""Hidden reference dynamics backend.

A complete, correct implementation of the same interface as the student
backend ``aste586.dynamics``. The harness selects it with
``--backend reference``; grading diffs the student backend against it.

This package is withheld from the student release (see
tools/make_student_release.py). It is kept in the instructor repository.
"""

from .damper import damper_eom
from .derivatives import state_derivative
from .kinematics import quaternion_derivative
from .part1 import analytical_solution, linear_ivp_rhs
from .rigid_body import euler_eqs

__all__ = [
    "linear_ivp_rhs",
    "analytical_solution",
    "euler_eqs",
    "quaternion_derivative",
    "damper_eom",
    "state_derivative",
]
