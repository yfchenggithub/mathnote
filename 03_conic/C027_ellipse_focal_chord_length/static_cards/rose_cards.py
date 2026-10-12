"""C027 portrait cards in the supplied rose visual language."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from .cards import Painter, W, H


WINE = "#69062c"
ROSE = "#ce2d62"
PINK = "#f3a4c0"
INK = "#25121f"
MUTED = "#90536b"


class RosePainter(Painter):
    def __init__(self, number: str, kind: str, subtitle: str):
        yy, xx = np.mgrid[0:H, 0:W]
        t = np.clip(.50*xx/W + .50*yy/H, 0, 1)
        a = np.array([255, 252, 252]); b = np.array([253, 235, 241])
        rgb = (a[None, None, :]*(1-t[:, :, None]) +
               b[None, None, :]*t[:, :, None]).astype("uint8")
        self.im = Image.fromarray(rgb, "RGB").convert("RGBA")
        self.d = ImageDraw.Draw(self.im)
        self.boxes = []
        self.image_boxes = []
        self.kind = kind
        self.number = number
        self.decor()
        self.header(kind, subtitle)

    def decor(self):
        self.d.ellipse((706, 138, 995, 322), fill="#ffe3ed")
        self.d.ellipse((-60, 1430, 140, 1650), fill="#fff2f7")
        self.d.arc((33, 217, 777, 313), 191, 346, fill="#ec7aa4", width=5)
        self.d.ellipse((811, 173, 826, 188), fill="#ed8eaf")
        self.d.ellipse((855, 208, 863, 216), fill="#ed8eaf")

    def header(self, kind, subtitle):
        self.gradient_strip((36, 31, 151, 91), "#ed779b", "#c51c53", 21)
        self.text(self.number, 56, 38, 38, "#ffffff", True)
        self.text(kind, 171, 36, 43, ROSE, True)
        self.d.line((296, 65, 675, 65), fill="#edb7c9", width=2)
        self.text("Zhishu", 690, 30, 35, "#efa3be")
        self.text("手握公式  心中有数", 695, 78, 17, ROSE)
        self.text("椭圆焦点弦长公式", 42, 125, 66, WINE, True)
        self.rounded((38, 230, 540, 279), "#fbd9e5", 24)
        self.text(subtitle, 68, 236, 26, WINE)
        # Open-book icon made from vector primitives; no false QR code.
        self.d.polygon([(780, 212), (834, 217), (850, 273), (791, 269)],
                       fill="#ffd4e3", outline="#ed85aa")
        self.d.polygon([(850, 273), (901, 256), (910, 198), (842, 215)],
                       fill="#ffeaf1", outline="#ed85aa")
        self.text("数学", 849, 220, 17, ROSE, True)

    def panel(self, y0, y1, number, title):
        self.rounded((21, y0, 920, y1), "#fffdfd", 25, "#ffffff", 2, True)
        self.gradient_strip((34, y0+13, 905, y0+66), "#f9cfde", "#fff9fb", 17)
        self.gradient_strip((34, y0+13, 91, y0+70), "#ea7098", "#c82458", 17)
        self.text(str(number), 51, y0+17, 38, "#ffffff", True)
        self.text(title, 112, y0+19, 32, WINE, True)

    def footer(self):
        self.d.line((42, 1623, 896, 1623), fill="#e9adc0", width=2)
        self.text("知树 · OK数学", 49, 1630, 19, MUTED)
        self.text("每一个公式，都是通往更高处的阶梯。", 382, 1631, 17, MUTED)


def _row(p, number, y, title, body):
    p.small_num(number, 53, y, ROSE)
    p.text(title, 112, y-2, 27, WINE, True)
    p.text(body, 112, y+40, 25, INK)


def card_001(geometry: Path, output: Path):
    p = RosePainter("001", "快记", "二级结论  /  焦点弦")
    p.panel(310, 600, 1, "适用条件")
    _row(p, 1, 390, "标准椭圆", "长轴沿 x 轴，a > b > 0")
    p.math(r"\frac{x^2}{a^2}+\frac{y^2}{b^2}=1", 530, 390, 30, WINE)
    _row(p, 2, 470, "直线过焦点", "F(±c,0)，c² = a² − b²")
    p.small_num(3, 53, 545, ROSE)
    p.text("交于 P、Q 两点，求 |PQ|", 112, 543, 26, WINE, True)

    p.panel(615, 1058, 2, "核心公式")
    p.text("斜率 k 存在时", 64, 710, 28, INK)
    p.rounded((48, 780, 477, 920), "#fff0f5", 20, "#f8c4d5", 2)
    p.math(r"|PQ|=\frac{2ab^2(1+k^2)}{a^2k^2+b^2}", 62, 802, 44, ROSE)
    p.image(geometry/"general.png", 486, 682, scale=.72,
            within=(21, 615, 920, 1058))
    p.rounded((536, 964, 859, 1008), "#dc597f", 20)
    p.text("过焦点弦 · 精确示意", 554, 971, 22, "#ffffff")
    p.text("图示 a=3，b=2，k=0.65", 522, 1016, 19, MUTED)

    p.panel(1073, 1360, 3, "重要特例  /  通径")
    p.text("直线垂直 x 轴：x = c 或 x = −c", 63, 1160, 27, INK)
    p.text("斜率不存在；这条焦点弦叫通径。", 63, 1205, 26, INK)
    p.rounded((155, 1260, 772, 1333), "#ffe9f0", 21)
    p.math(r"|PQ|=\frac{2b^2}{a}", 304, 1271, 39, ROSE)

    p.panel(1375, 1608, 4, "识别信号")
    for i, (head, line) in enumerate((("先看椭圆", "焦点在 x 轴"),
                                      ("再看直线", "确实过焦点"),
                                      ("最后看方向", "垂直用通径"))):
        x = 47 + i*294
        p.rounded((x, 1467, x+268, 1565), "#fff0f5", 19)
        p.text(head, x+16, 1480, 25, ROSE, True)
        p.text(line, x+16, 1522, 22, INK)
    p.footer()
    return p.save(output)


def card_002(geometry: Path, output: Path):
    p = RosePainter("002", "快懂", "一眼理解  /  为什么成立")
    p.panel(310, 604, 1, "问题模型")
    p.text("过右焦点 F(c,0) 作直线", 56, 397, 26, INK)
    p.text("与椭圆交于 P、Q。", 56, 439, 26, INK)
    p.rounded((53, 492, 454, 561), "#fff0f5", 15)
    p.text("先求交点，再算两点间距离。", 70, 509, 22, ROSE)
    p.image(geometry/"general.png", 475, 335, scale=.70,
            within=(21, 310, 920, 604))

    p.panel(620, 830, 2, "先求交点所在直线")
    p.text("过 F(c,0)，斜率 k 存在时：", 54, 708, 27, INK)
    p.rounded((491, 694, 870, 781), "#fff0f5", 17)
    p.math(r"y=k(x-c)", 565, 712, 39, ROSE)

    p.panel(846, 1117, 3, "联立得到一元二次方程")
    p.text("将 y = k(x − c) 代入椭圆方程，整理得", 54, 931, 26, INK)
    p.rounded((55, 981, 876, 1074), "#fff0f5", 17)
    p.math(r"(a^2k^2+b^2)x^2-2a^2k^2cx", 85, 991, 29, WINE)
    p.math(r"+a^2k^2c^2-a^2b^2=0", 248, 1034, 28, WINE)

    p.panel(1133, 1433, 4, "根差乘方向系数 = 弦长")
    p.math(r"|PQ|=\sqrt{1+k^2}\,|x_1-x_2|", 59, 1214, 32, WINE)
    p.math(r"\Delta=4a^2b^4(1+k^2)", 59, 1273, 29, WINE)
    p.math(r"|x_1-x_2|=\frac{\sqrt{\Delta}}{a^2k^2+b^2}", 59, 1314, 27, WINE)
    p.rounded((425, 1274, 871, 1396), "#ffe7ef", 20)
    p.math(r"|PQ|=\frac{2ab^2(1+k^2)}{a^2k^2+b^2}", 453, 1301, 35, ROSE)
    p.text("由 c² = a² − b² 化简", 70, 1365, 22, MUTED)

    p.rounded((30, 1450, 912, 1608), "#fffafb", 23, "#ffffff", 2, True)
    p.gradient_strip((42, 1462, 899, 1510), "#f9cfde", "#fff9fb", 15)
    p.text("通径为什么要单独处理？", 62, 1469, 28, WINE, True)
    p.text("x = ±c 垂直 x 轴，斜率不存在；交点纵坐标为 ±b²/a。", 62, 1529, 23, INK)
    p.math(r"|PQ|=\frac{2b^2}{a}", 346, 1561, 29, ROSE)
    p.footer()
    return p.save(output)


def card_003(geometry: Path, output: Path):
    p = RosePainter("003", "快用", "一眼会用  /  识别 + 套用 + 防坑")
    p.panel(310, 567, 1, "解题识别步骤")
    for i, (head, body) in enumerate((("先看", "椭圆焦点是否在 x 轴"),
                                      ("再看", "直线是否过焦点"),
                                      ("后看", "斜率是否存在"))):
        y = 384+i*58
        p.small_num(i+1, 56, y, ROSE)
        p.text(head, 113, y, 26, ROSE, True)
        p.text(body, 210, y, 25, INK)

    p.panel(583, 936, 2, "公式选择")
    p.rounded((43, 677, 468, 884), "#fff0f5", 22)
    p.text("一般情形 · 斜率 k 存在", 65, 696, 26, ROSE, True)
    p.math(r"|PQ|=\frac{2ab^2(1+k^2)}{a^2k^2+b^2}", 65, 754, 38, ROSE)
    p.rounded((487, 677, 899, 884), "#fff0f5", 22)
    p.text("通径 · 直线 x = ±c", 510, 696, 26, ROSE, True)
    p.math(r"|PQ|=\frac{2b^2}{a}", 563, 762, 37, ROSE)

    p.panel(952, 1362, 3, "典型例题")
    p.text("已知椭圆", 55, 1037, 26, INK)
    p.math(r"\frac{x^2}{9}+\frac{y^2}{3}=1", 212, 1029, 30, WINE)
    p.text("过右焦点的直线斜率 k = 1，求 |PQ|。", 55, 1088, 26, INK)
    p.small_num(1, 54, 1152, ROSE)
    p.math(r"a=3,\quad b^2=3,\quad c=\sqrt{6}", 114, 1154, 29, WINE)
    p.small_num(2, 54, 1213, ROSE)
    p.math(r"|PQ|=\frac{2\cdot3\cdot3(1+1)}{9+3}=3", 114, 1213, 31, ROSE)
    p.image(geometry/"example.png", 549, 1108, scale=.58,
            within=(21, 952, 920, 1362))

    p.panel(1378, 1608, 4, "常见陷阱")
    for i, (head, body) in enumerate((("①", "不过焦点，不能直接套用"),
                                      ("②", "垂直 x 轴，斜率不存在"),
                                      ("③", "c² = a² − b²；分子用 b²"))):
        y = 1457+i*46
        p.text(head, 55, y, 25, ROSE, True)
        p.text(body, 107, y, 23, INK)
    p.footer()
    return p.save(output)


CARDS = {"001": card_001, "002": card_002, "003": card_003}
