"""Small reusable V2 card composition primitives."""

import matplotlib.pyplot as plt

from scripts.static_cards.canvas import CardCanvas, WIDTH, HEIGHT
from .theme import P, S, T


class V2Canvas(CardCanvas):
    def __init__(self, uid: str, number: str, category: str, title: str, kicker: str):
        self.uid, self.number = uid, number
        self.layout_report = []
        self.text_coverage_report = []
        self.label_layout = None
        plt.rcParams.update({"svg.fonttype": "none", "svg.hashsalt": "mathnote-static-v2",
                             "mathtext.fontset": "dejavusans", "savefig.pad_inches": 0})
        self.fig = plt.figure(figsize=(10.8, 14.4), dpi=100, facecolor=P.paper)
        self.ax = self.fig.add_axes((0, 0, 1, 1))
        self.ax.set_xlim(0, WIDTH)
        self.ax.set_ylim(HEIGHT, 0)
        self.ax.axis("off")
        self.label("知树  /  数学关系", S.safe, 91, T.eyebrow, P.muted, bold=True)
        self.label(f"{number}  ·  {category}", 1004, 91, T.eyebrow, P.blue,
                   bold=True, ha="right")
        self.line(S.safe, 120, 1004, 120, P.line, 1.5)
        self.label(title, S.safe, 193, T.title, P.ink, bold=True)
        self.label(kicker, S.safe, 261, T.note, P.muted)
        self.line(S.safe, 1335, 1004, 1335, P.line, 1.5)
        self.label(uid, S.safe, S.footer_y, 18, P.muted)
        self.label("从点连成线 · 从线织成面", 1004, S.footer_y, 18, P.muted,
                   ha="right")

    def rule(self, x1, y, x2, color=None, width=1.5):
        return self.line(x1, y, x2, y, color or P.line, width)

    def eyebrow(self, text, x, y, color=None):
        return self.label(text, x, y, T.eyebrow, color or P.muted, bold=True)

    def note(self, text, x, y, color=None):
        return self.label(text, x, y, T.note, color or P.muted)

    def text_collision_audit(self):
        """Check ordinary copy blocks; diagram text is handled by LabelLayout."""
        self.fig.canvas.draw()
        renderer = self.fig.canvas.get_renderer()
        items = [(t, t.get_window_extent(renderer)) for t in self.ax.texts]
        failures = []
        for i, (a, abox) in enumerate(items):
            if abox.x0 < 36 or abox.x1 > 1044 or abox.y0 < 36 or abox.y1 > 1404:
                failures.append(f"edge: {a.get_text()}")
            for b, bbox in items[i + 1:]:
                if abox.overlaps(bbox):
                    failures.append(f"text: {a.get_text()} / {b.get_text()}")
        if failures:
            raise ValueError("V2 text layout collision: " + "; ".join(failures))
        return {"visible_text": len(items), "text_overlap": 0, "edge_overflow": 0}
