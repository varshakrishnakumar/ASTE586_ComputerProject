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

```bash
aste586 check --part 4          # momentum and energy checks catch sign errors
aste586 grade part4_intelsat    # fast (0.5 s)
aste586 grade --part 4          # the other two take ~30 s each
```

## Scenarios

- `part4_intelsat` — the INTELSAT-inspired spot-check. The nutation angle
  should fall from ≈ 4° to ≈ 2.7°; kinetic energy should decrease and level
  off.
- `part4_flat_spin` — Explorer I flat-spin: a minor-axis spin decays over
  two hours until the body spins flat (nutation → 90°).
- `part4_nonsymmetric` — a non-symmetric body transitioning from minor-axis
  toward major-axis spin.

## What the harness reports

Everything from Parts 2–3 plus the damper-wheel angle `Theta_d(t)`, its rate,
and the total energy `T(t)` (kinetic + spring), which must decrease. Angular
momentum in the inertial frame must still be constant.

## What a correct result looks like

| scenario | nutation (axis 3) | energy T | \|H\| | runtime |
|----------|-------------------|----------|-------|---------|
| `part4_intelsat` | 4.00° → 2.75° | 1.5294e6 → 1.5178e6 J | 60147 kg m²/s | 0.5 s |
| `part4_flat_spin` | 3.0° → 90.0° | 105.3 → 1.41 J | 3.515 kg m²/s | ≈ 30 s |
| `part4_nonsymmetric` | 47.9° → ≈ 100°, peaking at 126° | 123950 → 112990 J | 3236 kg m²/s | ≈ 30 s |

The energy plot for the damped model shows `T` itself, not `T − T(0)`; it
should be smooth and monotonically decreasing apart from a small ripple at
the precession frequency.
