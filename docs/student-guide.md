# Student guide

## What you do

You implement the **equations of motion** — and nothing else. Five files in
`src/aste586/dynamics/` ship as stubs that raise `NotImplementedError`. Fill
them in. The harness (integration, visualization, plotting, validation) is
already done.

Read [`conventions.md`](conventions.md) first. It defines the state vector,
the quaternion convention, and the function signatures. Your code must obey it.

## The functions, in order of difficulty

| File | Function | What it returns |
|------|----------|-----------------|
| `part1.py` | `linear_ivp_rhs(t, x, A)` | `dx/dt` for the Part 1 warm-up |
| `part1.py` | `analytical_solution(t)` | the closed form you derive by hand |
| `kinematics.py` | `quaternion_derivative(q, omega)` | `dq/dt` from the quaternion kinematic equation |
| `rigid_body.py` | `euler_eqs(omega, J, torque)` | angular acceleration from Euler's equations |
| `damper.py` | `damper_eom(...)` | Part 4 damper terms (Eqs 1–5 of the handout) |
| `derivatives.py` | `state_derivative(t, z, params)` | assembles the full `dz/dt` |

`state_derivative` is the only function the integrator calls directly; it
unpacks `z`, calls the others, and packs `dz`. Implement the small functions
first and `state_derivative` becomes a few lines of glue.

## Workflow

```bash
aste586 list                            # see scenarios
aste586 run   part2_direct_precession    # propagate (uses your code by default)
aste586 plot  part2_direct_precession    # report figures
aste586 view  part2_direct_precession    # 3-D replay
aste586 grade part2_direct_precession    # compare against the reference
```

`run` uses `--backend student` by default. While a function is still a stub
the run will fail with `NotImplementedError` naming what to implement next.

## Rules (from the project handout)

- **Do not** write your own integrator. The harness uses `scipy.solve_ivp`.
  You only supply the right-hand side.
- **Do not** use a symbolic solver. The Part 1 `analytical_solution` must be
  the closed form you derive yourself.
- Comments count toward your grade. Explain *why*, not *what*.

## Self-checking

`aste586 grade` checks two things: that physical invariants hold (your
quaternion stays unit-norm, angular momentum is conserved in the inertial
frame, energy behaves correctly) and that your time series match the reference
within tolerance. Green on `grade` for every scenario in a part means your
dynamics for that part are correct.
