"""C017: parallel translation reveals the discriminant boundary."""
from pathlib import Path
import sys
import numpy as np
from manim import *

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import EllipseLine

config.background_color = '#F7F8FA'
config.frame_width = 9
config.frame_height = 16
INK, MUTED, BLUE = '#213044', '#526275', '#2778BD'
ORANGE, GREEN, AXIS = '#CD6031', '#158068', '#A7B4C2'


def cn(s, size=26, color=INK):
    return Text(s, font='Microsoft YaHei', font_size=size, color=color)


def eq(s, size=32, color=INK):
    return MathTex(s, font_size=size, color=color)


class C017TangentCondition(Scene):
    def construct(self):
        model = EllipseLine()
        m = ValueTracker(0)
        xy = lambda p: np.array([.6*p[0], .6*p[1]+.7, 0])
        title = cn('两个交点，何时合为一个？', 31).move_to([0, 6.95, 0])
        setup = eq(r'\frac{x^2}{25}+\frac{y^2}{9}=1\qquad y=0.8x+m', 31).move_to([0, 5.85, 0])
        caption = cn('固定斜率，平移直线').move_to([0, 4.8, 0])
        axes = VGroup(
            Line(xy((-6.2, 0)), xy((6.2, 0)), color=AXIS, stroke_width=1.5),
            Line(xy((0, -5.3)), xy((0, 5.3)), color=AXIS, stroke_width=1.5),
            eq('x', 24, MUTED).move_to(xy((6.55, 0))),
            eq('y', 24, MUTED).move_to(xy((0, 5.65))),
            eq('O', 22, MUTED).move_to(xy((-.35, -.45))),
            eq('5', 21, MUTED).move_to(xy((5, -.45))),
            eq('3', 21, MUTED).move_to(xy((.4, 3.15))),
        )
        ellipse = ParametricFunction(lambda t: xy((5*np.cos(t), 3*np.sin(t))), t_range=[0, TAU], color=BLUE, stroke_width=3.2)

        def moving_line():
            ends = model.clipped_line(m.get_value())
            return Line(*[xy(p) for p in ends], color=ORANGE, stroke_width=3)

        line = always_redraw(moving_line)
        dots = always_redraw(lambda: VGroup(*[Dot(xy(p), radius=.075, color=GREEN) for p in model.intersections(m.get_value())]))
        number = DecimalNumber(0, num_decimal_places=2, font_size=31, color=ORANGE)
        readout = VGroup(eq(r'm\approx', 31, ORANGE), number).arrange(RIGHT, buff=.16).move_to([0, -3.3, 0])
        anchor = number.get_right().copy()
        number.add_updater(lambda mob: mob.set_value(0 if abs(m.get_value()) < .005 else m.get_value()).align_to(anchor, RIGHT))
        number.update(0)

        def relation_panel():
            state = model.relation(m.get_value())
            relation, text = {'secant': ('<', '相交 · 两个交点'), 'tangent': ('=', '相切 · 一个交点'), 'disjoint': ('>', '相离 · 没有交点')}[state]
            return VGroup(eq(r'm^2'+relation+'25', 33, GREEN if state == 'tangent' else INK), cn(text, 25)).arrange(DOWN, buff=.22).move_to([0, -4.45, 0])

        status = always_redraw(relation_panel)
        conclusion = cn('观察交点数如何变化', 26, MUTED).move_to([0, -6.05, 0])
        footer = cn('直线斜率始终为 0.8', 22, MUTED).move_to([0, -7.1, 0])
        self.add(title, setup, caption, axes, ellipse, line, dots, readout, status, conclusion, footer)
        self.wait(1)

        def swap(old, new):
            self.play(FadeOut(old), run_time=.15)
            old.become(new)
            self.play(FadeIn(old), run_time=.15)

        self.play(m.animate.set_value(4.4), run_time=2, rate_func=smooth)
        swap(caption, cn('继续平移，两个交点逐渐靠拢').move_to(caption))
        self.play(m.animate.set_value(5), run_time=2, rate_func=smooth)
        swap(caption, cn('两个交点合为切点', color=GREEN).move_to(caption))
        point_label = eq(r'P=(-4,\,1.8)', 25, GREEN).move_to(xy((-3.7, 3.1)))
        self.play(FadeIn(point_label), run_time=.25)
        tangent_condition = VGroup(
            cn('相切当且仅当', 23, GREEN),
            eq(r'm^2=a^2k^2+b^2', 35, GREEN),
        ).arrange(DOWN, buff=.14).move_to(conclusion)
        swap(conclusion, tangent_condition)
        swap(footer, eq(r'\Delta=4a^2b^2(a^2k^2+b^2-m^2)', 27, MUTED).move_to(footer))
        self.wait(1.5)
        self.play(FadeOut(point_label), run_time=.15)
        swap(caption, cn('越过相切位置，观察交点数').move_to(caption))
        self.play(m.animate.set_value(6.3), run_time=1.5, rate_func=smooth)
        self.wait(1)
        swap(caption, cn('反向平移，寻找另一条切线').move_to(caption))
        self.play(m.animate.set_value(-5), run_time=3.5, rate_func=smooth)
        swap(caption, cn('同一斜率，对应两条平行切线', color=GREEN).move_to(caption))
        upper = Line(*[xy(p) for p in model.clipped_line(5)], color=GREEN, stroke_width=2.6)
        upper_dot = Dot(xy(model.contact(5)), radius=.075, color=GREEN)
        pair = VGroup(eq(r'm=+5', 26, GREEN).move_to(xy((-3.6, 4.2))), eq(r'm=-5', 26, ORANGE).move_to(xy((3.7, -4.2))))
        self.play(FadeIn(upper), FadeIn(upper_dot), FadeIn(pair), run_time=.4)
        swap(conclusion, eq(r'm=\pm\sqrt{a^2k^2+b^2}', 36, GREEN).move_to(conclusion))
        swap(footer, cn('斜率式不含竖直切线 x = ±a', 23, MUTED).move_to(footer))
        self.wait(2)
        self.play(FadeOut(upper), FadeOut(upper_dot), FadeOut(pair), run_time=.3)
        swap(caption, cn('固定斜率，平移直线').move_to(caption))
        swap(conclusion, cn('观察交点数如何变化', 26, MUTED).move_to(conclusion))
        swap(footer, cn('直线斜率始终为 0.8', 22, MUTED).move_to(footer))
        self.play(m.animate.set_value(0), run_time=2, rate_func=smooth)
        self.wait(.5)
