"""Debug-line overlays for the PyBullet viewer -- provided.

A thin bookkeeping layer so the viewer can redraw labelled vectors each frame
without leaking debug-item ids.
"""

from __future__ import annotations

import numpy as np


class Overlay:
    """Manages a set of named debug lines, replacing them in place each frame."""

    def __init__(self, pybullet_module):
        self._p = pybullet_module
        self._lines: dict[str, int] = {}
        self._text: int | None = None

    def vector(self, name: str, origin, vec, color, scale: float = 1.0) -> None:
        """Draw/refresh an arrow ``name`` from ``origin`` along ``vec``."""
        origin = np.asarray(origin, float)
        end = origin + scale * np.asarray(vec, float)
        kw = dict(lineColorRGB=color, lineWidth=2.0)
        if name in self._lines:
            kw["replaceItemUniqueId"] = self._lines[name]
        self._lines[name] = self._p.addUserDebugLine(origin, end, **kw)

    def hud(self, text: str) -> None:
        """Draw/refresh the heads-up text block."""
        kw = dict(textPosition=[0, 0, 1.4], textColorRGB=[1, 1, 1], textSize=1.2)
        if self._text is not None:
            kw["replaceItemUniqueId"] = self._text
        self._text = self._p.addUserDebugText(text, **kw)
