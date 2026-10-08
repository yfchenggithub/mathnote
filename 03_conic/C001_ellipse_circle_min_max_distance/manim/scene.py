"""C001 vertical teaching animation. Render C001DistancePilot with Manim CE 0.21.0."""

from __future__ import annotations

from manim import (
    Axes, Circle, Create, DecimalNumber, Dot, Ellipse, LEFT, Line, MathTex,
    RIGHT, Scene, Text, UP, ValueTracker, VGroup, always_redraw, config, linear,
)

from math_model import (
    M, ellipse_point, intersection_points, minimum_distance, nearest_pair,
)


config.frame_width = 9
config.frame_height = 16

BG = "#F9FAFC"
INK = "#183047"
MUTED = "#6F8295"
BLUE_E = "#2377C4"
RED_C = "#E45361"
GOLD = "#E8AA28"
GREEN_I = "#25A080"
FONT = "Microsoft YaHei"


class C001DistancePilot(Scene):
    """The changing radius crosses two tangent thresholds; all points use math_model."""

    def construct(self):
        self.camera.background_color = BG
        radius = ValueTracker(0.5)

        axes = Axes(
            x_range=[-4, 8, 2], y_range=[-4, 4, 2],
            x_length=7.8, y_length=5.2, tips=False,
            axis_config={"color": "#CAD4DE", "stroke_width": 1.5},
        ).move_to([0, 1.4, 0])
        origin = axes.c2p(0, 0)
        unit = axes.c2p(1, 0)[0] - origin[0]
        center = axes.c2p(*M)

        ellipse = axes.plot_parametric_curve(
            lambda t: ellipse_point(t), t_range=[0, 6.283185307179586],
            color=BLUE_E, stroke_width=5,
        )
        circle = always_redraw(lambda: Circle(
            radius=unit * radius.get_value(), color=RED_C, stroke_width=4.5,
        ).move_to(center))
        points = always_redraw(lambda: self._closest_objects(axes, radius.get_value()))

        self.add(axes, ellipse, circle, points, Dot(center, radius=0.07, color=INK))

        # Opaque panels keep the large circle from crossing the interface.
        from manim import Rectangle
        top_panel = Rectangle(width=9, height=2.8, fill_color=BG, fill_opacity=1,
                              stroke_opacity=0).move_to([0, 6.9, 0])
        bottom_panel = Rectangle(width=9, height=5.05, fill_color=BG, fill_opacity=1,
                                 stroke_opacity=0).move_to([0, -5.48, 0])
        self.add(top_panel, bottom_panel)

        title = Text("椭圆到圆周的最短距离", font=FONT, font_size=34,
                     color=INK, weight="BOLD").move_to([0, 7.15, 0])
        subtitle = Text("圆心固定 · 半径 r 连续变化", font=FONT, font_size=25,
                        color=MUTED).move_to([0, 6.38, 0])
        e_label = Text("蓝：椭圆 E", font=FONT, font_size=25, color=BLUE_E)
        c_label = Text("红：圆周 Γ", font=FONT, font_size=25, color=RED_C)
        VGroup(e_label, c_label).arrange(RIGHT, buff=0.6).move_to([0, 5.63, 0])
        m_label = Text("M", font=FONT, font_size=19, color=INK).move_to(
            center + RIGHT * 0.19 + UP * 0.02
        )
        self.add(title, subtitle, e_label, c_label, m_label)

        # Same number line and scale throughout: r enters, stays in, then exits [1,7].
        yline = -4.17
        pos = lambda value: (-3.57 + value * 0.86, yline, 0)
        base = Line(pos(0), pos(8.25), color="#B4C2D0", stroke_width=3)
        interval = Line(pos(1), pos(7), color=GREEN_I, stroke_width=9)
        marker = always_redraw(lambda: Dot(pos(radius.get_value()), radius=0.115, color=RED_C))
        ticks = VGroup(*[
            Line((pos(v)[0], yline - 0.12, 0), (pos(v)[0], yline + 0.12, 0),
                 color=MUTED, stroke_width=2) for v in (1, 7)
        ])
        tick_labels = VGroup(
            Text("1", font=FONT, font_size=24, color=INK).move_to((pos(1)[0], yline - .4, 0)),
            Text("7", font=FONT, font_size=24, color=INK).move_to((pos(7)[0], yline - .4, 0)),
        )
        interval_label = Text("圆心到椭圆的距离范围 [1, 7]", font=FONT,
                              font_size=24, color=GREEN_I).move_to([0, -3.55, 0])
        self.add(interval_label, base, interval, ticks, tick_labels, marker)

        r_label = MathTex("r=", color=INK, font_size=36).move_to([-2.55, -5.07, 0])
        r_num = DecimalNumber(radius.get_value(), num_decimal_places=1,
                              font_size=36, color=RED_C).move_to([-1.25, -5.07, 0])
        r_num.add_updater(lambda d: d.set_value(radius.get_value()))
        d_label = MathTex("D_{\\min}=", color=INK, font_size=36).move_to([0.9, -5.07, 0])
        d_num = DecimalNumber(minimum_distance(radius.get_value()),
                              num_decimal_places=1, font_size=36, color=GOLD).move_to([3.0, -5.07, 0])
        d_num.add_updater(lambda d: d.set_value(minimum_distance(radius.get_value())))
        self.add(r_label, r_num, d_label, d_num)

        state = Text("圆周扩大：间隙逐渐缩小", font=FONT, font_size=27,
                     color=INK).move_to([0, -5.89, 0])
        formula = MathTex(r"D_{\min}=\operatorname{dist}(r,[1,7])",
                          color=INK, font_size=37).move_to([0, -6.92, 0])
        self.add(state, formula)

        self.play(Create(ellipse), run_time=1.0)
        self.wait(0.3)
        self.play(radius.animate.set_value(1), run_time=2.0, rate_func=linear)
        state = self._change_state(state, "第一次相切：最短距离为 0")
        self.wait(0.7)
        state = self._change_state(state, "继续变大：两个交点沿椭圆移动")
        self.play(radius.animate.set_value(4), run_time=3.2, rate_func=linear)
        self.wait(0.6)
        self.play(radius.animate.set_value(7), run_time=3.2, rate_func=linear)
        state = self._change_state(state, "第二次相切：最短距离仍为 0")
        self.wait(0.7)
        state = self._change_state(state, "越过临界半径：间隙重新增大")
        self.play(radius.animate.set_value(8), run_time=2.0, rate_func=linear)
        self.wait(1.0)

    def _change_state(self, old, message):
        new = Text(message, font=FONT, font_size=27, color=INK).move_to(old)
        self.remove(old)
        self.add(new)
        self.wait(0.25)
        return new

    @staticmethod
    def _closest_objects(axes, radius):
        intersections = intersection_points(radius)
        if intersections:
            return VGroup(*[
                Dot(axes.c2p(*p), radius=0.09, color=GOLD) for p in intersections
            ])
        p, q = nearest_pair(radius)
        return VGroup(
            Line(axes.c2p(*p), axes.c2p(*q), color=GOLD, stroke_width=6),
            Dot(axes.c2p(*p), radius=0.075, color=GOLD),
            Dot(axes.c2p(*q), radius=0.075, color=GOLD),
        )


class EnvironmentSmokeTest(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(Text("椭圆与圆周", font=FONT, color=INK).to_edge(UP))
        self.add(MathTex(r"\frac{x^2}{9}+\frac{y^2}{4}=1", color=INK))
        self.add(Circle(radius=1, color=RED_C).shift(2 * LEFT))
        self.add(Ellipse(width=2.8, height=1.8, color=BLUE_E).shift(2 * RIGHT))
        r = ValueTracker(0.3)
        moving = always_redraw(lambda: Circle(radius=r.get_value(), color=RED_C).shift(2 * LEFT))
        self.add(moving)
        self.play(r.animate.set_value(1.2), run_time=0.5)
