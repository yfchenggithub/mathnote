"""Independent C001 maximum-distance lesson. Render C001MaxDistance."""

from __future__ import annotations

from math import cos, pi, sin

from manim import (
    Axes, Circle, DecimalNumber, Dot, FadeIn, FadeOut, LEFT, Line,
    MathTex, RIGHT, Scene, Text, UP, ValueTracker, VGroup, always_redraw,
    config, linear,
)

from math_model import M, ellipse_point, farthest_pair, maximum_distance


config.frame_width = 9
config.frame_height = 16

BG = "#F9FAFC"
INK = "#183047"
MUTED = "#6F8295"
BLUE_E = "#2377C4"
RED_C = "#E45361"
GOLD = "#E8AA28"
FONT = "Microsoft YaHei"


class C001MaxDistance(Scene):
    """First maximize PM, then move Q to the far side of the circle."""

    def construct(self):
        self.camera.background_color = BG
        radius = ValueTracker(2.0)
        angle = ValueTracker(pi)

        axes = Axes(
            x_range=[-4, 9, 2], y_range=[-4.5, 4.5, 2],
            x_length=7.8, y_length=5.4, tips=False,
            axis_config={"color": "#CAD4DE", "stroke_width": 1.5},
        ).move_to([0, 1.55, 0])
        unit = axes.c2p(1, 0)[0] - axes.c2p(0, 0)[0]
        p, _ = farthest_pair(2.0)
        p_screen = axes.c2p(*p)
        m_screen = axes.c2p(*M)

        ellipse = axes.plot_parametric_curve(
            ellipse_point, t_range=[0, 2 * pi],
            color=BLUE_E, stroke_width=5.5,
        )
        circle = always_redraw(lambda: Circle(
            radius=unit * radius.get_value(), color=RED_C, stroke_width=5,
        ).move_to(m_screen))
        center_dot = Dot(m_screen, radius=0.085, color=INK)
        p_dot = Dot(p_screen, radius=0.12, color=GOLD)

        title = Text("椭圆与圆周的最大距离", font=FONT, font_size=35,
                     color=INK, weight="BOLD").move_to([0, 7.32, 0])
        model = MathTex(r"E:\frac{x^2}{9}+\frac{y^2}{4}=1,\quad M=(4,0),\quad r>0",
                        color=INK, font_size=33).move_to([0, 6.54, 0])
        legend = VGroup(
            Text("蓝：椭圆 E", font=FONT, font_size=24, color=BLUE_E),
            Text("红：圆周", font=FONT, font_size=24, color=RED_C),
        ).arrange(RIGHT, buff=0.72).move_to([0, 5.75, 0])
        p_label = MathTex(r"P=(-3,0)", color=GOLD, font_size=27).move_to(
            axes.c2p(-1.85, 2.55))
        m_label = MathTex("M", color=INK, font_size=27).move_to(
            m_screen + UP * 0.45)

        self.add(title, model, legend, axes, ellipse, circle, center_dot, m_label)
        self.wait(0.45)

        status = Text("① 先找离圆心最远的椭圆点", font=FONT,
                      font_size=27, color=INK).move_to([0, -2.25, 0])
        pm = Line(p_screen, m_screen, color=GOLD, stroke_width=8)
        pm_label = MathTex(r"PM=d_{\max}=7", color=GOLD,
                           font_size=35).move_to([0, -3.2, 0])
        self.play(FadeIn(p_dot), FadeIn(p_label), FadeIn(status),
                  FadeIn(pm), FadeIn(pm_label), run_time=0.8)
        self.wait(0.85)

        # A true point on the circumference sweeps from its near side to its
        # far side. Its segment is recomputed from the same radius and angle.
        q_candidate = always_redraw(lambda: Dot(
            axes.c2p(M[0] + radius.get_value() * cos(angle.get_value()),
                     M[1] + radius.get_value() * sin(angle.get_value())),
            radius=0.105, color=GOLD,
        ))
        candidate_line = always_redraw(lambda: Line(
            p_screen, q_candidate.get_center(), color=GOLD, stroke_width=6,
        ))
        next_status = Text("② 固定 P：沿圆周寻找最远点 Q", font=FONT,
                           font_size=27, color=INK).move_to(status)
        self.play(FadeOut(pm_label), FadeOut(pm), FadeOut(status),
                  run_time=0.25)
        self.play(FadeIn(next_status), run_time=0.25)
        self.add(candidate_line, q_candidate)
        status = next_status
        self.play(angle.animate.set_value(2 * pi), run_time=2.2,
                  rate_func=linear)

        q_label = always_redraw(lambda: MathTex(
            "Q", color=RED_C, font_size=27,
        ).move_to(axes.c2p(4 + radius.get_value(), 0) + RIGHT * 0.33 + UP * 0.17))
        q_coordinate = MathTex(r"Q=(4+r,0)", color=RED_C,
                               font_size=28).move_to([0, -2.85, 0])
        radius_segment = always_redraw(lambda: Line(
            m_screen, axes.c2p(4 + radius.get_value(), 0),
            color=RED_C, stroke_width=6,
        ))
        # The parallel gold span has the exact same horizontal scale as PQ.
        total_span = always_redraw(lambda: Line(
            axes.c2p(-3, -1.2), axes.c2p(4 + radius.get_value(), -1.2),
            color=GOLD, stroke_width=5,
        ))
        span_ends = always_redraw(lambda: VGroup(
            Line(axes.c2p(-3, -1.02), axes.c2p(-3, -1.38),
                 color=GOLD, stroke_width=3),
            Line(axes.c2p(4 + radius.get_value(), -1.02),
                 axes.c2p(4 + radius.get_value(), -1.38),
                 color=GOLD, stroke_width=3),
        ))
        next_status = Text("Q 在圆心背向 P 的一侧", font=FONT,
                           font_size=27, color=INK).move_to(status)
        self.play(FadeOut(status), run_time=0.2)
        self.play(FadeIn(next_status), run_time=0.3)
        self.add(q_label, q_coordinate, radius_segment, total_span, span_ends)
        status = next_status
        self.wait(0.8)

        # Fixed anchors keep the live numbers from jumping as digits change.
        r_text = MathTex("r=", color=INK, font_size=34).move_to([-2.9, -3.45, 0])
        r_number = DecimalNumber(radius.get_value(), num_decimal_places=2,
                                 color=RED_C, font_size=34).move_to([-1.6, -3.45, 0])
        r_number.add_updater(lambda mob: mob.set_value(radius.get_value()))
        d_text = MathTex(r"D_{\max}=", color=INK,
                         font_size=34).move_to([0.65, -3.45, 0])
        d_number = DecimalNumber(maximum_distance(radius.get_value()),
                                 num_decimal_places=2, color=GOLD,
                                 font_size=34).move_to([2.95, -3.45, 0])
        d_number.add_updater(lambda mob: mob.set_value(
            maximum_distance(radius.get_value())))
        addition = MathTex(r"PQ=PM+MQ=7+r", color=INK,
                           font_size=38).move_to([0, -4.55, 0])
        example = MathTex(r"D_{\max}=7+r", color=GOLD,
                          font_size=43).move_to([0, -5.60, 0])
        next_status = Text("③ 半径增长，最远距离同步增长", font=FONT,
                           font_size=27, color=INK).move_to(status)
        self.play(FadeOut(status), run_time=0.2)
        self.play(FadeIn(next_status), FadeIn(r_text),
                  FadeIn(r_number), FadeIn(d_text), FadeIn(d_number),
                  FadeIn(addition), FadeIn(example), run_time=0.4)
        status = next_status
        self.play(radius.animate.set_value(4.0), run_time=2.6,
                  rate_func=linear)
        self.wait(0.7)

        general = MathTex(r"D_{\max}=d_{\max}+r", color=INK,
                          font_size=39).move_to([0, -6.75, 0])
        next_status = Text("本例 dₘₐₓ=7；一般情形先求 dₘₐₓ", font=FONT,
                           font_size=25, color=MUTED).move_to(status)
        self.play(FadeOut(status), run_time=0.2)
        self.play(FadeIn(next_status), FadeIn(general), run_time=0.35)
        status = next_status
        self.wait(1.05)

        # Return to the opening composition for a soft infinite GIF loop.
        r_number.clear_updaters()
        d_number.clear_updaters()
        self.play(FadeOut(VGroup(
            p_dot, p_label, r_text, r_number, d_text, d_number,
            addition, example, general, status, q_coordinate,
        )), radius.animate.set_value(2.0), run_time=0.7)
        self.remove(q_candidate, candidate_line, q_label, radius_segment,
                    total_span, span_ends)
        self.wait(0.4)
