"""C001 vertical teaching animation. Render C001DistancePilot with Manim CE 0.21.0."""

from __future__ import annotations

from manim import (
    Axes, Circle, DashedLine, DecimalNumber, Dot, Ellipse, FadeIn, FadeOut,
    LEFT, Line, MathTex, Rectangle, RIGHT, Scene, Text, UP, ValueTracker,
    VGroup, always_redraw, config, linear,
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
            x_range=[-4.2, 7, 2], y_range=[-3.5, 3.5, 2],
            x_length=8.6, y_length=5.375, tips=False,
            axis_config={"color": "#CAD4DE", "stroke_width": 1.5},
        ).move_to([0, 0.9, 0])
        origin = axes.c2p(0, 0)
        unit = axes.c2p(1, 0)[0] - origin[0]
        center = axes.c2p(*M)

        ellipse = axes.plot_parametric_curve(
            lambda t: ellipse_point(t), t_range=[0, 6.283185307179586],
            color=BLUE_E, stroke_width=5.5,
        ).set_z_index(1)
        circle = always_redraw(lambda: Circle(
            radius=unit * radius.get_value(), color=RED_C, stroke_width=5,
        ).move_to(center).set_z_index(2))
        points = always_redraw(lambda: self._closest_objects(
            axes, radius.get_value()
        ).set_z_index(3))

        # The panels are a fixed viewport: a large circle remains circular and
        # correctly scaled, while its off-screen arcs cannot cross the UI.
        self.add(axes, ellipse)
        top_panel = Rectangle(width=9, height=3.35, fill_color=BG, fill_opacity=1,
                              stroke_opacity=0).move_to([0, 6.325, 0]).set_z_index(10)
        bottom_panel = Rectangle(width=9, height=5.25, fill_color=BG, fill_opacity=1,
                                 stroke_opacity=0).move_to([0, -5.375, 0]).set_z_index(10)
        self.add(top_panel, bottom_panel)

        title = Text("椭圆到圆周的最短距离", font=FONT, font_size=34,
                     color=INK, weight="BOLD").move_to([0, 7.37, 0])
        example = MathTex(r"E:\frac{x^2}{9}+\frac{y^2}{4}=1", color=INK,
                          font_size=34).move_to([0, 6.58, 0])
        condition = MathTex(r"M=(4,0),\qquad r>0", color=INK,
                            font_size=31).move_to([0, 5.94, 0])
        e_label = Text("蓝：椭圆 E", font=FONT, font_size=24, color=BLUE_E)
        c_label = Text("红：圆周 Γ", font=FONT, font_size=24, color=RED_C)
        VGroup(e_label, c_label).arrange(RIGHT, buff=0.65).move_to([0, 5.20, 0])
        center_dot = Dot(center, radius=0.08, color=INK)
        m_label = Text("M", font=FONT, font_size=22, color=INK).move_to(
            center + RIGHT * 0.22
        )
        for item in (title, example, condition, e_label, c_label):
            item.set_z_index(11)
        self.add(title, example, condition, e_label, c_label, center_dot, m_label)

        # The number-line gold gap uses exactly the same radius and D_min state.
        yline = -4.36
        pos = lambda value: (-3.60 + value * 0.87, yline, 0)
        base = Line(pos(0), pos(8.25), color="#B4C2D0", stroke_width=3)
        interval = Line(pos(1), pos(7), color=GREEN_I, stroke_width=9)
        gap = always_redraw(lambda: self._number_line_gap(
            pos, radius.get_value()
        ).set_z_index(12))
        marker = always_redraw(lambda: Dot(
            pos(radius.get_value()), radius=0.13, color=RED_C
        ).set_z_index(12))
        ticks = VGroup(*[
            Line((pos(v)[0], yline - 0.12, 0), (pos(v)[0], yline + 0.12, 0),
                 color=MUTED, stroke_width=2) for v in (1, 7)
        ])
        tick_labels = VGroup(
            Text("1", font=FONT, font_size=24, color=INK).move_to((pos(1)[0], yline - .39, 0)),
            Text("7", font=FONT, font_size=24, color=INK).move_to((pos(7)[0], yline - .39, 0)),
        )
        interval_label = Text("本例：圆心到椭圆的距离范围 [1,7]", font=FONT,
                              font_size=23, color=GREEN_I).move_to([0, -3.69, 0])
        line_caption = Text("金线：几何最短距离 = 数轴间隙", font=FONT,
                            font_size=22, color=INK).move_to([0, -3.10, 0])
        point_caption = Text("金点：真实交点；数轴间隙为 0", font=FONT,
                             font_size=22, color=INK).move_to([0, -3.10, 0])
        line_caption.add_updater(lambda m: m.set_opacity(
            1 if radius.get_value() < 1 - 1e-8 or radius.get_value() > 7 + 1e-8 else 0
        ))
        point_caption.add_updater(lambda m: m.set_opacity(
            0 if radius.get_value() < 1 - 1e-8 or radius.get_value() > 7 + 1e-8 else 1
        ))
        for item in (interval_label, base, interval, ticks, tick_labels,
                     line_caption, point_caption):
            item.set_z_index(11)
        self.add(interval_label, base, interval, ticks, tick_labels)

        r_label = MathTex("r=", color=INK, font_size=34).move_to([-2.45, -5.31, 0])
        r_num = DecimalNumber(radius.get_value(), num_decimal_places=2,
                              font_size=34, color=RED_C).move_to([-1.15, -5.31, 0])
        r_num.add_updater(lambda d: d.set_value(radius.get_value()).set_z_index(12))
        d_label = MathTex("D_{\\min}=", color=INK, font_size=34).move_to([0.75, -5.31, 0])
        d_num = DecimalNumber(minimum_distance(radius.get_value()),
                              num_decimal_places=2, font_size=34, color=GOLD).move_to([2.95, -5.31, 0])
        d_num.add_updater(lambda d: d.set_value(
            minimum_distance(radius.get_value())
        ).set_z_index(12))

        state = Text("先看 1 和 7 从哪里来", font=FONT, font_size=27,
                     color=INK).move_to([0, -6.05, 0])
        formula = MathTex(r"D_{\min}=\operatorname{dist}(r,[1,7])",
                          color=INK, font_size=34).move_to([0, -6.81, 0])
        general = VGroup(
            Text("一般：", font=FONT, color="#42576C", font_size=23),
            MathTex(r"D_{\min}=\operatorname{dist}(r,[d_{\min},d_{\max}])",
                    color="#42576C", font_size=28),
        ).arrange(RIGHT, buff=0.15).move_to([0, -7.50, 0])
        for item in (r_label, r_num, d_label, d_num, state, formula, general):
            item.set_z_index(11)
        self.add(state, formula, general)

        # Brief exact endpoint construction, specific to this axis-aligned example.
        a, b = axes.c2p(3, 0), axes.c2p(-3, 0)
        endpoint_marks = VGroup(
            Dot(a, radius=0.11, color=GREEN_I),
            Dot(b, radius=0.11, color=GREEN_I),
            Text("A(3,0)", font=FONT, font_size=20, color=BLUE_E).move_to(a + UP * .43),
            Text("B(-3,0)", font=FONT, font_size=20, color=BLUE_E).move_to(b + UP * .43),
        )
        ma = self._distance_callout(axes, 3, 4, 2.7, r"MA=1")
        mb = self._distance_callout(axes, -3, 4, 3.75, r"MB=7")
        self.wait(0.2)
        self.play(FadeIn(endpoint_marks), FadeIn(ma), run_time=0.4)
        self.wait(0.65)
        self.play(FadeOut(ma), FadeIn(mb), run_time=0.35)
        self.wait(0.65)
        self.play(FadeOut(endpoint_marks), FadeOut(mb), run_time=0.3)

        state = self._change_state(state, "半径增大：金色间隙逐渐缩小")
        dynamic = (circle, points, gap, marker, r_label, r_num, d_label, d_num,
                   line_caption, point_caption)
        self.play(*(FadeIn(item) for item in dynamic), run_time=0.45)
        self.play(radius.animate.set_value(1), run_time=1.8, rate_func=linear)
        state = self._change_state(state, "第一次相切：最短距离为 0")
        self._tangent_pulse(axes.c2p(3, 0))

        state = self._change_state(state, "继续扩大：金点沿两曲线移动")
        self.play(radius.animate.set_value(4), run_time=2.7, rate_func=linear)
        self.wait(0.35)
        self.play(radius.animate.set_value(7), run_time=2.7, rate_func=linear)
        state = self._change_state(state, "第二次相切：最短距离仍为 0")
        self._tangent_pulse(axes.c2p(-3, 0))

        state = self._change_state(state, "越过 7：金色间隙重新增大")
        self.play(radius.animate.set_value(8), run_time=1.8, rate_func=linear)
        self.wait(0.65)

        # Return to the same static opening composition before the GIF loops.
        self.play(*(FadeOut(item) for item in dynamic), run_time=0.4)
        radius.set_value(0.5)
        self.remove(*dynamic)
        state = self._change_state(state, "先看 1 和 7 从哪里来")
        self.wait(0.2)

    def _change_state(self, old, message):
        new = Text(message, font=FONT, font_size=27, color=INK).move_to(old).set_z_index(11)
        self.remove(old)
        self.add(new)
        return new

    def _tangent_pulse(self, point):
        ring = Circle(radius=0.23, color=GOLD, stroke_width=3).move_to(point)
        self.play(FadeIn(ring), run_time=0.2)
        self.wait(0.55)
        self.play(FadeOut(ring), run_time=0.2)

    @staticmethod
    def _distance_callout(axes, x1, x2, height, label):
        y = axes.c2p(0, height)[1]
        p1, p2 = axes.c2p(x1, 0), axes.c2p(x2, 0)
        return VGroup(
            DashedLine(p1, (p1[0], y, 0), color=GREEN_I, stroke_width=2),
            DashedLine(p2, (p2[0], y, 0), color=GREEN_I, stroke_width=2),
            Line((p1[0], y, 0), (p2[0], y, 0), color=GREEN_I, stroke_width=5),
            MathTex(label, color=GREEN_I, font_size=30).move_to(
                ((p1[0] + p2[0]) / 2, y + 0.36, 0)
            ),
        )

    @staticmethod
    def _number_line_gap(pos, radius):
        if radius < 1:
            return Line(pos(radius), pos(1), color=GOLD, stroke_width=8)
        if radius > 7:
            return Line(pos(7), pos(radius), color=GOLD, stroke_width=8)
        return VGroup()

    @staticmethod
    def _closest_objects(axes, radius):
        intersections = intersection_points(radius)
        if intersections:
            return VGroup(*[
                Dot(axes.c2p(*p), radius=0.12, color=GOLD) for p in intersections
            ])
        p, q = nearest_pair(radius)
        return VGroup(
            Line(axes.c2p(*p), axes.c2p(*q), color=GOLD, stroke_width=8),
            Dot(axes.c2p(*p), radius=0.105, color=GOLD),
            Dot(axes.c2p(*q), radius=0.105, color=GOLD),
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
