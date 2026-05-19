# Part 1 — Initial Value Problem (tool setup)

A warm-up: confirm you can integrate an ODE accurately and check it against an
analytical solution.

## Problem

```
xdot = A x ,   A = [[ 0,   2,    0,    0  ],
                    [-2,   0,    0,    0  ],
                    [ 0,   0,    0,  200  ],
                    [ 0,   0, -200,    0  ]]
x(0) = [1, 0, 1, 0]
```

Scenario: `part1_ivp`.

## What to implement

`dynamics/part1.py`:

- `linear_ivp_rhs(t, x, A)` — return `A @ x`.
- `analytical_solution(t)` — derive the closed form **by hand** (not with a
  symbolic solver) and return `x(t)`. The system splits into two independent
  rotations; expect sinusoids at 2 rad/s and 200 rad/s.

## What the harness reports

`aste586 plot part1_ivp` produces:

- each component, numerical vs analytical;
- the max component-wise error vs time (should reach ≈ 1e-3 or better at
  t = 10 — report your tolerances);
- `x1^2 + x2^2 + x3^2 + x4^2 - 2` vs time, which should stay near zero.
