"""The ``aste586`` command-line interface -- provided.

Every verb takes a **scenario name** (see ``aste586 list``); none takes a file
path. Run artifacts are addressed by name and resolved internally.
"""

from __future__ import annotations

import argparse
import sys

from .io import list_configs, load_run
from .sim import run as run_scenario


def _cmd_list(args: argparse.Namespace) -> int:
    print("Available scenarios:")
    for name in list_configs():
        print(f"  {name}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    run_scenario(args.scenario, backend=args.backend)
    print(f"ran {args.scenario} [{args.backend}] -> runs/"
          f"{args.scenario}__{args.backend}/")
    return 0


def _get_or_run(scenario: str, backend: str):
    """Load a stored run, propagating it first if it does not exist yet."""
    try:
        return load_run(scenario, backend)
    except FileNotFoundError:
        return run_scenario(scenario, backend=backend)


def _cmd_plot(args: argparse.Namespace) -> int:
    from .plots import plot_run
    artifact = _get_or_run(args.scenario, args.backend)
    paths = plot_run(artifact)
    print(f"wrote {len(paths)} figure(s):")
    for p in paths:
        print(f"  {p}")
    return 0


def _cmd_view(args: argparse.Namespace) -> int:
    from .viz import view
    artifact = _get_or_run(args.scenario, args.backend)
    view(artifact, speed=args.speed)
    return 0


def _cmd_grade(args: argparse.Namespace) -> int:
    from .grading import grade
    return 0 if grade(args.scenario) else 1


def _cmd_export(args: argparse.Namespace) -> int:
    """Advanced: dump a run to CSV for external inspection. Not used by any
    other command -- the normal workflow never touches a data file."""
    import csv

    from .io import run_dir
    artifact = _get_or_run(args.scenario, args.backend)
    out = run_dir(args.scenario, args.backend) / "export.csv"
    t = artifact["time"]
    if artifact.meta["model"] == "linear":
        cols, data = ["x1", "x2", "x3", "x4"], artifact["x"]
    else:
        cols, data = ["qx", "qy", "qz", "qw"], artifact["q"]
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["time", *cols])
        for i in range(len(t)):
            w.writerow([t[i], *data[i]])
    print(f"wrote {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="aste586", description="ASTE 586 attitude-dynamics toolkit")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_scenario(sp, backend=True):
        sp.add_argument("scenario", help="scenario name (see `aste586 list`)")
        if backend:
            sp.add_argument("--backend", choices=["student", "reference"],
                            default="student", help="dynamics backend")

    sub.add_parser("list", help="list scenarios").set_defaults(func=_cmd_list)

    sp = sub.add_parser("run", help="propagate a scenario")
    add_scenario(sp)
    sp.set_defaults(func=_cmd_run)

    sp = sub.add_parser("plot", help="render the report figures")
    add_scenario(sp)
    sp.set_defaults(func=_cmd_plot)

    sp = sub.add_parser("view", help="3-D PyBullet replay")
    add_scenario(sp)
    sp.add_argument("--speed", type=float, default=1.0,
                    help="playback rate (1.0 = real time)")
    sp.set_defaults(func=_cmd_view)

    sp = sub.add_parser("grade", help="check student code vs the reference")
    add_scenario(sp, backend=False)
    sp.set_defaults(func=_cmd_grade)

    sp = sub.add_parser("export", help="(advanced) dump a run to CSV")
    add_scenario(sp)
    sp.set_defaults(func=_cmd_export)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (FileNotFoundError, ValueError, RuntimeError, NotImplementedError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
