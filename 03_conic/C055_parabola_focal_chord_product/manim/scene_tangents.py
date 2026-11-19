"""Rotate a focal chord while its tangent intersection slides on the directrix."""

from pathlib import Path
import sys

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP, DashedLine, Dot, FadeIn, FadeOut, Line,
    MathTex, ParametricFunction, Scene, Text, ValueTracker, VGroup,
    VMobject, always_redraw, config, smooth,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model_tangents import right_angle_vertices, tangent_state, unit_from_to


config.background_color = "#F7F8FA"
config.frame_width = 9
config.frame_height = 16
INK = "#213044"
MUTED = "#526275"
CURVE = "#2778BD"
TANGENT_A = "#CD6031"
TANGENT_B = "#8055B2"
GREEN = "#158068"
GOLD = "#B77D12"
AXIS = "#A7B4C2"


def chinese(text, size=28, color=INK):
    return Text(text, font="Microsoft YaHei", font_size=size, color=color)


def formula(text, size=32, color=INK):
    return MathTex(text, font_size=size, color=color)


def screen(point):
    # Identical scale on both axes is required for the displayed right angle.
    return np.array([point[0] - 1.25, point[1] + 0.5, 0.0])


class C055TangentPerpendicular(Scene):
    def construct(self):
        parameter = ValueTracker(0.75)
        title = chinese("焦点弦的两端切线", 36).move_to([0, 7.0, 0])
        condition = formula(r"y^2=4x\ (p=2),\quad F(1,0)", 32).move_to([0, 6.15, 0])
        caption = chinese("过焦点 F 的弦 AB", 27).move_to([0, 5.45, 0])
        footer = VGroup(
            chinese("查结论 · 看图解 · 学证明｜知树 App", 24, MUTED).move_to([0, -6.8, 0]),
            chinese("公众号 ok-shuxue｜获取入口", 22, MUTED).move_to([0, -7.35, 0]),
        )
        axes = VGroup(
            Line(screen((-1.55, 0)), screen((4.9, 0)), color=AXIS, stroke_width=1.4),
            Line(screen((0, -4.3)), screen((0, 4.3)), color=AXIS, stroke_width=1.4),
            formula("O", 24, MUTED).move_to(screen((0, 0)) + RIGHT * 0.35 + UP * 0.35),
            formula("x", 25, MUTED).move_to(screen((4.9, 0)) + UP * 0.22),
            formula("y", 25, MUTED).move_to(screen((0, 4.3)) + UP * 0.22),
        )
        curve = ParametricFunction(
            lambda y: screen((y * y / 4, y)),
            t_range=[-4.2, 4.2], color=CURVE, stroke_width=3,
        )
        focus = VGroup(
            Dot(screen((1, 0)), radius=0.065, color=INK),
            formula("F", 27).move_to(screen((1, 0)) + DOWN * 0.32 + RIGHT * 0.16),
        )
        # Text glyphs are constructed once, then copied by the geometry updater.
        label_a = formula("A", 28, TANGENT_A)
        label_b = formula("B", 28, TANGENT_B)
        label_t = formula("T", 28, GOLD)

        def chord_geometry():
            state = tangent_state(parameter.get_value())
            return VGroup(
                Line(screen(state.a), screen(state.b), color=MUTED, stroke_width=2.2),
                Dot(screen(state.a), color=TANGENT_A, radius=0.075),
                Dot(screen(state.b), color=TANGENT_B, radius=0.075),
                label_a.copy().move_to(screen(state.a) + RIGHT * 0.4 + DOWN * 0.15),
                label_b.copy().move_to(screen(state.b) + RIGHT * 0.4 + UP * 0.15),
            )

        def tangent_geometry():
            state = tangent_state(parameter.get_value())
            t = state.intersection
            u = np.array(unit_from_to(t, state.a))
            v = np.array(unit_from_to(t, state.b))
            a_end = np.array(state.a) + 0.35 * u
            b_end = np.array(state.b) + 0.35 * v
            corners = [screen(point) for point in right_angle_vertices(state)]
            marker = VMobject(color=GREEN, stroke_width=2.7).set_points_as_corners(corners)
            return VGroup(
                Line(screen(t), screen(a_end), color=TANGENT_A, stroke_width=3.5),
                Line(screen(t), screen(b_end), color=TANGENT_B, stroke_width=3.5),
                marker,
                Dot(screen(t), color=GOLD, radius=0.085),
                label_t.copy().move_to(screen(t) + LEFT * 0.34 + UP * 0.3),
            )

        chord = always_redraw(chord_geometry)
        tangents = always_redraw(tangent_geometry)
        directrix = VGroup(
            DashedLine(screen((-1, -4.2)), screen((-1, 4.2)),
                       dash_length=0.12, color=TANGENT_B, stroke_width=1.8),
            chinese("准线", 23, TANGENT_B).move_to([-3.35, 3.8, 0]),
            formula("x=-1", 25, TANGENT_B).move_to([-3.35, 3.28, 0]),
        )
        perpendicular = formula(r"k_Ak_B=\frac{p^2}{y_1y_2}=-1", 36, GREEN).move_to([0, -4.7, 0])
        intersection = formula(r"x_T=-\frac p2=-1", 35, GOLD).move_to([0, -5.65, 0])
        self.add(title, condition, caption, axes, curve, focus, chord, footer)
        self.wait(0.7)
        self.play(FadeOut(caption), run_time=0.2)
        caption = chinese("作两端切线，交于 T", 27).move_to([0, 5.45, 0])
        self.play(FadeIn(caption), FadeIn(directrix), FadeIn(tangents),
                  FadeIn(perpendicular), FadeIn(intersection), run_time=0.6)
        self.wait(0.7)

        self.play(FadeOut(caption), run_time=0.15)
        caption = chinese("弦在旋转，两切线始终垂直", 27).move_to([0, 5.45, 0])
        self.play(FadeIn(caption), run_time=0.15)
        self.play(parameter.animate.set_value(0), run_time=2.8, rate_func=smooth)
        self.wait(0.8)

        self.play(FadeOut(caption), run_time=0.15)
        caption = chinese("交点 T 始终沿准线运动", 27).move_to([0, 5.45, 0])
        self.play(FadeIn(caption), run_time=0.15)
        self.play(parameter.animate.set_value(-0.75), run_time=2.8, rate_func=smooth)
        self.wait(0.8)
        self.play(parameter.animate.set_value(0.75), run_time=3.5, rate_func=smooth)
        self.wait(1.0)

        # Return to the exact opening state for a quiet, continuous loop.
        self.play(FadeOut(caption), FadeOut(tangents), FadeOut(directrix),
                  FadeOut(perpendicular), FadeOut(intersection), run_time=0.5)
        caption = chinese("过焦点 F 的弦 AB", 27).move_to([0, 5.45, 0])
        self.play(FadeIn(caption), run_time=0.2)
        self.wait(0.7)
