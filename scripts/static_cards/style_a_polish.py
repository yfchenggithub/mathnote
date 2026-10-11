"""Small, UID-neutral polish of the selected Style A visual language.

The 13G.4V.3 canvas remains untouched so its reviewed preview can be rebuilt.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

from scripts.static_cards.style_a import P, StyleACanvas
from scripts.static_cards.canvas import HEIGHT, WIDTH


TAB_BLUE = "#1B70B9"
TAB_GREEN = "#10794F"
TAB_AMBER = "#9D6818"
TEXT_BLUE = "#1F60B4"
TEXT_TEAL = "#087E70"
TEXT_AMBER = "#9D6008"


class StyleAPolishCanvas(StyleACanvas):
    """Rounded brand header, stronger section hierarchy and readable recall box."""

    def __init__(self, uid: str, number: str, kind: str, title: str):
        self.uid, self.number = uid, number
        self.layout_report = []
        self.text_coverage_report = []
        self.label_layout = None
        self.areas = {"header": (24, 229), "content": (250, 1240),
                      "memory": (1250, 1398), "bottom_margin": (1398, 1440)}
        plt.rcParams.update({"svg.fonttype": "none", "svg.hashsalt": "c043-style-a-polish",
                             "mathtext.fontset": "dejavusans", "savefig.pad_inches": 0})
        self.fig = plt.figure(figsize=(10.8, 14.4), dpi=100, facecolor=P.paper)
        self.ax = self.fig.add_axes((0, 0, 1, 1))
        self.ax.set_xlim(0, WIDTH)
        self.ax.set_ylim(HEIGHT, 0)
        self.ax.axis("off")

        # Keep the selected blue palette, with the C007-inspired rounded masthead.
        x, y, w, h = 26, 24, 1028, 205
        first, last = "#0869C9", "#2587D1"
        a = np.array([int(first[i:i+2], 16) for i in (1, 3, 5)]) / 255
        b = np.array([int(last[i:i+2], 16) for i in (1, 3, 5)]) / 255
        t = np.linspace(0, 1, 256)[:, None]
        rgb = a[None, :] * (1-t) + b[None, :] * t
        image = self.ax.imshow(rgb[:, None, :], extent=(x, x+w, y+h, y),
                               aspect="auto", zorder=0)
        clipping = FancyBboxPatch((x, y), w, h,
                                   boxstyle="round,pad=0,rounding_size=36",
                                   facecolor="none", edgecolor="none")
        self.ax.add_patch(clipping)
        image.set_clip_path(clipping)
        self.box(58, 54, 183, 61, "#D9FFBD", radius=27)
        self.label(uid, 149, 98, 36, "#123A64", bold=True, ha="center")
        self.label("知树  /  解析几何", 281, 96, 26, "#F0FAFF", bold=True)
        self.box(783, 54, 237, 61, "#E9F6FF", radius=26)
        self.label(f"{number}  /  {kind}", 901, 98, 30, "#165B9E", bold=True,
                   ha="center")
        self.label(title, 65, 184, 51, "#FFFFFF", bold=True)

    def panel(self, y: float, height: float, *, kind: str = "white",
              x: float = 58, width: float = 964):
        fill, edge = {
            "white": ("#FFFFFF", "#B6DAF4"),
            "formula": ("#FFF8DE", "#ECCB6E"),
            "green": ("#EAFBF1", "#9FDEBC"),
            "blue": ("#EAF5FF", "#B6DAF4"),
        }[kind]
        self.box(x, y, width, height, fill, edge=edge, radius=27, width=2.2)

    def tab(self, text: str, x: float, y: float, *, color: str = TAB_BLUE,
            width: float = 260):
        self.box(x, y, width, 54, color, radius=20)
        return self.label(text, x+22, y+39, 31, "#FFFFFF", bold=True)

    def memory(self, title: str, first: str, second: str):
        self.box(58, 1250, 964, 148, "#E5F9EE", edge="#8EDBB6",
                 radius=28, width=2.2)
        self.box(78, 1270, 206, 108, "#167D57", radius=22)
        self.label(title, 181, 1334, 32, "#FFFFFF", bold=True, ha="center")
        self.label(first, 310, 1314, 33, "#174E40", bold=True)
        self.label(second, 310, 1364, 33, "#174E40", bold=True)


__all__ = ["P", "StyleAPolishCanvas", "TAB_BLUE", "TAB_GREEN", "TAB_AMBER",
           "TEXT_BLUE", "TEXT_TEAL", "TEXT_AMBER"]
