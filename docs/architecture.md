# Architecture

## The one idea

The project is a fixed **harness** wrapped around one swappable **backend**.
The backend is the equations of motion. Students write one backend; a hidden
reference is the other. Grading runs both and compares.

```
config (YAML)
    |
    v
scenario  -->  initial state z0, Params
    |
    v
integrator (scipy.solve_ivp)  --calls-->  BACKEND.state_derivative(t, z, params)
    |                                       ^
    v                                       |
run artifact (.npz + meta.json)        student  OR  reference
    |
    +--> viewer (PyBullet)
    +--> plots (matplotlib)
    +--> grading (diff vs reference + invariant checks)
```

## Backends

A backend is a Python module exposing a fixed set of callables (`part1`,
`rigid_body`, `kinematics`, `damper`, `derivatives`, re-exported from its
package `__init__`). Two exist:

- **student** — `src/aste586/dynamics/`. Committed as documented stubs that
  raise `NotImplementedError`. This is what students fill in.
- **reference** — `reference/aste586_reference/`. A complete implementation of
  the identical interface. Withheld from the student release.

`aste586.sim.runner.load_backend(name)` returns the right module. The two
backends share provided code (`aste586.model`, `aste586.conventions`) so they
cannot drift apart on conventions.

## Why no CSV / no file paths

Students implement *functions*, not file formats. They never produce a data
file. A "run" is addressed by **scenario name**, not a path:

```
aste586 run part2_direct_precession --backend student
```

writes `runs/part2_direct_precession__student/` containing `result.npz`
(all time series) and `meta.json` (config, backend, tolerances, code hash).
`view`, `plot`, and `grade` resolve that location themselves. The string
`csv` appears in no command and no student-facing path. `aste586 export` can
emit a CSV for external inspection, but it is an advanced convenience and an
input to nothing.

## Directory map

| Path | Role |
|------|------|
| `src/aste586/model.py`, `conventions.py` | shared, provided primitives |
| `src/aste586/dynamics/` | **student backend** (stubs) |
| `reference/aste586_reference/` | **hidden reference backend** |
| `src/aste586/analysis/` | invariants, Euler angles, geometry, analytical solutions — provided |
| `src/aste586/sim/` | integrator, scenario builder, runner — provided |
| `src/aste586/io/` | YAML config loader, run store (.npz) — provided |
| `src/aste586/viz/` | PyBullet viewer + overlays — provided |
| `src/aste586/plots/` | report figures — provided |
| `src/aste586/cli.py` | the `aste586` command |
| `configs/` | one YAML scenario per assignment case |
| `grading/` | rubric + grader |
| `tools/make_student_release.py` | strips `reference/` to produce the student zip |

## The grading path

`aste586 grade <scenario>` runs the scenario on both backends, then:

1. checks the **reference** run against physical invariants (|q|≈1, angular
   momentum constant in `F`, energy behavior) — this validates the rubric;
2. diffs the **student** run against the reference, component-wise, against
   per-case tolerances in `grading/rubric.yaml`;
3. prints a pass/fail report.

Students can self-check the same way; `grading/expected/` ships precomputed
reference series so grading works even without the hidden backend installed.
