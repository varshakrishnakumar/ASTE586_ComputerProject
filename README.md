# ASTE 586 — Spacecraft Attitude Dynamics Computer Project

A simulation toolkit for the ASTE 586 attitude-dynamics project. You simulate
the torque-free (and, later, damped) rotational motion of a rigid spacecraft,
visualize it in 3-D, and verify it against analytical solutions and physical
invariants.

## What you implement

You do **not** write an integrator, a file parser, or a plotter — those are
provided. You implement the **equations of motion**: a handful of pure Python
functions in `src/aste586/dynamics/` that, given the current state, return its
time derivative. The provided harness does everything else.

The interface you implement against is documented in
[`docs/conventions.md`](docs/conventions.md). Start with
[`docs/student-guide.md`](docs/student-guide.md).

## Install

```bash
conda env create -f environment.yml
conda activate aste586
pip install -e .
```

## Use

Everything is driven by **named scenarios** in `configs/`. You never create,
name, or open a data file.

```bash
aste586 list                          # show available scenarios
aste586 run   part2_direct_precession  # propagate the dynamics
aste586 view  part2_direct_precession  # 3-D PyBullet replay
aste586 plot  part2_direct_precession  # the report figures
aste586 grade part2_direct_precession  # check your code against the reference
```

See [`docs/architecture.md`](docs/architecture.md) for how the pieces fit
together and [`docs/parts/`](docs/parts/) for the four assignment parts.
