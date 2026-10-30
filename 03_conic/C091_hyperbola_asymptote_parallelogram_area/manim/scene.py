"""C091: moving point, changing shape, constant parallelogram area."""
import sys
from pathlib import Path
import numpy as np
from manim import *

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import on_hyperbola

config.background_color = "#F7F8FA"
config.frame_width = 8
config.frame_height = 128/9

INK = "#213044"
MUTED = "#526275"
BLUE = "#2778BD"
ORANGE = "#CD6031"
GOLD = "#B77D12"
GREEN = "#158068"
GUIDE = "#8B98A8"


class C091ConstantArea(Scene):
    def construct(self):
        def text(s, size=27, color=INK):
            return Text(s, font="Microsoft YaHei", font_size=size, color=color)

        title = text("形状在变，面积不变", 34).move_to([0, 6.15, 0])
        condition = MathTex(r"\frac{x^2}{9}-\frac{y^2}{4}=1,\quad a=3,\ b=2",
                            color=MUTED, font_size=30).move_to([0, 5.28, 0])
        footer = VGroup(
            text("查结论 · 看图解 · 学证明｜知树 App", 23, MUTED),
            text("公众号 ok-shuxue｜获取入口", 21, MUTED),
        ).arrange(DOWN, buff=.18).move_to([0,-6.12,0])
        self.add(title, condition, footer)

        # Equal coordinate units: no anisotropic stretching.
        origin = np.array([-2.65, .9, 0.0])
        def xy(x, y):
            return origin + np.array([x, y, 0])
        axes = VGroup(
            Arrow(xy(-.25,0), xy(5.65,0), buff=0, color=GUIDE, stroke_width=1.4,
                  max_tip_length_to_length_ratio=.018),
            Arrow(xy(0,-3.25), xy(0,3.3), buff=0, color=GUIDE, stroke_width=1.4,
                  max_tip_length_to_length_ratio=.018),
        )
        labels = VGroup(MathTex('O',color=INK,font_size=25).next_to(xy(0,0),DL,buff=.12),
                        MathTex('x',color=MUTED,font_size=25).next_to(xy(5.65,0),RIGHT,buff=.06),
                        MathTex('y',color=MUTED,font_size=25).next_to(xy(0,3.3),UP,buff=.06))
        asymptotes = VGroup(*[
            DashedLine(xy(-.2, sign*(-.2)*2/3), xy(4.95,sign*3.3),
                       color=GUIDE, stroke_width=1.7, dash_length=.12)
            for sign in (1,-1)
        ])
        curve = ParametricFunction(lambda t: xy(3*np.cosh(t),2*np.sinh(t)),
                                   t_range=[-1.2,1.2], color=BLUE, stroke_width=3)
        asym_labels = VGroup(
            MathTex(r'y=\frac23x',color=MUTED,font_size=24).move_to(xy(4.7,3.52)),
            MathTex(r'y=-\frac23x',color=MUTED,font_size=24).move_to(xy(4.7,-3.53)))
        tracker = ValueTracker(.4)
        def state():
            return on_hyperbola(tracker.get_value())
        def polygon():
            s = state()
            return Polygon(xy(0,0),xy(*s.q),xy(*s.p),xy(*s.r),
                           color=ORANGE,stroke_width=3,fill_color=ORANGE,fill_opacity=.16)
        shape = always_redraw(polygon)
        points = always_redraw(lambda: VGroup(
            Dot(xy(*state().p),radius=.065,color=GOLD),
            Dot(xy(*state().q),radius=.045,color=ORANGE),
            Dot(xy(*state().r),radius=.045,color=ORANGE)))
        def p_label_position():
            t = tracker.get_value()
            normal = np.array([np.cosh(t)/3, -np.sinh(t)/2, 0])
            normal *= .45/np.linalg.norm(normal)
            # Smoothly lift the label clear of the x axis near the vertex.
            return xy(*state().p)+normal+UP*(.32*np.exp(-t*t/.04))
        point_labels = always_redraw(lambda: VGroup(
            MathTex('P',color=GOLD,font_size=29).move_to(p_label_position())
                .add_background_rectangle(color=config.background_color,opacity=1,buff=.045),
            MathTex('Q',color=ORANGE,font_size=26).next_to(xy(*state().q),UP,buff=.15),
            MathTex('R',color=ORANGE,font_size=26).next_to(xy(*state().r),DOWN,buff=.15)))
        status = text("过 P 分别作两条渐近线的平行线",25).move_to([0,-3.4,0])
        area_label = MathTex(r'S_{OQPR}=',font_size=42,color=GREEN).move_to([-.55,-4.25,0])
        area_value = DecimalNumber(3,num_decimal_places=2,font_size=42,color=GREEN)
        area_value.next_to(area_label,RIGHT,buff=.15)
        area_value.add_updater(lambda m: m.set_value(state().area).next_to(area_label,RIGHT,buff=.15))
        area = VGroup(area_label,area_value)
        note = text("P 与 O 是对顶点",24,MUTED).move_to([0,-5.05,0])

        self.play(FadeIn(axes),FadeIn(labels),Create(asymptotes),Create(curve),
                  FadeIn(asym_labels),run_time=1.2)
        self.add(shape,points,point_labels)
        self.play(FadeIn(status),FadeIn(area),FadeIn(note),run_time=.6)
        self.wait(1)
        moving_status = text("P 沿双曲线移动，观察橙色面积",25).move_to(status)
        self.play(Transform(status,moving_status),run_time=.3)
        self.play(tracker.animate.set_value(1),run_time=2,rate_func=smooth)
        self.wait(.7)
        self.play(tracker.animate.set_value(0),run_time=2.5,rate_func=smooth)
        vertex_note = text("经过顶点：成为菱形，面积仍为 3",24,MUTED).move_to(note)
        self.play(Transform(note,vertex_note),run_time=.3)
        self.wait(1)
        self.play(Transform(note,text("边长改变，面积始终为 3",24,MUTED).move_to(note)),run_time=.3)
        self.play(tracker.animate.set_value(-1),run_time=3,rate_func=smooth)
        self.wait(.7)
        self.play(tracker.animate.set_value(.4),run_time=3,rate_func=smooth)
        self.wait(.6)

        explanation = text("为什么恒定？双曲线固定了平方差",25).move_to(status)
        formula = MathTex(r'S=\frac{ab}{2}\left|\frac{x^2}{a^2}-\frac{y^2}{b^2}\right|',
                          color=GREEN,font_size=36).move_to([0,-4.3,0])
        final_note = text("括号内恒为 1，所以 S = ab/2",25,MUTED).move_to(note)
        area_value.clear_updaters()
        self.play(Transform(status,explanation),FadeOut(area),FadeIn(formula),
                  Transform(note,final_note),run_time=.5)
        self.wait(2.6)
        self.play(FadeOut(formula),FadeIn(area),
                  Transform(status,text("过 P 分别作两条渐近线的平行线",25).move_to(status)),
                  Transform(note,text("P 与 O 是对顶点",24,MUTED).move_to(note)),run_time=.4)
        self.wait(.8)
        for mob in (shape, points, point_labels):
            mob.clear_updaters()
        self.play(*[FadeOut(mob) for mob in
                    (axes,labels,asymptotes,curve,asym_labels,shape,points,
                     point_labels,status,area,note)],run_time=.5)
