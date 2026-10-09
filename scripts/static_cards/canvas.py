"""Small matplotlib layout and exact-coordinate diagram helpers."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch
from matplotlib.font_manager import FontProperties


WIDTH, HEIGHT = 1080, 1440
NAVY = "#12345b"
BLUE = "#176dcb"
TEAL = "#008e8c"
GOLD = "#e2a035"
MUTED = "#64778c"
PALE = "#eaf5ff"


def chinese_font(bold: bool = False) -> FontProperties:
    root = Path("C:/Windows/Fonts")
    name = "Noto Sans SC Bold (TrueType).otf" if bold else "Noto Sans SC (TrueType).otf"
    if (root / name).exists():
        return FontProperties(fname=str(root / name))
    return FontProperties(family="Microsoft YaHei", weight="bold" if bold else "normal")


class CardCanvas:
    def __init__(self, uid: str, number: str, category: str, title: str, subtitle: str):
        self.uid, self.number = uid, number
        self.layout_report = []
        self.text_coverage_report = []
        self.label_layout = None
        plt.rcParams.update({"svg.fonttype": "none", "svg.hashsalt": "mathnote-static-v1",
                             "mathtext.fontset": "dejavusans", "savefig.pad_inches": 0})
        self.fig = plt.figure(figsize=(10.8, 14.4), dpi=100, facecolor="#f7fbff")
        self.ax = self.fig.add_axes((0, 0, 1, 1))
        self.ax.set_xlim(0, WIDTH)
        self.ax.set_ylim(HEIGHT, 0)
        self.ax.axis("off")
        self.box(34, 34, 1012, 1372, "#ffffff", radius=35, edge="#dceaf6")
        self.box(64, 65, 132, 49, BLUE, radius=23)
        self.label(number, 130, 98, 22, "#ffffff", bold=True, ha="center")
        self.label(category, 218, 98, 21, BLUE, bold=True)
        self.label(title, 65, 187, 48, NAVY, bold=True)
        self.label(subtitle, 68, 233, 24, MUTED)
        self.line(65, 269, 1015, 269, "#d9e8f6", 2)
        self.label(uid, 68, 1370, 19, MUTED)

    def box(self, x, y, w, h, color, radius=24, edge="none", width=1.6):
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                                         linewidth=width, edgecolor=edge, facecolor=color))

    def label(self, value, x, y, size, color=NAVY, bold=False, ha="left", va="baseline"):
        return self.ax.text(x, y, value, fontsize=size, color=color,
                            fontproperties=chinese_font(bold), ha=ha, va=va)

    def math(self, value, x, y, size=32, color=NAVY, ha="left"):
        return self.ax.text(x, y, f"${value}$", fontsize=size, color=color, ha=ha, va="center")

    def line(self, x1, y1, x2, y2, color=BLUE, width=3, style="-", name=None):
        artist, = self.ax.plot((x1, x2), (y1, y2), color=color, lw=width, ls=style,
                               solid_capstyle="round", zorder=3)
        artist._mathnote_name = name
        return artist

    def dot(self, x, y, color=BLUE, r=8, name=None):
        artist = Circle((x, y), r, facecolor=color, edgecolor="white", lw=2, zorder=5)
        artist._mathnote_name = name
        self.ax.add_patch(artist)
        return artist

    def export(self, png: Path, svg: Path):
        self.fig.canvas.draw()
        renderer = self.fig.canvas.get_renderer()
        for label in self.ax.texts:
            bounds = label.get_window_extent(renderer)
            if bounds.x0 < 18 or bounds.y0 < 18 or bounds.x1 > WIDTH - 18 or bounds.y1 > HEIGHT - 18:
                raise ValueError(f"text exceeds card canvas: {label.get_text()}")
        self.fig.savefig(png, dpi=100, facecolor=self.fig.get_facecolor())
        self.fig.savefig(svg, format="svg", facecolor=self.fig.get_facecolor(),
                         metadata={"Date": None})
        plt.close(self.fig)


class MathFrame:
    """One affine scale for all mathematical points and lines in a diagram."""

    def __init__(self, canvas: CardCanvas, x0, y0, scale):
        self.c, self.x0, self.y0, self.scale = canvas, x0, y0, scale

    def xy(self, x, y):
        return self.x0 + self.scale * x, self.y0 - self.scale * y

    def segment(self, a, b, color=BLUE, width=4, style="-", name=None):
        return self.c.line(*self.xy(*a), *self.xy(*b), color, width, style, name)

    def point(self, point, name, dx=12, dy=-12, color=BLUE, object_name=None):
        x, y = self.xy(*point)
        self.c.dot(x, y, color, name=object_name)
        if name:
            self.c.math(name, x + dx, y + dy, 25, color)

    def parabola(self, p, ymax, color=BLUE):
        ys = [(-ymax + 2 * ymax * i / 400) for i in range(401)]
        xs, py = zip(*(self.xy(y * y / (2 * p), y) for y in ys))
        self.c.ax.plot(xs, py, color=color, lw=5, solid_capstyle="round", zorder=4)
