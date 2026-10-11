"""Task 13G.4V.2: six isolated, comparable C043-002 visual studies.

Run from the repository root with:
    python 03_conic/C043_hyperbola_abc_relation/static_cards/style_lab.py

Only .build/static_cards_style_lab/C043 is written. All geometry comes from
the existing C043 model; no formal card or shared renderer is modified.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.static_cards.canvas import CardCanvas, MathFrame  # noqa: E402
from scripts.static_cards.labels import LabelLayout, PointLabel, SegmentLabel  # noqa: E402
from model import Hyperbola, validation_results  # noqa: E402


SOURCE = ROOT / "03_conic/C043_hyperbola_abc_relation"
OUT = ROOT / ".build/static_cards_style_lab/C043"
W, H = 1080, 1440
NAMES = {
    "A": ("premium_infographic", "精品彩色信息图"),
    "B": ("math_textbook", "高级数学教科书"),
    "C": ("science_infographic", "现代科普信息图"),
    "D": ("elegant_notes", "精品学习笔记"),
    "E": ("dark_geometry", "深色数学几何"),
    "F": ("structural_geometry", "结构几何图解"),
}
DESIGN = {
    "A": {"composition": "gradient masthead → amber theorem → framed diagram → green recall",
          "hierarchy": "colorful education infographic", "formula": "warm highlighted theorem"},
    "B": {"composition": "editorial title → large unframed figure → caption and proof relation",
          "hierarchy": "book typography and warm paper", "formula": "typeset conclusion"},
    "C": {"composition": "high contrast question → broad science figure → dark formula band",
          "hierarchy": "poster scale image first", "formula": "white hero on navy"},
    "D": {"composition": "ruled notebook → sticky formula → annotated figure → study note",
          "hierarchy": "soft study journal", "formula": "pinned memory note"},
    "E": {"composition": "dark editorial opening → floating geometry → luminous conclusion",
          "hierarchy": "spatial geometry at night", "formula": "bright type on navy"},
    "F": {"composition": "semantic parameter tiles → relationship arrow → coordinate figure → result",
          "hierarchy": "process diagram and strict alignment", "formula": "result strip"},
}


class Card(CardCanvas):
    def __init__(self, key: str, background: str):
        self.uid, self.number = "C043", "002"
        self.key = key
        self.layout_report = []
        self.text_coverage_report = []
        self.label_layout = None
        plt.rcParams.update({"svg.fonttype": "none", "svg.hashsalt": "c043-style-lab",
                             "mathtext.fontset": "dejavusans", "savefig.pad_inches": 0})
        self.fig = plt.figure(figsize=(10.8, 14.4), dpi=100, facecolor=background)
        self.ax = self.fig.add_axes((0, 0, 1, 1))
        self.ax.set_xlim(0, W)
        self.ax.set_ylim(H, 0)
        self.ax.axis("off")

    def gradient(self, y0, y1, first, last):
        first = np.array([int(first[i:i+2], 16) for i in (1, 3, 5)]) / 255
        last = np.array([int(last[i:i+2], 16) for i in (1, 3, 5)]) / 255
        row = np.linspace(0, 1, 256)[:, None]
        rgb = (first[None, :] * (1-row) + last[None, :] * row)
        self.ax.imshow(rgb[:, None, :], extent=(0, W, y1, y0), aspect="auto", zorder=0)

    def audit_text(self):
        self.fig.canvas.draw()
        renderer = self.fig.canvas.get_renderer()
        artists = [t for t in self.ax.texts if t.get_visible()]
        boxes = [(t, t.get_window_extent(renderer)) for t in artists]
        issues = []
        for i, (a, ab) in enumerate(boxes):
            if min(ab.x0, ab.y0) < 20 or ab.x1 > W-20 or ab.y1 > H-20:
                issues.append(f"bounds: {a.get_text()}")
            for b, bb in boxes[i+1:]:
                dx = min(ab.x1, bb.x1) - max(ab.x0, bb.x0)
                dy = min(ab.y1, bb.y1) - max(ab.y0, bb.y0)
                if dx > 2 and dy > 2:
                    issues.append(f"overlap: {a.get_text()} / {b.get_text()}")
        if issues:
            raise ValueError(f"{self.key} text audit: " + "; ".join(issues))
        return {"visible_text": len(artists), "text_overlap": 0, "bounds": "PASS"}


def geom(c: Card, *, origin, scale, bounds, colors, curve_width=5, show_asymptotes=False):
    """One exact mathematical construction, laid out in six different contexts."""
    m = Hyperbola(3, 4)
    assert m.c_squared == 25 and m.c == 5
    O, A, B, F = (0, 0), (m.a, 0), (m.a, m.b), (m.c, 0)
    assert m.equation_value(B) == 0 and B != F
    assert math.dist(O, B) == math.dist(O, F) == 5
    f = MathFrame(c, *origin, scale)
    axis, curve, a_color, b_color, c_color = colors
    f.segment((-5.7, 0), (6.0, 0), axis, 2.2, name="x axis")
    if show_asymptotes:
        for sign in (-1, 1):
            f.segment((-4.3, m.asymptote_y(-4.3, sign)),
                      (4.3, m.asymptote_y(4.3, sign)), axis, 1.5, "--",
                      name=f"asymptote {sign}")
    for side in (-1, 1):
        pts = [m.branch_point(side, -0.82 + 1.64*i/240) for i in range(241)]
        xs, ys = zip(*(f.xy(x, y) for x, y in pts))
        line, = c.ax.plot(xs, ys, color=curve, lw=curve_width,
                          solid_capstyle="round", zorder=4)
        line._mathnote_name = f"hyperbola {'left' if side < 0 else 'right'}"
    # The three colored segments form the exact auxiliary right triangle.
    f.segment(O, A, a_color, 5, name="OA")
    f.segment(A, B, b_color, 5, name="AB")
    f.segment(O, B, c_color, 5, name="OB")
    for name, p, color in (("O", O, axis), ("A", A, a_color), ("F_2", F, c_color)):
        f.point(p, "", color=color, object_name=f"point {name}")
    bx, by = f.xy(*B)
    marker, = c.ax.plot((bx,), (by,), marker="o", markersize=10,
                        markerfacecolor=c.fig.get_facecolor(), markeredgecolor=b_color,
                        markeredgewidth=2.5, zorder=6)
    marker._mathnote_name = "point B"
    layout = LabelLayout(c, f, bounds)
    for name, p, color, priority in (("O", O, axis, 100), ("A", A, a_color, 90),
                                     ("B", B, b_color, 80), (r"F_2", F, c_color, 70)):
        layout.add(PointLabel(name, f"point {name if name != 'F_2' else 'F_2'}", p,
                              color=color, priority=priority, clearance=6, size=27))
    for name, target, p, q, color, priority in (("a", "OA", O, A, a_color, 60),
                                                ("b", "AB", A, B, b_color, 50),
                                                ("c", "OB", O, B, c_color, 40)):
        # OB converges with AB at B. The precise OB exception lets the generic
        # label search choose the triangle's interior without mistaking the
        # neighboring diagonal for an unrelated mathematical object.
        exceptions = frozenset({"OB"}) if name == "b" else frozenset()
        layout.add(SegmentLabel(name, target, p, endpoint=q, color=color,
                                priority=priority, clearance=6, size=27,
                                exceptions=exceptions))
    try:
        layout.resolve()
    except Exception as exc:
        if hasattr(exc, "report"):
            print({k: exc.report.get(k) for k in ("label", "collisions", "association")})
        raise
    c.label_layout = layout
    return m


def common(c, *, ink, muted, accent):
    c.label("C043  /  解析几何", 70, 1380, 20, muted, bold=True)
    c.label("知树  ·  快懂  002", 1010, 1380, 20, accent, bold=True, ha="right")


def style_a():
    c = Card("A", "#F1F8FF")
    c.gradient(0, 244, "#0869C9", "#54B5F4")
    c.label("知树   /   C043  ·  002 快懂", 68, 76, 26, "#FFFFFF", bold=True)
    c.label("双曲线 a、b、c 的关系", 68, 164, 51, "#FFFFFF", bold=True)
    c.box(62, 270, 956, 176, "#FFF8DE", edge="#F1CE6D", radius=26)
    c.label("核心关系", 94, 325, 27, "#9A660A", bold=True)
    c.math(r"c^2=a^2+b^2", 94, 390, 53, "#122B58")
    c.label("标准方程  /  横轴型", 62, 502, 24, "#135FAD", bold=True)
    c.math(r"\frac{x^2}{a^2}-\frac{y^2}{b^2}=1\quad(a,b>0)", 1008, 501, 25, "#15375F", ha="right")
    c.box(62, 532, 956, 502, "#FFFFFF", edge="#B9DBF3", radius=26)
    geom(c, origin=(506, 790), scale=48, bounds=(88, 551, 992, 1013),
         colors=("#94B7D5", "#1675D1", "#2671D5", "#12A28F", "#DD8C17"))
    c.box(62, 1054, 956, 196, "#E9FAF0", edge="#8BDDB2", radius=25)
    c.label("看图得关系", 94, 1102, 27, "#11764D", bold=True)
    c.math(r"OA=a,\quad AB=b,\quad OB=OF_2=c", 94, 1157, 31, "#123C48")
    c.label("B 是辅助矩形角点，不在曲线上，也不是焦点。", 94, 1210, 23, "#256957")
    c.box(62, 1271, 956, 65, "#DFF4EC", edge="#AFE0CA", radius=18)
    c.label("一眼记忆  ·  斜边与半焦距等长，但不是同一线段。",
            90, 1314, 22, "#155C49", bold=True)
    return c


def style_b():
    c = Card("B", "#F7F3E9")
    c.line(73, 116, 1007, 116, "#3A5870", 2)
    c.label("MATH NOTE    02 / CONIC SECTIONS", 73, 94, 19, "#6F8190")
    c.label("双曲线的 a、b、c 关系", 73, 216, 51, "#23374A", bold=True)
    c.label("从辅助三角形看半焦距", 73, 273, 29, "#597284")
    c.math(r"\frac{x^2}{a^2}-\frac{y^2}{b^2}=1\qquad (a>0,\ b>0)",
           73, 344, 30, "#32495C")
    c.line(73, 383, 1007, 383, "#AAB8B8", 1.5)
    geom(c, origin=(505, 730), scale=57, bounds=(84, 406, 998, 1085),
         colors=("#A4B4BA", "#386A8E", "#356A9A", "#3B8A7C", "#B78143"),
         curve_width=4)
    c.line(73, 1093, 1007, 1093, "#AAB8B8", 1.5)
    c.label("图 1", 73, 1143, 24, "#7A6551", bold=True)
    c.label("O、A、B 构成辅助直角三角形。", 157, 1143, 26, "#354C5B")
    c.label("B 是辅助矩形角点，不在曲线上，也不是焦点。", 73, 1183, 24, "#354C5B")
    c.math(r"OA=a,\quad AB=b,\quad OB=OF_2=c", 73, 1235, 31, "#23374A")
    c.math(r"c^2=a^2+b^2", 73, 1299, 39, "#2D617D")
    c.label("同长不重合：斜边与焦距是不同线段。", 1007, 1299, 22, "#6D7D81", ha="right")
    common(c, ink="#23374A", muted="#71818A", accent="#426E8A")
    return c


def style_c():
    c = Card("C", "#EAF5FF")
    c.gradient(0, 243, "#102B69", "#1B78BF")
    c.label("02  /  看懂双曲线", 68, 76, 24, "#A7F1F1", bold=True)
    c.label("为什么 c 比 a、b 都长？", 68, 162, 48, "#FFFFFF", bold=True)
    c.box(64, 263, 952, 714, "#FFFFFF", edge="#A7D3EF", radius=25)
    c.label("真实坐标图  ·  同一比例", 94, 312, 24, "#1877B6", bold=True)
    geom(c, origin=(510, 652), scale=58, bounds=(85, 327, 994, 958),
         colors=("#A8BECD", "#176DE4", "#195FED", "#00A994", "#F28D32"),
         curve_width=6)
    c.box(64, 999, 952, 188, "#0E3A67", radius=26)
    c.label("把长度看成直角三角形", 96, 1049, 25, "#91EAE0", bold=True)
    c.math(r"c^2=a^2+b^2", 96, 1130, 56, "#FFFFFF")
    c.math(r"\frac{x^2}{a^2}-\frac{y^2}{b^2}=1", 1014, 1131, 25, "#D3EBFF", ha="right")
    c.math(r"OA=a,\quad AB=b,\quad OB=OF_2=c", 66, 1236, 30, "#143D68")
    c.label("B 是辅助矩形角点，不在曲线上，也不是焦点。", 66, 1295, 22, "#45647B")
    c.math(r"a>0,\ b>0", 1010, 1295, 24, "#45647B", ha="right")
    common(c, ink="#143D68", muted="#527995", accent="#1469AA")
    return c


def style_d():
    c = Card("D", "#FFF9EB")
    for y in range(150, 1370, 46):
        c.box(59, y, 966, 1, "#DDECE8", radius=0)
    c.box(110, 0, 2, 1440, "#E8C2B0", radius=0)
    c.box(152, 62, 844, 190, "#E9F2EE", edge="#B7D6CB", radius=19)
    c.label("知树笔记   /   C043 · 快懂", 181, 118, 24, "#437C77", bold=True)
    c.label("双曲线 a、b、c 怎么连起来？", 181, 205, 42, "#24435A", bold=True)
    c.box(164, 288, 825, 166, "#FFF2C9", edge="#E7D08C", radius=16)
    c.label("先记住", 191, 336, 25, "#A16C2B", bold=True)
    c.math(r"c^2=a^2+b^2", 191, 403, 47, "#24435A")
    c.label("把三段长度放进同一坐标系 ↓", 162, 511, 24, "#46817B", bold=True)
    geom(c, origin=(552, 787), scale=49, bounds=(142, 534, 998, 1049),
         colors=("#AFC8C2", "#578AB7", "#5B8EC9", "#47A58F", "#D58C50"),
         curve_width=4)
    c.box(162, 1076, 827, 214, "#EAF5F1", edge="#BADBD0", radius=18)
    c.label("图上做标记", 190, 1126, 25, "#2D7C71", bold=True)
    c.math(r"OA=a,\quad AB=b,\quad OB=OF_2=c", 190, 1183, 29, "#24435A")
    c.label("B 是辅助矩形角点：不在曲线上，也不是焦点。", 190, 1230, 22, "#476B6C")
    c.label("斜边与半焦距等长，但不是同一条线段。", 190, 1273, 21, "#476B6C")
    c.math(r"\frac{x^2}{a^2}-\frac{y^2}{b^2}=1\quad(a,b>0)", 163, 1324, 25, "#55747A")
    return c


def style_e():
    c = Card("E", "#0B1830")
    c.gradient(0, 1440, "#09172B", "#163252")
    c.label("ZHISHU    /    C043   002", 70, 86, 24, "#74D5D7", bold=True)
    c.label("双曲线的几何骨架", 70, 179, 50, "#EEF8FF", bold=True)
    c.label("a、b 是直角边；c 是辅助斜边与半焦距。", 70, 242, 26, "#B7CEDC")
    geom(c, origin=(515, 704), scale=57, bounds=(89, 328, 995, 1030),
         colors=("#7292A9", "#69B7FF", "#68A8FF", "#55D9BF", "#FFA35B"),
         curve_width=5)
    c.line(71, 1041, 1009, 1041, "#42647D", 1.5)
    c.math(r"c^2=a^2+b^2", 71, 1131, 54, "#F5FAFF")
    c.math(r"\frac{x^2}{a^2}-\frac{y^2}{b^2}=1", 1009, 1126, 27, "#A8C5DD", ha="right")
    c.math(r"a>0,\ b>0", 1009, 1198, 22, "#A8C5DD", ha="right")
    c.math(r"OA=a,\quad AB=b,\quad OB=OF_2=c", 71, 1213, 29, "#A9EAE2")
    c.label("B 是辅助矩形角点，不在双曲线上，也不是焦点。", 71, 1271, 24, "#D3E3E9")
    c.label("斜边与半焦距等长，但不是同一条线段。", 71, 1314, 22, "#A6C1D1")
    common(c, ink="#EEF8FF", muted="#A8C5D1", accent="#74D5D7")
    return c


def style_f():
    c = Card("F", "#F4F8F7")
    c.box(0, 0, 1080, 116, "#143C5A", radius=0)
    c.label("结构图解  /  C043", 65, 76, 29, "#FFFFFF", bold=True)
    c.label("002  快懂", 1010, 76, 25, "#A3E5DB", bold=True, ha="right")
    c.label("从三段长度，到一个关系式", 65, 204, 48, "#183B51", bold=True)
    c.label("标准横轴型", 65, 270, 23, "#55798A", bold=True)
    c.math(r"\frac{x^2}{a^2}-\frac{y^2}{b^2}=1\quad(a,b>0)", 1009, 267, 26, "#224B63", ha="right")
    c.box(65, 315, 950, 166, "#FFFFFF", edge="#D0E1E3", radius=22)
    for x, sym, word, color in ((176, "a", "OA", "#3176BE"),
                                 (502, "b", "AB", "#139985"),
                                 (828, "c", "OB = OF2", "#CC7740")):
        c.box(x-91, 341, 182, 105, color, radius=18)
        c.math(sym, x, 372, 38, "#FFFFFF", ha="center")
        if sym == "c":
            c.math(r"OB=OF_2", x, 428, 20, "#FFFFFF", ha="center")
        else:
            c.label(word, x, 437, 22, "#FFFFFF", ha="center", bold=True)
    c.label("直角边", 339, 421, 20, "#698998", ha="center")
    c.label("直角边", 665, 421, 20, "#698998", ha="center")
    c.label("↓  对应到同一坐标图", 540, 535, 23, "#2C7281", ha="center", bold=True)
    c.box(65, 567, 950, 577, "#FFFFFF", edge="#D0E1E3", radius=22)
    geom(c, origin=(510, 855), scale=50, bounds=(91, 598, 989, 1118),
         colors=("#9DB7C3", "#347CB7", "#3176BE", "#139985", "#CC7740"),
         curve_width=4.5)
    c.box(65, 1170, 950, 143, "#DFF2EB", edge="#A8D7C6", radius=20)
    c.math(r"c^2=a^2+b^2", 95, 1228, 42, "#164963")
    c.label("B 是辅助矩形角点，不在曲线上，也不是焦点。", 95, 1280, 22, "#396B68")
    c.label("斜边与半焦距等长，但不是同一条线段。", 65, 1350, 22, "#55798A")
    return c


STYLES = {"A": style_a, "B": style_b, "C": style_c,
          "D": style_d, "E": style_e, "F": style_f}


def sheet(path, images, *, card_width, columns, title):
    gap, label_h, margin = 22, 62, 28
    card_h = round(card_width * 4/3)
    rows = math.ceil(len(images)/columns)
    width = margin*2 + columns*card_width + (columns-1)*gap
    height = 96 + rows*(card_h+label_h) + (rows-1)*gap + margin
    bg = Image.new("RGB", (width, height), "#EAF0F5")
    draw = ImageDraw.Draw(bg)
    font_path = Path("C:/Windows/Fonts/msyh.ttc")
    font = ImageFont.truetype(str(font_path), 25) if font_path.exists() else ImageFont.load_default()
    draw.text((margin, 28), title, fill="#173B55", font=font)
    for i, (key, img) in enumerate(images):
        row, col = divmod(i, columns)
        x = margin + col*(card_width+gap)
        y = 96 + row*(card_h+label_h+gap)
        label = f"STYLE {key}  /  {NAMES[key][1]}"
        draw.text((x, y), label, fill="#173B55", font=font)
        thumb = img.resize((card_width, card_h), Image.Resampling.LANCZOS)
        bg.paste(thumb, (x, y+label_h))
    bg.save(path)


def main():
    if not (SOURCE / "01_statement.tex").exists():
        raise SystemExit("Run from an intact C043 workspace")
    formal = (SOURCE / "01_statement.tex").read_text(encoding="utf-8")
    explanation = (SOURCE / "02_explanation.tex").read_text(encoding="utf-8")
    proof = (SOURCE / "03_proof.tex").read_text(encoding="utf-8")
    assert all(s in formal for s in (r"\frac{x^2}{a^2}", r"\frac{y^2}{b^2}",
                                     "c^2 = a^2 + b^2", "a>0, b>0"))
    assert "直角三角形" in explanation and "b^2 = c^2 - a^2" in proof
    model_checks = validation_results()
    OUT.mkdir(parents=True, exist_ok=True)
    full, mobile = [], []
    report = {"uid": "C043", "card": "002", "size": [W, H],
              "model": {"a": 3, "b": 4, "c": 5, "checks": model_checks},
              "source_agreement": "PASS", "styles": {}}
    for key, make in STYLES.items():
        started = time.perf_counter()
        folder = OUT / f"{key}_{NAMES[key][0]}"
        folder.mkdir(exist_ok=True)
        c = make()
        coverage = c.label_layout.finalize()
        text_audit = c.audit_text()
        png, svg = folder / "002.png", folder / "002.svg"
        c.export(png, svg)
        im = Image.open(png).convert("RGB")
        assert im.size == (W, H)
        previews = {}
        for width in (360, 390):
            dest = folder / f"002_mobile_{width}.png"
            im.resize((width, round(width*4/3)), Image.Resampling.LANCZOS).save(dest)
            previews[str(width)] = str(dest.relative_to(ROOT))
        note = {"style": key, "name": NAMES[key][1],
                "design": DESIGN[key],
                "geometry": "C043 Hyperbola(3,4), same isotropic coordinates",
                "math_facts": ["x²/a²-y²/b²=1; a,b>0", "c²=a²+b²", "O=(0,0)",
                               "A=(a,0)", "B=(a,b), auxiliary corner, not on curve or focus",
                               "F₂=(c,0)", "OA=a", "AB=b", "OB=OF₂=c, distinct segments"],
                "preview": previews, "layout_labels": c.layout_report,
                "coverage": coverage, "text_audit": text_audit,
                "png_sha256": hashlib.sha256(png.read_bytes()).hexdigest(),
                "render_seconds": round(time.perf_counter()-started, 3)}
        (folder / "style_notes.json").write_text(json.dumps(note, ensure_ascii=False, indent=2), encoding="utf-8")
        report["styles"][key] = {"name": NAMES[key][1], "png": str(png.relative_to(ROOT)),
                                  "svg": str(svg.relative_to(ROOT)), "mobile": previews,
                                  "design": DESIGN[key], "render_seconds": note["render_seconds"],
                                  "sha256": note["png_sha256"],
                                  "label_count": len(c.layout_report),
                                  "coverage": coverage, "text_audit": text_audit}
        full.append((key, im))
        mobile.append((key, Image.open(folder / "002_mobile_360.png").convert("RGB")))
    sheet(OUT / "style_contact_sheet.png", full, card_width=540, columns=3,
          title="C043-002  /  六种视觉方案  ·  等比例对照")
    sheet(OUT / "style_contact_sheet_mobile.png", mobile, card_width=360, columns=3,
          title="C043-002  /  360px 手机阅读对照")
    (OUT / "style_comparison_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Rendered 6 styles to {OUT}")


if __name__ == "__main__":
    main()
