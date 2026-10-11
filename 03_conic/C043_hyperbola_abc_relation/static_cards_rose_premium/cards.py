"""C043 Rose Premium recall/apply cards; the selected 002 stays a copied asset."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SOURCE))
sys.path.insert(0, str(SOURCE / "static_cards"))

from model import Hyperbola  # noqa: E402
from static_cards_ab_experiment.cards import PremiumCanvas, THEMES  # noqa: E402
from static_cards_style_a_polish.cards import triangle  # noqa: E402
from scripts.static_cards.style_a import P  # noqa: E402
from scripts.static_cards.style_a_polish import (  # noqa: E402
    TEXT_AMBER, TEXT_BLUE, TEXT_TEAL)


ROSE = THEMES["B_rose"]


def section(canvas, y, height, title, tab_y, tab_width, *, kind="white"):
    """Register existing panel/capsule artists for final-renderer spacing checks."""
    canvas.panel(y, height, kind)
    panel = canvas.ax.patches[-1]
    title_artist = canvas.tab(title, 80, tab_y, tab_width)
    capsule = canvas.ax.patches[-1]
    region = {"name": title, "panel": panel, "capsule": capsule,
              "title": title_artist, "formulas": []}
    canvas.formula_regions.append(region)
    return region


def card_001():
    m = Hyperbola(3, 4)
    assert m.c_squared == 25 and m.c == 5 and m.equation_value((3, 4)) == 0
    c = PremiumCanvas(ROSE, "001", "快记", "双曲线 a、b、c 的关系")
    c.formula_regions = []

    core = section(c, 240, 220, "核心公式", 255, 220, kind="tinted")
    c.box(83, 333, 914, 116, P.formula_bg, edge=P.formula_edge,
          radius=24, width=2.8)
    core["highlight"] = c.ax.patches[-1]
    core["formulas"].append(c.math(r"c^2=a^2+b^2", 540, 391, 76,
                                   "#122B58", ha="center"))

    standard = section(c, 470, 166, "标准方程  /  横轴型", 475, 424, kind="tinted")
    standard["formulas"].append(c.math(
        r"\frac{x^2}{a^2}-\frac{y^2}{b^2}=1\quad(a,b>0)",
        86, 580, 35, P.ink))

    c.panel(650, 436)
    diagram_tab = c.tab("辅助直角三角形 OAB", 80, 662, 430)
    c.extra_capsules = [(c.ax.patches[-1], diagram_tab)]
    triangle(c, diagram_tab)

    for x, letter, caption, color, fill in (
        (58, "a", "实半轴长", TEXT_BLUE, "#E5F1FF"),
        (385, "b", "虚半轴长", TEXT_TEAL, "#E6F9F3"),
        (712, "c", "半焦距  c>0", TEXT_AMBER, "#FFF2DC"),
    ):
        c.box(x, 1104, 310, 126, fill, edge=ROSE.pale_edge,
              radius=24, width=2)
        c.math(letter, x+24, 1138, 47, color)
        c.label(caption, x+24, 1210, 31, P.ink, bold=True)
    c.memory("一眼记忆", "c 是辅助直角三角形的斜边。", "B 是辅助点，不是焦点。")
    return c


def card_003():
    m = Hyperbola(4, 3)
    assert m.c_squared == 25 and m.foci == ((-5, 0), (5, 0))
    assert m.asymptote_y(4) == 3 and m.asymptote_y(-4) == -3
    c = PremiumCanvas(ROSE, "003", "快用", "双曲线参数的直接应用")
    c.formula_regions = []

    problem = section(c, 255, 164, "典型例题", 267, 208, kind="tinted")
    c.label("求参数、焦点与渐近线", 324, 305, 30, ROSE.tab_dark, bold=True)
    problem["formulas"].append(c.math(r"9x^2-16y^2=144", 89, 371, 54, P.ink))

    normal = section(c, 441, 208, "01  化标准式", 449, 277)
    normal["formulas"].append(c.math(r"\frac{x^2}{16}-\frac{y^2}{9}=1",
                                     92, 567, 48, P.ink))
    c.label("正项是 x²，焦点在 x 轴。", 500, 570, 32, "#466981")

    parameter = section(c, 669, 275, "02  读参数，求半焦距", 681, 460, kind="tinted")
    parameter["formulas"].append(c.math(r"a^2=16,\quad b^2=9", 92, 792, 46, P.ink))
    parameter["formulas"].append(c.math(
        r"a=4,\quad b=3,\quad c=\sqrt{16+9}=5", 92, 879, 40, P.ink))

    answer = section(c, 964, 268, "03  写结果", 977, 237, kind="tinted")
    c.box(85, 1046, 911, 170, P.formula_bg, edge=P.formula_edge,
          radius=23, width=2)
    answer["highlight"] = c.ax.patches[-1]
    c.label("焦点", 109, 1105, 32, "#976009", bold=True)
    answer["formulas"].append(c.math(r"F_1=(-5,0),\quad F_2=(5,0)",
                                     258, 1089, 42, "#122B58"))
    c.label("渐近线", 109, 1181, 32, "#976009", bold=True)
    answer["formulas"].append(c.math(r"y=\pm\frac{3}{4}x", 258, 1170, 43,
                                     "#122B58"))
    c.memory("一眼方法", "先看正项，确定实轴。", "再用 c²=a²+b² 求 c。")
    return c


def validate_visible_content(number: str, canvas: PremiumCanvas):
    texts = {artist.get_text() for artist in canvas.ax.texts}
    required = {
        "001": {
            "$c^2=a^2+b^2$",
            "$\\frac{x^2}{a^2}-\\frac{y^2}{b^2}=1\\quad(a,b>0)$",
            "实半轴长", "虚半轴长", "半焦距  c>0",
            "c 是辅助直角三角形的斜边。", "B 是辅助点，不是焦点。",
        },
        "003": {
            "$9x^2-16y^2=144$", "$\\frac{x^2}{16}-\\frac{y^2}{9}=1$",
            "$a^2=16,\\quad b^2=9$",
            "$a=4,\\quad b=3,\\quad c=\\sqrt{16+9}=5$",
            "$F_1=(-5,0),\\quad F_2=(5,0)$", "$y=\\pm\\frac{3}{4}x$",
            "正项是 x²，焦点在 x 轴。", "先看正项，确定实轴。",
            "再用 c²=a²+b² 求 c。",
        },
    }[number]
    if not required.issubset(texts):
        raise ValueError(f"{number} missing visible content: {required-texts}")
    expected_labels = {"001": {"O", "A", "B", "a", "b", "c"}, "003": set()}[number]
    actual_labels = {x["label"] for x in canvas.layout_report}
    if actual_labels != expected_labels:
        raise ValueError(f"{number} diagram labels changed: {actual_labels}")
    return "PASS"
