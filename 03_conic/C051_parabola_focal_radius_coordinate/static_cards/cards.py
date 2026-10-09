"""C051 card definitions, copy and mathematically derived diagrams."""

from fractions import Fraction
from math import hypot

from scripts.static_cards.canvas import CardCanvas, MathFrame, BLUE, GOLD, MUTED, NAVY, PALE, TEAL

from .model import Parabola


SPECS = {
    "001": {"uid": "C051", "kind": "快记", "title": "抛物线焦半径公式",
            "formula": r"|PF|=x_0+\frac{p}{2}",
            "geometry": {"p": 2, "point_y": 4, "objects": ["parabola", "focus", "directrix", "P", "PF"]},
            "copy": "焦半径 = 点到准线的距离",
            "assertions": ["p_positive", "point_on_curve", "focus", "directrix", "focal_radius"],
            "source": ["01_statement.tex", "03_proof.tex", "06_summary.tex"], "review": "VISUAL REVIEW PENDING"},
    "002": {"uid": "C051", "kind": "快懂", "title": "为什么能直接用坐标计算？",
            "formula": r"|PF|=PH=x_0+\frac{p}{2}",
            "geometry": {"p": 2, "point_y": 4, "objects": ["parabola", "focus", "directrix", "P", "H", "PF", "PH"]},
            "copy": "作垂线，按定义转化，再取横坐标差",
            "assertions": ["point_on_curve", "foot_on_directrix", "perpendicular", "PF_equals_PH"],
            "source": ["02_explanation.tex", "03_proof.tex"], "review": "VISUAL REVIEW PENDING"},
    "003": {"uid": "C051", "kind": "快用", "title": "求焦半径，先看横坐标",
            "formula": r"|PF|=x_0+\frac{p}{2}",
            "geometry": {"p": 2, "point_x": 3, "objects": []},
            "copy": "对照标准式、读出横坐标、代入公式",
            "assertions": ["p_positive", "formal_example", "focal_radius"],
            "source": ["04_examples.tex", "05_traps.tex"], "review": "VISUAL REVIEW PENDING"},
}

MODEL = Parabola(Fraction(SPECS["001"]["geometry"]["p"]))
POINT = MODEL.point(Fraction(SPECS["001"]["geometry"]["point_y"]))
CURVE_Y_MIN = Fraction(-4)
CURVE_Y_MAX = Fraction(19, 4)


def curve_points():
    """Include P exactly, then continue the same parabola above it."""
    py = POINT[1]
    ys = ([CURVE_Y_MIN + (py - CURVE_Y_MIN) * Fraction(i, 400)
           for i in range(401)]
          + [py + (CURVE_Y_MAX - py) * Fraction(i, 80)
             for i in range(1, 81)])
    return [MODEL.point(y) for y in ys]


def validate_content(formal_texts: dict[str, str]):
    statement = formal_texts["01_statement.tex"]
    examples = formal_texts["04_examples.tex"]
    required = ("y^2=2px", "p>0", "x_0 + \\frac{p}{2}")
    if not all(item in statement for item in required):
        raise ValueError("statement formula differs from C051 card specification")
    if not all(item in examples for item in ("y^2=4x", "x_0=3", "= 4")):
        raise ValueError("formal example 1 differs from C051 card specification")
    return "PASS"


def diagram(c: CardCanvas, ytop=470, show_foot=False):
    """All positions come from one p=2 model and one isotropic frame."""
    data = MODEL.check_geometry(POINT)
    frame = MathFrame(c, 400, ytop + 340, 65)
    c.box(84, ytop - 46, 912, 672, "#f5faff", radius=27, edge="#d9eafa")
    xs, ys = zip(*(frame.xy(float(x), float(y)) for x, y in curve_points()))
    c.ax.plot(xs, ys, color=BLUE, lw=5, solid_capstyle="round", zorder=4)
    frame.segment((MODEL.directrix_x, Fraction(-4)),
                  (MODEL.directrix_x, Fraction(4)), MUTED, 3, "--")
    frame.segment((Fraction(-2), 0), (Fraction(6), 0), "#9eafc2", 2)
    frame.segment(data["F"], data["P"], GOLD, 5)
    if show_foot:
        frame.segment(data["H"], data["P"], TEAL, 5)
        frame.point(data["H"], "", -35, -13, TEAL)
        hx, hy = frame.xy(*data["H"])
        c.line(hx, hy, hx+16, hy, TEAL, 2)
        c.line(hx+16, hy, hx+16, hy+16, TEAL, 2)
    frame.point(data["F"], "F", 8, 33, GOLD)
    frame.point(data["P"], "", 12, -15, BLUE)
    c.math(r"O", *(_shift(frame.xy(0, 0), 4, 22)), 21, MUTED)
    dx, dy = frame.xy(MODEL.directrix_x, 0)
    label_x = dx - 104
    c.label("准线", label_x, ytop + 506, 22, MUTED, ha="center")
    c.math(r"x=-\frac{p}{2}", label_x, ytop + 555, 22, MUTED, ha="center")
    c.ax.annotate("", xy=(dx - 8, ytop + 531), xytext=(label_x + 48, ytop + 531),
                  arrowprops={"arrowstyle": "->", "color": MUTED, "lw": 1.4})
    c.math(r"F(\frac{p}{2},0)", *(_shift(frame.xy(*data["F"]), 12, 67)), 21, GOLD)
    c.math(r"P(x_0,y_0)", *(_shift(frame.xy(*data["P"]), 12, 56)), 21, BLUE)
    if show_foot:
        c.math(r"H(-\frac{p}{2},y_0)", dx-65, ytop + 30, 20, TEAL)
        c.math(r"PH", 445, ytop + 53, 25, TEAL)
    fx, fy = frame.xy(*data["F"])
    px, py = frame.xy(*data["P"])
    vx, vy = px - fx, py - fy
    segment_length = hypot(vx, vy)
    normal_x, normal_y = -vy / segment_length, vx / segment_length
    c.math(r"PF", (fx + px) / 2 + 42 * normal_x,
           (fy + py) / 2 + 42 * normal_y, 25, GOLD, ha="center")


def _shift(point, dx, dy):
    return point[0] + dx, point[1] + dy


def draw_card(number: str) -> CardCanvas:
    spec = SPECS[number]
    if number == "001":
        c = CardCanvas("C051", number, "快记  /  一眼记住", spec["title"], "开口向右 · 点在曲线上")
        c.box(85, 302, 910, 114, PALE, edge="#c8e3fb")
        c.math(r"y^2=2px,\quad p>0", 120, 358, 27)
        c.math(spec["formula"], 746, 358, 31, BLUE, ha="center")
        diagram(c, 490)
        c.box(85, 1168, 910, 131, "#f0fbf8", edge="#c7eee3")
        c.label("记住定义", 122, 1214, 24, TEAL, bold=True)
        c.label(spec["copy"], 122, 1265, 30, NAVY, bold=True)
        return c
    if number == "002":
        c = CardCanvas("C051", number, "快懂  /  看见等距", spec["title"], "一条垂线，把距离变成横坐标之差")
        c.box(85, 304, 910, 96, PALE, edge="#c8e3fb")
        c.math(r"y^2=2px,\quad p>0", 116, 351, 29)
        c.label("P 在曲线上", 654, 360, 25, NAVY)
        diagram(c, 465, show_foot=True)
        c.box(85, 1124, 910, 188, "#f0fbf8", edge="#c7eee3")
        c.label("01   P 到准线的垂足是 H，PH 为水平线段", 121, 1170, 25, NAVY)
        c.label("02   根据抛物线定义：", 121, 1223, 25, NAVY)
        c.math(r"PF=PH=x_0+\frac{p}{2}", 482, 1217, 31, TEAL)
        c.label("曲线上横坐标非负，横坐标差直接取正。", 121, 1276, 23, MUTED)
        return c
    if number == "003":
        c = CardCanvas("C051", number, "快用  /  三步算出", spec["title"], "典型例题 · 直接代入")
        c.box(85, 303, 910, 175, PALE, edge="#c8e3fb")
        c.label("已知", 122, 353, 26, BLUE, bold=True)
        c.math(r"y^2=4x", 245, 346, 38)
        c.label("点 P 在曲线上，横坐标", 122, 428, 26)
        c.math(r"x_0=3", 692, 421, 37, BLUE)
        c.label("求点 P 到焦点 F 的距离。", 122, 545, 29, NAVY, bold=True)
        steps = [
            ("01", "对照标准式", r"y^2=2px\ \Rightarrow\ 2p=4\ \Rightarrow\ p=2"),
            ("02", "读出横坐标", r"x_0=3"),
            ("03", "代入焦半径公式", r"|PF|=x_0+\frac{p}{2}=3+\frac{2}{2}=4"),
        ]
        for idx, (no, label, formula) in enumerate(steps):
            y = 606 + idx * 174
            c.box(85, y, 910, 147, "#ffffff", edge="#dae8f4")
            c.box(109, y + 29, 73, 73, BLUE, radius=22)
            c.label(no, 145, y + 77, 28, "#ffffff", bold=True, ha="center")
            c.label(label, 210, y + 51, 26, NAVY, bold=True)
            c.math(formula, 210, y + 105, 28 if idx != 2 else 27, BLUE)
        c.box(85, 1144, 910, 148, "#fff9e9", edge="#f3dfb2")
        c.label("易错提醒", 124, 1195, 25, "#a4680d", bold=True)
        c.label("焦点横坐标是 p/2 = 1，别把 p = 2 当成焦点横坐标。", 124, 1252, 23, NAVY)
        return c
    raise ValueError(f"unknown card: {number}")
