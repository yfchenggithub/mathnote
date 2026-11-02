"""C070: contact chord and its midpoint's horizontal alignment with P."""
from pathlib import Path
import sys
import numpy as np
from manim import *

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import state, curve, chord_midpoint

config.background_color = '#F7F8FA'
config.frame_width, config.frame_height = 9, 16
INK, MUTED, BLUE = '#213044', '#526275', '#2778BD'
ORANGE, GREEN, PURPLE, GOLD, AXIS = '#CD6031', '#158068', '#8055B2', '#B77D12', '#A7B4C2'

def cn(text, size=26, color=INK):
    return Text(text, font='Microsoft YaHei', font_size=size, color=color)

def eq(text, size=32, color=INK):
    return MathTex(text, font_size=size, color=color)

class C070Animation(Scene):
    def construct(self):
        t = ValueTracker(-.8)
        xy = lambda q: np.array([1.42*q[0]-1.25, 1.42*q[1]+.45, 0])
        title = cn('切点弦的中点，始终与 P 同高', 29).move_to([0, 6.95, 0])
        caption = cn('P 引出两条切线，A、B 是切点', 25).move_to([0, 6.05, 0])
        condition = eq(r'y^2=2px,\quad p=1,\quad P=(-1,y_0)', 28, MUTED).move_to([0, 5.23, 0])
        footer = VGroup(cn('查结论 · 看图解 · 学证明｜知树 App', 24, MUTED),
                        cn('公众号 ok-shuxue｜获取入口', 22, MUTED)).arrange(DOWN, buff=.19).move_to([0, -7.05, 0])
        axis = VGroup(
            Arrow(xy((-1.65, 0)), xy((3.55, 0)), buff=0, color=AXIS, stroke_width=1.5, tip_length=.12),
            Arrow(xy((0, -2.75)), xy((0, 2.75)), buff=0, color=AXIS, stroke_width=1.5, tip_length=.12),
            eq('x', 25, MUTED).move_to(xy((3.55, 0))+RIGHT*.2+DOWN*.22),
            eq('y', 25, MUTED).move_to(xy((0, 2.75))+LEFT*.22))
        parabola = ParametricFunction(lambda u: xy(curve(u)), t_range=[-2.6, 2.6], color=BLUE, stroke_width=3)
        labels = {name: eq(name, 28, color) for name, color in [('P', ORANGE), ('A', PURPLE), ('B', PURPLE), ('M', GOLD)]}

        def geometry():
            P, A, B = state(t.get_value())
            return VGroup(
                Line(xy(P), xy(A), color=ORANGE, stroke_width=2.5),
                Line(xy(P), xy(B), color=ORANGE, stroke_width=2.5),
                Line(xy(A), xy(B), color=PURPLE, stroke_width=3.5),
                Dot(xy(P), radius=.075, color=ORANGE),
                Dot(xy(A), radius=.065, color=PURPLE), Dot(xy(B), radius=.065, color=PURPLE),
                labels['P'].copy().move_to(xy(P)+LEFT*.32),
                labels['A'].copy().move_to(xy(A)+LEFT*.26+UP*.22),
                labels['B'].copy().move_to(xy(B)+LEFT*.26+DOWN*.22))

        def midpoint_geometry():
            P, A, B = state(t.get_value())
            M = chord_midpoint(t.get_value())
            direction = xy(A)-xy(B)
            normal = np.array([-direction[1], direction[0], 0]) / np.linalg.norm(direction)
            ticks = []
            for w in (.25, .75):
                center = xy(B)+w*direction
                ticks.append(Line(center-.09*normal, center+.09*normal, color=PURPLE, stroke_width=2.5))
            offset = RIGHT*.32 + (DOWN if t.get_value() >= 0 else UP)*.32
            return VGroup(DashedLine(xy(P), xy(M), dash_length=.12, dashed_ratio=.65, color=GREEN, stroke_width=4),
                *ticks, Dot(xy(M), radius=.09, color=GOLD), labels['M'].copy().move_to(xy(M)+offset))

        moving, midpoint = always_redraw(geometry), always_redraw(midpoint_geometry)
        chord_formula = eq(r'AB:\ y_0y=p(x+x_0)', 30, PURPLE).move_to([0, -4.05, 0])
        invariant = VGroup(
            eq(r'y_M=\frac{y_A+y_B}{2}=y_0', 38, GREEN).move_to([0,-5.48,0]),
            VGroup(eq(r'MP\parallel x', 38, GREEN), cn('轴', 27, GREEN))
                .arrange(RIGHT,buff=.12).move_to([0,-6.15,0]))
        p_value = DecimalNumber(-.8, num_decimal_places=2, font_size=31, color=ORANGE)
        m_value = DecimalNumber(-.8, num_decimal_places=2, font_size=31, color=GOLD)
        p_value.add_updater(lambda m: m.set_value(0 if abs(t.get_value()) < .00001 else state(t.get_value())[0][1]))
        m_value.add_updater(lambda m: m.set_value(0 if abs(chord_midpoint(t.get_value())[1]) < .00001 else chord_midpoint(t.get_value())[1]))
        values = VGroup(
            VGroup(eq(r'y_P=',31,ORANGE), p_value).arrange(RIGHT,buff=.15),
            VGroup(eq(r'y_M=',31,GOLD), m_value).arrange(RIGHT,buff=.15)).arrange(RIGHT,buff=.65).move_to([0,-4.82,0])
        p_anchor, m_anchor = p_value.get_right().copy(), m_value.get_right().copy()
        p_value.add_updater(lambda m: m.align_to(p_anchor, RIGHT))
        m_value.add_updater(lambda m: m.align_to(m_anchor, RIGHT))

        self.add(title, caption, condition, footer, axis, parabola, moving, chord_formula)
        self.wait(1)
        self.play(FadeOut(caption), run_time=.2)
        caption = cn('标出中点 M，连接 MP', 26).move_to([0,6.05,0])
        self.play(FadeIn(caption), FadeIn(midpoint), FadeIn(values), FadeIn(invariant), run_time=.65)
        self.wait(1)
        self.play(FadeOut(caption), run_time=.2)
        caption = cn('P 上下移动，MP 始终水平', 26, GREEN).move_to([0,6.05,0])
        self.play(FadeIn(caption), run_time=.2)
        self.play(t.animate.set_value(0), run_time=2.8, rate_func=smooth)
        self.wait(.8)
        self.play(t.animate.set_value(.8), run_time=2.8, rate_func=smooth)
        self.wait(1.2)
        self.play(t.animate.set_value(-.8), run_time=4, rate_func=smooth)
        self.wait(1.2)
