"""T021: two horizontal transformation orders, one tracked source peak."""

from __future__ import annotations

from math import pi

from manim import (
    Axes, Circle, Dot, FadeIn, FadeOut, MathTex, Rectangle, Scene, Text,
    ValueTracker, VGroup, always_redraw, config, linear,
)

from math_model import (
    DEMO, TRACKED_T, amplitude_scale, baseline, first_scale, first_shift,
    horizontal_result, reflection, second_scale, second_shift,
)


config.frame_width = 9
config.frame_height = 16

BG = "#F8FAFD"
INK = "#183047"
MUTED = "#5E7285"
BLUE = "#2377C4"
ORANGE = "#DC7142"
PURPLE = "#785DA9"
GREEN = "#168A69"
GOLD = "#D49A16"
LINE = "#C9D6E2"
FONT = "Microsoft YaHei"
XMIN, XMAX = -pi, pi


class T021TransformOrderLesson(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG

        title = Text("两条路径，为何到同一图像？", font=FONT,
                     font_size=36, color=INK, weight="BOLD").move_to([0, 7.20, 0])
        params = MathTex(r"\omega=2,\quad\varphi=\frac{\pi}{2},\quad A=-2",
                         font_size=37, color=INK).move_to([0, 6.42, 0])

        stage = Text("共同起点：同一条正弦曲线", font=FONT,
                     font_size=30, color=INK, weight="BOLD").move_to([0, 5.58, 0])
        chart_bg = Rectangle(
            width=8.12, height=6.57, fill_color="#FFFFFF", fill_opacity=1,
            stroke_color=LINE, stroke_width=1.4,
        ).move_to([0, 1.74, 0])
        axes = Axes(
            x_range=[-3.3, 3.3, pi / 2], y_range=[-2.32, 2.32, 1],
            x_length=7.46, y_length=5.23, tips=False,
            axis_config={"color": "#AABAC9", "stroke_width": 1.5},
        ).move_to([0, 1.80, 0])

        def curve(state_value, color: str, width: float = 5.5, opacity: float = 1.0):
            return axes.plot(
                lambda x: state_value.value(x),
                x_range=[XMIN, XMAX, 0.025],
                color=color, stroke_width=width,
            ).set_stroke(opacity=opacity)

        base_curve = curve(baseline(), BLUE, 5.3, 1.0)
        x_labels = VGroup(
            MathTex(r"-\pi", font_size=25, color=MUTED).move_to(axes.c2p(-pi, -2.17)),
            MathTex("0", font_size=25, color=MUTED).move_to(axes.c2p(0, -2.17)),
            MathTex(r"\pi", font_size=25, color=MUTED).move_to(axes.c2p(pi, -2.17)),
        )
        chart_legend = Text("蓝：基准曲线     金：同一个峰点 P", font=FONT,
                            font_size=22, color=MUTED).move_to([0, 4.67, 0])

        source_point = Dot(axes.c2p(*baseline().point(TRACKED_T)),
                           radius=0.103, color=GOLD).set_stroke(BG, width=2)
        source_label = MathTex("P", font_size=28, color=GOLD)
        source_label.move_to(source_point.get_center() + [0.32, 0.27, 0])

        note = Text("P 从 t=π/2 出发，起点 (π/2, 1)", font=FONT,
                    font_size=26, color=MUTED).move_to([0, -2.07, 0])
        formula = MathTex(r"y=\sin x", font_size=42, color=INK).move_to([0, -2.91, 0])

        path_one = Text("① 先平移 π/2，再横坐标 ×1/2", font=FONT,
                        font_size=26, color=ORANGE).move_to([0, -4.02, 0])
        path_two = Text("② 先横坐标 ×1/2，再平移 π/4", font=FONT,
                        font_size=26, color=PURPLE).move_to([0, -4.69, 0])
        path_one.set_opacity(0.50)
        path_two.set_opacity(0.50)
        law = MathTex(
            r"S_2\circ L_{\pi/2}=L_{\pi/4}\circ S_2",
            font_size=35, color=INK,
        ).move_to([0, -5.83, 0])
        caution = Text("调整平移量后等价；不能直接交换", font=FONT,
                       font_size=25, color=MUTED).move_to([0, -6.65, 0])

        self.add(title, params, stage, chart_bg, axes, x_labels, chart_legend,
                 base_curve, source_point, source_label, note, formula,
                 path_one, path_two)
        self.wait(0.85)

        def labels(stage_text: str, note_text: str, formula_tex: str,
                   formula_color: str = INK, run_time: float = 0.24) -> None:
            nonlocal stage, note, formula
            new_stage = Text(stage_text, font=FONT, font_size=30,
                             color=INK, weight="BOLD").move_to(stage)
            new_note = Text(note_text, font=FONT, font_size=26,
                            color=MUTED).move_to(note)
            new_formula = MathTex(formula_tex, font_size=42,
                                  color=formula_color).move_to(formula)
            self.play(FadeOut(stage), FadeOut(note), FadeOut(formula),
                      run_time=run_time / 2)
            self.play(FadeIn(new_stage), FadeIn(new_note), FadeIn(new_formula),
                      run_time=run_time / 2)
            stage, note, formula = new_stage, new_note, new_formula

        def dynamic_path(color: str, mode: dict, progress: ValueTracker):
            dynamic_curve = always_redraw(
                lambda: curve(mode["function"](DEMO, progress.get_value()), color)
            )
            dynamic_dot = always_redraw(lambda: Dot(
                axes.c2p(*mode["function"](DEMO, progress.get_value()).point(TRACKED_T)),
                radius=0.112, color=GOLD,
            ).set_stroke(BG, width=2))
            point_label = MathTex("P", font_size=28, color=GOLD)
            point_label.move_to(dynamic_dot.get_center() + [0.32, 0.27, 0])
            point_label.add_updater(
                lambda mob: mob.move_to(dynamic_dot.get_center() + [0.32, 0.27, 0])
            )
            return dynamic_curve, dynamic_dot, point_label

        # Path one: the original peak travels π/2 left, then its x coordinate halves.
        self.remove(source_point, source_label)
        base_curve.set_stroke(opacity=0.23)
        path_one.set_opacity(1)
        p1_progress = ValueTracker(0)
        p1_mode = {"function": first_shift}
        p1_curve, p1_dot, p1_label = dynamic_path(ORANGE, p1_mode, p1_progress)
        self.add(p1_curve, p1_dot, p1_label)
        labels("路径一：先平移", "P：π/2 → 0；左移量逐渐达到 π/2",
               r"x_P=\pi/2-\delta,\quad 0\leq\delta\leq\pi/2", ORANGE)
        self.play(p1_progress.animate.set_value(1), run_time=1.55, rate_func=linear)
        self.wait(0.25)
        p1_progress.set_value(0)
        p1_mode["function"] = first_scale
        labels("路径一：再横向压缩", "P 在 y 轴上不动；整条曲线横坐标 ×1/2",
               r"x=s(t-\pi/2),\quad s:1\to1/2", ORANGE)
        self.play(p1_progress.animate.set_value(1), run_time=1.55, rate_func=linear)
        self.wait(0.35)

        # The orange trace is the exact model endpoint, kept behind path two.
        orange_result = curve(horizontal_result(DEMO), ORANGE, 8.0, 0.70)
        endpoint_xy = axes.c2p(*horizontal_result(DEMO).point(TRACKED_T))
        orange_ring = Circle(radius=0.17, color=ORANGE,
                             stroke_width=3.5).move_to(endpoint_xy)
        self.add(orange_result, orange_ring)
        self.remove(p1_curve, p1_dot, p1_label)

        # A visible reset avoids implying that path two continues from path one.
        labels("路径二：重新从 y=sin x 出发", "仍追踪同一个峰点 P=(π/2,1)",
               r"y=\sin x", BLUE)
        path_one.set_opacity(0.58)
        path_two.set_opacity(1)
        p2_progress = ValueTracker(0)
        p2_mode = {"function": second_scale}
        p2_curve, p2_dot, p2_label = dynamic_path(PURPLE, p2_mode, p2_progress)
        self.add(p2_curve, p2_dot, p2_label)
        self.wait(0.32)
        labels("路径二：先横向压缩", "P：π/2 → π/4；横坐标逐渐减半",
               r"x=s t,\quad s:1\to1/2", PURPLE)
        self.play(p2_progress.animate.set_value(1), run_time=1.55, rate_func=linear)
        self.wait(0.25)
        p2_progress.set_value(0)
        p2_mode["function"] = second_shift
        labels("路径二：再平移", "P：π/4 → 0；左移量逐渐达到 π/4",
               r"x=t/2-\delta,\quad 0\leq\delta\leq\pi/4", PURPLE)
        self.play(p2_progress.animate.set_value(1), run_time=1.55, rate_func=linear)
        self.wait(0.45)

        # Same analytic curve and same tracked point, with orange outer / purple inner.
        labels("两条路径：曲线与 P 完全重合", "π/2 先移，或 π/4 后移；终点都是 (0,1)",
               r"S_2L_{\pi/2}=L_{\pi/4}S_2", GREEN)
        self.play(FadeIn(law), FadeIn(caution), run_time=0.35)
        self.wait(1.15)

        # Apply the signed coefficient to the common horizontal result.
        self.remove(p2_curve, p2_dot, p2_label, orange_result, orange_ring)
        base_curve.set_stroke(opacity=0.10)
        v_progress = ValueTracker(0)
        v_mode = {"function": amplitude_scale}
        v_curve, v_dot, v_label = dynamic_path(GREEN, v_mode, v_progress)
        self.add(v_curve, v_dot, v_label)
        labels("共同结果：先按 |A|=2 纵向伸缩", "P：(0,1) → (0,2)；振幅最终是 2",
               r"y=c\sin(2x+\pi/2),\quad c:1\to2", GREEN)
        self.play(v_progress.animate.set_value(1), run_time=1.2, rate_func=linear)
        self.wait(0.25)
        v_progress.set_value(0)
        v_mode["function"] = reflection
        labels("再关于 x 轴翻折", "几何翻折过程；终点 A=-2，P=(0,-2)",
               r"y=c\sin(2x+\pi/2),\quad c:2\to-2", GREEN)
        self.play(v_progress.animate.set_value(1), run_time=1.4, rate_func=linear)
        self.wait(0.75)

        labels("结论：顺序改变，平移量要调整", "先移 π/2；后移 π/4；两路终点相同",
               r"y=-2\sin(2x+\pi/2)", GREEN)
        self.wait(1.20)

        # Return to the baseline composition before the GIF loops.
        self.play(FadeOut(v_curve), FadeOut(v_dot), FadeOut(v_label),
                  FadeOut(law), FadeOut(caution),
                  base_curve.animate.set_stroke(opacity=1), run_time=0.42)
        path_one.set_opacity(0.50)
        path_two.set_opacity(0.50)
        self.add(source_point, source_label)
        labels("共同起点：同一条正弦曲线", "P 从 t=π/2 出发，起点 (π/2, 1)",
               r"y=\sin x", INK, run_time=0.28)
        self.wait(0.20)
