"""C093: one sum and one difference determine the focal distances."""
from pathlib import Path
import sys

import numpy as np
from manim import *

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c093_model import ConfocalConics


config.background_color = "#F7F8FA"
config.frame_width = 9
config.frame_height = 16

INK = "#213044"
SECONDARY = "#526275"
ELLIPSE = "#2778BD"
HYPERBOLA = "#B34D59"
LONG = "#CD6031"
SHORT = "#158068"
AXIS = "#A7B4C2"
FONT = "Microsoft YaHei"


class C093FocalDistances(Scene):
    def construct(self):
        self.A = ValueTracker(1.0)
        self.scale_xy = 0.82
        self.graph_origin = np.array([0., 1.1, 0.])

        def cn(text, size=27, color=INK):
            return Text(text, font=FONT, font_size=size, color=color)

        title = cn("共焦交点：一和一差定长度", 32).move_to([0, 6.95, 0])
        caption = cn("同一公共点，同时满足两种定义", 24, SECONDARY).move_to([0, 6.2, 0])
        parameters = VGroup(
            MathTex("a=4,\\quad c=2,\\quad A=", color=INK, font_size=38),
            DecimalNumber(1, num_decimal_places=2, color=HYPERBOLA, font_size=38),
        ).arrange(RIGHT, buff=0.1).move_to([0, 5.35, 0])
        parameters[1].add_updater(lambda m: m.set_value(self.A.get_value()).next_to(parameters[0], RIGHT, buff=0.14))
        brand = VGroup(
            cn("查结论 · 看图解 · 学证明｜知树 App", 23, SECONDARY),
            cn("公众号 ok-shuxue｜获取入口", 21, SECONDARY),
        ).arrange(DOWN, buff=0.17).move_to([0, -7.1, 0])
        separator = Line([-3.85, -6.48, 0], [3.85, -6.48, 0], color=AXIS, stroke_width=1)

        axes = VGroup(
            Arrow(self.xy(-4.5, 0), self.xy(4.65, 0), buff=0,
                  color=AXIS, stroke_width=1.4, max_tip_length_to_length_ratio=0.018),
            Arrow(self.xy(0, -3.65), self.xy(0, 3.8), buff=0,
                  color=AXIS, stroke_width=1.4, max_tip_length_to_length_ratio=0.022),
            MathTex("x", color=SECONDARY, font_size=25).move_to(self.xy(4.85, 0)),
            MathTex("y", color=SECONDARY, font_size=25).move_to(self.xy(0, 4.02)),
            MathTex("O", color=SECONDARY, font_size=22).move_to(self.xy(0.22, -0.28)),
        )
        ellipse = ParametricFunction(
            lambda t: self.xy(4*np.cos(t), np.sqrt(12)*np.sin(t)),
            t_range=[0, TAU, TAU/220], color=ELLIPSE, stroke_width=3.4,
        )
        hyperbola = VGroup(*[self.hyperbola_curve(sign) for sign in (-1, 1)])
        for curve, sign in zip(hyperbola, (-1, 1)):
            curve.add_updater(lambda m, sign=sign: m.become(self.hyperbola_curve(sign)))
        names = VGroup(
            cn("E  椭圆", 24, ELLIPSE).move_to([-2.8, 4.42, 0]),
            cn("H  双曲线", 24, HYPERBOLA).move_to([2.65, 4.42, 0]),
        )
        foci = VGroup()
        for sign, text in [(-1, "F_1"), (1, "F_2")]:
            p = self.xy(sign*2, 0)
            foci.add(Dot(p, radius=0.055, color=INK),
                     MathTex(text, font_size=32, color=INK).move_to(p+DOWN*0.35))

        self.add(title, caption, parameters, brand, separator, axes, ellipse, hyperbola, names, foci)
        self.wait(0.7)
        geometry = self.focal_geometry(1)
        readings = self.readings(1)
        self.play(FadeIn(geometry), FadeIn(readings), run_time=0.8)
        self.wait(0.8)

        sum_line = MathTex(r"PF_1+PF_2=8=2a", font_size=40, color=ELLIPSE).move_to([0, -5.15, 0])
        difference = self.difference_reading()
        next_caption = cn("椭圆定和，双曲线定差", 26, SECONDARY).move_to(caption)
        self.play(Transform(caption, next_caption), FadeIn(sum_line), run_time=0.4)
        self.play(FadeIn(difference), run_time=0.4)
        self.wait(1.4)

        self.play(Transform(caption, cn("固定椭圆，改变双曲线的 A", 25, SECONDARY).move_to(caption)), run_time=0.4)
        self.play(self.A.animate.set_value(0.6), run_time=2.2, rate_func=smooth)
        self.wait(0.8)
        self.play(self.A.animate.set_value(1.5), run_time=3.1, rate_func=smooth)
        self.wait(1.0)
        self.play(self.A.animate.set_value(1.0), run_time=2.2, rate_func=smooth)
        self.wait(0.7)

        self.play(Transform(caption, cn("改看左支公共点：焦点对应交换", 24, SECONDARY).move_to(caption)),
                  FadeOut(geometry), FadeOut(readings), run_time=0.45)
        geometry = self.focal_geometry(-1)
        readings = self.readings(-1)
        self.play(FadeIn(geometry), FadeIn(readings), run_time=0.45)
        self.wait(1.8)

        summary = MathTex(r"\{PF_1,PF_2\}=\{a+A,\ a-A\}", font_size=40, color=INK).move_to([0, -5.15, 0])
        condition = MathTex("a>c>A>0", font_size=36, color=SECONDARY).move_to([0, -5.9, 0])
        self.play(Transform(caption, cn("先求长短，再按左右支对应", 26, SECONDARY).move_to(caption)),
                  FadeOut(sum_line), FadeOut(difference), FadeIn(summary), FadeIn(condition), run_time=0.5)
        self.wait(2.2)

        # Return to exactly the opening content; never move a common point
        # through positions that are not intersections of these fixed conics.
        self.play(FadeOut(geometry), FadeOut(readings), FadeOut(summary), FadeOut(condition),
                  Transform(caption, cn("同一公共点，同时满足两种定义", 24, SECONDARY).move_to(caption)), run_time=0.5)
        self.wait(0.8)

    def model(self):
        return ConfocalConics(A=self.A.get_value())

    def xy(self, x, y):
        return self.graph_origin + self.scale_xy*np.array([x, y, 0.])

    def hyperbola_curve(self, branch):
        m = self.model()
        limit = m.visible_hyperbola_y_limit()
        points = [self.xy(*m.hyperbola_point(y, branch)) for y in np.linspace(-limit, limit, 181)]
        return VMobject(color=HYPERBOLA, stroke_width=3).set_points_as_corners(points)

    def focal_geometry(self, branch):
        def location():
            return self.xy(*self.model().intersection(branch))

        result = VGroup()
        for index, fx in [(0, -2), (1, 2)]:
            color = LONG if (branch == 1) == (index == 0) else SHORT
            ray = Line(self.xy(fx, 0), location(), color=color, stroke_width=4.5)
            ray.add_updater(lambda line, fx=fx: line.put_start_and_end_on(self.xy(fx, 0), location()))
            result.add(ray)
        point = Dot(location(), radius=0.073, color=INK)
        point.add_updater(lambda dot: dot.move_to(location()))
        label = MathTex("P", font_size=32, color=INK)
        label.add_updater(lambda text: text.move_to(location()+np.array([branch*0.55, 0.06, 0.])))
        result.add(point, label)
        return result

    def readings(self, branch):
        result = VGroup()
        for index, y in [(0, -2.5), (1, -3.8)]:
            is_long = (branch == 1) == (index == 0)
            color = LONG if is_long else SHORT
            sign = "+" if is_long else "-"
            value = lambda index=index: self.model().distances(branch)[index]
            formula = MathTex(f"PF_{index+1}=a{sign}A=", color=color, font_size=42)
            number = DecimalNumber(value(), num_decimal_places=2, font_size=42, color=color)
            row = VGroup(formula, number).arrange(RIGHT, buff=0.16).move_to([0, y, 0])
            number.add_updater(lambda number, value=value, formula=formula: number.set_value(value()).next_to(formula, RIGHT, buff=0.16))
            bar_y = y-0.48
            start = np.array([-3.3, bar_y, 0.])
            bar = Line(start, start+RIGHT*value()*1.16, color=color, stroke_width=8)
            bar.add_updater(lambda line, value=value, start=start: line.put_start_and_end_on(start, start+RIGHT*value()*1.16))
            left_tick = Line(start+UP*0.1, start+DOWN*0.1, color=SECONDARY, stroke_width=1.2)
            right_tick = left_tick.copy()
            right_tick.add_updater(lambda tick, value=value, start=start: tick.move_to(start+RIGHT*value()*1.16))
            result.add(row, bar, left_tick, right_tick)
        return result

    def difference_reading(self):
        group = VGroup(
            MathTex(r"|PF_1-PF_2|=", font_size=40, color=HYPERBOLA),
            DecimalNumber(2, num_decimal_places=2, font_size=40, color=HYPERBOLA),
            MathTex("=2A", font_size=40, color=HYPERBOLA),
        ).arrange(RIGHT, buff=0.08).move_to([0, -5.9, 0])
        group[1].add_updater(lambda n: n.set_value(2*self.A.get_value()).next_to(group[0], RIGHT, buff=0.12))
        group[2].add_updater(lambda m: m.next_to(group[1], RIGHT, buff=0.12))
        return group
