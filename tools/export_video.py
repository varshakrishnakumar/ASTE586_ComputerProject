#!/usr/bin/env python3
"""Render a stored run to a sequence of PNG frames (headless PyBullet).

    python tools/export_video.py <scenario> [--backend student|reference]

Frames are written to ``runs/<scenario>__<backend>/frames/``. Stitch them
into a video with, e.g.:

    ffmpeg -framerate 30 -i frames/frame_%05d.png run.mp4
"""

from __future__ import annotations

import argparse

import numpy as np

from aste586.io import load_run, run_dir
from aste586.sim import run as run_scenario


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario")
    ap.add_argument("--backend", default="reference",
                    choices=["student", "reference"])
    ap.add_argument("--stride", type=int, default=10,
                    help="render every Nth time sample")
    args = ap.parse_args()

    try:
        artifact = load_run(args.scenario, args.backend)
    except FileNotFoundError:
        artifact = run_scenario(args.scenario, backend=args.backend)

    import pybullet as p

    p.connect(p.DIRECT)
    from aste586.viz.viewer import body_geometry, make_body
    body = make_body(p, body_geometry(artifact))

    frames_dir = run_dir(args.scenario, args.backend) / "frames"
    frames_dir.mkdir(exist_ok=True)
    view = p.computeViewMatrixFromYawPitchRoll([0, 0, 0], 3.0, 45, -30, 0, 2)
    proj = p.computeProjectionMatrixFOV(60, 1.0, 0.1, 100)

    q = artifact["q"]
    count = 0
    for i in range(0, len(q), args.stride):
        p.resetBasePositionAndOrientation(body, [0, 0, 0], q[i])
        _, _, rgb, _, _ = p.getCameraImage(640, 640, view, proj)
        img = np.reshape(rgb, (640, 640, 4))[:, :, :3].astype(np.uint8)
        _save_png(frames_dir / f"frame_{count:05d}.png", img)
        count += 1

    p.disconnect()
    print(f"wrote {count} frames to {frames_dir}")
    return 0


def _save_png(path, img) -> None:
    """Write an RGB array to PNG via matplotlib (already a dependency)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.image as mpimg

    mpimg.imsave(path, img)


if __name__ == "__main__":
    raise SystemExit(main())
