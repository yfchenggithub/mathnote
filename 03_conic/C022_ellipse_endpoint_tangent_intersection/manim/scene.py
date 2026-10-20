"""C022: fixed product of vertical heights, then the minimum area rectangle."""
from pathlib import Path
import sys
import numpy as np
from manim import *

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import EndpointModel

config.background_color = '#F7F8FA'
config.frame_width, config.frame_height = 9, 16
INK, MUTED, BLUE = '#213044', '#526275', '#2778BD'
ORANGE, PURPLE, GREEN, AXIS = '#CD6031', '#8055B2', '#158068', '#A7B4C2'


def cn(s, size=26, color=INK):
    return Text(s, font='Microsoft YaHei', font_size=size, color=color)


def eq(s, size=32, color=INK):
    return MathTex(s, font_size=size, color=color)


class C022EndpointIntersection(Scene):
    def construct(self):
        model = EndpointModel()
        start, end = np.arccos(.6), np.arccos(-.6)
        t = ValueTracker(start)
        state = lambda: model.state(t.get_value())
        xy = lambda p: np.array([.95*p[0], .95*p[1]-.5, 0])
        title = cn('一边变长，一边变短', 32).move_to([0, 6.95, 0])
        setup = eq(r'\frac{x^2}{9}+\frac{y^2}{4}=1\qquad(a=3,\ b=2)', 30).move_to([0, 5.85, 0])
        caption = cn('第三条切线，截出两段竖直长度', 25).move_to([0, 4.8, 0])
        shade = always_redraw(lambda: Polygon(*[xy(p) for p in state()['vertices']], stroke_width=0, fill_color=GREEN, fill_opacity=.09))
        axes = VGroup(Line(xy((-3.65, 0)), xy((3.65, 0)), color=AXIS, stroke_width=1.3),
                      Line(xy((0, -2.3)), xy((0, 4.35)), color=AXIS, stroke_width=1.3),
                      eq('x', 23, MUTED).move_to(xy((3.9, 0))),
                      eq('y', 23, MUTED).move_to(xy((0, 4.6))),
                      eq('O', 22, MUTED).move_to(xy((-.23, -.28))))
        rails = VGroup(*[Line(xy((x, -2.25)), xy((x, 4.35)), color=AXIS, stroke_width=2) for x in (-3, 3)])
        curve = ParametricFunction(lambda u: xy(model.point(u)), t_range=[0, TAU], color=BLUE, stroke_width=3)
        tangent = always_redraw(lambda: Line(*[xy(p) for p in model.tangent_ends(t.get_value())], color=INK, stroke_width=2.7))
        heights = always_redraw(lambda: VGroup(
            Line(xy((-3, 0)), xy(state()['p1']), color=ORANGE, stroke_width=4),
            Line(xy((3, 0)), xy(state()['p2']), color=PURPLE, stroke_width=4)))
        endpoints = VGroup(*[Dot(xy((x, 0)), radius=.055, color=INK) for x in (-3, 3)],
                           eq('A_1', 24, MUTED).move_to(xy((-3, 0))+LEFT*.35+DOWN*.25),
                           eq('A_2', 24, MUTED).move_to(xy((3, 0))+RIGHT*.35+DOWN*.25))
        points = always_redraw(lambda: VGroup(Dot(xy(state()['p1']), radius=.06, color=ORANGE),
                                               Dot(xy(state()['p2']), radius=.06, color=PURPLE),
                                               Dot(xy(state()['p']), radius=.078, color=GREEN)))
        def point_labels():
            s = state()
            A, B = s['p'][0]/9, s['p'][1]/4
            n = np.array([A, B]); n /= np.linalg.norm(n)
            return VGroup(eq('P_1', 25, ORANGE).move_to(xy(s['p1'])+LEFT*.35+UP*.4),
                          eq('P_2', 25, PURPLE).move_to(xy(s['p2'])+RIGHT*.35+UP*.4),
                          eq('P', 26, GREEN).move_to(xy(s['p'])+np.array([*n, 0])*.35),
                          eq('h_1', 26, ORANGE).move_to(xy((-3, s['h1']/2))+LEFT*.4),
                          eq('h_2', 26, PURPLE).move_to(xy((3, s['h2']/2))+RIGHT*.4))
        width = VGroup(DoubleArrow(xy((-3, -.55)), xy((3, -.55)), buff=0, tip_length=.09, color=AXIS, stroke_width=1.4),
                       eq('2a', 24, MUTED).move_to(xy((0, -.55))+DOWN*.23))

        def numeric(symbol, key, position, color):
            number = DecimalNumber(-88.88, num_decimal_places=2, font_size=31, color=color)
            group = VGroup(eq(symbol+r'\approx', 31, color), number).arrange(RIGHT, buff=.14).move_to(position)
            anchor = number.get_right().copy()
            number.add_updater(lambda mob: mob.set_value(state()[key]).align_to(anchor, RIGHT))
            number.update(0)
            return group

        h1 = numeric('h_1', 'h1', [-2, -3.15, 0], ORANGE)
        h2 = numeric('h_2', 'h2', [2, -3.15, 0], PURPLE)
        question = cn('两段长度的积会改变吗？', 27).move_to([0, -4.25, 0])
        area = numeric('S', 'area', [0, -5.25, 0], GREEN)
        conclusion = eq(r'h_1=|A_1P_1|\qquad h_2=|A_2P_2|', 28, MUTED).move_to([0, -6.3, 0])
        footer = VGroup(eq(r'y_0\ne0', 25, MUTED), cn('长轴端点除外', 23, MUTED)).arrange(RIGHT, buff=.25).move_to([0, -7.3, 0])
        self.add(title, setup, caption, shade, axes, rails, curve, width, tangent, heights,
                 endpoints, points, always_redraw(point_labels), h1, h2, question, area, conclusion, footer)
        self.wait(1)

        def swap(*pairs):
            self.play(*[FadeOut(old) for old, new in pairs], run_time=.15)
            for old, new in pairs:
                old.become(new)
            self.play(*[FadeIn(old) for old, new in pairs], run_time=.15)

        self.play(t.animate.set_value(70*DEGREES), run_time=2, rate_func=smooth)
        product = numeric('h_1h_2', 'product', [0, -4.25, 0], GREEN)
        self.play(FadeOut(question), FadeIn(product), run_time=.3)
        swap((caption, cn('两段竖直长度，乘积恒为 b²', 26, GREEN).move_to(caption)))
        self.play(t.animate.set_value(PI/2), run_time=1.5, rate_func=smooth)
        swap((caption, cn('等高时成为矩形，面积最小', 26, GREEN).move_to(caption)),
             (conclusion, eq(r'S=a(h_1+h_2)\ge2ab=12', 32, GREEN).move_to(conclusion)))
        self.wait(1.4)
        swap((caption, cn('另一侧变高，长度乘积仍不变', 26).move_to(caption)))
        self.play(t.animate.set_value(end), run_time=2.5, rate_func=smooth)
        self.wait(.6)
        swap((caption, cn('回到等高位置，观察面积变化', 26).move_to(caption)))
        self.play(t.animate.set_value(PI/2), run_time=2.5, rate_func=smooth)
        swap((caption, eq(r'h_1=h_2=b\quad\Longrightarrow\quad S_{\min}=2ab', 30, GREEN).move_to(caption)))
        self.wait(1.5)
        swap((caption, cn('移动切点，矩形重新变为梯形', 26).move_to(caption)))
        self.play(t.animate.set_value(start), run_time=2, rate_func=smooth)
        self.play(FadeOut(product), run_time=.3)
        swap((caption, cn('第三条切线，截出两段竖直长度', 25).move_to(caption)),
             (conclusion, eq(r'h_1=|A_1P_1|\qquad h_2=|A_2P_2|', 28, MUTED).move_to(conclusion)))
        self.play(FadeIn(question), run_time=.2)
        self.wait(.5)
