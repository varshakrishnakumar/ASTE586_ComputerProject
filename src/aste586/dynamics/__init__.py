"""Student dynamics backend.

This package is the **equations of motion** you implement. Every function here
ships as a stub that raises ``NotImplementedError``; replace each body with
your own code. Do not change the function signatures — the harness calls them
exactly as declared.

See docs/student-guide.md for the recommended order and docs/conventions.md
for the state-vector layout and quaternion convention.
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
