"""G020: one UID-local 3D lesson; all geometry comes from math_model."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import (
    DEGREES, DOWN, UP, DashedLine, Dot3D, FadeIn, FadeOut,
    Line, MathTex, Polygon, Text, ThreeDScene, VGroup,
    ValueTracker, always_redraw, config, linear,
)

from math_model import G020State, INITIAL, PERPENDICULAR, RAISED


config.frame_width = 9
config.frame_height = 16

BG = "#F7F8FA"
INK = "#213044"
MUTED = "#526275"
PLANE = "#DCE7EF"
EDGE = "#A7B4C2"
PROJECTION = "#2778BD"
SLANTED = "#CD6031"
IN_PLANE = "#158068"
LINE_L = "#8055B2"
GOLD = "#B77D12"


def vec(point):
    return np.array(point, dtype=float)


def stage_text(sentence):
    return Text(sentence, font="Microsoft YaHei", font_size=29, color=INK).move_to(DOWN * 4.85)


def marker(state, space):
    b, c, d = state.right_angle_corners(with_space_line=space, size=.33)
    color = SLANTED if space else IN_PLANE
    return VGroup(
        Line(vec(b), vec(c), color=color, stroke_width=5),
        Line(vec(c), vec(d), color=color, stroke_width=5),
    )


class G020ThreePerpendiculars(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(
            phi=45 * DEGREES, theta=-35 * DEGREES, zoom=1.4,
            frame_center=vec((1.6, 0, .2)),
        )

        height = ValueTracker(INITIAL.height)
        angle = ValueTracker(INITIAL.line_angle_deg)

        def current():
            return G020State(INITIAL.a, height.get_value(), angle.get_value())

        # The plane is z=0. O/A/l/OA all use world coordinates on that plane.
        plane = Polygon(
            vec((-.25, -1.85, 0)), vec((4.1, -1.85, 0)),
            vec((4.1, 1.85, 0)), vec((-.25, 1.85, 0)),
            fill_color=PLANE, fill_opacity=.30, stroke_color=EDGE, stroke_width=1.5,
        )
        oa = Line(vec(INITIAL.O), vec(INITIAL.A), color=IN_PLANE, stroke_width=8)
        l = always_redraw(lambda: Line(
            vec(current().point_on_l(-1.9)), vec(current().point_on_l(1.9)),
            color=LINE_L, stroke_width=7,
        ))
        po = always_redraw(lambda: DashedLine(
            vec(current().P), vec(current().O),
            color=PROJECTION, stroke_width=4, dash_length=.12,
        ))
        pa = always_redraw(lambda: Line(
            vec(current().P), vec(current().A), color=SLANTED, stroke_width=9,
        ))
        o_dot = Dot3D(point=vec(INITIAL.O), radius=.09, color=PROJECTION)
        a_dot = Dot3D(point=vec(INITIAL.A), radius=.09, color=GOLD)
        p_dot = always_redraw(lambda: Dot3D(point=vec(current().P), radius=.10, color=GOLD))

        projections = always_redraw(lambda: VGroup(*(
            DashedLine(
                vec(current().point_on_PA(t)),
                vec(current().projected_point_on_PA(t)),
                color=PROJECTION, stroke_width=2.3, dash_length=.08,
            ) for t in (.25, .5, .75)
        )))

        self.add(plane, oa, l, po, pa, o_dot, a_dot, p_dot)

        o_label = MathTex("O", color=INK, font_size=31).move_to(vec((-.26, -.20, .02)))
        a_label = MathTex("A", color=INK, font_size=31).move_to(vec((3.05, -.20, .02)))
        p_label = MathTex("P", color=INK, font_size=31)
        p_label.add_updater(lambda m: m.move_to(vec(current().P) + np.array([-.28, 0, .19])))
        alpha_label = MathTex(r"\alpha", color=MUTED, font_size=31).move_to(vec((-.50, -1.85, .02)))
        l_label = MathTex(r"\ell", color=LINE_L, font_size=32)
        l_label.add_updater(lambda m: m.move_to(vec(current().point_on_l(2.08)) + np.array([.03, .05, .05])))
        self.add_fixed_orientation_mobjects(o_label, a_label, p_label, alpha_label, l_label)

        title = Text("斜线的影子，决定垂直", font="Microsoft YaHei", font_size=35, color=INK)
        title.move_to(UP * 6.55)
        condition = MathTex(r"PO\perp\alpha,\quad \ell\subset\alpha", color=MUTED, font_size=34)
        condition.move_to(UP * 5.73)
        stage = stage_text("斜线 PA 的影子是 OA")
        self.add_fixed_in_frame_mobjects(title, condition, stage)

        def change_stage(old, sentence, duration=.35):
            next_stage = stage_text(sentence)
            next_stage.set_opacity(0)
            self.add_fixed_in_frame_mobjects(next_stage)
            self.play(FadeOut(old), run_time=duration / 2)
            self.play(next_stage.animate.set_opacity(1), run_time=duration / 2)
            return next_stage

        self.wait(.7)

        # Project several true points of PA vertically to OA. A camera-only
        # perspective crossing is never labelled as a world intersection.
        self.play(FadeIn(projections), run_time=.75)
        self.wait(.6)
        stage = change_stage(stage, "让平面内的 l 转向 OA")
        self.play(angle.animate.set_value(PERPENDICULAR.line_angle_deg),
                  run_time=2.25, rate_func=linear)
        plane_marker = always_redraw(lambda: marker(current(), space=False))
        self.play(FadeIn(plane_marker), run_time=.4)
        stage = change_stage(stage, "l 与 OA 垂直，PA 也垂直")
        self.wait(.95)

        stage = change_stage(stage, "抬高 P：斜线变，影子不变")
        self.play(height.animate.set_value(RAISED.height), run_time=2.35, rate_func=linear)
        space_marker = always_redraw(lambda: marker(current(), space=True))
        self.play(FadeIn(space_marker), run_time=.45)
        self.wait(.85)

        final_formula = MathTex(
            r"\ell\perp OA\ \Longleftrightarrow\ \ell\perp PA",
            color=INK, font_size=42,
        ).move_to(DOWN * 6.05)
        final_formula.set_opacity(0)
        self.add_fixed_in_frame_mobjects(final_formula)
        stage = change_stage(stage, "面内的影子，判定空间垂直", duration=.35)
        self.play(final_formula.animate.set_opacity(1), run_time=.3)
        self.wait(1.45)

        # Reconstruct the exact initial state to make a true looping GIF.
        self.play(FadeOut(plane_marker), FadeOut(space_marker),
                  FadeOut(projections), FadeOut(final_formula), run_time=.4)
        stage = change_stage(stage, "再看一次这条斜线的影子", duration=.25)
        self.play(height.animate.set_value(INITIAL.height),
                  angle.animate.set_value(INITIAL.line_angle_deg),
                  run_time=1.5, rate_func=linear)
        stage = change_stage(stage, "斜线 PA 的影子是 OA", duration=.3)
        self.wait(.25)
