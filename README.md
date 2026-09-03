# ASTE 586 — Spacecraft Attitude Dynamics Computer Project

A simulation toolkit for the ASTE 586 attitude-dynamics project. You simulate
the torque-free (and, later, damped) rotational motion of a rigid spacecraft,
visualize it in 3-D, and verify it against analytical solutions and physical
invariants.

## What you implement

You do **not** write an integrator, a file parser, or a plotter — those are
provided. You implement the **equations of motion**: six small pure Python
functions in `src/aste586/dynamics/` that, given the current state, return its
time derivative. The provided harness does everything else.

Start with [`docs/student-guide.md`](docs/student-guide.md). The interface you
implement against is documented in [`docs/conventions.md`](docs/conventions.md).

## Install

```bash
conda env create -f environment.yml
conda activate aste586
python -s -m pip install -e .
```

The `-s` flag prevents Python from treating packages installed for a
different Python version (e.g. a system Python 3.9) as already satisfying
requirements.  Without it, macOS machines with a pre-existing user-level numpy
or matplotlib can silently end up with ABI-mismatched C extensions and obscure
import errors.

PyBullet (used by `aste586 view`) is installed as a conda-forge binary by
the environment above — no compilation step on any platform. That is why the
conda environment is the supported route: a plain `pip install` tries to
build PyBullet from source on Apple Silicon and fails.

Check that the install worked:

```bash
aste586 list        # the nine scenarios, one line each
aste586 check       # every function you must write, all still TODO
pytest -q           # harness tests pass; your (unwritten) functions are skipped
```

If `aste586 <verb>` ever fails to start (rare; an editable-install quirk),
`python -m aste586.cli <verb> ...` is the equivalent fallback.

## The loop you will repeat

```bash
aste586 check --part 2                  # unit-check each function as you write it
aste586 run   part2_direct_precession   # propagate; prints a physics summary
aste586 plot  part2_direct_precession   # report figures -> runs/<scenario>__student/
aste586 view  part2_direct_precession   # 3-D replay (add --speed 10 for long runs)
aste586 grade --part 2                  # invariants + comparison with the reference
```

Everything is driven by **named scenarios** in `configs/`. You never create,
name, or open a data file. `plot`, `view`, and `grade` re-propagate
automatically when your code or the scenario has changed since the last run.

See [`docs/architecture.md`](docs/architecture.md) for how the pieces fit
together and [`docs/parts/`](docs/parts/) for the four assignment parts,
including what a correct result looks like for each scenario.
