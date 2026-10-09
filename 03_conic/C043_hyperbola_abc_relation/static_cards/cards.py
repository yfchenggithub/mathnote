"""C043 card copy and geometry derived from the hyperbola model."""

from scripts.static_cards.canvas import CardCanvas, MathFrame, BLUE, GOLD, MUTED, NAVY, PALE, TEAL
from scripts.static_cards.labels import LabelLayout, LineLabel, PointLabel, SegmentLabel

from .model import Hyperbola


REVIEW_STATUS = "TASK 13G.2A — VISUAL REVIEW PENDING"
TERMINOLOGY_REVIEW = "PASS: b labels only auxiliary geometry; the rectangle corners are not curve points."
LABEL_GATE_REQUIRED = {"002": {"A", "B", "F_2", "O", "a", "b", "c", "x"}}

SPECS = {
    "001": {"uid": "C043", "kind": "快记", "title": "双曲线 a、b、c 的关系",
            "formula": r"c^2=a^2+b^2", "geometry": {"a": 3, "b": 4},
            "source": ["01_statement.tex", "06_summary.tex"], "review": REVIEW_STATUS},
    "002": {"uid": "C043", "kind": "快懂", "title": "b 为什么画在辅助图形上？",
            "formula": r"OA=a,\quad AB=b,\quad OB=c", "geometry": {"a": 3, "b": 4},
            "source": ["02_explanation.tex", "03_proof.tex"], "review": REVIEW_STATUS},
    "003": {"uid": "C043", "kind": "快用", "title": "读参数，求焦点与渐近线",
            "formula": r"c^2=a^2+b^2", "geometry": {"a": 4, "b": 3},
            "source": ["04_examples.tex", "05_traps.tex"], "review": REVIEW_STATUS},
}


def validate_content(formal_texts: dict[str, str]):
    statement = formal_texts["01_statement.tex"]
    proof = formal_texts["03_proof.tex"]
    examples = formal_texts["04_examples.tex"]
    traps = formal_texts["05_traps.tex"]
    summary = formal_texts["06_summary.tex"]
    required = {
        "statement": ("\\frac{x^2}{a^2}", "\\frac{y^2}{b^2}", "c^2 = a^2 + b^2", "a>0, b>0"),
        "proof": ("b^2 = c^2 - a^2", "c>a>0"),
        "example": ("9x^2-16y^2=144", "a=4", "b=3", "c=5", "(\\pm5,0)"),
        "trap": ("\\frac{y^2}{9} - \\frac{x^2}{4}", "焦点在该轴上"),
        "summary": ("c^2=a^2+b^2", "c>a"),
    }
    for name, source in (("statement", statement), ("proof", proof),
                         ("example", examples), ("trap", traps), ("summary", summary)):
        if not all(token in source for token in required[name]):
            raise ValueError(f"formal {name} differs from C043 card specification")
    return "PASS"


def _hyperbola(c: CardCanvas, frame: MathFrame, model: Hyperbola, tmax=1.25,
               color=BLUE, width=5):
    for side in (-1, 1):
        points = [model.branch_point(side, -tmax + 2 * tmax * i / 280)
                  for i in range(281)]
        xs, ys = zip(*(frame.xy(x, y) for x, y in points))
        artist, = c.ax.plot(xs, ys, color=color, lw=width, solid_capstyle="round", zorder=4)
        artist._mathnote_name = "hyperbola left branch" if side == -1 else "hyperbola right branch"


def _axis(c: CardCanvas, frame: MathFrame, extent=7.7, label=True):
    frame.segment((-extent, 0), (extent, 0), "#a5b9ce", 2, name="x axis")
    if label:
        c.math("x", *frame.xy(extent - 0.1, 0.45), 20, MUTED)


def _point(c: CardCanvas, frame: MathFrame, xy, name, color, dx, dy):
    frame.point(xy, name, dx, dy, color)


def _card_001():
    m = Hyperbola(3, 4)
    c = CardCanvas("C043", "001", "快记  /  一眼记住", SPECS["001"]["title"],
                   "横轴型示意 · 两支曲线的焦点在 x 轴")
    c.box(85, 304, 910, 110, PALE, edge="#c8e3fb")
    c.math(r"\frac{x^2}{a^2}-\frac{y^2}{b^2}=1", 124, 358, 31)
    c.math(SPECS["001"]["formula"], 648, 358, 36, BLUE)
    c.box(85, 452, 910, 630, "#f5faff", edge="#d9eafa")
    f = MathFrame(c, 540, 766, 46)
    _axis(c, f)
    _hyperbola(c, f, m, 1.15)
    _point(c, f, (0, 0), "O", MUTED, -19, 38)
    for side, idx in ((-1, "1"), (1, "2")):
        _point(c, f, (side * m.a, 0), rf"A_{idx}", BLUE,
               -35 if side == -1 else 7, -24)
        _point(c, f, (side * m.c, 0), rf"F_{idx}", GOLD,
               -35 if side == -1 else 7, 39)
    # The measured intervals share the same isotropic coordinate frame.
    ox, _ = f.xy(0, 0)
    ax, _ = f.xy(m.a, 0)
    fx, _ = f.xy(m.c, 0)
    c.line(ox, 862, ax, 862, BLUE, 3)
    c.line(ox, 854, ox, 870, BLUE, 2)
    c.line(ax, 854, ax, 870, BLUE, 2)
    c.math("a", (ox + ax) / 2, 900, 28, BLUE, ha="center")
    c.math(r"OF_2=c", 780, 701, 27, GOLD)
    c.box(85, 1116, 910, 190, "#f0fbf8", edge="#c7eee3")
    c.label("a  实半轴长    b  虚半轴长    c  半焦距", 123, 1176, 27, NAVY, bold=True)
    c.label("b 是辅助构造中的长度，不是曲线与 y 轴的交点。", 123, 1237, 24, TEAL)
    c.label("c > a；两焦点间距为 2c。", 123, 1280, 24, BLUE)
    return c


def _card_002():
    m = Hyperbola(3, 4)
    c = CardCanvas("C043", "002", "快懂  /  区分位置", SPECS["002"]["title"],
                   "辅助直角三角形表示长度；焦点仍在 x 轴")
    c.box(85, 306, 910, 116, PALE, edge="#c8e3fb")
    c.math(r"c^2=a^2+b^2", 125, 364, 38, BLUE)
    c.label("关系由双曲线定义推得。", 485, 369, 23, NAVY)
    c.box(85, 461, 910, 613, "#f5faff", edge="#d9eafa")
    f = MathFrame(c, 420, 772, 49)
    _axis(c, f, 6.4, label=False)
    _hyperbola(c, f, m, 1.18, color="#9ac8f5", width=4)
    corners = m.rectangle
    for i in range(4):
        f.segment(corners[i], corners[(i + 1) % 4], "#9db2c6", 2, "--",
                  name=f"auxiliary rectangle edge {i + 1}")
    for sign in (-1, 1):
        f.segment((-4.5, m.asymptote_y(-4.5, sign)),
                  (4.5, m.asymptote_y(4.5, sign)), "#c3ad88", 2, "--",
                  name=f"asymptote {'positive' if sign == 1 else 'negative'}")
    O, A, B, F = (0, 0), (m.a, 0), (m.a, m.b), (m.c, 0)
    f.segment(O, A, BLUE, 5, name="OA")
    f.segment(A, B, TEAL, 5, name="AB")
    f.segment(O, B, TEAL, 3, ":", name="OB")
    f.segment(O, F, GOLD, 4, name="OF₂")
    f.point(O, "", color=MUTED, object_name="point O")
    f.point(A, "", color=BLUE, object_name="point A")
    f.point(F, "", color=GOLD, object_name="point F₂")
    # B is deliberately unfilled: it is an auxiliary rectangle corner.
    bx, by = f.xy(*B)
    b_marker, = c.ax.plot((bx,), (by,), marker="o", markersize=9, markerfacecolor="white",
                          markeredgecolor=TEAL, markeredgewidth=2, zorder=6)
    b_marker._mathnote_name = "point B"
    c.label("辅助矩形角点不在曲线上", 511, 528, 22, MUTED)
    layout = LabelLayout(c, f, (103, 479, 978, 1056))
    for name, point, color, priority in (("A", A, BLUE, 90), ("B", B, TEAL, 80),
                                         (r"F_2", F, GOLD, 70), ("O", O, MUTED, 60)):
        layout.add(PointLabel(name, f"point {name}", point, color=color,
                              priority=priority, clearance=7))
    for name, start, end, color, priority in (("b", A, B, TEAL, 50),
                                              ("a", O, A, BLUE, 40),
                                              ("c", O, B, TEAL, 30)):
        layout.add(SegmentLabel(name, f"segment {name}", start, endpoint=end,
                                color=color, priority=priority, clearance=7))
    layout.add(LineLabel("x", "horizontal axis", (6.2, 0),
                         color=MUTED, size=20, priority=20, clearance=6))
    layout.resolve()
    c.box(85, 1109, 910, 199, "#f0fbf8", edge="#c7eee3")
    c.math(SPECS["002"]["formula"], 122, 1158, 30, NAVY)
    c.label("OB 是辅助斜边；OF 才是实际半焦距线段。", 122, 1220, 25, TEAL, bold=True)
    c.label("二者等长，位置不同；B 不是焦点。", 122, 1272, 23, MUTED)
    return c


def _card_003():
    m = Hyperbola(4, 3)  # Formal example 1.
    c = CardCanvas("C043", "003", "快用  /  按序求解", SPECS["003"]["title"],
                   "正式例题 1 · 先化标准形，再确定焦点轴")
    c.box(85, 307, 910, 159, PALE, edge="#c8e3fb")
    c.label("已知", 123, 365, 27, BLUE, bold=True)
    c.math(r"9x^2-16y^2=144", 240, 359, 38, NAVY)
    c.math(r"\frac{x^2}{16}-\frac{y^2}{9}=1", 330, 426, 34, BLUE)
    steps = [
        ("01", "看正项：焦点在 x 轴", r"a^2=16,\quad b^2=9"),
        ("02", "取正根，求半焦距", r"a=4,\quad b=3,\quad c=\sqrt{16+9}=5"),
        ("03", "写出焦点与渐近线", r"F_{1,2}=(\pm5,0),\quad y=\pm\frac{3}{4}x"),
    ]
    for i, (no, label, formula) in enumerate(steps):
        y = 510 + i * 188
        c.box(85, y, 910, 165, "#ffffff", edge="#dae8f4")
        c.box(110, y + 30, 72, 72, BLUE, radius=21)
        c.label(no, 146, y + 78, 27, "#ffffff", bold=True, ha="center")
        c.label(label, 216, y + 58, 27, NAVY, bold=True)
        c.math(formula, 215, y + 119, 29 if i != 1 else 27, BLUE)
    c.box(85, 1124, 910, 183, "#fff9e9", edge="#f3dfb2")
    c.label("核对", 123, 1177, 27, "#a4680d", bold=True)
    c.math(r"c^2=4^2+3^2=25", 244, 1172, 30, NAVY)
    c.label("正项对应实轴；双曲线用加法关系，c > a。", 123, 1244, 25, NAVY)
    assert m.c == 5 and m.asymptote_y(4) == 3
    return c


def draw_card(number: str) -> CardCanvas:
    if number == "001":
        return _card_001()
    if number == "002":
        return _card_002()
    if number == "003":
        return _card_003()
    raise ValueError(f"unknown card: {number}")
