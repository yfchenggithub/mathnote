"""C019's two changing slopes and their invariant product."""
from pathlib import Path
import sys
import numpy as np
from manim import *

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import SlopeProductModel

config.background_color = '#F7F8FA'
config.frame_width, config.frame_height = 9, 16
INK, MUTED, BLUE = '#213044', '#526275', '#2778BD'
PURPLE, ORANGE, GREEN, AXIS = '#8055B2', '#CD6031', '#158068', '#A7B4C2'


def cn(s, size=26, color=INK):
    return Text(s, font='Microsoft YaHei', font_size=size, color=color)


def eq(s, size=32, color=INK):
    return MathTex(s, font_size=size, color=color)


class C019SlopeProduct(Scene):
    def construct(self):
        model = SlopeProductModel()
        theta = ValueTracker(PI/3)
        xy = lambda p: np.array([.75*p[0], .75*p[1]+.7, 0])
        title = cn('两条斜率在变，乘积呢？', 31).move_to([0, 6.95, 0])
        setup = eq(r'\frac{x^2}{16}+\frac{y^2}{9}=1\qquad(a=4,\ b=3)', 30).move_to([0, 5.85, 0])
        caption = cn('移动切点 P，比较 OP 与切线').move_to([0, 4.8, 0])
        axes = VGroup(
            Line(xy((-4.8, 0)), xy((4.8, 0)), color=AXIS, stroke_width=1.5),
            Line(xy((0, -4.2)), xy((0, 4.2)), color=AXIS, stroke_width=1.5),
            eq('x', 24, MUTED).move_to(xy((5.15, 0))),
            eq('y', 24, MUTED).move_to(xy((0, 4.55))),
            eq('O', 23, MUTED).move_to(xy((-.3, -.3))),
        )
        curve = ParametricFunction(lambda t: xy(model.point(t)), t_range=[0, TAU], color=BLUE, stroke_width=3)
        radius = always_redraw(lambda: Line(xy((0, 0)), xy(model.point(theta.get_value())), color=PURPLE, stroke_width=3.3))
        tangent = always_redraw(lambda: Line(*[xy(p) for p in model.clipped_tangent(theta.get_value())], color=ORANGE, stroke_width=3))
        point = always_redraw(lambda: Dot(xy(model.point(theta.get_value())), radius=.078, color=GREEN))
        def plabel():
            p = np.array(model.point(theta.get_value()))
            n = p/np.linalg.norm(p)
            return eq('P', 27, GREEN).move_to(xy(p)+np.array([*n, 0])*.34)
        def tlabel():
            t = theta.get_value()
            p = np.array(model.point(t))
            A, B, _ = model.tangent(t)
            n = np.array([A, B]); n /= np.linalg.norm(n)
            d = np.array([-4*np.sin(t), 3*np.cos(t)]); d /= np.linalg.norm(d)
            return eq('l', 27, ORANGE).move_to(xy(p+d)+np.array([*n, 0])*.24)
        labels = VGroup(always_redraw(plabel), always_redraw(tlabel))

        def numeric(symbol, value, position, color, places=2):
            number = DecimalNumber(-8.8888, num_decimal_places=places, font_size=31, color=color)
            group = VGroup(eq(symbol+r'\approx', 31, color), number).arrange(RIGHT, buff=.14).move_to(position)
            anchor = number.get_right().copy()
            number.add_updater(lambda mob: mob.set_value(value()).align_to(anchor, RIGHT))
            number.update(0)
            return group

        radial_readout = numeric(r'k_{OP}', lambda: model.slopes(theta.get_value())[0], [-2, -3.35, 0], PURPLE)
        tangent_readout = numeric(r'k_l', lambda: model.slopes(theta.get_value())[1], [2, -3.35, 0], ORANGE)
        question = cn('两个斜率相乘，会得到什么？', 27).move_to([0, -4.5, 0])
        principle = cn('OP 从椭圆中心 O 出发', 25, MUTED).move_to([0, -5.7, 0])
        footer = VGroup(cn('切点在椭圆上，且不在坐标轴上', 23, MUTED), eq(r'x_0y_0\ne0', 25, MUTED)).arrange(RIGHT, buff=.22).move_to([0, -7.2, 0])
        self.add(title, setup, caption, axes, curve, radius, tangent, point, labels, radial_readout, tangent_readout, question, principle, footer)
        self.wait(1)
        self.play(theta.animate.set_value(20*DEGREES), run_time=2.2, rate_func=smooth)
        self.play(theta.animate.set_value(70*DEGREES), run_time=3, rate_func=smooth)

        def swap(*pairs):
            self.play(*[FadeOut(old) for old, new in pairs], run_time=.15)
            for old, new in pairs:
                old.become(new)
            self.play(*[FadeIn(old) for old, new in pairs], run_time=.15)

        product = numeric(r'k_{OP}k_l', lambda: model.measured_product(theta.get_value()), [0, -4.5, 0], GREEN, places=4)
        self.play(FadeOut(question), FadeIn(product), run_time=.3)
        swap((caption, cn('一个变陡，另一个变平，乘积不变', 25, GREEN).move_to(caption)))
        self.play(theta.animate.set_value(35*DEGREES), run_time=2, rate_func=smooth)
        self.wait(.6)
        swap((principle, eq(r'k_{OP}k_l=-\frac{b^2}{a^2}=e^2-1', 35, GREEN).move_to(principle)),
             (caption, cn('切点坐标约去，只留下轴长比', 26, GREEN).move_to(caption)))
        proof = eq(r'k_{OP}=\frac{y_0}{x_0}\qquad k_l=-\frac{b^2x_0}{a^2y_0}', 28, MUTED).move_to([0, -6.55, 0])
        self.play(FadeIn(proof), run_time=.3)
        self.wait(1.5)
        self.play(theta.animate.set_value(65*DEGREES), run_time=2.2, rate_func=smooth)
        swap((caption, cn('OP 与切线一般不垂直', 26, GREEN).move_to(caption)),
             (principle, eq(r'k_{OP}k_l=-\frac9{16}\ne-1', 35, GREEN).move_to(principle)))
        self.wait(1.1)
        self.play(theta.animate.set_value(PI/3), run_time=1.5, rate_func=smooth)
        self.play(FadeOut(proof), FadeOut(product), run_time=.3)
        self.add(question)
        swap((caption, cn('移动切点 P，比较 OP 与切线').move_to(caption)),
             (principle, cn('OP 从椭圆中心 O 出发', 25, MUTED).move_to(principle)))
        self.play(FadeIn(question), run_time=.2)
        self.wait(.5)
