# Part 4 — Energy dissipation (damper)

Add a damper to the rigid body — a reaction wheel with a spring and a dashpot.
Energy is now dissipated; angular momentum is still conserved.

## What to implement

`dynamics/damper.py` — `damper_eom(omega, J, Id, D, K, theta_d, omega_d)`:
implement Eqs 1–5 of the Part 4 handout. Return the angular acceleration
`alpha` (3-vector) and the damper derivatives `theta_d_dot, omega_d_dot`.

> Eq 5 uses the result of Eq 2 — compute `alpha2` first.

`dynamics/derivatives.py` — `state_derivative` must handle `params.model ==
"damped"`: the state is length 9 (`omega, q, theta_d, omega_d`), and the
quaternion kinematics are unchanged.

## Scenarios

- `part4_intelsat` — the INTELSAT-inspired spot-check. The nutation angle
  should fall from ≈ 4° to ≈ 2.7°; kinetic energy should decrease and level
  off.
- `part4_flat_spin` — Explorer I flat-spin: nutation grows toward 60°.
- `part4_nonsymmetric` — a non-symmetric body transitioning from minor-axis to
  major-axis spin.

## What the harness reports

Everything from Parts 2–3 plus the damper-wheel angle `Theta_d(t)` and the
kinetic energy `T(t)` (which should monotonically decrease). Angular momentum
in the inertial frame must still be constant.
