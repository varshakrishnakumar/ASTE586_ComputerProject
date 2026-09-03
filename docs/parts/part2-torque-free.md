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

```bash
aste586 check --part 2                 # after each function
aste586 run   part2_direct_precession
aste586 plot  part2_direct_precession
aste586 view  part2_direct_precession
aste586 grade --part 2
```

## Scenarios

- `part2_direct_precession` — `I2` smallest, `I1 = I3` (oblate about body
  axis 2): direct precession.
- `part2_retrograde_precession` — `I1` largest, `I2 = I3` (prolate about
  body axis 1): retrograde precession.

## What the harness reports

`omega(t)`, the nutation angle, the 3-1-3 precession and spin angles,
quaternion-norm error, angular momentum components in the inertial frame
(which must be constant), and kinetic-energy drift. The error against the
analytical axisymmetric solution is plotted automatically.

The scenario builder always places the angular momentum along inertial **z**,
so the nutation angle is the angle between `H` and the chosen body reference
axis (`analysis.reference_axis` in the config). For an axisymmetric body it is
**constant**.

## What a correct result looks like

| scenario | nutation | precession rate ψ̇ | spin rate φ̇ | \|H\| | T |
|----------|----------|--------------------|--------------|-------|---|
| `part2_direct_precession` | 10.0° constant | +0.1047 rad/s | +0.0258 rad/s | 0.5236 kg m²/s | 0.03406 J |
| `part2_retrograde_precession` | 45.0° constant | +0.1047 rad/s | −0.0148 rad/s | 0.4186 kg m²/s | 0.01971 J |

Things to verify in your write-up: ψ̇ = |H| / I_lateral in both cases; the
spin and precession rates have the **same** sign for the oblate body (direct)
and **opposite** signs for the prolate body (retrograde); the polhode is a
circle about the symmetry axis; `omega` along the symmetry axis is constant.
`aste586 run` prints all of these numbers.
