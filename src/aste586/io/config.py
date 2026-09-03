"""Scenario configuration loading — provided.

Scenarios are named YAML files in ``configs/``. Students and the CLI refer to
a scenario by **name** (e.g. ``part2_direct_precession``), never by path.
"""

from __future__ import annotations

from pathlib import Path

import yaml


def _repo_root() -> Path:
    """Locate the repository root by walking up to the ``configs/`` folder."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "configs").is_dir():
            return parent
    raise FileNotFoundError("could not locate the repo root (no configs/ dir)")


def config_path(name: str) -> Path:
    """Absolute path to the YAML file for scenario ``name``."""
    name = name.removesuffix(".yaml")  # tolerate a stray extension
    p = _repo_root() / "configs" / f"{name}.yaml"
    if not p.is_file():
        raise FileNotFoundError(
            f"no scenario named {name!r}; try `aste586 list`"
        )
    return p


def list_configs() -> list[str]:
    """Sorted names of all available scenarios."""
    cfg_dir = _repo_root() / "configs"
    return sorted(p.stem for p in cfg_dir.glob("*.yaml"))


def describe_configs() -> list[dict]:
    """One summary row per scenario: name, part, model, tf, description."""
    rows = []
    for name in list_configs():
        cfg = load_config(name)
        rows.append({
            "name": name,
            "part": int(cfg["part"]),
            "model": cfg["model"],
            "tf": float(cfg["tf"]),
            "description": cfg.get("description", ""),
        })
    return rows


_REQUIRED = {"name", "part", "model", "tf", "n_points"}
_MODELS = {"linear", "rigid", "damped"}


def load_config(name: str) -> dict:
    """Load and lightly validate the scenario named ``name``.

    Returns the parsed YAML as a plain dict. Raises ``ValueError`` on an
    obviously malformed scenario so failures point at the config, not at a
    downstream NumPy traceback.
    """
    with open(config_path(name)) as fh:
        cfg = yaml.safe_load(fh)
    if not isinstance(cfg, dict):
        raise ValueError(f"scenario {name!r} is not a YAML mapping")

    missing = _REQUIRED - cfg.keys()
    if missing:
        raise ValueError(f"scenario {name!r} missing keys: {sorted(missing)}")
    if cfg["model"] not in _MODELS:
        raise ValueError(
            f"scenario {name!r}: model must be one of {sorted(_MODELS)}"
        )
    if cfg["name"] != name:
        raise ValueError(
            f"scenario file {name!r} has mismatched internal name "
            f"{cfg['name']!r}"
        )
    return cfg
