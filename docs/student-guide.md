# Student guide

## What you do

You implement the **equations of motion** — and nothing else. Five files in
`src/aste586/dynamics/` ship as stubs that raise `NotImplementedError`. Fill
them in. The harness (integration, visualization, plotting, checking, grading)
is already done.

Read [`conventions.md`](conventions.md) first. It defines the state vector,
the quaternion convention, and the function signatures. Your code must obey it.

## The functions, in order

| Part | File | Function | What it returns |
|------|------|----------|-----------------|
| 1 | `part1.py` | `linear_ivp_rhs(t, x, A)` | `dx/dt` for the Part 1 warm-up |
| 1 | `part1.py` | `analytical_solution(t)` | the closed form you derive by hand |
| 2 | `kinematics.py` | `quaternion_derivative(q, omega)` | `dq/dt` from the quaternion kinematic equation |
| 2 | `rigid_body.py` | `euler_eqs(omega, J, torque)` | angular acceleration from Euler's equations |
| 2 | `derivatives.py` | `state_derivative(t, z, params)` | assembles the full `dz/dt` |
| 4 | `damper.py` | `damper_eom(...)` | Part 4 damper terms (Eqs 1–5 of the handout) |

`state_derivative` is the only function the integrator calls directly; it
unpacks `z`, calls the others, and packs `dz`. Implement the small functions
first and `state_derivative` becomes a few lines of glue. Part 3 needs no new
code.

## The workflow

Each part is the same loop:

```
write one function  ->  aste586 check --part N  ->  green?  ->  next function
all green           ->  aste586 run <scenario>  ->  read the summary
                    ->  aste586 plot / view      ->  look at the motion
                    ->  aste586 grade --part N   ->  all PASS?  ->  write it up
```

### `aste586 check` — one function at a time

```
$ aste586 check --part 2

  Checking your dynamics functions (Part 2)
  ------------------------------------------------------------------
  quaternion_derivative  [kinematics.py]
    [PASS] dq/dt at the identity attitude           ok
    [FAIL] known values                             value: expected [...], got [...]
           hint: the identity case is fine but a general one is not: the
           quaternion product is in the wrong order ...
    [PASS] keeps |q| constant (q . dq/dt = 0)       ok
  ...
```

Every function gets a few *known values* and a few *physical properties*
(energy conserved, |q| preserved, angular momentum conserved, ...). A property
that fails comes with a hint about what kind of mistake produces it. Functions
you have not written yet show as `TODO`; checks that depend on them as `SKIP`.
`pytest -q` runs the same checks.

### `aste586 run` — propagate and summarise

```
$ aste586 run part2_direct_precession
ran part2_direct_precession [student] in 0.1 s -> runs/part2_direct_precession__student/
    t = 0 .. 200 s  (2000 samples)
    max | |q| - 1 |          = 2.87e-09
    |H| = 0.523569 kg m^2/s, max drift in inertial frame = 3.35e-10
    T = 0.0340585 J, spread = 4.43e-15
    nutation about body axis 2: 10.009 deg at t=0, range [10.009, 10.009] deg, ...
    mean precession rate +0.10471 rad/s, mean spin rate +0.02578 rad/s
    max |omega - analytical (axisymmetric)| = 2.92e-14 rad/s
```

If a stub is still in the way the run stops with the file and line to go to.
Any other exception in your code is reported the same way, without the
integrator's stack trace.

### `aste586 plot` and `aste586 view` — look at it

`plot` writes PNGs next to the run (the path is printed). `view` replays the
motion in PyBullet: the red arrow is the angular-momentum vector (fixed in
space), the orange arrow is `omega`, and the pastel red/green/blue lines are
body axes 1/2/3. Use `--speed 10` for the 7200 s flat-spin case. Both commands
re-propagate automatically if your code or the config changed since the run
was saved, so you never look at a stale figure.

### `aste586 grade` — the same checks the grader runs

`grade <scenario>`, `grade --part N`, or `grade --all`. Two groups of checks:

1. **Physical invariants** on *your* run: unit quaternion, angular momentum
   constant in the inertial frame, kinetic energy conserved (rigid) or
   decreasing (damped). Each failure names the function to look at.
2. **Comparison with the reference** series shipped in `grading/expected/`,
   component-wise within the tolerance in `grading/rubric.yaml`. A correct
   implementation written differently from the reference agrees to about
   1e-6; the tolerance is 1e-4.

Green on `grade --part N` means your dynamics for that part are correct.

## Rules (from the project handout)

- **Do not** write your own integrator. The harness uses `scipy.solve_ivp`.
  You only supply the right-hand side.
- **Do not** use a symbolic solver. The Part 1 `analytical_solution` must be
  the closed form you derive yourself.
- Comments count toward your grade. Explain *why*, not *what*.

## Common mistakes

- **Quaternion order.** `q = [x, y, z, w]`, scalar **last**. If the identity
  check passes but the known values fail, the product is in the wrong order
  for the body-to-inertial convention.
- **`omega` is in body coordinates.** Never rotate it before using it in
  Euler's equations or the kinematic equation.
- **Inertia pairing in Euler's equations.** Each component pairs one inertia
  difference with the *other two* angular-velocity components. If the energy
  check fails, one sign or pairing is off.
- **Packing order.** `dz` must have the same layout as `z`: use `IDX_W`,
  `IDX_Q`, `IDX_THETA_D`, `IDX_OMEGA_D` from `aste586.model`, and return a
  single flat array (`np.concatenate`), not a list of arrays.
- **Returning the wrong shape from `analytical_solution`.** It must be
  `(N, 4)` for `N` times; build it with `np.column_stack`.
- **Normalising `q` inside `state_derivative`.** Don't. The harness
  normalises after the fact; the derivative must be the true kinematic
  derivative or the norm check will flag it.
- **Damper signs.** The spring/dashpot torque appears in Eq 2 and Eq 5 with
  opposite signs (action/reaction). The momentum and energy checks in
  `aste586 check --part 4` catch this.
