"""C088: a moving asymptote intercept, then the user's x-axis split proof."""
from pathlib import Path
import sys
import math
import numpy as np
from manim import *

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import AreaModel

config.frame_width = 9
config.frame_height = 16
config.background_color = '#F7F8FA'

BG = '#F7F8FA'
INK = '#213044'
MUTED = '#526275'
BLUE = '#2778BD'
ORANGE = '#CD6031'
PURPLE = '#8873A4'
GREEN = '#158068'
GOLD = '#B77D12'
AXIS = '#A7B4C2'


class C088AreaProduct(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.x2 = ValueTracker(3)
        self.split = ValueTracker(0)
        self.unit = 1.28
        self.origin = np.array([-2.5, 1.1, 0.])

        def pt(x, y):
            return self.origin + self.unit * np.array([x, y, 0.])

        def model():
            return AreaModel(2 / 3, 3, self.x2.get_value())

        def cn(s, size, y, color=INK):
            obj = Text(s, font='Microsoft YaHei', font_size=size, color=color)
            if obj.width > 8:
                obj.scale_to_fit_width(8)
            return obj.move_to([0, y, 0])

        def formula(s, y, size=34, color=INK):
            obj = MathTex(s, font_size=size, color=color)
            if obj.width > 7.9:
                obj.scale_to_fit_width(7.9)
            return obj.move_to([0, y, 0])

        title = cn('横坐标的乘积，为什么是面积？', 32, 7.08)
        subtitle = cn('A、B 在渐近线上，演示横坐标同为正', 22, 6.35, MUTED)
        setting = formula(r'\frac{x^2}{9}-\frac{y^2}{4}=1,\quad k=\frac ba=\frac23', 5.55, 30)
        footer = VGroup(
            cn('查结论 · 看图解 · 学证明｜知树 App', 20, -6.65, MUTED),
            cn('公众号 ok-shuxue｜获取入口', 18, -7.23, MUTED),
        )
        footer.set_z_index(20)

        axes = VGroup(
            Arrow(pt(-.25, 0), pt(4.2, 0), buff=0, color=AXIS, stroke_width=2, max_tip_length_to_length_ratio=.025),
            Arrow(pt(0, -2.5), pt(0, 2.65), buff=0, color=AXIS, stroke_width=2, max_tip_length_to_length_ratio=.025),
            MathTex('x', color=MUTED, font_size=28).move_to(pt(4.42, 0)),
            MathTex('y', color=MUTED, font_size=28).move_to(pt(0, 2.88)),
        )
        # Only the visible right branch is needed: its vertex is at (3,0).
        # t=+-1 gives x=4.63; clip t to keep the entire curve within the canvas.
        hyperbola = ParametricFunction(
            lambda t: pt(3 * math.cosh(t), 2 * math.sinh(t)),
            t_range=[-.85, .85], color='#CDD5DE', stroke_width=2,
        )
        asymptotes = VGroup(
            Line(pt(-.12, -.08), pt(3.85, 2 * 3.85 / 3), color=BLUE, stroke_width=3),
            DashedLine(pt(-.12, .08), pt(3.65, -2 * 3.65 / 3), color=PURPLE, stroke_width=2.6, dash_length=.12),
        )
        gplus = MathTex(r'y=kx', color=BLUE, font_size=27).move_to(pt(2.95, 2.65))
        gminus = MathTex(r'y=-kx', color=PURPLE, font_size=27).move_to([2.7, -1.3, 0])
        o = VGroup(Dot(pt(0, 0), radius=.055, color=INK), MathTex('O', color=INK, font_size=28).move_to(pt(-.22, -.24)))
        a = VGroup(Dot(pt(*model().A), radius=.07, color=BLUE), MathTex('A', color=BLUE, font_size=30).next_to(pt(*model().A), UP, buff=.14))
        bdot = always_redraw(lambda: Dot(pt(*model().B), radius=.075, color=ORANGE))
        blabel = MathTex('B', color=ORANGE, font_size=30)
        blabel.add_updater(lambda obj: obj.next_to(pt(*model().B), DOWN + LEFT, buff=.12))
        segment = always_redraw(lambda: Line(pt(*model().A), pt(*model().B), color=ORANGE, stroke_width=3.4))
        whole = always_redraw(lambda: Polygon(pt(0, 0), pt(*model().A), pt(*model().B), stroke_width=0,
                                              fill_color=GREEN, fill_opacity=.23 * (1 - self.split.get_value())))
        upper = always_redraw(lambda: Polygon(pt(0, 0), pt(model().intercept, 0), pt(*model().A),
                                              stroke_width=0, fill_color=ORANGE, fill_opacity=.24 * self.split.get_value()))
        lower = always_redraw(lambda: Polygon(pt(0, 0), pt(*model().B), pt(model().intercept, 0),
                                              stroke_width=0, fill_color=GREEN, fill_opacity=.3 * self.split.get_value()))
        projections = VGroup(
            DashedLine(pt(*model().A), pt(3, 0), color=BLUE, stroke_width=2, dash_length=.1),
            always_redraw(lambda: DashedLine(pt(*model().B), pt(model().x2, 0), color=ORANGE, stroke_width=2, dash_length=.1)),
        )

        # Dimension lines live below the mathematical figure, away from labels.
        x1dim = VGroup(DoubleArrow([-2.5, -2.47, 0], [1.34, -2.47, 0], buff=0, color=BLUE, stroke_width=2,
                                   max_tip_length_to_length_ratio=.04),
                        MathTex(r'x_1=3', font_size=28, color=BLUE).move_to([-.58, -2.73, 0]))
        x2line = always_redraw(lambda: DoubleArrow([-2.5, -3.1, 0], [pt(model().x2, 0)[0], -3.1, 0],
                                                   buff=0, color=ORANGE, stroke_width=2, max_tip_length_to_length_ratio=.06))
        x2label = MathTex(r'x_2\approx', font_size=28, color=ORANGE)
        x2value = DecimalNumber(3, num_decimal_places=2, font_size=28, color=ORANGE)
        x2readout = VGroup(x2label, x2value)
        def update_x2(obj):
            x2value.set_value(model().x2)
            obj.arrange(RIGHT, buff=.07).move_to([(pt(model().x2, 0)[0] - 2.5) / 2, -3.38, 0])
        x2readout.add_updater(update_x2)

        status = cn('固定 A，沿渐近线移动 B', 25, -4.03)
        area_label = MathTex(r'S=kx_1x_2\approx', font_size=36, color=GREEN)
        area_number = DecimalNumber(6, num_decimal_places=2, font_size=36, color=GREEN)
        readout = VGroup(area_label, area_number)
        def update_area(obj):
            area_number.set_value(model().area)
            obj.arrange(RIGHT, buff=.13).move_to([0, -4.85, 0])
        readout.add_updater(update_area)
        note = cn('截线改变，面积随之改变', 23, -5.65, MUTED)

        cgroup = always_redraw(lambda: VGroup(
            Dot(pt(model().intercept, 0), radius=.065, color=GOLD),
            MathTex('C', font_size=28, color=GOLD).next_to(pt(model().intercept, 0), DOWN + RIGHT, buff=.13),
            Line(pt(0, 0), pt(model().intercept, 0), color=GOLD, stroke_width=4),
        ))
        height_a = MathTex(r'kx_1', font_size=28, color=ORANGE).next_to(pt(3, 1), RIGHT, buff=.16)
        height_b = MathTex(r'kx_2', font_size=28, color=GREEN).next_to(pt(1.5, -.5), LEFT, buff=.16)
        rights = VGroup(
            VMobject(color=INK, stroke_width=1.4).set_points_as_corners([pt(2.86, 0), pt(2.86, .14), pt(3, .14)]),
            VMobject(color=INK, stroke_width=1.4).set_points_as_corners([pt(1.64, 0), pt(1.64, -.14), pt(1.5, -.14)]),
        )
        phi = math.atan2(2, 1)
        angles = VGroup(Arc(radius=.25, start_angle=0, angle=phi, color=GOLD, stroke_width=2).move_arc_center_to(pt(2, 0)),
                        Arc(radius=.25, start_angle=PI, angle=phi, color=GOLD, stroke_width=2).move_arc_center_to(pt(2, 0)))
        construction = VGroup(cgroup, height_a, height_b, rights, angles)

        # A static opening wait can be cached without invoking updaters. Lay out
        # every tracked label now so frame zero is identical to the loop end.
        for tracked in (blabel, x2readout, readout):
            tracked.update(0)
        assert abs(readout.get_center()[1] + 4.85) < 1e-8
        assert abs(x2readout.get_center()[1] + 3.38) < 1e-8

        self.add(title, subtitle, setting, footer, whole, upper, lower, axes, hyperbola, asymptotes,
                 projections, segment, o, a, bdot, blabel, gplus, gminus, x1dim, x2line, x2readout, status, readout, note)
        self.wait(1.2)
        self.play(self.x2.animate.set_value(1.5), run_time=3, rate_func=smooth)
        note2 = cn('横坐标减半，面积也减半', 23, -5.65, MUTED)
        self.play(Transform(note, note2), run_time=.3)
        self.wait(1.1)
        note.become(cn('截线改变，面积随之改变', 23, -5.65, MUTED))
        self.play(self.x2.animate.set_value(2.4), run_time=2, rate_func=smooth)
        self.wait(.5)
        self.play(self.x2.animate.set_value(1.5), run_time=1.6, rate_func=smooth)
        self.wait(.4)

        cformula = formula(r'OC=\frac{2x_1x_2}{x_1+x_2}=2', -4.85, 34, GOLD)
        similarity = formula(r'\frac{x_1-c}{c-x_2}=\frac{kx_1}{kx_2}=\frac{x_1}{x_2}', -5.7, 29)
        newstatus = cn('先用相似，求横轴交点 C', 25, -4.03)
        self.play(Transform(status, newstatus), FadeOut(readout), FadeOut(note),
                  FadeIn(construction), FadeIn(cformula), FadeIn(similarity), run_time=.8)
        self.wait(2.4)
        splitformula = formula(r'S=\frac12\,OC\,(kx_1+kx_2)', -4.85, 34, GREEN)
        numbers = formula(r'OC=2,\quad S=2+1=3', -5.7, 31)
        self.play(Transform(status, cn('两块共底 OC，面积直接相加', 25, -4.03)),
                  Transform(cformula, splitformula), Transform(similarity, numbers),
                  self.split.animate.set_value(1), run_time=1.1)
        self.wait(3)
        final = formula(r'S_{\triangle OAB}=\frac ba\,|x_1x_2|', -4.85, 38, GREEN)
        final_note = cn('一般情形取绝对值，面积不一定恒定', 22, -5.7, MUTED)
        self.play(Transform(status, cn('两个横坐标的乘积，决定面积', 25, -4.03)),
                  Transform(cformula, final), FadeOut(similarity), FadeIn(final_note), run_time=.6)
        self.wait(2.5)

        # Restore the same mathematical and visual state for a quiet loop.
        self.play(FadeOut(construction), FadeOut(cformula), FadeOut(final_note),
                  self.split.animate.set_value(0),
                  Transform(status, cn('固定 A，沿渐近线移动 B', 25, -4.03)), run_time=.6)
        self.play(self.x2.animate.set_value(3), run_time=1.6, rate_func=smooth)
        note.become(cn('截线改变，面积随之改变', 23, -5.65, MUTED))
        self.play(FadeIn(readout), FadeIn(note), run_time=.3)
        self.wait(.7)
