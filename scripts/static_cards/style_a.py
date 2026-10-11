"""Small UID-neutral visual primitives extracted from the selected Style A card.

This module contains no mathematical facts, UID discovery, or publication code.
"""

from __future__ import annotations

from scripts.static_cards.canvas import CardCanvas, HEIGHT, WIDTH

import matplotlib.pyplot as plt
import numpy as np


class Palette:
    paper = "#F1F8FF"
    header_start = "#0869C9"
    header_end = "#54B5F4"
    ink = "#15375F"
    blue = "#2671D5"
    teal = "#12A28F"
    amber = "#DD8C17"
    formula_bg = "#FFF8DE"
    formula_edge = "#F1CE6D"
    diagram_edge = "#B9DBF3"
    green_bg = "#E9FAF0"
    green_edge = "#8BDDB2"
    memory_bg = "#DFF4EC"
    memory_edge = "#AFE0CA"


P = Palette()


class StyleACanvas(CardCanvas):
    """Selected A-002's canvas, header proportions, panels, and text audit."""

    def __init__(self, uid: str, number: str, kind: str, title: str):
        self.uid, self.number = uid, number
        self.layout_report = []
        self.text_coverage_report = []
        self.label_layout = None
        plt.rcParams.update({"svg.fonttype": "none", "svg.hashsalt": "c043-style-a",
                             "mathtext.fontset": "dejavusans", "savefig.pad_inches": 0})
        self.fig = plt.figure(figsize=(10.8, 14.4), dpi=100, facecolor=P.paper)
        self.ax = self.fig.add_axes((0, 0, 1, 1))
        self.ax.set_xlim(0, WIDTH)
        self.ax.set_ylim(HEIGHT, 0)
        self.ax.axis("off")
        self._gradient(0, 244, P.header_start, P.header_end)
        self.label(f"知树   /   {uid}  ·  {number} {kind}", 68, 76, 26, "#FFFFFF", bold=True)
        self.label(title, 68, 164, 51, "#FFFFFF", bold=True)

    def _gradient(self, y0, y1, first, last):
        a = np.array([int(first[i:i+2], 16) for i in (1, 3, 5)]) / 255
        b = np.array([int(last[i:i+2], 16) for i in (1, 3, 5)]) / 255
        t = np.linspace(0, 1, 256)[:, None]
        rgb = a[None, :] * (1-t) + b[None, :] * t
        self.ax.imshow(rgb[:, None, :], extent=(0, WIDTH, y1, y0), aspect="auto", zorder=0)

    def panel(self, y, height, *, kind="white", x=62, width=956):
        fill, edge = {
            "white": ("#FFFFFF", P.diagram_edge),
            "formula": (P.formula_bg, P.formula_edge),
            "green": (P.green_bg, P.green_edge),
            "blue": ("#EAF5FF", "#B9DBF3"),
        }[kind]
        self.box(x, y, width, height, fill, edge=edge, radius=26)

    def memory(self, text):
        self.box(62, 1271, 956, 65, P.memory_bg, edge=P.memory_edge, radius=18)
        self.label(text, 90, 1314, 22, "#155C49", bold=True)

    def audit_text(self):
        self.fig.canvas.draw()
        renderer = self.fig.canvas.get_renderer()
        items = [(t, t.get_window_extent(renderer)) for t in self.ax.texts if t.get_visible()]
        errors = []
        for i, (a, ab) in enumerate(items):
            if min(ab.x0, ab.y0) < 20 or ab.x1 > WIDTH-20 or ab.y1 > HEIGHT-20:
                errors.append(f"bounds: {a.get_text()}")
            for b, bb in items[i+1:]:
                dx = min(ab.x1, bb.x1) - max(ab.x0, bb.x0)
                dy = min(ab.y1, bb.y1) - max(ab.y0, bb.y0)
                if dx > 2 and dy > 2:
                    errors.append(f"overlap: {a.get_text()} / {b.get_text()}")
        if errors:
            raise ValueError("Style A text audit: " + "; ".join(errors))
        return {"visible_text": len(items), "text_overlap": 0, "bounds": "PASS"}
