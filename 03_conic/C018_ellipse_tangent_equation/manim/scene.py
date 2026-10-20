"""C018: a chord approaches its tangent, which follows the contact point."""
from pathlib import Path
import sys
import numpy as np
from manim import *

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import Ellipse

config.background_color = '#F7F8FA'
config.frame_width, config.frame_height = 9, 16
INK, MUTED, BLUE = '#213044', '#526275', '#2778BD'
ORANGE, GREEN, AXIS = '#CD6031', '#158068', '#A7B4C2'


def cn(s, size=26, color=INK):
    return Text(s, font='Microsoft YaHei', font_size=size, color=color)


def eq(s, size=32, color=INK):
    return MathTex(s, font_size=size, color=color)


class C018TangentEquation(Scene):
    def construct(self):
        model = Ellipse()
        start = PI/3
        theta, other = ValueTracker(start), ValueTracker(0)
        xy = lambda p: np.array([p[0], p[1]+.65, 0])
        title = cn('切点一动，切线如何跟随？', 30).move_to([0, 6.95, 0])
        setup = eq(r'\frac{x^2}{9}+\frac{y^2}{4}=1\qquad(a=3,\ b=2)', 31).move_to([0, 5.85, 0])
        caption = cn('先看经过 P、Q 的割线').move_to([0, 4.8, 0])
        axes = VGroup(
            Line(xy((-3.75, 0)), xy((3.75, 0)), color=AXIS, stroke_width=1.5),
            Line(xy((0, -3.1)), xy((0, 3.1)), color=AXIS, stroke_width=1.5),
            eq('x', 24, MUTED).move_to(xy((4.05, 0))),
            eq('y', 24, MUTED).move_to(xy((0, 3.4))),
            eq('O', 22, MUTED).move_to(xy((-.23, -.25))),
        )
        curve = ParametricFunction(lambda t: xy(model.point(t)), t_range=[0, TAU], color=BLUE, stroke_width=3.2)
        point = always_redraw(lambda: Dot(xy(model.point(theta.get_value())), radius=.08, color=GREEN))
        def label():
            p = np.array(model.point(theta.get_value()))
            n = p/np.linalg.norm(p)
            return eq('P', 27, GREEN).move_to(xy(p)+np.array([n[0], n[1], 0])*.35)
        p_label = always_redraw(label)
        q_point = always_redraw(lambda: Dot(xy(model.point(other.get_value())), radius=.065, color=ORANGE))
        def qlabel():
            opacity = np.clip((abs(other.get_value()-start)-.25)/.3, 0, 1)
            return eq('Q', 25, ORANGE).move_to(xy(model.point(other.get_value()))+np.array([.25, .35, 0])).set_opacity(opacity)
        q_label = always_redraw(qlabel)
        chord = always_redraw(lambda: Line(*[xy(p) for p in model.clipped(model.chord(theta.get_value(), other.get_value()))], color=ORANGE, stroke_width=3))
        condition = cn('P、Q 都在椭圆上', 25, MUTED).move_to([0, -3.5, 0])
        formula = cn('让 Q 沿椭圆靠近 P', 28).move_to([0, -4.75, 0])
        detail = cn('观察割线的极限位置', 25, MUTED).move_to([0, -6.15, 0])
        self.add(title, setup, caption, axes, curve, chord, q_point, q_label, point, p_label, condition, formula, detail)
        self.wait(1)

        def swap(old, new):
            self.play(FadeOut(old), run_time=.15)
            old.become(new)
            self.play(FadeIn(old), run_time=.15)

        swap(caption, cn('Q 靠近 P，割线逐渐变为切线').move_to(caption))
        self.play(other.animate.set_value(start), run_time=3, rate_func=smooth)
        self.remove(chord, q_point, q_label)
        tangent = always_redraw(lambda: Line(*[xy(p) for p in model.clipped(model.tangent(theta.get_value()))], color=ORANGE, stroke_width=3))
        self.add(tangent)
        self.bring_to_front(point, p_label)
        swap(caption, cn('在 P 处，得到唯一的切线', color=GREEN).move_to(caption))
        swap(condition, cn('切点 P(x₀, y₀) 必须在椭圆上', 25, MUTED).move_to(condition))
        swap(formula, eq(r'\frac{x_0x}{a^2}+\frac{y_0y}{b^2}=1', 39, GREEN).move_to(formula))
        swap(detail, eq(r'x^2\mapsto x_0x\qquad y^2\mapsto y_0y', 31, MUTED).move_to(detail))
        self.wait(1)

        def travel(target, duration):
            swap(caption, cn('移动切点，切线随之改变').move_to(caption))
            swap(detail, cn('统一公式，覆盖椭圆上的所有切点', 25, MUTED).move_to(detail))
            self.play(theta.animate.set_value(target), run_time=duration, rate_func=smooth)

        travel(PI/2, 1.2)
        swap(caption, cn('到达上顶点：切线水平', color=GREEN).move_to(caption))
        swap(detail, eq(r'P=(0,2)\quad\Longrightarrow\quad y=2', 31, GREEN).move_to(detail))
        self.wait(.8)
        travel(PI, 2)
        swap(caption, cn('到达左顶点：切线竖直', color=GREEN).move_to(caption))
        swap(detail, eq(r'P=(-3,0)\quad\Longrightarrow\quad x=-3', 31, GREEN).move_to(detail))
        self.wait(.8)
        travel(3*PI/2, 2)
        swap(caption, cn('到达下顶点：切线水平', color=GREEN).move_to(caption))
        swap(detail, eq(r'P=(0,-2)\quad\Longrightarrow\quad y=-2', 31, GREEN).move_to(detail))
        self.wait(.8)
        travel(TAU, 2)
        swap(caption, cn('到达右顶点：切线竖直', color=GREEN).move_to(caption))
        swap(detail, eq(r'P=(3,0)\quad\Longrightarrow\quad x=3', 31, GREEN).move_to(detail))
        self.wait(.8)
        travel(TAU+start, 1.2)
        swap(caption, cn('不必除以 y₀，也就不会漏掉顶点', 25, GREEN).move_to(caption))
        self.wait(1.1)

        # Exact same geometry at the loop seam; re-open the chord continuously.
        theta.set_value(start)
        other.set_value(start)
        self.remove(tangent)
        self.add(chord, q_point, q_label)
        self.bring_to_front(point, p_label)
        swap(caption, cn('让 Q 离开 P，重新观察割线').move_to(caption))
        swap(condition, cn('P、Q 都在椭圆上', 25, MUTED).move_to(condition))
        swap(formula, cn('让 Q 沿椭圆靠近 P', 28).move_to(formula))
        swap(detail, cn('观察割线的极限位置', 25, MUTED).move_to(detail))
        self.play(other.animate.set_value(0), run_time=1.5, rate_func=smooth)
        swap(caption, cn('先看经过 P、Q 的割线').move_to(caption))
        self.wait(.5)
