"""R028: recondition the population after a positive medical test."""

from manim import *

from math_model import MODEL


# Match scene coordinates to the 576×1024 portrait output chosen by Task 13F.
config.frame_width = 9
config.frame_height = 16


BG = "#F7F8FA"
INK = "#213044"
MUTED = "#526275"
TRACK = "#DFE5EA"
ORANGE = "#CD6031"  # disease and positive
PURPLE = "#8055B2"  # healthy and positive
GREEN = "#158068"
FONT = "Microsoft YaHei"


def label(words, size=31, color=INK, weight=NORMAL):
    return Text(words, font=FONT, font_size=size, color=color, weight=weight)


def segment(left, y, width, color, height=0.42):
    return Rectangle(width=width, height=height, stroke_width=0,
                     fill_color=color, fill_opacity=1).move_to(
        [left + width / 2, y, 0])


class R028BayesScreening(Scene):
    """Exact count badges feed a positive-only pool with a new denominator."""

    def construct(self):
        self.camera.background_color = BG
        counts = MODEL.exact_counts()
        source_width = 6.8
        left = -source_width / 2
        pool_width = 7.0
        pool_left = -pool_width / 2
        pool_true, pool_false = MODEL.positive_pool_widths(pool_width)

        title = label("阳性后，患病概率是多少？", 35, INK, BOLD).move_to([0, 6.9, 0])
        subtitle = label("先看所有人", 29, MUTED).move_to([0, 5.95, 0])
        self.add(title, subtitle)
        self.wait(0.4)

        total = label(f"假设 {counts['all']:,} 人", 53, INK, BOLD).move_to([0, 1.0, 0])
        prior = MathTex(r"P(D)=0.1\%", color=ORANGE, font_size=49).move_to([0, -0.1, 0])
        self.play(FadeIn(total, scale=0.94), FadeIn(prior), run_time=0.9)
        self.wait(0.7)

        diseased_name = label(f"患病  {counts['diseased']:,} 人", 35, ORANGE, BOLD).move_to([-1.65, 3.4, 0])
        healthy_name = label(f"未患病  {counts['healthy']:,} 人", 35, PURPLE, BOLD).move_to([-1.55, 0.55, 0])
        diseased_track = segment(left, 2.55, source_width, TRACK)
        healthy_track = segment(left, -0.3, source_width, TRACK)
        symbolic = label("分组容器等宽；人数以标签为准", 24, MUTED).move_to([0, -1.35, 0])
        self.play(FadeOut(total), FadeOut(prior),
                  FadeIn(diseased_name), FadeIn(healthy_name),
                  FadeIn(diseased_track), FadeIn(healthy_track),
                  FadeIn(symbolic), run_time=1.15)
        self.wait(0.65)

        operation = label("每组内部，分别筛出阳性", 30, INK).move_to([0, 4.65, 0])
        self.play(Transform(subtitle, operation), run_time=0.45)
        d_positive = segment(left, 2.55, source_width * float(MODEL.sensitivity), ORANGE)
        d_rate = MathTex(r"P(+\mid D)=99\%", color=ORANGE, font_size=43).move_to([-0.9, 1.65, 0])
        d_badge = label(f"真阳性  {counts['true_positive']} 人", 30, ORANGE, BOLD).move_to([1.7, 1.02, 0])
        self.play(GrowFromEdge(d_positive, LEFT), FadeIn(d_rate), run_time=1.1)
        self.play(FadeIn(d_badge, shift=UP * 0.12), run_time=0.4)
        self.wait(0.65)

        h_positive = segment(left, -0.3, source_width * float(MODEL.false_positive_rate), PURPLE)
        h_rate = MathTex(r"P(+\mid \overline D)=1\%", color=PURPLE, font_size=43).move_to([-0.8, -1.95, 0])
        pointer = Line([left + 0.035, -0.55, 0], [-2.95, -1.1, 0],
                       color=PURPLE, stroke_width=3)
        h_badge = label(f"假阳性  {counts['false_positive']} 人", 30, PURPLE, BOLD).move_to([1.55, -2.68, 0])
        self.play(GrowFromEdge(h_positive, LEFT), Create(pointer), FadeIn(h_rate), run_time=1.15)
        self.play(FadeIn(h_badge, shift=UP * 0.12), run_time=0.4)
        self.wait(0.7)

        new_subtitle = label("现在只研究阳性者", 31, INK, BOLD).move_to([0, 5.95, 0])
        self.play(Transform(subtitle, new_subtitle), run_time=0.5)
        # The moving objects are count badges, not area-scaled people icons.
        self.play(
            FadeOut(VGroup(diseased_name, healthy_name, diseased_track,
                           healthy_track, d_positive, h_positive, d_rate,
                           h_rate, pointer, symbolic)),
            d_badge.animate.move_to([-1.55, 1.25, 0]),
            h_badge.animate.move_to([1.55, 1.25, 0]),
            run_time=1.25,
        )
        self.wait(0.35)

        pool_title = label(f"阳性新总体  {counts['all_positive']:,} 人", 36, INK, BOLD).move_to([0, 3.25, 0])
        pool_true_bar = segment(pool_left, -0.25, pool_true, ORANGE, 0.78)
        pool_false_bar = segment(pool_left + pool_true, -0.25, pool_false, PURPLE, 0.78)
        scale_note = label("新比例：以 1,098 名阳性者为整体", 25, MUTED).move_to([0, -1.22, 0])
        self.play(FadeIn(pool_title), FadeIn(scale_note), run_time=0.55)
        self.play(GrowFromEdge(pool_true_bar, LEFT), GrowFromEdge(pool_false_bar, LEFT),
                  run_time=1.25)
        self.wait(0.9)

        numerator = label("分子：99 名患病且阳性", 30, ORANGE, BOLD).move_to([0, -2.25, 0])
        denominator = label("分母：全部 1,098 名阳性者", 30, INK).move_to([0, -3.0, 0])
        focus = SurroundingRectangle(pool_true_bar, color=ORANGE, buff=0.01, stroke_width=4)
        self.play(Create(focus), FadeIn(numerator), run_time=0.8)
        self.wait(0.45)
        self.play(FadeIn(denominator), run_time=0.5)
        self.wait(0.55)

        formula = MathTex(r"P(D\mid +)=\frac{P(D\cap +)}{P(+)}"
                          r"=\frac{99}{1098}", color=INK, font_size=49)
        formula.move_to([0, -4.3, 0])
        result = label("≈ 9.02%", 55, GREEN, BOLD).move_to([0, -5.38, 0])
        ending = label("已知阳性，就在阳性人群中重新计算", 28, MUTED).move_to([0, -6.62, 0])
        self.play(FadeIn(formula, shift=UP * 0.12), run_time=0.75)
        self.play(FadeIn(result, scale=0.95), FadeIn(ending), run_time=0.7)
        self.wait(1.9)
        reset_subtitle = label("先看所有人", 29, MUTED).move_to([0, 5.95, 0])
        self.play(
            FadeOut(VGroup(d_badge, h_badge, pool_title, pool_true_bar,
                           pool_false_bar, scale_note, numerator, denominator,
                           focus, formula, result, ending)),
            Transform(subtitle, reset_subtitle),
            run_time=0.7,
        )
        self.wait(0.35)
