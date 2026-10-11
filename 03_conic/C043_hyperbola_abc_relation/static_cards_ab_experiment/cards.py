"""C043-002 A/B experiment: one layout, two brand palettes, frozen math."""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SOURCE / "static_cards"))

from scripts.static_cards.canvas import HEIGHT, WIDTH  # noqa: E402
from scripts.static_cards.style_a import P, StyleACanvas  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "c043_polish_cards_for_ab", SOURCE / "static_cards_style_a_polish/cards.py")
_polish = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_polish)
hyperbola_diagram = _polish.hyperbola_diagram
mathematical_checks = _polish.mathematical_checks
validate_visible_copy = _polish.validate_visible_copy


@dataclass(frozen=True)
class Theme:
    name: str
    paper: str
    border: str
    start: str
    end: str
    tab: str
    tab_dark: str
    pale: str
    pale_edge: str
    memory: str
    memory_edge: str
    memory_ink: str


THEMES = {
    "A_blue": Theme("Blue Premium", "#F7FBFF", "#D9EAF8", "#115DAE",
                    "#2686D5", "#176DB8", "#115A9A", "#EEF7FF",
                    "#B8D9F2", "#E7F4FF", "#A6D0EE", "#174F7E"),
    "B_rose": Theme("Rose Premium", "#FFF8FA", "#F5D9E2", "#BB2857",
                    "#E84F80", "#C52C5C", "#A71F4C", "#FFF0F5",
                    "#EEC1D0", "#FCEAF0", "#E9B0C3", "#832343"),
}


class PremiumCanvas(StyleACanvas):
    def __init__(self, theme: Theme, number: str = "002", kind: str = "快懂",
                 title: str = "双曲线 a、b、c 的关系"):
        self.uid, self.number, self.kind, self.title = "C043", number, kind, title
        self.theme = theme
        self.layout_report = []
        self.text_coverage_report = []
        self.label_layout = None
        self.areas = {"header": (24, 230), "content": (250, 1240),
                      "memory": (1250, 1398), "bottom_margin": (1398, 1440)}
        plt.rcParams.update({"svg.fonttype": "none", "svg.hashsalt": "c043-ab-premium",
                             "mathtext.fontset": "dejavusans", "savefig.pad_inches": 0})
        self.fig = plt.figure(figsize=(10.8, 14.4), dpi=100, facecolor=theme.paper)
        self.ax = self.fig.add_axes((0, 0, 1, 1))
        self.ax.set_xlim(0, WIDTH)
        self.ax.set_ylim(HEIGHT, 0)
        self.ax.axis("off")
        self.box(12, 11, 1056, 1418, theme.paper, edge=theme.border,
                 radius=38, width=2.1)
        self.ax.patches[-1].set_zorder(-1)
        self._header()

    def _header(self):
        theme = self.theme
        x, y, w, h = 30, 26, 1020, 204
        start = np.array([int(theme.start[i:i+2], 16) for i in (1, 3, 5)]) / 255
        end = np.array([int(theme.end[i:i+2], 16) for i in (1, 3, 5)]) / 255
        t = np.linspace(0, 1, 256)[:, None]
        rgb = start[None, :] * (1-t) + end[None, :] * t
        image = self.ax.imshow(rgb[:, None, :], extent=(x, x+w, y+h, y),
                               aspect="auto", zorder=0)
        clipping = FancyBboxPatch((x, y), w, h,
                                   boxstyle="round,pad=0,rounding_size=35",
                                   facecolor="none", edgecolor="none")
        self.ax.add_patch(clipping)
        image.set_clip_path(clipping)
        # The index badge and capsule echo the supplied rose reference card.
        self.box(58, 51, 180, 68, "#FFFFFF", radius=24)
        self.label("C043", 148, 99, 38, theme.tab_dark, bold=True, ha="center")
        self.label("知树  /  解析几何", 270, 97, 26, "#FFFFFF", bold=True)
        self.box(790, 53, 224, 62, "#FFFFFF", radius=23)
        self.label(f"{self.number}  /  {self.kind}", 902, 97, 29, theme.tab_dark,
                   bold=True, ha="center")
        self.label(self.title, 64, 187, 51, "#FFFFFF", bold=True)

    def panel(self, y: float, h: float, kind: str = "white"):
        theme = self.theme
        fill = "#FFFFFF" if kind == "white" else theme.pale
        self.box(58, y, 964, h, fill, edge=theme.pale_edge,
                 radius=27, width=2.0)

    def tab(self, title: str, x: float, y: float, w: float, baseline: float = 38):
        self.box(x, y, w, 52, self.theme.tab, radius=19)
        return self.label(title, x+22, y+baseline, 30, "#FFFFFF", bold=True)

    def memory(self, title: str = "一眼记忆", first: str = "斜边与半焦距等长，",
               second: str = "但它们不是同一线段。"):
        theme = self.theme
        self.box(58, 1250, 964, 148, theme.memory, edge=theme.memory_edge,
                 radius=27, width=2.1)
        self.box(76, 1269, 210, 110, theme.tab_dark, radius=22)
        self.label(title, 181, 1336, 32, "#FFFFFF", bold=True, ha="center")
        self.label(first, 310, 1314, 33, theme.memory_ink, bold=True)
        self.label(second, 310, 1364, 33,
                   theme.memory_ink, bold=True)


def card_002(theme_name: str) -> PremiumCanvas:
    c = PremiumCanvas(THEMES[theme_name])
    c.panel(234, 171, "tinted")
    equation_panel = c.ax.patches[-1]
    equation_title = c.tab("标准方程  /  横轴型", 80, 238, 424)
    equation_capsule = c.ax.patches[-1]
    equation = c.math(r"\frac{x^2}{a^2}-\frac{y^2}{b^2}=1\quad(a,b>0)",
                      85, 351, 40, P.ink)
    c.standard_equation = (equation_panel, equation_capsule, equation_title, equation)

    c.panel(410, 594)
    diagram_tab = c.tab("精确图形  /  辅助构造", 80, 425, 460)
    hyperbola_diagram(c, diagram_tab)

    c.panel(1023, 207, "tinted")
    c.tab("看图得关系", 80, 1035, 236)
    c.box(750, 1040, 246, 56, P.formula_bg, edge=P.formula_edge,
          radius=18, width=2)
    c.math(r"c^2=a^2+b^2", 873, 1068, 31, "#122B58", ha="center")
    c.math(r"OA=a,\quad AB=b,\quad OB=OF_2=c", 88, 1136, 38, "#174F50")
    c.label("B 是辅助矩形角点，不在双曲线上，也不是焦点。", 88, 1204,
            30, "#206759")
    c.memory()
    return c
