# Part 3 — Torque-free cases

No new dynamics code — Part 3 reuses the Part 2 backend. It is an exploration
of cases. Run them, produce the figures, and write the discussion.

```bash
aste586 grade --part 3          # confirms the Part 2 code handles all three
aste586 plot  part3_dish_earthline
aste586 view  part3_middle_axis
```

## Scenarios

- `part3_dish_earthline` — a 39 kg cylinder spinning at 45 RPM with an antenna
  offset 5° from the symmetry axis. The harness computes the **off-nadir
  angle** (antenna axis vs. the initial Earth line). Predict the bounds, then
  compare.
- `part3_nonsymmetric` — a non-axisymmetric body; observe which body axis the
  angular velocity encircles (the polhode).
- `part3_middle_axis` — the angular velocity started near the intermediate
  axis. Observe the instability.

## What the harness reports

`omega(t)`, the polhode (3-D `omega` plot, equal axes), nutation and Euler
angles for a selectable reference axis, and — for the dish scenario — the
off-nadir angle vs. time.

The reference axis used for Euler-angle extraction is set per scenario in the
config (`analysis.reference_axis`); change it to compare choices.

## What a correct result looks like

| scenario | nutation about the reference axis | other |
|----------|-----------------------------------|-------|
| `part3_dish_earthline` | 4.74° constant (axis 3) | off-nadir angle oscillates between 0 and ≈ 10.0°; ψ̇ ≈ +4.97 rad/s |
| `part3_nonsymmetric` | 7.1°–8.4° (axis 3), periodic | closed polhode around body axis 3 (the major axis); T = 49.5 J |
| `part3_middle_axis` | swings from ≈ 1° to ≈ 179° (axis 2) | `w2` periodically reverses sign; T = 32.0 J stays constant throughout |

Why is the off-nadir bound about twice the 5° offset? Why does the
intermediate-axis case still conserve energy and momentum while tumbling?
Those are the discussion questions.
