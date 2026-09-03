# Control flow of one `aste586` command

Every verb resolves a scenario by name, makes sure an up-to-date run exists,
then does one thing with it.

```mermaid
flowchart TD
  CLI["aste586 &lt;verb&gt; &lt;scenario&gt;"] --> V{verb}

  V -->|list| L["print configs/*.yaml summaries"]
  V -->|check| CK["checks.run_checks()<br/>known values + physical properties<br/>per student function"] --> RPT["report: PASS / FAIL / TODO / SKIP"]

  V -->|run| RUN
  V -->|plot / view / export| GET{"runs/&lt;scenario&gt;__&lt;backend&gt;/ exists<br/>and backend hash + config hash match?"}
  GET -->|no / stale| RUN
  GET -->|yes| ART

  subgraph RUN["sim.run(scenario, backend)"]
    C["io.load_config"] --> S["sim.build_scenario<br/>z0, Params, t_eval<br/>(H aligned with inertial z)"]
    S --> I["sim.integrate (scipy DOP853)<br/>calls backend.state_derivative(t, z, params)"]
    I --> A["analysis: |q|, H_F, T, 3-1-3 Euler angles,<br/>analytical omega, off-nadir"]
    A --> SAVE["io.save_run -> result.npz + meta.json"]
  end
  RUN --> ART["RunArtifact"]

  ART -->|run| SUM["summary.summarize -> terminal"]
  ART -->|plot| P["plots.plot_run -> PNGs"]
  ART -->|view| W["viz.view -> PyBullet replay"]

  V -->|grade| G1["sim.run(scenario, 'student')"]
  G1 --> G2["invariant checks on the student run"]
  G2 --> G3["load grading/expected/&lt;scenario&gt;.npz<br/>(or run the reference if installed)"]
  G3 --> G4["component-wise diff vs rubric tolerances"] --> RPT
```

The student backend is called from exactly one place: the integrator's
right-hand side inside `sim.run`. Nothing else in the harness imports
`aste586.dynamics` except `aste586 check`, which calls the functions directly
with fixed inputs.
