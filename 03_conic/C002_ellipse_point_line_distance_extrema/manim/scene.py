"""C002: slide a line across an ellipse's two normal support points."""

from __future__ import annotations

from math import cos, pi, sin

from manim import (Axes, DecimalNumber, Dot, FadeIn, FadeOut, Line,
                   MathTex, Scene, Text, ValueTracker, VGroup, always_redraw,
                   config, linear)

from math_model import A, B, R, SEMIMAJOR, SEMIMINOR, state


config.frame_width = 9
config.frame_height = 16
BG = "#F9FAFC"
INK = "#183047"
MUTED = "#607589"
BLUE = "#2377C4"
RED = "#D95464"
GOLD = "#DC9A1B"
PURPLE = "#8060AC"
TEAL = "#168C85"
FONT = "Microsoft YaHei"


def clipped_line(c: float):
    """Endpoints of 3x+4y+c=0 within the geometry viewport."""
    xmin, xmax, ymin, ymax = -3.25, 3.25, -2.15, 2.15
    candidates = []
    for x in (xmin, xmax):
        y = (-c - A * x) / B
        if ymin <= y <= ymax:
            candidates.append((x, y))
    for y in (ymin, ymax):
        x = (-c - B * y) / A
        if xmin <= x <= xmax:
            candidates.append((x, y))
    return candidates[0], candidates[1]


class C002DistanceLesson(Scene):
    def construct(self):
        self.camera.background_color = BG
        c = ValueTracker(10.0)

        axes = Axes(
            x_range=[-3.3, 3.3, 1], y_range=[-2.2, 2.2, 1],
            x_length=7.1, y_length=4.73, tips=False,
            axis_config={"color": "#CDD7E0", "stroke_width": 1.3},
        ).move_to([0, 1.72, 0])
        xy = lambda point: axes.c2p(*point)
        ellipse = axes.plot_parametric_curve(
            lambda t: (SEMIMAJOR * cos(t), SEMIMINOR * sin(t), 0),
            t_range=[0, 2 * pi], color=BLUE, stroke_width=6,
        )
        near, far = state(10).near, state(10).far
        near_dot = Dot(xy(near), radius=.095, color=GOLD)
        far_dot = Dot(xy(far), radius=.095, color=PURPLE)
        near_label = MathTex("P_-", color=GOLD, font_size=34).move_to(xy(near) + [-.9, -.66, 0])
        far_label = MathTex("P_+", color=PURPLE, font_size=34).move_to(xy(far) + [.52, .3, 0])

        moving_line = always_redraw(lambda: Line(
            xy(clipped_line(c.get_value())[0]),
            xy(clipped_line(c.get_value())[1]),
            color=RED, stroke_width=5,
        ))
        far_segment = always_redraw(lambda: Line(
            xy(state(c.get_value()).far), xy(state(c.get_value()).far_foot),
            color=PURPLE, stroke_width=5,
        ))
        near_geometry = always_redraw(lambda: VGroup(*(
            [Line(xy(state(c.get_value()).near), xy(state(c.get_value()).near_foot),
                  color=GOLD, stroke_width=7)]
            if state(c.get_value()).relation == "separate" else
            [Dot(xy(point), radius=.085, color=TEAL)
             for point in state(c.get_value()).intersections]
        )))

        title = Text("椭圆点到直线：距离怎样变化？", font=FONT,
                     font_size=34, color=INK, weight="BOLD").move_to([0, 7.17, 0])
        model = MathTex(r"E:\frac{x^2}{4}+y^2=1,\quad l_C:3x+4y+C=0",
                        color=INK, font_size=34).move_to([0, 6.43, 0])
        condition = MathTex(r"C\geq0,\qquad R=2\sqrt{13}\approx7.21",
                            color=MUTED, font_size=31).move_to([0, 5.74, 0])

        c_label = MathTex("C=", color=RED, font_size=40).move_to([-1.1, -1.18, 0])
        c_number = DecimalNumber(10, num_decimal_places=2, font_size=40,
                                 color=RED).move_to([.55, -1.18, 0])
        c_number.add_updater(lambda mob: mob.set_value(c.get_value()))

        min_label = MathTex(r"d_{\min}=", color=INK, font_size=38).move_to([-1.55, -2.29, 0])
        min_number = DecimalNumber(state(10).d_min, num_decimal_places=2,
                                   font_size=38, color=GOLD).move_to([.72, -2.29, 0])
        min_number.add_updater(lambda mob: mob.set_value(state(c.get_value()).d_min))
        max_label = MathTex(r"d_{\max}=", color=INK, font_size=38).move_to([-1.55, -3.16, 0])
        max_number = DecimalNumber(state(10).d_max, num_decimal_places=2,
                                   font_size=38, color=PURPLE).move_to([.72, -3.16, 0])
        max_number.add_updater(lambda mob: mob.set_value(state(c.get_value()).d_max))
        formula_min = MathTex(r"d_{\min}=\max\left\{0,\frac{C-R}{5}\right\}",
                              color=INK, font_size=38).move_to([0, -4.48, 0])
        formula_max = MathTex(r"d_{\max}=\frac{C+R}{5}",
                              color=INK, font_size=38).move_to([0, -6.0, 0])

        def caption(value: str):
            return Text(value, font=FONT, font_size=26, color=MUTED).move_to([0, -7.19, 0])

        status = caption("相离：金色线段是最近距离")
        self.add(title, model, condition, axes, ellipse, moving_line,
                 far_segment, near_geometry, near_dot, far_dot,
                 near_label, far_label, c_label, c_number,
                 min_label, min_number, max_label, max_number,
                 formula_min, formula_max, status)
        self.wait(1.0)

        self.play(c.animate.set_value(R), run_time=2.3, rate_func=linear)
        next_status = caption("相切：金色间隔缩为零")
        self.play(FadeOut(status), run_time=.12)
        self.play(FadeIn(next_status), run_time=.13)
        status = next_status
        self.wait(.9)

        next_status = caption("相交：青色交点出现，最近距离为零")
        self.play(FadeOut(status), run_time=.12)
        self.play(FadeIn(next_status), run_time=.13)
        status = next_status
        self.play(c.animate.set_value(2.0), run_time=2.7, rate_func=linear)
        self.play(c.animate.set_value(0), run_time=.9, rate_func=linear)
        self.wait(1.0)

        next_status = caption("紫色垂线始终给出最远距离")
        self.play(FadeOut(status), run_time=.12)
        self.play(FadeIn(next_status), run_time=.13)
        status = next_status
        self.play(c.animate.set_value(10.0), run_time=2.6, rate_func=linear)
        initial = caption("相离：金色线段是最近距离")
        self.play(FadeOut(status), run_time=.12)
        self.play(FadeIn(initial), run_time=.13)
        self.wait(.75)
