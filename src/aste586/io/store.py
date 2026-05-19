"""Run-artifact store — provided.

A "run" is the output of propagating one scenario with one backend. It lives
in ``runs/<scenario>__<backend>/`` as a single ``result.npz`` (all time
series) plus ``meta.json``. Students never open these files; the CLI verbs
``view``/``plot``/``grade`` resolve and read them.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .config import _repo_root


def run_dir(scenario: str, backend: str) -> Path:
    """Directory holding the run of ``scenario`` under ``backend``."""
    return _repo_root() / "runs" / f"{scenario}__{backend}"


@dataclass
class RunArtifact:
    """An in-memory run: named time series plus metadata."""

    scenario: str
    backend: str
    series: dict[str, np.ndarray]   # e.g. {"time", "omega", "q", "H_F", "T"}
    meta: dict

    def __getitem__(self, key: str) -> np.ndarray:
        return self.series[key]

    def __contains__(self, key: str) -> bool:
        return key in self.series


def save_run(artifact: RunArtifact) -> Path:
    """Write ``artifact`` to its run directory; return that directory."""
    d = run_dir(artifact.scenario, artifact.backend)
    d.mkdir(parents=True, exist_ok=True)
    np.savez(d / "result.npz", **artifact.series)
    with open(d / "meta.json", "w") as fh:
        json.dump(artifact.meta, fh, indent=2, sort_keys=True)
    return d


def load_run(scenario: str, backend: str) -> RunArtifact:
    """Read a previously saved run. Raises ``FileNotFoundError`` if absent."""
    d = run_dir(scenario, backend)
    npz = d / "result.npz"
    if not npz.is_file():
        raise FileNotFoundError(
            f"no run for {scenario!r} backend={backend!r}; "
            f"run `aste586 run {scenario} --backend {backend}` first"
        )
    with np.load(npz) as data:
        series = {k: data[k] for k in data.files}
    meta = json.loads((d / "meta.json").read_text())
    return RunArtifact(scenario, backend, series, meta)
