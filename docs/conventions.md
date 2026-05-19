# Conventions — the single source of truth

Everything in this project obeys the conventions below. If your code and the
harness disagree, it is almost always because a convention was broken. When in
doubt, this file wins.

## Frames

| Symbol | Name        | Notes |
|--------|-------------|-------|
| `F`    | inertial    | "world" frame; fixed. PyBullet's world frame. |
| `C`    | body-fixed  | fixed to the spacecraft bus `B`, aligned with the principal axes. |

The moments of inertia are **principal** moments, so the inertia matrix `J` is
diagonal: `J = diag(I1, I2, I3)`.

## Quaternion

The attitude quaternion `q` has **scalar-last** component order:

```
q = [x, y, z, w]          # w is the scalar part
```

This matches PyBullet's quaternion order, so no reordering happens at the
viewer boundary. The Euler–Rodrigues parameters from the class notes map
directly: `e1,e2,e3 -> x,y,z` and `e4 -> w`.

`q` rotates **body-frame vectors into the inertial frame**:

```
v_F = R(q) @ v_C          # R(q) is the body->inertial rotation matrix C^FC
```

`q` and `-q` represent the same attitude. The harness enforces sign continuity
for plotting and viewing; your dynamics code does not need to.

## State vector

The integrator works with a single 1-D state vector `z`.

**Rigid body (Parts 2–3)** — length 7:

```
z = [ w1, w2, w3,  x, y, z, w ]
      \__omega__/  \__quat__/
```

**Damped body (Part 4)** — length 9, appends the damper wheel state:

```
z = [ w1, w2, w3,  x, y, z, w,  Theta_d, Omega_d ]
```

`omega` is the angular velocity of the body relative to the inertial frame,
**expressed in body coordinates** (rad/s). `Theta_d` is the damper-wheel angle
(rad); `Omega_d` is its rate (rad/s).

Index constants live in `aste586.model` (`IDX_W`, `IDX_Q`, `IDX_THETA_D`,
`IDX_OMEGA_D`) — use them instead of hard-coding slices.

**Part 1** is a warm-up with its own 4-vector state `x` and its own RHS; it
does not use the layout above.

## Euler angles

A **3-1-3** sequence `(psi, theta, phi)` = (precession, nutation, spin),
extracted from the body→inertial rotation matrix. The reference axis is
selectable (Parts 2–3 ask you to compare choices); the default is body axis 3.

## The interface you implement

The integrator (provided) calls your RHS:

```
state_derivative(t, z, params) -> dz
```

`params` is an `aste586.model.Params` dataclass:

| Field   | Meaning |
|---------|---------|
| `J`     | 3×3 principal inertia matrix (diagonal) |
| `model` | `"rigid"` or `"damped"` |
| `torque`| external torque in body coords (zero for this project) |
| `Id`    | damper-wheel inertia (damped model only) |
| `D`     | damper damping coefficient, N·m/(rad/s) |
| `K`     | damper spring coefficient, N·m/rad |

Your RHS functions are **pure**: no file I/O, no printing, no global state.
Given the same inputs they return the same outputs.

## Units

SI throughout: seconds, radians, rad/s, kg·m², N·m. Angles are converted to
degrees only at the plotting/HUD boundary.
