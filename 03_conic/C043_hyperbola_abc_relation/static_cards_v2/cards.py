"""Three C043 V2 cards, with exact geometry supplied by the frozen C043 model."""

from math import isclose

from scripts.static_cards.canvas import MathFrame
from scripts.static_cards.labels import LabelLayout, LineLabel, PointLabel, SegmentLabel
from scripts.static_cards.v2.components import V2Canvas
from scripts.static_cards.v2.theme import P, T, L


REVIEW_STATUS = "TASK 13G.4V — V2 VISUAL REVIEW PENDING"
LABEL_GATE_REQUIRED = {
    "001": {"O", "A", "B", "a", "b", "c"},
    "002": {"O", "A", "B", "F_2", "a", "b", "c", "x"},
}
SPECS = {
    n: {"uid": "C043", "kind": k, "geometry": {"a": a, "b": b}}
    for n, k, a, b in (("001", "快记", 3, 4),
                       ("002", "快懂", 3, 4),
                       ("003", "快用", 4, 3))
}


def validate_content(formal_texts):
    checks = {
        "standard_form": ("01_statement.tex", (r"\frac{x^2}{a^2}", r"\frac{y^2}{b^2}", "a>0, b>0")),
        "relation": ("01_statement.tex", ("c^2 = a^2 + b^2",)),
        "construction": ("02_explanation.tex", ("直角三角形", "斜边")),
        "worked_example": ("04_examples.tex", ("9x^2-16y^2=144", "a=4", "b=3", "c=5", r"(\pm5,0)")),
        "axis_warning": ("05_traps.tex", ("焦点在该轴上",)),
    }
    for name, (file, tokens) in checks.items():
        if not all(token in formal_texts[file] for token in tokens):
            raise ValueError(f"V2 content differs from formal source: {name}")
    return {name: "PASS" for name in checks}


def _hyperbola(c, frame, m, tmax, *, color=P.blue, width=L.curve):
    for side in (-1, 1):
        points = [m.branch_point(side, -tmax + 2 * tmax * i / 280)
                  for i in range(281)]
        xs, ys = zip(*(frame.xy(x, y) for x, y in points))
        artist, = c.ax.plot(xs, ys, color=color, lw=width,
                            solid_capstyle="round", zorder=4)
        artist._mathnote_name = "hyperbola left branch" if side < 0 else "hyperbola right branch"


def _triangle(c, frame, m, *, plot_bounds, focus=False):
    O, A, B = (0, 0), (m.a, 0), (m.a, m.b)
    frame.segment(O, A, P.blue, L.construction, name="OA")
    frame.segment(A, B, P.teal, L.construction, name="AB")
    frame.segment(O, B, P.amber, L.emphasis, name="OB")
    for point, name, color in ((O, "O", P.ink), (A, "A", P.blue)):
        frame.point(point, "", color=color, object_name=f"point {name}")
    if focus:
        bx, by = frame.xy(*B)
        marker, = c.ax.plot((bx,), (by,), marker="o", markersize=10,
                            markerfacecolor=P.paper, markeredgecolor=P.teal,
                            markeredgewidth=2, zorder=6)
        marker._mathnote_name = "point B"
    else:
        frame.point(B, "", color=P.teal, object_name="point B")
    layout = LabelLayout(c, frame, plot_bounds)
    for name, point, color, priority in (("O", O, P.ink, 90),
                                         ("A", A, P.blue, 80),
                                         ("B", B, P.teal, 70)):
        layout.add(PointLabel(name, f"point {name}", point, color=color,
                              priority=priority, clearance=7, size=T.diagram))
    for name, object_name, start, end, color, priority in (
            ("a", "OA", O, A, P.blue, 60),
            ("b", "AB", A, B, P.teal, 50),
            ("c", "OB", O, B, P.amber, 40)):
        layout.add(SegmentLabel(name, object_name, start, endpoint=end,
                                color=color, priority=priority, clearance=7,
                                size=T.diagram))
    if focus:
        F = (m.c, 0)
        frame.point(F, "", color=P.amber, object_name="point F_2")
        layout.add(PointLabel(r"F_2", "point F_2", F, color=P.amber,
                              priority=65, clearance=7, size=T.diagram))
        layout.add(LineLabel("x", "x axis", (5.65, 0), color=P.muted,
                             priority=20, clearance=6, size=20))
    layout.resolve()
    return layout


def card_001(m):
    c = V2Canvas("C043", "001", "快记", "双曲线的三段长度", "横轴型 · a、b、c 都是正长度")
    c.eyebrow("记住这一式", 76, 333, P.blue)
    c.math(r"c^2=a^2+b^2", 540, 442, T.formula_hero, P.ink, ha="center")
    c.rule(76, 516, 1004)
    c.math(r"\frac{x^2}{a^2}-\frac{y^2}{b^2}=1", 76, 592, 31, P.muted)
    c.label("a > 0，b > 0，c > 0", 1004, 598, 27, P.muted, ha="right")
    c.eyebrow("一眼看懂：c 是辅助直角三角形的斜边", 76, 686)
    frame = MathFrame(c, 405, 1060, 63)
    _triangle(c, frame, m, plot_bounds=(232, 720, 824, 1113))
    c.rule(76, 1167, 1004)
    c.label("a  实半轴", 76, 1234, 28, P.blue, bold=True)
    c.label("b  虚半轴", 382, 1234, 28, P.teal, bold=True)
    c.label("c  半焦距", 701, 1234, 28, P.amber, bold=True)
    c.note("b 是辅助长度；不是双曲线在 y 轴上的截距。", 76, 1295)
    return c


def card_002(m):
    c = V2Canvas("C043", "002", "快懂", "c 为什么是最长的一段？", "看辅助三角形，也看真实焦点")
    c.eyebrow("同一坐标系 · 精确比例", 76, 314)
    c.math(r"\frac{x^2}{a^2}-\frac{y^2}{b^2}=1", 1004, 306, 26, P.muted, ha="right")
    frame = MathFrame(c, 456, 724, 65)
    frame.segment((-5.55, 0), (6.0, 0), P.axis, L.axis, name="x axis")
    _hyperbola(c, frame, m, 0.98, color=P.blue)
    for sign in (-1, 1):
        frame.segment((-3.9, m.asymptote_y(-3.9, sign)),
                      (3.9, m.asymptote_y(3.9, sign)), P.axis,
                      L.auxiliary, "--", name=f"asymptote {sign}")
    for i in range(4):
        corners = m.rectangle
        frame.segment(corners[i], corners[(i + 1) % 4], P.line,
                      L.auxiliary, "--", name=f"auxiliary rectangle {i}")
    _triangle(c, frame, m, plot_bounds=(84, 343, 998, 1090), focus=True)
    c.rule(76, 1116, 1004)
    c.math(r"OA=a,\quad AB=b,\quad OB=c", 76, 1169, 30, P.ink)
    c.math(r"OB=OF_2=c", 76, 1225, 29, P.amber)
    c.math(r"c^2=a^2+b^2", 1004, 1225, 29, P.ink, ha="right")
    c.note("B 是辅助矩形角点；不在双曲线上，也不是焦点。", 76, 1292)
    return c


def card_003(m):
    c = V2Canvas("C043", "003", "快用", "先化标准形，再找焦点", "例题  ·  9x² − 16y² = 144")
    c.eyebrow("题目", 76, 328, P.blue)
    c.math(r"9x^2-16y^2=144", 76, 408, 46, P.ink)
    c.rule(76, 480, 1004)
    c.eyebrow("01  化标准形", 76, 558, P.blue)
    c.math(r"\frac{x^2}{16}-\frac{y^2}{9}=1", 76, 620, 40, P.ink)
    c.note("正项是 x²，焦点就在 x 轴。", 76, 714)
    c.rule(76, 743, 1004)
    c.eyebrow("02  读参数并取正根", 76, 807, P.teal)
    c.math(r"a^2=16,\quad b^2=9", 76, 879, 38, P.ink)
    c.math(r"a=4,\quad b=3,\quad c=\sqrt{16+9}=5", 76, 954, 34, P.ink)
    c.rule(76, 1002, 1004)
    c.eyebrow("03  写结果", 76, 1068, P.amber)
    c.box(76, 1097, 928, 170, P.pale_blue, radius=20)
    c.math(r"F_{1,2}=(\pm5,0)", 108, 1161, 38, P.blue)
    c.math(r"y=\pm\frac{3}{4}x", 590, 1161, 38, P.blue)
    c.note("方法：先看正项定焦点轴，再用 c² = a² + b²。", 76, 1300)
    assert isclose(m.c, 5) and m.asymptote_y(4) == 3
    return c


def draw_card(number, model_class):
    if number not in SPECS:
        raise ValueError(f"unknown card {number}")
    a, b = SPECS[number]["geometry"].values()
    m = model_class(a, b)
    return {"001": card_001, "002": card_002, "003": card_003}[number](m)
