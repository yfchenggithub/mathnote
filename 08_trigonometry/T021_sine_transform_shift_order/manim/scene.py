"""T021: two horizontal transformation orders, one tracked source peak."""

from __future__ import annotations

from math import pi

from manim import (
    Axes, Circle, Dot, FadeIn, FadeOut, MathTex, Scene, Text,
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
MUTED = "#52677A"
BLUE = "#2377C4"
ORANGE = "#C75E31"
PURPLE = "#71539E"
GREEN = "#168A69"
GOLD = "#BA810B"
FONT = "Microsoft YaHei"
XMIN, XMAX = -pi, pi


class T021TransformOrderLesson(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG

        title = Text("顺序不同，结果相同", font=FONT,
                     font_size=36, color=INK, weight="SEMIBOLD").move_to([0, 7.24, 0])
        stage = Text("共同起点 · y=sin x", font=FONT,
                     font_size=28, color=MUTED, weight="MEDIUM").move_to([0, 6.38, 0])
        axes = Axes(
            x_range=[-3.3, 3.3, pi / 2], y_range=[-2.32, 2.32, 1],
            x_length=7.78, y_length=6.25, tips=False,
            axis_config={"color": "#A9B9C8", "stroke_width": 1.4},
        ).move_to([0, 1.60, 0])

        def curve(state_value, color: str, width: float = 5.0, opacity: float = 1.0):
            return axes.plot(
                lambda x: state_value.value(x),
                x_range=[XMIN, XMAX, 0.025],
                color=color, stroke_width=width,
            ).set_stroke(opacity=opacity)

        base_curve = curve(baseline(), BLUE)
        x_labels = VGroup(
            MathTex(r"-\pi", font_size=26, color=MUTED).move_to(axes.c2p(-pi, -2.17)),
            MathTex("0", font_size=26, color=MUTED).move_to(axes.c2p(0, -2.17)),
            MathTex(r"\pi", font_size=26, color=MUTED).move_to(axes.c2p(pi, -2.17)),
        )

        source_point = Dot(axes.c2p(*baseline().point(TRACKED_T)),
                           radius=0.11, color=GOLD).set_stroke(BG, width=2)
        source_label = MathTex("P", font_size=30, color=GOLD)
        source_label.move_to(source_point.get_center() + [0.34, 0.28, 0])

        operation = Text("从同一条正弦曲线出发", font=FONT, font_size=30,
                         color=INK, weight="SEMIBOLD").move_to([0, -3.05, 0])
        formula = MathTex(r"y=\sin x", font_size=43, color=INK).move_to([0, -4.07, 0])
        detail = Text("追踪点 P=(π/2, 1)", font=FONT, font_size=25,
                      color=MUTED).move_to([0, -5.04, 0])

        self.add(title, stage, axes, x_labels, base_curve,
                 source_point, source_label, operation, formula, detail)
        self.wait(0.85)

        def labels(stage_text: str, operation_text: str, formula_tex: str,
                   detail_text: str, color: str = INK, run_time: float = 0.24) -> None:
            nonlocal stage, operation, formula, detail
            new_stage = Text(stage_text, font=FONT, font_size=28,
                             color=MUTED, weight="MEDIUM").move_to(stage)
            new_operation = Text(operation_text, font=FONT, font_size=30,
                                 color=color, weight="SEMIBOLD").move_to(operation)
            new_formula = MathTex(formula_tex, font_size=42,
                                  color=color).move_to(formula)
            new_detail = Text(detail_text, font=FONT, font_size=25,
                              color=MUTED).move_to(detail)
            self.play(FadeOut(stage), FadeOut(operation), FadeOut(formula),
                      FadeOut(detail), run_time=run_time / 2)
            self.play(FadeIn(new_stage), FadeIn(new_operation), FadeIn(new_formula),
                      FadeIn(new_detail), run_time=run_time / 2)
            stage, operation, formula, detail = (
                new_stage, new_operation, new_formula, new_detail)

        def dynamic_path(color: str, mode: dict, progress: ValueTracker):
            dynamic_curve = always_redraw(
                lambda: curve(mode["function"](DEMO, progress.get_value()), color)
            )
            dynamic_dot = always_redraw(lambda: Dot(
                axes.c2p(*mode["function"](DEMO, progress.get_value()).point(TRACKED_T)),
                radius=0.115, color=GOLD,
            ).set_stroke(BG, width=2))
            point_label = MathTex("P", font_size=30, color=GOLD)
            point_label.move_to(dynamic_dot.get_center() + [0.34, 0.28, 0])
            point_label.add_updater(
                lambda mob: mob.move_to(dynamic_dot.get_center() + [0.34, 0.28, 0])
            )
            return dynamic_curve, dynamic_dot, point_label

        # Path one: the original peak travels π/2 left, then its x coordinate halves.
        self.remove(source_point, source_label)
        base_curve.set_stroke(opacity=0.20)
        p1_progress = ValueTracker(0)
        p1_mode = {"function": first_shift}
        p1_curve, p1_dot, p1_label = dynamic_path(ORANGE, p1_mode, p1_progress)
        self.add(p1_curve, p1_dot, p1_label)
        labels("路径一 · 先平移，再横向压缩", "左移 π/2",
               r"x_P=\pi/2-\delta,\quad 0\leq\delta\leq\pi/2",
               "P 从 (π/2, 1) 移到 (0, 1)", ORANGE)
        self.play(p1_progress.animate.set_value(1), run_time=1.55, rate_func=linear)
        self.wait(0.25)
        p1_progress.set_value(0)
        p1_mode["function"] = first_scale
        labels("路径一 · 先平移，再横向压缩", "横坐标 ×1/2",
               r"x=s(t-\pi/2),\quad s:1\to1/2",
               "P 在 y 轴上不动", ORANGE)
        self.play(p1_progress.animate.set_value(1), run_time=1.55, rate_func=linear)
        self.wait(0.35)

        # The orange trace is the exact model endpoint, kept behind path two.
        orange_result = curve(horizontal_result(DEMO), ORANGE, 7.0, 0.50)
        endpoint_xy = axes.c2p(*horizontal_result(DEMO).point(TRACKED_T))
        orange_ring = Circle(radius=0.18, color=ORANGE,
                             stroke_width=3.0).move_to(endpoint_xy)
        self.add(orange_result, orange_ring)
        self.remove(p1_curve, p1_dot, p1_label)

        # A visible reset avoids implying that path two continues from path one.
        labels("路径二 · 先横向压缩，再平移", "重新从 y=sin x 出发",
               r"y=\sin x", "仍追踪同一个点 P=(π/2, 1)", BLUE)
        p2_progress = ValueTracker(0)
        p2_mode = {"function": second_scale}
        p2_curve, p2_dot, p2_label = dynamic_path(PURPLE, p2_mode, p2_progress)
        self.add(p2_curve, p2_dot, p2_label)
        self.wait(0.32)
        labels("路径二 · 先横向压缩，再平移", "横坐标 ×1/2",
               r"x=s t,\quad s:1\to1/2",
               "P 从 (π/2, 1) 移到 (π/4, 1)", PURPLE)
        self.play(p2_progress.animate.set_value(1), run_time=1.55, rate_func=linear)
        self.wait(0.25)
        p2_progress.set_value(0)
        p2_mode["function"] = second_shift
        labels("路径二 · 先横向压缩，再平移", "左移 π/4",
               r"x=t/2-\delta,\quad 0\leq\delta\leq\pi/4",
               "P 从 (π/4, 1) 移到 (0, 1)", PURPLE)
        self.play(p2_progress.animate.set_value(1), run_time=1.55, rate_func=linear)
        self.wait(0.45)

        # Same analytic curve and same tracked point, with orange outer / purple inner.
        labels("两条路径 · 最终重合", "曲线与 P 完全重合",
               r"S_2\circ L_{\pi/2}=L_{\pi/4}\circ S_2",
               "平移量随顺序调整", GREEN)
        path_one = Text("路径一  左移 π/2 → 横坐标 ×1/2", font=FONT,
                        font_size=25, color=ORANGE).move_to([0, -5.93, 0])
        path_two = Text("路径二  横坐标 ×1/2 → 左移 π/4", font=FONT,
                        font_size=25, color=PURPLE).move_to([0, -6.52, 0])
        self.play(FadeIn(path_one), FadeIn(path_two), run_time=0.35)
        self.wait(1.15)

        # Apply the signed coefficient to the common horizontal result.
        self.play(FadeOut(path_one), FadeOut(path_two), run_time=0.22)
        self.remove(p2_curve, p2_dot, p2_label, orange_result, orange_ring)
        base_curve.set_stroke(opacity=0.10)
        v_progress = ValueTracker(0)
        v_mode = {"function": amplitude_scale}
        v_curve, v_dot, v_label = dynamic_path(GREEN, v_mode, v_progress)
        self.add(v_curve, v_dot, v_label)
        labels("纵向变化 · A=-2", "纵坐标 ×2",
               r"y=c\sin(2x+\pi/2),\quad c:1\to2",
               "P：(0, 1) → (0, 2)；振幅为 2", GREEN)
        self.play(v_progress.animate.set_value(1), run_time=1.2, rate_func=linear)
        self.wait(0.25)
        v_progress.set_value(0)
        v_mode["function"] = reflection
        labels("纵向变化 · A=-2", "关于 x 轴翻折",
               r"y=c\sin(2x+\pi/2),\quad c:2\to-2",
               "P：(0, 2) → (0, -2)", GREEN)
        self.play(v_progress.animate.set_value(1), run_time=1.4, rate_func=linear)
        self.wait(0.75)

        labels("结论", "顺序改变，平移量要调整",
               r"y=-2\sin(2x+\pi/2)",
               "先移 π/2；后移 π/4；两路终点相同", GREEN)
        self.wait(1.20)

        # Return to the baseline composition before the GIF loops.
        self.play(FadeOut(v_curve), FadeOut(v_dot), FadeOut(v_label),
                  base_curve.animate.set_stroke(opacity=1), run_time=0.42)
        self.add(source_point, source_label)
        labels("共同起点 · y=sin x", "从同一条正弦曲线出发",
               r"y=\sin x", "追踪点 P=(π/2, 1)", INK, run_time=0.28)
        self.wait(0.20)
