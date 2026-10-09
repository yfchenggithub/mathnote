"""F031: the nearest interval point switches at endpoints; the farthest at midpoint."""

from __future__ import annotations

from math import sqrt

from manim import (
    Axes, DashedLine, DecimalNumber, Dot, FadeIn, FadeOut, Line, MathTex,
    Rectangle, Scene, Text, ValueTracker, VGroup, always_redraw, config, linear,
)

from math_model import QuadraticSpec, analytic_state


config.frame_width = 9
config.frame_height = 16

BG = "#F8FAFD"
INK = "#183047"
MUTED = "#65788A"
BLUE = "#2377C4"
PURPLE = "#785DA9"
GREEN = "#168A69"
ORANGE = "#DC7142"
PALE_BLUE = "#DCE9F3"
LINE = "#CDD9E4"
FONT = "Microsoft YaHei"
LEFT = -2.0
RIGHT = 2.0
AXIS_START = -2.8


def axis_label(text: str, color: str, at: list[float]) -> Text:
    return Text(text, font=FONT, font_size=24, color=color).move_to(at)


def point_name(points: tuple[float, ...], spec: QuadraticSpec) -> str:
    if len(points) == 2:
        return "L 和 R"
    x = points[0]
    if abs(x - spec.left) < 1e-10:
        return "L"
    if abs(x - spec.right) < 1e-10:
        return "R"
    return "顶点 h"


def graph_for(axes: Axes, spec: QuadraticSpec) -> VGroup:
    """Compute every visible geometric object from one exact spec."""
    top = 6.06
    # Clip curves mathematically to the chart height, not by arbitrary shape.
    if spec.a > 0:
        radius = sqrt(max(0.0, (top - spec.k) / spec.a))
    else:
        radius = sqrt(max(0.0, spec.k / -spec.a))
    low = max(-3.25, spec.h - radius)
    high = min(3.25, spec.h + radius)
    pieces = VGroup()
    for start, end, color, width, opacity in (
        (low, min(high, LEFT), BLUE, 3, 0.35),
        (max(low, LEFT), min(high, RIGHT), BLUE, 6, 1.0),
        (max(low, RIGHT), high, BLUE, 3, 0.35),
    ):
        if end - start > 0.025:
            curve = axes.plot(
                lambda x: spec.value(x), x_range=[start, end, 0.035],
                color=color, stroke_width=width,
            )
            curve.set_stroke(opacity=opacity)
            pieces.add(curve)
    line = DashedLine(
        axes.c2p(spec.h, -0.04), axes.c2p(spec.h, top),
        color=PURPLE, stroke_width=2.5, dash_length=0.13,
    )
    state = analytic_state(spec)
    vertex = Dot(axes.c2p(*state.vertex), radius=0.075, color=PURPLE)
    minimum = VGroup(*[
        Dot(axes.c2p(x, spec.value(x)), radius=0.12, color=GREEN)
        .set_stroke(BG, width=2)
        for x in state.minimum_points
    ])
    maximum = VGroup(*[
        Dot(axes.c2p(x, spec.value(x)), radius=0.12, color=ORANGE)
        .set_stroke(BG, width=2)
        for x in state.maximum_points
    ])
    return VGroup(pieces, line, vertex, minimum, maximum)


class F031MovingAxisLesson(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        h = ValueTracker(AXIS_START)
        mode = {"a": 0.25, "k": 0.0}

        def spec() -> QuadraticSpec:
            return QuadraticSpec(LEFT, RIGHT, mode["a"], h.get_value(), mode["k"])

        title = Text(
            "定区间：最值点何时换位？", font=FONT, font_size=37,
            color=INK, weight="BOLD",
        ).move_to([0, 7.26, 0])
        formula = MathTex(
            r"f_h(x)=\frac14(x-h)^2,\quad x\in[-2,2]",
            font_size=37, color=INK,
        ).move_to([0, 6.54, 0])
        fixed = Text("区间不动　·　对称轴移动", font=FONT, font_size=25,
                     color=MUTED).move_to([0, 5.92, 0])

        chart_bg = Rectangle(
            width=8.05, height=7.10, fill_color="#FFFFFF",
            fill_opacity=1, stroke_color=LINE, stroke_width=1.5,
        ).move_to([0, 1.42, 0])
        axes = Axes(
            x_range=[-3.3, 3.3, 1], y_range=[-0.65, 6.2, 1],
            x_length=7.30, y_length=6.15, tips=False,
            axis_config={"color": "#AABBCB", "stroke_width": 1.4},
        ).move_to([0, 1.50, 0])
        plot_band = Rectangle(
            width=abs(axes.c2p(RIGHT, 0)[0] - axes.c2p(LEFT, 0)[0]),
            height=abs(axes.c2p(0, 6.08)[1] - axes.c2p(0, 0)[1]),
            fill_color=PALE_BLUE, fill_opacity=0.32,
            stroke_width=0,
        ).move_to(
            (axes.c2p(LEFT, 0) + axes.c2p(RIGHT, 6.08)) / 2
        )
        boundary = VGroup(*[
            Line(axes.c2p(x, 0), axes.c2p(x, 6.08),
                 color="#B6C9D8", stroke_width=2)
            for x in (LEFT, RIGHT)
        ])
        xlabels = VGroup(
            axis_label("L=-2", INK, axes.c2p(LEFT, -0.40)),
            axis_label("m=0", PURPLE, axes.c2p(0, -0.40)),
            axis_label("R=2", INK, axes.c2p(RIGHT, -0.40)),
        )
        graph = always_redraw(lambda: graph_for(axes, spec()))

        h_symbol = MathTex(r"h=", color=PURPLE, font_size=34).move_to([-0.60, 5.39, 0])
        h_value = DecimalNumber(
            AXIS_START, num_decimal_places=2, include_sign=False,
            font_size=34, color=PURPLE,
        ).move_to([0.37, 5.39, 0])
        h_value.add_updater(lambda mob: mob.set_value(h.get_value()))
        up_tag = Text("开口向上", font=FONT, font_size=25, color=BLUE).move_to([2.55, 5.39, 0])

        legend = Text(
            "绿：最小值点     橙：最大值点     紫：对称轴",
            font=FONT, font_size=24, color=INK,
        ).move_to([0, -2.40, 0])
        min_title = Text("最小值点", font=FONT, font_size=27, color=GREEN).move_to([-2.28, -3.13, 0])
        max_title = Text("最大值点", font=FONT, font_size=27, color=ORANGE).move_to([1.45, -3.13, 0])

        def names_for(extreme: str, x: float) -> VGroup:
            names = VGroup()
            for label in ("L", "顶点 h", "R", "L 和 R"):
                txt = Text(
                    label, font=FONT, font_size=27,
                    color=GREEN if extreme == "min" else ORANGE,
                    weight="BOLD",
                ).move_to([x, -3.61, 0])

                def update(mob, expected=label, which=extreme):
                    state = analytic_state(spec())
                    pts = state.minimum_points if which == "min" else state.maximum_points
                    mob.set_opacity(1 if point_name(pts, spec()) == expected else 0)

                txt.add_updater(update)
                names.add(txt)
            return names

        min_names = names_for("min", -2.28)
        max_names = names_for("max", 1.45)
        left_distance = axis_label("到 L 的距离", INK, [-2.87, -4.37, 0])
        right_distance = axis_label("到 R 的距离", INK, [-2.87, -4.87, 0])

        def distance_bar(which: str, y: float) -> VGroup:
            state = analytic_state(spec())
            x = LEFT if which == "left" else RIGHT
            value = abs(x - spec().h)
            farthest = x in state.farthest_points
            width = max(0.025, value * 0.66)
            bar = Rectangle(
                width=width, height=0.17,
                fill_color=BLUE if farthest else "#8FADC6",
                fill_opacity=0.90, stroke_width=0,
            ).move_to([-0.98 + width / 2, y, 0])
            return VGroup(bar)

        bars = VGroup(
            always_redraw(lambda: distance_bar("left", -4.37)),
            always_redraw(lambda: distance_bar("right", -4.87)),
        )
        min_val_title = Text("最小值", font=FONT, font_size=26, color=GREEN).move_to([-2.78, -5.68, 0])
        min_val = DecimalNumber(
            analytic_state(spec()).minimum_value, num_decimal_places=2,
            font_size=30, color=GREEN,
        ).move_to([-1.35, -5.68, 0])
        min_val.add_updater(lambda mob: mob.set_value(analytic_state(spec()).minimum_value))
        max_val_title = Text("最大值", font=FONT, font_size=26, color=ORANGE).move_to([0.95, -5.68, 0])
        max_val = DecimalNumber(
            analytic_state(spec()).maximum_value, num_decimal_places=2,
            font_size=30, color=ORANGE,
        ).move_to([2.39, -5.68, 0])
        max_val.add_updater(lambda mob: mob.set_value(analytic_state(spec()).maximum_value))
        body = VGroup(
            legend, min_title, max_title, min_names, max_names,
            left_distance, right_distance, bars,
            min_val_title, max_val_title, min_val, max_val,
        )
        up_rule = Text(
            "开口向上：近轴取小，远轴取大",
            font=FONT, font_size=28, color=INK, weight="BOLD",
        ).move_to([0, -6.52, 0])

        def caption(message: str) -> Text:
            return Text(message, font=FONT, font_size=24, color=MUTED).move_to([0, -7.22, 0])

        status = caption("轴在区间外：绿点仍留在区间端点")
        self.add(
            title, formula, fixed, chart_bg, plot_band, axes, boundary, xlabels,
            graph, h_symbol, h_value, up_tag, body, up_rule, status,
        )
        self.wait(0.65)

        self.play(h.animate.set_value(LEFT), run_time=1.45, rate_func=linear)
        next_status = caption("h=L：顶点刚进入区间")
        self.play(FadeOut(status), FadeIn(next_status), run_time=0.2)
        status = next_status
        self.wait(0.45)

        self.play(h.animate.set_value(0), run_time=2.35, rate_func=linear)
        tie = MathTex(r"f(L)=f(R)", color=ORANGE, font_size=34).move_to([0, -6.52, 0])
        next_status = caption("h=m：两端点同时取得最大值")
        self.play(FadeOut(up_rule), FadeIn(tie),
                  FadeOut(status), FadeIn(next_status), run_time=0.22)
        status = next_status
        self.wait(0.85)

        next_status = caption("越过中点：最大值点直接换到左端")
        self.play(FadeOut(tie), FadeIn(up_rule),
                  FadeOut(status), FadeIn(next_status), run_time=0.22)
        status = next_status
        self.play(h.animate.set_value(RIGHT), run_time=2.35, rate_func=linear)
        next_status = caption("h=R：顶点即将离开区间")
        self.play(FadeOut(status), FadeIn(next_status), run_time=0.2)
        status = next_status
        self.wait(0.45)
        self.play(h.animate.set_value(2.8), run_time=1.25, rate_func=linear)
        self.wait(0.35)

        self.play(h.animate.set_value(0), run_time=1.25, rate_func=linear)
        self.play(FadeOut(formula), FadeOut(up_tag),
                  FadeOut(up_rule), FadeOut(status), run_time=0.35)
        self.remove(graph, body)
        mode["a"], mode["k"] = -0.25, 3.0
        down_formula = MathTex(
            r"g_h(x)=3-\frac14(x-h)^2,\quad x\in[-2,2]",
            font_size=37, color=INK,
        ).move_to([0, 6.54, 0])
        down_tag = Text("开口向下", font=FONT, font_size=25, color=BLUE).move_to([2.55, 5.39, 0])
        down_rule = Text(
            "开口向下：近轴取大，远轴取小",
            font=FONT, font_size=28, color=INK, weight="BOLD",
        ).move_to([0, -6.52, 0])
        down_status = caption("同一轴位置：绿、橙角色交换")
        self.add(graph, body)
        self.play(FadeIn(down_formula), FadeIn(down_tag),
                  FadeIn(down_rule), FadeIn(down_status), run_time=0.55)
        self.wait(1.25)

        self.play(FadeOut(down_formula), FadeOut(down_tag),
                  FadeOut(down_rule), FadeOut(down_status), run_time=0.35)
        self.remove(graph, body)
        mode["a"], mode["k"] = 0.25, 0.0
        h.set_value(AXIS_START)
        self.add(graph, body)
        self.play(FadeIn(formula), FadeIn(up_tag),
                  FadeIn(up_rule), FadeIn(caption("轴在区间外：绿点仍留在区间端点")),
                  run_time=0.55)
        self.wait(0.3)
