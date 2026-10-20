"""C020: two focal radii and the actual perpendicular from the center."""
from pathlib import Path
import sys
import numpy as np
from manim import *

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import DistanceProductModel

config.background_color = '#F7F8FA'
config.frame_width, config.frame_height = 9, 16
INK, MUTED, BLUE = '#213044', '#526275', '#2778BD'
PURPLE, ORANGE, GREEN, AXIS = '#8055B2', '#CD6031', '#158068', '#A7B4C2'


def cn(s, size=26, color=INK):
    return Text(s, font='Microsoft YaHei', font_size=size, color=color)


def eq(s, size=32, color=INK):
    return MathTex(s, font_size=size, color=color)


class C020DistanceProduct(Scene):
    def construct(self):
        model = DistanceProductModel()
        t = ValueTracker(PI/3)
        xy = lambda p: np.array([.72*p[0], .72*p[1]+.8, 0])
        state = lambda: model.state(t.get_value())
        title = cn('距离在变，什么保持不变？', 30).move_to([0, 6.95, 0])
        setup = eq(r'\frac{x^2}{16}+\frac{y^2}{9}=1\qquad(a=4,\ b=3)', 30).move_to([0, 5.85, 0])
        caption = cn('从中心 O 向切线作垂线 OH', 26).move_to([0, 4.8, 0])
        axes = VGroup(
            Line(xy((-5, 0)), xy((5, 0)), color=AXIS, stroke_width=1.3),
            Line(xy((0, -4.35)), xy((0, 4.35)), color=AXIS, stroke_width=1.3),
            eq('x', 23, MUTED).move_to(xy((5.35, 0))),
            eq('y', 23, MUTED).move_to(xy((0, 4.65))),
            eq('O', 23, MUTED).move_to(xy((-.25, -.35))),
        )
        curve = ParametricFunction(lambda u: xy(model.point(u)), t_range=[0, TAU], color=BLUE, stroke_width=3)
        focal_marks = VGroup()
        for i, f in enumerate(model.foci, 1):
            focal_marks.add(Dot(xy(f), radius=.055, color=INK), eq('F_'+str(i), 25, MUTED).move_to(xy(f)+DOWN*.34))
        focal_radii = always_redraw(lambda: VGroup(*[Line(xy(f), xy(state()['p']), color=PURPLE, stroke_width=2.5) for f in model.foci]))
        tangent = always_redraw(lambda: Line(*[xy(p) for p in model.clipped_tangent(t.get_value())], color=MUTED, stroke_width=2.7))
        perpendicular = always_redraw(lambda: Line(xy((0, 0)), xy(state()['h']), color=ORANGE, stroke_width=3.4))
        hdot = always_redraw(lambda: Dot(xy(state()['h']), radius=.06, color=ORANGE))
        pdot = always_redraw(lambda: Dot(xy(state()['p']), radius=.078, color=GREEN))

        def right_angle():
            A, B, _ = model.tangent(t.get_value())
            n = np.array([A, B]); n /= np.linalg.norm(n)
            u, v = -n, np.array([-n[1], n[0]])
            h = np.array(state()['h'])
            return VMobject(color=ORANGE, stroke_width=1.6).set_points_as_corners([xy(h+.2*u), xy(h+.2*(u+v)), xy(h+.2*v)])

        def point_labels():
            p, h = np.array(state()['p']), np.array(state()['h'])
            unit = p/np.linalg.norm(p)
            label = eq('P=H' if np.linalg.norm(p-h) < 1e-8 else 'P', 25, GREEN).move_to(xy(p)+np.array([*unit, 0])*.36)
            result = VGroup(label)
            if np.linalg.norm(p-h) >= .5:
                A, B, _ = model.tangent(t.get_value())
                n = np.array([A, B]); n /= np.linalg.norm(n)
                v = np.array([-n[1], n[0]])
                away = -v if np.dot(p-h, v) > 0 else v
                offset = .35*n+.4*away
                result.add(eq('H', 24, ORANGE).move_to(xy(h)+np.array([*offset, 0])))
            return result

        def length_labels():
            p, h = np.array(state()['p']), np.array(state()['h'])
            result = VGroup()
            for i, focus in enumerate(model.foci):
                f = np.array(focus)
                v = p-f; v /= np.linalg.norm(v)
                offset = np.array([-v[1], v[0]]) if i == 0 else np.array([v[1], -v[0]])
                result.add(eq('r_'+str(i+1), 25, PURPLE).move_to(xy((p+f)/2)+np.array([*offset, 0])*.24))
            A, B, _ = model.tangent(t.get_value())
            n = np.array([A, B]); n /= np.linalg.norm(n)
            result.add(eq('d', 27, ORANGE).move_to(xy(h/2)+np.array([n[1], -n[0], 0])*.25))
            return result

        def numeric(symbol, key, position, color, places=2):
            number = DecimalNumber(-8.888, num_decimal_places=places, font_size=31, color=color)
            group = VGroup(eq(symbol+r'\approx', 31, color), number).arrange(RIGHT, buff=.14).move_to(position)
            anchor = number.get_right().copy()
            number.add_updater(lambda mob: mob.set_value(state()[key]).align_to(anchor, RIGHT))
            number.update(0)
            return group

        mean_readout = numeric(r'\sqrt{r_1r_2}', 'geometric_mean', [-2.05, -3.25, 0], PURPLE)
        distance_readout = numeric('d', 'd', [2.05, -3.25, 0], ORANGE)
        question = cn('让 P 移动，观察两个距离量', 27).move_to([0, -4.5, 0])
        conclusion = cn('一个来自焦半径，一个来自垂距', 24, MUTED).move_to([0, -5.7, 0])
        definitions = eq(r'r_1=PF_1\quad r_2=PF_2\quad d=OH', 27, MUTED).move_to([0, -7.25, 0])
        self.add(title, setup, caption, axes, curve, focal_radii, tangent, perpendicular,
                 focal_marks, hdot, pdot, always_redraw(right_angle), always_redraw(point_labels),
                 always_redraw(length_labels), mean_readout, distance_readout, question, conclusion, definitions)
        self.wait(1)

        def swap(*pairs):
            self.play(*[FadeOut(old) for old, new in pairs], run_time=.15)
            for old, new in pairs:
                old.become(new)
            self.play(*[FadeIn(old) for old, new in pairs], run_time=.15)

        swap((caption, cn('P 移动，焦半径与垂距都在变化').move_to(caption)))
        self.play(t.animate.set_value(25*DEGREES), run_time=2, rate_func=smooth)
        self.play(t.animate.set_value(PI/2), run_time=2.5, rate_func=smooth)
        swap((caption, cn('上顶点：切点 P 与垂足 H 重合', 25, GREEN).move_to(caption)))
        product = numeric(r'\sqrt{r_1r_2}\,d', 'product', [0, -4.5, 0], GREEN)
        self.play(FadeOut(question), FadeIn(product), run_time=.3)
        self.wait(.9)
        swap((caption, cn('焦半径几何均值变小，垂距变大', 25).move_to(caption)))
        self.play(t.animate.set_value(155*DEGREES), run_time=3, rate_func=smooth)
        swap((caption, cn('两项此消彼长，乘积始终不变', 26, GREEN).move_to(caption)),
             (conclusion, eq(r'\sqrt{r_1r_2}\,d=ab', 39, GREEN).move_to(conclusion)))
        square = eq(r'r_1r_2d^2=a^2b^2', 29, MUTED).move_to([0, -6.5, 0])
        self.play(FadeIn(square), run_time=.3)
        self.wait(1.2)
        swap((caption, cn('继续移动，乘积仍然等于 12', 26, GREEN).move_to(caption)))
        self.play(t.animate.set_value(PI/3), run_time=3, rate_func=smooth)
        self.wait(.8)
        self.play(FadeOut(square), FadeOut(product), run_time=.3)
        swap((caption, cn('从中心 O 向切线作垂线 OH', 26).move_to(caption)),
             (conclusion, cn('一个来自焦半径，一个来自垂距', 24, MUTED).move_to(conclusion)))
        self.play(FadeIn(question), run_time=.2)
        self.wait(.5)
