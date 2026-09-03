"""The ``aste586`` command-line interface -- provided.

Every verb takes a **scenario name** (see ``aste586 list``); none takes a file
path. Run artifacts are addressed by name and resolved internally.

    aste586 list                      what scenarios exist, and for which part
    aste586 check  [--part N]         unit-check each function you implemented
    aste586 run    <scenario>         propagate and print a physics summary
    aste586 plot   <scenario>         write the report figures
    aste586 view   <scenario>         3-D replay (needs pybullet)
    aste586 grade  <scenario>|--part N|--all
"""

from __future__ import annotations

import argparse
import sys
import time

from .io import describe_configs, load_run
from .report import locate_student_frame
from .sim import backend_hash, load_backend, run as run_scenario
from .sim.runner import config_hash


def _cmd_list(args: argparse.Namespace) -> int:
    rows = describe_configs()
    print(f"  {'scenario':28s} {'part':>4s}  {'model':7s} {'tf (s)':>8s}  description")
    print("  " + "-" * 90)
    for r in rows:
        print(f"  {r['name']:28s} {r['part']:>4d}  {r['model']:7s} {r['tf']:>8g}  {r['description']}")
    print("\n  run one with:  aste586 run <scenario>")
    return 0


def _print_summary(artifact) -> None:
    from .summary import summarize
    for line in summarize(artifact):
        print(f"    {line}")


def _cmd_run(args: argparse.Namespace) -> int:
    t0 = time.perf_counter()
    artifact = run_scenario(args.scenario, backend=args.backend)
    print(f"ran {args.scenario} [{args.backend}] in {time.perf_counter() - t0:.1f} s "
          f"-> runs/{args.scenario}__{args.backend}/")
    _print_summary(artifact)
    return 0


def _get_or_run(scenario: str, backend: str):
    """Load a stored run, re-propagating if it is missing or **stale** (the
    backend source or the scenario config changed since it was saved)."""
    try:
        artifact = load_run(scenario, backend)
    except FileNotFoundError:
        return run_scenario(scenario, backend=backend)
    meta = artifact.meta
    if meta.get("backend_hash") != backend_hash(load_backend(backend)):
        print(f"note: {backend} code changed since this run was saved; re-running {scenario}")
        return run_scenario(scenario, backend=backend)
    if meta.get("config_hash") != config_hash(scenario):
        print(f"note: configs/{scenario}.yaml changed since this run was saved; re-running")
        return run_scenario(scenario, backend=backend)
    return artifact


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


def _cmd_check(args: argparse.Namespace) -> int:
    from .checks import run_checks
    from .report import print_report
    title = "Checking your dynamics functions" + (f" (Part {args.part})" if args.part else "")
    ok = print_report(title, run_checks(part=args.part))
    if ok:
        print("  next: aste586 grade --part N   (or `aste586 run <scenario>`)\n")
    return 0 if ok else 1


def _cmd_grade(args: argparse.Namespace) -> int:
    from .grading import grade, grade_many, scenarios_for_part
    from .io import list_configs
    if args.scenario:
        return 0 if grade(args.scenario) else 1
    if args.part:
        names = scenarios_for_part(args.part)
    elif args.all:
        names = list_configs()
    else:
        print("error: give a scenario name, --part N, or --all", file=sys.stderr)
        return 2
    return 0 if grade_many(names) else 1


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
        cols = ["w1", "w2", "w3", "qx", "qy", "qz", "qw", "psi", "theta", "phi"]
        import numpy as np
        data = np.column_stack([artifact["omega"], artifact["q"],
                                artifact["psi"], artifact["theta"], artifact["phi"]])
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

    def add_scenario(sp, backend=True, required=True):
        sp.add_argument("scenario", nargs=None if required else "?",
                        help="scenario name (see `aste586 list`)")
        if backend:
            sp.add_argument("--backend", choices=["student", "reference"],
                            default="student", help="dynamics backend")

    sub.add_parser("list", help="list scenarios").set_defaults(func=_cmd_list)

    sp = sub.add_parser("check", help="unit-check each function you implemented")
    sp.add_argument("--part", type=int, choices=[1, 2, 3, 4],
                    help="only the functions needed for this part")
    sp.set_defaults(func=_cmd_check)

    sp = sub.add_parser("run", help="propagate a scenario and print a summary")
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

    sp = sub.add_parser("grade", help="check your code against the reference")
    add_scenario(sp, backend=False, required=False)
    sp.add_argument("--part", type=int, choices=[1, 2, 3, 4],
                    help="grade every scenario of this part")
    sp.add_argument("--all", action="store_true", help="grade every scenario")
    sp.set_defaults(func=_cmd_grade)

    sp = sub.add_parser("export", help="(advanced) dump a run to CSV")
    add_scenario(sp)
    sp.set_defaults(func=_cmd_export)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except NotImplementedError as exc:
        print(f"error: {exc}", file=sys.stderr)
        loc = locate_student_frame(exc)
        if loc:
            print(f"  -> {loc}", file=sys.stderr)
        print("  `aste586 check` lists every function that is still a stub.", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        loc = locate_student_frame(exc)
        if loc:
            print(f"error in your code at {loc}", file=sys.stderr)
            print(f"  {type(exc).__name__}: {exc}", file=sys.stderr)
            return 1
        if isinstance(exc, (FileNotFoundError, ValueError, RuntimeError)):
            print(f"error: {exc}", file=sys.stderr)
            return 1
        raise  # a harness problem: show the full traceback


if __name__ == "__main__":
    sys.exit(main())
