"""C043 Style A 001/003 content. Selected 002 is copied byte-for-byte."""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.static_cards.canvas import MathFrame
from scripts.static_cards.labels import LabelLayout, PointLabel, SegmentLabel
from scripts.static_cards.style_a import P, StyleACanvas


SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / "static_cards"))
from model import Hyperbola  # noqa: E402 — the frozen model for this same UID


def validate_formal_sources():
    statement = (SOURCE / "01_statement.tex").read_text(encoding="utf-8")
    explanation = (SOURCE / "02_explanation.tex").read_text(encoding="utf-8")
    example = (SOURCE / "04_examples.tex").read_text(encoding="utf-8")
    summary = (SOURCE / "06_summary.tex").read_text(encoding="utf-8")
    checks = {
        "standard_form": all(s in statement for s in
                             (r"\frac{x^2}{a^2}", r"\frac{y^2}{b^2}", "a>0, b>0")),
        "core_relation": "c^2 = a^2 + b^2" in statement and "c^2=a^2+b^2" in summary,
        "triangle_intuition": "直角三角形" in explanation and "斜边" in explanation,
        "example_1": all(s in example for s in
                         ("9x^2-16y^2=144", r"\frac{x^2}{16}", r"\frac{y^2}{9}",
                          "a=4", "b=3", "c=5", r"(\pm5,0)")),
        "axis_method": "正项分母" in summary,
    }
    if not all(checks.values()):
        raise ValueError(f"C043 formal-source agreement failed: {checks}")
    return {name: "PASS" for name in checks}


def _triangle(canvas: StyleACanvas, model: Hyperbola):
    """OAB is an exact 3:4:5 auxiliary triangle, independent of canvas styling."""
    O, A, B = (0, 0), (model.a, 0), (model.a, model.b)
    assert model.a == 3 and model.b == 4 and model.c == 5
    assert model.equation_value(B) == 0 and B != model.foci[1]
    assert math.dist(O, B) == model.c
    frame = MathFrame(canvas, 385, 982, 80)
    frame.segment(O, A, P.blue, 6, name="OA")
    frame.segment(A, B, P.teal, 6, name="AB")
    frame.segment(O, B, P.amber, 6, name="OB")
    for name, point, color in (("O", O, "#8EACC2"), ("A", A, P.blue)):
        frame.point(point, "", color=color, object_name=f"point {name}")
    bx, by = frame.xy(*B)
    marker, = canvas.ax.plot((bx,), (by,), marker="o", markersize=10,
                             markerfacecolor="white", markeredgecolor=P.teal,
                             markeredgewidth=2.5, zorder=6)
    marker._mathnote_name = "point B"
    layout = LabelLayout(canvas, frame, (176, 652, 884, 1015))
    for name, point, color, priority in (("O", O, "#6E91A8", 100),
                                         ("A", A, P.blue, 90),
                                         ("B", B, P.teal, 80)):
        layout.add(PointLabel(name, f"point {name}", point, color=color,
                              priority=priority, clearance=7, size=28))
    for name, obj, start, end, color, priority in (("a", "OA", O, A, P.blue, 60),
                                                   ("b", "AB", A, B, P.teal, 50),
                                                   ("c", "OB", O, B, P.amber, 40)):
        layout.add(SegmentLabel(name, obj, start, endpoint=end, color=color,
                                priority=priority, clearance=7, size=28,
                                exceptions=frozenset({"OB"}) if name == "b" else frozenset()))
    layout.resolve()
    canvas.label_layout = layout
    return frame


def card_001():
    m = Hyperbola(3, 4)
    c = StyleACanvas("C043", "001", "快记", "双曲线 a、b、c 的关系")
    c.panel(270, 235, kind="green")
    c.label("一眼记住", 94, 321, 27, "#11764D", bold=True)
    c.box(90, 349, 900, 127, P.formula_bg, edge=P.formula_edge, radius=22)
    c.math(r"c^2=a^2+b^2", 540, 414, 63, "#122B58", ha="center")

    c.label("标准方程  /  横轴型", 62, 555, 24, "#135FAD", bold=True)
    c.math(r"\frac{x^2}{a^2}-\frac{y^2}{b^2}=1\quad(a,b>0)",
           1008, 554, 25, P.ink, ha="right")
    c.panel(587, 460)
    c.label("辅助直角三角形 OAB", 94, 635, 26, "#2078A9", bold=True)
    _triangle(c, m)

    for x, letter, caption, color, fill in (
        (62, "a", "实半轴长", P.blue, "#EAF4FF"),
        (383, "b", "虚半轴长", P.teal, "#E8F8F4"),
        (704, "c", "半焦距 · c>0", P.amber, "#FFF5E6"),
    ):
        c.box(x, 1070, 314, 169, fill, edge="#D9EAF1", radius=22)
        c.math(letter, x+28, 1131, 43, color)
        c.label(caption, x+28, 1201, 25, P.ink, bold=True)
    c.memory("一眼记忆  ·  a、b 是辅助直角边，c 是斜边；B 不是焦点。")
    return c


def card_003():
    m = Hyperbola(4, 3)
    assert m.c_squared == 25 and m.c == 5 and m.foci == ((-5, 0), (5, 0))
    assert m.asymptote_y(4) == 3
    c = StyleACanvas("C043", "003", "快用", "双曲线参数的直接应用")
    c.panel(270, 170, kind="blue")
    c.label("典型例题  /  求参数、焦点与渐近线", 94, 324, 27, "#135FAD", bold=True)
    c.math(r"9x^2-16y^2=144", 94, 389, 44, P.ink)

    c.label("01  化为标准式", 63, 501, 29, "#176DCA", bold=True)
    c.box(63, 515, 954, 145, "#FFFFFF", edge=P.diagram_edge, radius=22)
    c.math(r"\frac{x^2}{16}-\frac{y^2}{9}=1", 100, 570, 40, P.ink)
    c.label("正项在 x²，焦点位于 x 轴。", 100, 647, 23, "#56738C")

    c.panel(675, 222, kind="green")
    c.label("02  读参数，求半焦距", 94, 725, 28, "#11764D", bold=True)
    c.math(r"a^2=16,\quad b^2=9", 94, 790, 36, P.ink)
    c.math(r"a=4,\quad b=3,\quad c=\sqrt{16+9}=5", 94, 858, 34, P.ink)

    c.label("03  写出结果", 63, 960, 29, "#A66B17", bold=True)
    c.panel(980, 254, kind="formula")
    c.label("焦点", 95, 1049, 27, "#9A660A", bold=True)
    c.math(r"F_{1,2}=(\pm5,0)", 250, 1045, 39, "#122B58")
    c.label("渐近线", 95, 1160, 27, "#9A660A", bold=True)
    c.math(r"y=\pm\frac{3}{4}x", 250, 1153, 39, "#122B58")
    c.memory("一眼方法  ·  先看正项定焦点轴，再用 c²=a²+b² 求 c。")
    return c


def validate_card_copy(number: str, canvas: StyleACanvas):
    texts = {artist.get_text() for artist in canvas.ax.texts}
    if number == "001":
        required = {"$c^2=a^2+b^2$", "实半轴长", "虚半轴长", "半焦距 · c>0",
                    "$\\frac{x^2}{a^2}-\\frac{y^2}{b^2}=1\\quad(a,b>0)$"}
        required_labels = {"O", "A", "B", "a", "b", "c"}
    elif number == "003":
        required = {"$9x^2-16y^2=144$", "$\\frac{x^2}{16}-\\frac{y^2}{9}=1$",
                    "$a^2=16,\\quad b^2=9$",
                    "$a=4,\\quad b=3,\\quad c=\\sqrt{16+9}=5$",
                    "$F_{1,2}=(\\pm5,0)$", "$y=\\pm\\frac{3}{4}x$"}
        required_labels = set()
    else:
        raise ValueError(number)
    if not required.issubset(texts):
        raise ValueError(f"{number} missing displayed facts: {required-texts}")
    labels = {item["label"] for item in canvas.layout_report}
    if labels != required_labels:
        raise ValueError(f"{number} semantic labels differ: {labels}")
    return "PASS"


def validate_selected_copy(canvas):
    """Check the visible mathematics in the unchanged, selected A-002 artwork."""
    texts = {artist.get_text() for artist in canvas.ax.texts}
    required = {
        "$c^2=a^2+b^2$",
        "$\\frac{x^2}{a^2}-\\frac{y^2}{b^2}=1\\quad(a,b>0)$",
        "$OA=a,\\quad AB=b,\\quad OB=OF_2=c$",
        "$O$", "$A$", "$B$", "$F_2$", "$a$", "$b$", "$c$",
        "B 是辅助矩形角点，不在曲线上，也不是焦点。",
    }
    if not required.issubset(texts):
        raise ValueError(f"selected A-002 missing displayed facts: {required-texts}")
    return "PASS"
