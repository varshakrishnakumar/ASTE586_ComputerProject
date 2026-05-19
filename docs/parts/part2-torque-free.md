# Part 2 — Torque-free motion of a rigid body

Simulate the torque-free rotation of an **axisymmetric** rigid body and verify
it against the analytical solution and physical invariants.

## What to implement

- `dynamics/rigid_body.py` — `euler_eqs(omega, J, torque)`: Euler's equations
  for a body with principal inertia `J = diag(I1, I2, I3)`.
- `dynamics/kinematics.py` — `quaternion_derivative(q, omega)`: the quaternion
  kinematic equation, `omega` in body coordinates.
- `dynamics/derivatives.py` — `state_derivative`: unpack `z` into `omega, q`,
  call the two functions above, pack `dz`.

## Scenarios

- `part2_direct_precession` — `I2` smallest, `I1 = I3`: direct precession.
- `part2_retrograde_precession` — `I1` largest, `I2 = I3`: retrograde precession.

## What the harness reports

`omega(t)`, the 3-1-3 Euler angles, quaternion-norm error, and angular
momentum components in the inertial frame (which must be constant). The error
against the analytical axisymmetric solution is plotted automatically.
