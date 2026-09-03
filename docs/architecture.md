# Architecture

## The one idea

The project is a fixed **harness** wrapped around one swappable **backend**.
The backend is the equations of motion. Students write one backend; a hidden
reference is the other. Grading compares them.

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
    +--> summary  (aste586 run)
    +--> viewer   (PyBullet)
    +--> plots    (matplotlib)
    +--> grading  (invariants + diff vs grading/expected/)
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
(all time series) and `meta.json` (config, backend, tolerances, a hash of the
backend source and of the config). `view`, `plot`, and `grade` resolve that
location themselves and **re-run automatically when either hash is stale**, so
a student never looks at a figure produced by old code. The string `csv`
appears in no command and no student-facing path. `aste586 export` can emit a
CSV for external inspection, but it is an advanced convenience and an input to
nothing.

## Directory map

| Path | Role |
|------|------|
| `src/aste586/model.py`, `conventions.py` | shared, provided primitives |
| `src/aste586/dynamics/` | **student backend** (stubs) |
| `reference/aste586_reference/` | **hidden reference backend** |
| `src/aste586/checks.py` | per-function checks (`aste586 check`) — known values + physical properties |
| `src/aste586/grading.py` | invariants + comparison with expected series (`aste586 grade`) |
| `src/aste586/report.py` | the PASS/FAIL/TODO/SKIP report both of the above print |
| `src/aste586/summary.py` | the physics summary `aste586 run` prints |
| `src/aste586/analysis/` | invariants, Euler angles, geometry, analytical solutions — provided |
| `src/aste586/sim/` | integrator, scenario builder, runner — provided |
| `src/aste586/io/` | YAML config loader, run store (.npz) — provided |
| `src/aste586/viz/` | PyBullet viewer + overlays — provided |
| `src/aste586/plots/` | report figures — provided |
| `src/aste586/cli.py` | the `aste586` command |
| `configs/` | one YAML scenario per assignment case |
| `grading/rubric.yaml` | tolerances |
| `grading/expected/` | reference time series, one `.npz` per scenario, shipped to students |
| `tools/make_expected.py` | regenerates `grading/expected/` from the reference backend |
| `tools/make_student_release.py` | regenerates expected data, then strips `reference/` to produce the student zip |

## The checking and grading path

`aste586 check` never integrates anything. It calls each student function
with fixed inputs and compares against values stored in `checks.py`, plus
physical properties (energy and momentum conservation, quaternion norm
preservation, action/reaction in the damper) whose failures map to specific
kinds of mistake. The reference backend must pass every check
(`tests/test_checks.py` enforces this), and a deliberately wrong backend must
fail.

`aste586 grade <scenario>` runs the scenario on the **student** backend, then:

1. checks the student run against physical invariants (|q|≈1, angular
   momentum constant in `F`, energy behaviour) — diagnostics with hints;
2. diffs it against the reference series in `grading/expected/<scenario>.npz`,
   component-wise, against per-case tolerances in `grading/rubric.yaml`;
3. prints a pass/fail report and the physics summary.

The expected files are produced from the reference backend by
`tools/make_expected.py` and carry the reference's source hash;
`tests/test_grading_expected.py` fails in the instructor checkout if they are
stale. If an expected file is missing and the reference backend *is*
installed, `grade` falls back to running the reference.

## Instructor workflow

```bash
pytest -q                                   # harness + reference + checks
python tools/make_expected.py               # after editing reference/ or configs/
python tools/make_student_release.py        # regenerates expected, strips reference/, zips
```

`ci/github-workflows.yaml` does the same and additionally installs the
generated student release in a clean environment to prove `check` and
`grade` work without the reference.
