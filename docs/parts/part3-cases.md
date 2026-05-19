# Part 3 — Torque-free cases

No new dynamics code — Part 3 reuses the Part 2 backend. It is an exploration
of cases. Run them, produce the figures, and write the discussion.

## Scenarios

- `part3_dish_earthline` — a spinning satellite with an antenna offset 5° from
  the symmetry axis. The harness computes the **off-nadir angle** (antenna axis
  vs. the initial Earth line). Predict the bounds, then compare.
- `part3_nonsymmetric` — a non-axisymmetric body; observe which body axis the
  angular velocity encircles (the polhode).
- `part3_middle_axis` — the angular velocity started near the intermediate
  axis. Observe the instability.

## What the harness reports

`omega(t)`, the polhode (3-D `omega` plot), Euler angles for a selectable
reference axis, and — for the dish scenario — the off-nadir angle vs. time.

The reference axis used for Euler-angle extraction is set per scenario in the
config (`analysis.reference_axis`); change it to compare choices.
