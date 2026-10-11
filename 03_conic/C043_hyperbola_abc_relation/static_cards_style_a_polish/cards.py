"""C043-only content and geometry for the isolated Style A polish."""

from __future__ import annotations

import math
import importlib.util
import sys
from pathlib import Path

from matplotlib.patches import Polygon

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SOURCE / "static_cards"))

from model import Hyperbola, validation_results  # noqa: E402
from scripts.static_cards.canvas import MathFrame  # noqa: E402
from scripts.static_cards.labels import LabelLayout, PointLabel, SegmentLabel  # noqa: E402
from scripts.static_cards.style_a_polish import (  # noqa: E402
    P, StyleAPolishCanvas, TAB_AMBER, TAB_BLUE, TAB_GREEN,
    TEXT_AMBER, TEXT_BLUE, TEXT_TEAL)

_baseline_spec = importlib.util.spec_from_file_location(
    "c043_style_a_baseline_cards", SOURCE / "static_cards_style_a/cards.py")
_baseline_module = importlib.util.module_from_spec(_baseline_spec)
_baseline_spec.loader.exec_module(_baseline_module)
validate_formal_sources = _baseline_module.validate_formal_sources


def triangle(canvas: StyleAPolishCanvas, tab_artist):
    model = Hyperbola(3, 4)
    O, A, B = (0, 0), (model.a, 0), (model.a, model.b)
    assert model.c_squared == 25 and math.dist(O, B) == model.c
    assert model.equation_value(B) == 0 and B != model.foci[1]
    frame = MathFrame(canvas, 405, 1034, 90)
    canvas.ax.add_patch(Polygon([frame.xy(*p) for p in (O, A, B)],
                                closed=True, facecolor="#DCF5E9", edgecolor="none",
                                alpha=0.9, zorder=1))
    for name, p, q, color, width in (("OA", O, A, P.blue, 6),
                                      ("AB", A, B, P.teal, 6),
                                      ("OB", O, B, P.amber, 7)):
        frame.segment(p, q, color, width, name=name)
    for name, point, color in (("O", O, "#4E7897"), ("A", A, P.blue)):
        frame.point(point, "", color=color, object_name=f"point {name}")
    bx, by = frame.xy(*B)
    marker, = canvas.ax.plot((bx,), (by,), marker="o", markersize=12,
                             markerfacecolor="white", markeredgecolor=P.teal,
                             markeredgewidth=3, zorder=6)
    marker._mathnote_name = "point B"
    layout = LabelLayout(canvas, frame, (70, 650, 1000, 1075))
    layout.exempt_text(tab_artist, "diagram section title")
    for name, point, color, priority in (("O", O, "#4E7897", 100),
                                         ("A", A, TEXT_BLUE, 90),
                                         ("B", B, TEXT_TEAL, 80)):
        layout.add(PointLabel(name, f"point {name}", point, color=color,
                              priority=priority, clearance=7, size=34))
    for name, obj, start, end, color, priority in (("a", "OA", O, A, TEXT_BLUE, 60),
                                                   ("b", "AB", A, B, TEXT_TEAL, 50),
                                                   ("c", "OB", O, B, TEXT_AMBER, 40)):
        layout.add(SegmentLabel(name, obj, start, endpoint=end, color=color,
                                priority=priority, clearance=7, size=34,
                                exceptions=frozenset({"OB"}) if name == "b" else frozenset()))
    layout.resolve()
    canvas.label_layout = layout
    return model


def hyperbola_diagram(canvas: StyleAPolishCanvas, tab_artist):
    """The frozen 3:4:5 model drives all coordinates; style changes only pixels."""
    model = Hyperbola(3, 4)
    O, A, B, F = (0, 0), (model.a, 0), (model.a, model.b), (model.c, 0)
    assert model.c_squared == 25 and model.equation_value(B) == 0
    assert B != F and math.dist(O, B) == math.dist(O, F) == 5
    frame = MathFrame(canvas, 500, 750, 64)
    canvas.ax.add_patch(Polygon([frame.xy(*p) for p in (O, A, B)],
                                closed=True, facecolor="#DCF5E9", edgecolor="none",
                                alpha=0.9, zorder=1))
    frame.segment((-5.7, 0), (6.0, 0), "#94B7D5", 2.6, name="x axis")
    for side in (-1, 1):
        pts = [model.branch_point(side, -0.82 + 1.64*i/240) for i in range(241)]
        xs, ys = zip(*(frame.xy(x, y) for x, y in pts))
        curve, = canvas.ax.plot(xs, ys, color="#1675D1", lw=5.7,
                                solid_capstyle="round", zorder=4)
        curve._mathnote_name = f"hyperbola {'left' if side < 0 else 'right'}"
    for name, p, q, color in (("OA", O, A, P.blue),
                              ("AB", A, B, P.teal), ("OB", O, B, P.amber)):
        frame.segment(p, q, color, 6, name=name)
    for name, p, color in (("O", O, "#94B7D5"), ("A", A, P.blue),
                           ("F_2", F, P.amber)):
        frame.point(p, "", color=color, object_name=f"point {name}")
    bx, by = frame.xy(*B)
    marker, = canvas.ax.plot((bx,), (by,), marker="o", markersize=12,
                             markerfacecolor="white", markeredgecolor=P.teal,
                             markeredgewidth=3, zorder=6)
    marker._mathnote_name = "point B"
    layout = LabelLayout(canvas, frame, (70, 410, 1000, 991))
    layout.exempt_text(tab_artist, "diagram section title")
    for name, p, color, priority in (("O", O, "#4E7897", 100),
                                     ("A", A, TEXT_BLUE, 90), ("B", B, TEXT_TEAL, 80),
                                     (r"F_2", F, TEXT_AMBER, 70)):
        layout.add(PointLabel(name, f"point {name}", p, color=color,
                              priority=priority, clearance=6, size=33))
    for name, target, p, q, color, priority in (("a", "OA", O, A, TEXT_BLUE, 60),
                                                ("b", "AB", A, B, TEXT_TEAL, 50),
                                                ("c", "OB", O, B, TEXT_AMBER, 40)):
        layout.add(SegmentLabel(name, target, p, endpoint=q, color=color,
                                priority=priority, clearance=6, size=33,
                                exceptions=frozenset({"OB"}) if name == "b" else frozenset()))
    layout.resolve()
    canvas.label_layout = layout
    return model


def card_001():
    c = StyleAPolishCanvas("C043", "001", "快记", "双曲线 a、b、c 的关系")
    c.panel(255, 220, kind="green")
    c.tab("核心公式", 80, 267, color=TAB_GREEN, width=193)
    c.box(83, 333, 914, 116, P.formula_bg, edge=P.formula_edge,
          radius=24, width=2.8)
    c.math(r"c^2=a^2+b^2", 540, 391, 76, "#122B58", ha="center")

    c.panel(494, 139, kind="blue")
    c.label("标准方程  /  横轴型", 86, 525, 31, "#1764A8", bold=True)
    c.math(r"\frac{x^2}{a^2}-\frac{y^2}{b^2}=1\quad(a,b>0)",
           86, 581, 35, P.ink)

    c.panel(650, 436)
    diagram_tab = c.tab("辅助直角三角形 OAB", 80, 662, color=TAB_BLUE, width=367)
    triangle(c, diagram_tab)

    for x, letter, caption, color, fill in (
        (58, "a", "实半轴长", TEXT_BLUE, "#E5F1FF"),
        (385, "b", "虚半轴长", TEXT_TEAL, "#E6F9F3"),
        (712, "c", "半焦距  c>0", TEXT_AMBER, "#FFF2DC"),
    ):
        c.box(x, 1104, 310, 126, fill, edge="#CADFEF", radius=24, width=2)
        c.math(letter, x+24, 1138, 47, color)
        c.label(caption, x+24, 1210, 31, P.ink, bold=True)
    c.memory("一眼记忆", "c 是辅助直角三角形的斜边。", "B 是辅助点，不是焦点。")
    return c


def card_002():
    c = StyleAPolishCanvas("C043", "002", "快懂", "双曲线 a、b、c 的关系")
    c.panel(255, 145, kind="blue")
    c.label("标准方程  /  横轴型", 85, 293, 31, "#1764A8", bold=True)
    c.math(r"\frac{x^2}{a^2}-\frac{y^2}{b^2}=1\quad(a,b>0)",
           85, 351, 40, P.ink)

    c.panel(410, 594)
    diagram_tab = c.tab("精确图形  /  辅助构造", 80, 425, color=TAB_BLUE, width=390)
    hyperbola_diagram(c, diagram_tab)

    c.panel(1023, 207, kind="green")
    c.tab("看图得关系", 80, 1035, color=TAB_GREEN, width=236)
    c.box(750, 1040, 246, 56, P.formula_bg, edge=P.formula_edge,
          radius=18, width=2)
    c.math(r"c^2=a^2+b^2", 873, 1068, 31, "#122B58", ha="center")
    c.math(r"OA=a,\quad AB=b,\quad OB=OF_2=c", 88, 1136, 38, "#174F50")
    c.label("B 是辅助矩形角点，不在双曲线上，也不是焦点。", 88, 1204,
            30, "#206759")
    c.memory("一眼记忆", "斜边与半焦距等长，", "但它们不是同一线段。")
    return c


def card_003():
    m = Hyperbola(4, 3)
    assert m.c_squared == 25 and m.c == 5 and m.foci == ((-5, 0), (5, 0))
    assert m.asymptote_y(4) == 3
    c = StyleAPolishCanvas("C043", "003", "快用", "双曲线参数的直接应用")
    c.panel(255, 164, kind="blue")
    c.tab("典型例题", 80, 267, color=TAB_BLUE, width=208)
    c.label("求参数、焦点与渐近线", 324, 305, 30, "#1764A8", bold=True)
    c.math(r"9x^2-16y^2=144", 89, 365, 54, P.ink)

    c.panel(441, 208)
    c.tab("01  化标准式", 80, 454, color=TAB_BLUE, width=277)
    c.math(r"\frac{x^2}{16}-\frac{y^2}{9}=1", 92, 567, 48, P.ink)
    c.label("正项是 x²，焦点在 x 轴。", 500, 570, 32, "#466981")

    c.panel(669, 275, kind="green")
    c.tab("02  读参数", 80, 681, color=TAB_GREEN, width=237)
    c.math(r"a^2=16,\quad b^2=9", 92, 792, 46, P.ink)
    c.math(r"a=4,\quad b=3,\quad c=\sqrt{16+9}=5", 92, 879, 40, P.ink)

    c.panel(964, 268, kind="formula")
    c.tab("03  写结果", 80, 977, color=TAB_AMBER, width=237)
    c.box(85, 1046, 911, 162, "#FFFDF3", edge="#E8CC86", radius=23, width=2)
    c.label("焦点", 109, 1105, 32, "#976009", bold=True)
    c.math(r"F_1=(-5,0),\quad F_2=(5,0)", 258, 1095, 42, "#122B58")
    c.label("渐近线", 109, 1181, 32, "#976009", bold=True)
    c.math(r"y=\pm\frac{3}{4}x", 258, 1170, 43, "#122B58")
    c.memory("一眼方法", "先看正项，确定焦点轴。", "再用 c²=a²+b² 求 c。")
    return c


def validate_visible_copy(number: str, canvas: StyleAPolishCanvas):
    texts = {artist.get_text() for artist in canvas.ax.texts}
    required = {
        "001": {"$c^2=a^2+b^2$", "实半轴长", "虚半轴长", "半焦距  c>0",
                "$\\frac{x^2}{a^2}-\\frac{y^2}{b^2}=1\\quad(a,b>0)$",
                "B 是辅助点，不是焦点。"},
        "002": {"$c^2=a^2+b^2$",
                "$\\frac{x^2}{a^2}-\\frac{y^2}{b^2}=1\\quad(a,b>0)$",
                "$OA=a,\\quad AB=b,\\quad OB=OF_2=c$",
                "B 是辅助矩形角点，不在双曲线上，也不是焦点。",
                "但它们不是同一线段。"},
        "003": {"$9x^2-16y^2=144$", "$\\frac{x^2}{16}-\\frac{y^2}{9}=1$",
                "$a^2=16,\\quad b^2=9$",
                "$a=4,\\quad b=3,\\quad c=\\sqrt{16+9}=5$",
                "$F_1=(-5,0),\\quad F_2=(5,0)$", "$y=\\pm\\frac{3}{4}x$",
                "正项是 x²，焦点在 x 轴。"},
    }[number]
    if not required.issubset(texts):
        raise ValueError(f"{number} missing visible facts: {required-texts}")
    expected_labels = {"001": {"O", "A", "B", "a", "b", "c"},
                       "002": {"O", "A", "B", "F_2", "a", "b", "c"},
                       "003": set()}[number]
    actual_labels = {entry["label"] for entry in canvas.layout_report}
    if actual_labels != expected_labels:
        raise ValueError(f"{number} labels differ: {actual_labels}")
    return "PASS"


def mathematical_checks():
    checks = validation_results()
    assert len(checks) == 11 and all(result == "PASS" for result in checks.values())
    assert all(result == "PASS" for result in validate_formal_sources().values())
    return checks
