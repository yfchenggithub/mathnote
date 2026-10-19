"""C003: one orbit, two genuine focal-angle maxima."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import Ellipse as EllipseModel
from manim import *
import numpy as np

config.background_color = '#F7F8FA'
config.frame_width = 9
config.frame_height = 16
INK, MUTED = '#213044', '#526275'
BLUE, ORANGE, GREEN, AXIS = '#2778BD', '#CD6031', '#158068', '#A7B4C2'


class C003MaxFocalAngle(Scene):
    def construct(self):
        model = EllipseModel()
        scale = 1.08
        center = np.array([0., 1.0, 0.])
        def xy(x, y):
            return center + scale*np.array([x, y, 0.])
        tracker = ValueTracker(0)
        def p():
            return xy(*model.point(tracker.get_value()))
        f1, f2 = xy(-model.c, 0), xy(model.c, 0)
        def text(s, size=30, color=INK):
            return Text(s, font='Microsoft YaHei', font_size=size, color=color)
        title = text('焦角何时最大？', 40).move_to([0, 6.85, 0])
        subtitle = text('动点 P 沿椭圆运动，观察两条焦半径', 25, MUTED).move_to([0, 5.95, 0])
        equation = MathTex(r'\frac{x^2}{9}+\frac{y^2}{4}=1\quad(c=\sqrt5)', color=INK, font_size=34).move_to([0, 4.95, 0])
        axes = VGroup(Line(xy(-3.65, 0), xy(3.65, 0)), Line(xy(0, -2.65), xy(0, 2.65))).set_stroke(AXIS, 1.5)
        labels = VGroup(MathTex('F_1', color=INK, font_size=29).next_to(f1, DOWN, buff=.18),
                        MathTex('F_2', color=INK, font_size=29).next_to(f2, DOWN, buff=.18),
                        MathTex('O', color=MUTED, font_size=25).move_to(xy(0, -.3)),
                        MathTex('x', color=MUTED, font_size=25).next_to(xy(3.65, 0), DOWN, buff=.1),
                        MathTex('y', color=MUTED, font_size=25).next_to(xy(0, 2.65), LEFT, buff=.12))
        ellipse = ParametricFunction(lambda t: xy(*model.point(t)), t_range=[0, TAU], color=BLUE, stroke_width=3.8)
        foci = VGroup(Dot(f1, radius=.065, color=INK), Dot(f2, radius=.065, color=INK))
        triangle = always_redraw(lambda: Polygon(f1, f2, p(), fill_color=BLUE, fill_opacity=.07, stroke_width=0))
        rays = always_redraw(lambda: VGroup(Line(p(), f1), Line(p(), f2)).set_stroke(ORANGE, 3.5))
        def height():
            q = p().copy(); q[1] = center[1]
            if np.linalg.norm(p()-q) < .01:
                return VGroup()
            return DashedLine(q, p(), dash_length=.09, color=GREEN, stroke_width=2.2)
        altitude = always_redraw(height)
        def angle_arc():
            v1, v2 = f1-p(), f2-p()
            sweep = np.arctan2(np.cross(v1, v2)[2], np.dot(v1, v2))
            if abs(sweep) < 1e-7:
                return VGroup()
            return Arc(radius=.48, start_angle=np.arctan2(v1[1], v1[0]), angle=sweep,
                       arc_center=p(), color=ORANGE, stroke_width=3)
        arc = always_redraw(angle_arc)
        dot = always_redraw(lambda: Dot(p(), radius=.085, color=ORANGE))
        plabel = always_redraw(lambda: MathTex('P', color=ORANGE, font_size=31).next_to(p(), UP if model.point(tracker.get_value())[1] >= 0 else DOWN, buff=.15))
        theta = MathTex(r'\theta=\angle F_1PF_2=', color=INK, font_size=34)
        # Reserve three integer digits so wider values never overlap the equals sign.
        number = DecimalNumber(100.0, num_decimal_places=1, color=ORANGE, font_size=36)
        degree = MathTex(r'{}^\circ', color=ORANGE, font_size=34)
        readout = VGroup(theta, number, degree).arrange(RIGHT, buff=.08).move_to([0, -2.55, 0])
        anchor = number.get_right().copy()
        number.add_updater(lambda m: m.set_value(model.angle(tracker.get_value())*180/PI).align_to(anchor, RIGHT))
        number.update(0)  # Manim may freeze the opening wait before its first updater tick.
        state = text('从长轴端点出发：焦角为 0°', 29).move_to([0, -3.55, 0])
        formula = MathTex(r'\tan\frac{\theta}{2}=\frac{c|y_P|}{b^2}', color=INK, font_size=43).move_to([0, -4.8, 0])
        footer = text('到焦点连线的距离越大，焦角越大', 26, MUTED).move_to([0, -6.25, 0])
        self.add(title, subtitle, equation, axes, ellipse, triangle, altitude, rays, arc, foci, labels, dot, plabel, readout, state, formula, footer)
        self.wait(1.2)
        def caption(s):
            self.play(Transform(state, text(s, 29).move_to([0, -3.55, 0])), run_time=.3)
        caption('向短轴端点靠近，焦角逐渐增大')
        self.play(tracker.animate.set_value(PI/2), run_time=3, rate_func=smooth)
        caption('上短轴端点：焦角取得最大值')
        top = Circle(radius=.16, color=GREEN, stroke_width=3).move_to(xy(0, model.b))
        self.play(FadeIn(top), Transform(formula, MathTex(r'|y_P|=b\quad\Longrightarrow\quad\tan\frac{\theta_{\max}}2=\frac cb', color=GREEN, font_size=36).move_to([0, -4.8, 0])), run_time=.4)
        self.wait(1.7)
        caption('离开短轴端点，焦角逐渐减小')
        self.play(Transform(formula, MathTex(r'\tan\frac{\theta}{2}=\frac{c|y_P|}{b^2}\leq\frac cb', color=INK, font_size=40).move_to([0, -4.8, 0])), run_time=.3)
        self.play(tracker.animate.set_value(PI), run_time=2.8, rate_func=smooth)
        caption('另一长轴端点：焦角回到 0°')
        self.wait(.7)
        caption('进入下半椭圆，仍由 |y| 决定焦角')
        self.play(tracker.animate.set_value(3*PI/2), run_time=2.8, rate_func=smooth)
        caption('下短轴端点：同样取得最大值')
        bottom = Circle(radius=.16, color=GREEN, stroke_width=3).move_to(xy(0, -model.b))
        self.play(FadeIn(bottom), Transform(formula, MathTex(r'\theta_{\max}=2\arctan\frac cb=2\arcsin e', color=GREEN, font_size=37).move_to([0, -4.8, 0])),
                  Transform(footer, text('最大值恰在 P = (0, ±b) 处取得', 28, GREEN).move_to([0, -6.25, 0])), run_time=.4)
        self.wait(2.2)
        caption('继续运动，焦角再次减小至 0°')
        self.play(tracker.animate.set_value(TAU), run_time=2.8, rate_func=smooth)
        self.wait(.6)
        self.play(FadeOut(top), FadeOut(bottom),
                  Transform(state, text('从长轴端点出发：焦角为 0°', 29).move_to([0, -3.55, 0])),
                  Transform(formula, MathTex(r'\tan\frac{\theta}{2}=\frac{c|y_P|}{b^2}', color=INK, font_size=43).move_to([0, -4.8, 0])),
                  Transform(footer, text('到焦点连线的距离越大，焦角越大', 26, MUTED).move_to([0, -6.25, 0])), run_time=.4)
        self.wait(.7)
