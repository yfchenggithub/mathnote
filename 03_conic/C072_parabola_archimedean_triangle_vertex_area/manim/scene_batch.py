"""C072: retain the area lesson, then reveal the curve bisecting its median."""
from pathlib import Path
import sys
import json

import numpy as np
from manim import *

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import area, midpoint_state, p, rounded_for_display, state

config.background_color = '#F7F8FA'
config.frame_width, config.frame_height = 9, 16
INK, MUTED, BLUE, ORANGE, GREEN, PURPLE, AXIS, GOLD = (
    '#213044', '#526275', '#2778BD', '#CD6031', '#158068',
    '#8055B2', '#A7B4C2', '#B77D12',
)


def cn(s, size=26, color=INK):
    return Text(s, font='Microsoft YaHei', font_size=size, color=color)


def eq(s, size=32, color=INK):
    return MathTex(s, font_size=size, color=color)


def number(symbol, value, pos, color=INK):
    value_mob = DecimalNumber(0, num_decimal_places=2, font_size=32, color=color)
    group = VGroup(eq(symbol + r'\approx', 32, color), value_mob).arrange(RIGHT, buff=.13)
    group.move_to(pos)
    right = value_mob.get_right().copy()

    def update(mob):
        # Remove floating-point noise before rounding a real length to 2 places.
        mob.set_value(rounded_for_display(value())).align_to(right, RIGHT)

    value_mob.add_updater(update)
    value_mob.update(0)
    return group


class C072Animation(Scene):
    def construct(self):
        t, d = ValueTracker(.45), ValueTracker(.8)
        xy = lambda q: np.array([1.85 * q[0], 1.85 * q[1] + .65, 0])
        current = lambda: state(t.get_value(), d.get_value())
        midpoint = lambda: midpoint_state(t.get_value(), d.get_value())
        audit_records = []

        title = cn('切线三角形：面积与中点', 30).move_to([0, 6.95, 0])
        caption = cn('先看面积：改变切点间距', 26).move_to([0, 5.85, 0])
        condition = eq(r'x^2=2py,\quad p=1', 25, MUTED).move_to([0, 4.95, 0])
        curve = ParametricFunction(
            lambda u: xy((u, u*u / (2*p))), t_range=[-2, 2],
            color=BLUE, stroke_width=3.2,
        )

        def geometry():
            A, B, P, M = current()
            N, PN, NM = midpoint()
            audit_records.append(dict(time=float(self.time), t=t.get_value(),
                d=d.get_value(), A=A, B=B, P=P, M=M, N=N, PN=PN, NM=NM,
                displayed_PN=f'{rounded_for_display(PN):.2f}',
                displayed_NM=f'{rounded_for_display(NM):.2f}'))
            labels = [(A, 'A', BLUE, LEFT*.38 + DOWN*.2),
                      (B, 'B', BLUE, RIGHT*.36 + DOWN*.16),
                      (P, 'P', ORANGE, DOWN*.4),
                      (M, 'M', PURPLE, UP*.4)]
            return VGroup(
                Polygon(xy(A), xy(B), xy(P), stroke_opacity=0,
                        fill_color=ORANGE, fill_opacity=.09),
                Line(xy(P), xy(A), color=ORANGE, stroke_width=3),
                Line(xy(P), xy(B), color=ORANGE, stroke_width=3),
                Line(xy(A), xy(B), color=PURPLE, stroke_width=3),
                DashedLine(xy(P), xy(M), color=MUTED, stroke_width=2),
                *[VGroup(Dot(xy(Q), color=color, radius=.07),
                         eq(name, 42, color).move_to(xy(Q) + offset))
                  for Q, name, color, offset in labels],
            )

        def midpoint_geometry():
            _, _, P, M = current()
            N, _, _ = midpoint()
            result = VGroup(
                Line(xy(P), xy(N), color=GREEN, stroke_width=5),
                Line(xy(N), xy(M), color=GREEN, stroke_width=5),
            )
            for Q, R in [(P, N), (N, M)]:
                center = (xy(Q) + xy(R)) / 2
                result.add(Line(center + LEFT*.13, center + RIGHT*.13,
                                color=GREEN, stroke_width=4))
            # Label the concave side of the curve with enough room below AB.
            # Fade just the letter when its side changes at t=0; N itself stays.
            horizontal = LEFT if t.get_value() >= 0 else RIGHT
            label = eq('N', 42, GOLD).move_to(
                xy(N) + horizontal*.45 + UP*(.36 - .6*abs(t.get_value())))
            label.set_opacity(min(1., abs(t.get_value())/.07))
            result.add(Dot(xy(N), color=GOLD, radius=.09), label)
            return result

        moving = always_redraw(geometry)
        area_value = number('S', lambda: area(t.get_value(), d.get_value()),
                            [0, -2.55, 0], ORANGE)
        area_formula = eq(r'S_{\triangle PAB}=\frac{|x_1-x_2|^3}{8p}',
                          36, GREEN).move_to([0, -3.85, 0])
        area_note = eq(r'x_P=x_M=\frac{x_1+x_2}{2}', 30, MUTED).move_to([0, -5.0, 0])
        midpoint_formula = eq(r'PN=NM=\frac{PM}{2}', 40, GREEN).move_to([0, -3.85, 0])
        midpoint_note = cn('N 始终在线段 PM 的正中间', 25).move_to([0, -5.0, 0])
        footer = VGroup(
            cn('查结论 · 看图解 · 学证明｜知树 App', 22, MUTED),
            cn('公众号 ok-shuxue｜获取入口', 20, MUTED),
        ).arrange(DOWN, buff=.16).move_to([0, -7.0, 0])

        self.add(title, caption, condition, curve, moving,
                 area_value, area_formula, area_note, footer)
        self.wait(1)
        self.play(d.animate.set_value(1.3), run_time=2.6)
        self.play(Transform(caption,
            cn('再平移切点，面积保持不变', 26).move_to(caption)), run_time=.3)
        self.play(t.animate.set_value(-.45), run_time=2.6)
        self.wait(.6)
        self.play(
            FadeOut(area_value), FadeOut(area_formula), FadeOut(area_note),
            Transform(caption, cn('竖直中线与抛物线交于 N', 26).move_to(caption)),
            run_time=.4,
        )
        # Construct at the current t,d; an off-scene always_redraw would otherwise
        # fade in its stale initial geometry before its updater first runs.
        bisector = always_redraw(midpoint_geometry)
        equal_values = VGroup(
            number('PN', lambda: midpoint()[1], [-1.65, -2.55, 0], GREEN),
            number('NM', lambda: midpoint()[2], [1.65, -2.55, 0], GREEN),
        )
        self.play(FadeIn(bisector), FadeIn(equal_values),
                  FadeIn(midpoint_formula), FadeIn(midpoint_note), run_time=.6)
        self.wait(1.2)
        self.play(d.animate.set_value(.8), run_time=2.8)
        self.play(t.animate.set_value(.45), run_time=2.8)
        self.play(Transform(caption,
            cn('切点移动，PN 与 NM 仍然相等', 26).move_to(caption)), run_time=.3)
        self.wait(1.5)
        self.play(FadeOut(bisector), FadeOut(equal_values),
                  FadeOut(midpoint_formula), FadeOut(midpoint_note),
                  Transform(caption, cn('先看面积：改变切点间距', 26).move_to(caption)),
                  run_time=.4)
        self.play(FadeIn(area_value), FadeIn(area_formula), FadeIn(area_note), run_time=.4)
        self.wait(.6)
        (Path(config.media_dir) / 'c072_state_audit.json').write_text(
            json.dumps(audit_records, indent=2), encoding='utf-8')
