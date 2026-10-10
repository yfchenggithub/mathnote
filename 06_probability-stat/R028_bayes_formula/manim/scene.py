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


def display_labels(model):
    """Format labels from the one frozen mathematical model."""
    c = model.exact_counts()
    return {
        "prior_tex": rf"P(D)={float(model.prevalence) * 100:.1f}\%",
        "formula_tex": (rf"P(D\mid +)=\frac{{P(D\cap +)}}{{P(+)}}"
                        rf"=\frac{{{c['true_positive']}}}{{{c['all_positive']}}}"),
        "all": f"假设 {c['all']:,} 人",
        "d_group": f"患病组 · 共 {c['diseased']:,} 人",
        "h_group": f"未患病组 · 共 {c['healthy']:,} 人",
        "d_ratio": f"{c['true_positive']} / {c['diseased']} = {float(model.sensitivity) * 100:.0f}%",
        "h_ratio": f"{c['false_positive']} / {c['healthy']:,} = {float(model.false_positive_rate) * 100:.0f}%",
        "true_positive": f"真阳性  {c['true_positive']} 人",
        "false_positive": f"假阳性  {c['false_positive']} 人",
        "sum": f"{c['true_positive']} + {c['false_positive']} = {c['all_positive']:,} 人",
        "pool": f"阳性新总体  {c['all_positive']:,} 人",
        "pool_note": f"新比例：以 {c['all_positive']:,} 名阳性者为整体",
        "numerator": f"分子：{c['true_positive']} 名患病且阳性",
        "denominator": f"分母：全部 {c['all_positive']:,} 名阳性者",
        "result": f"≈ {float(model.posterior) * 100:.2f}%",
    }


def numerator_pointer(pool_left, pool_true):
    """Mark the numerator from outside the proportional data rectangle."""
    x = pool_left + pool_true / 2
    return Arrow([x, 0.83, 0], [x, 0.22, 0],
                 buff=0, color=ORANGE, stroke_width=4)


class R028BayesScreening(Scene):
    """Exact count badges feed a positive-only pool with a new denominator."""

    def construct(self):
        self.camera.background_color = BG
        words = display_labels(MODEL)
        source_width = 6.8
        left = -source_width / 2
        pool_width = 7.0
        pool_left = -pool_width / 2
        pool_true, pool_false = MODEL.positive_pool_widths(pool_width)

        title = label("阳性后，患病概率是多少？", 35, INK, BOLD).move_to([0, 6.9, 0])
        subtitle = label("先看所有人", 29, MUTED).move_to([0, 5.95, 0])
        self.add(title, subtitle)
        self.wait(0.4)

        total = label(words["all"], 53, INK, BOLD).move_to([0, 1.0, 0])
        prior = MathTex(words["prior_tex"], color=ORANGE, font_size=49).move_to([0, -0.1, 0])
        self.play(FadeIn(total, scale=0.94), FadeIn(prior), run_time=0.9)
        self.wait(0.7)

        diseased_name = label(words["d_group"], 33, ORANGE, BOLD).move_to([-1.0, 3.4, 0])
        healthy_name = label(words["h_group"], 33, PURPLE, BOLD).move_to([-0.7, 0.55, 0])
        diseased_track = segment(left, 2.55, source_width, TRACK)
        healthy_track = segment(left, -0.3, source_width, TRACK)
        symbolic = label("两条均表示各自组内的 100%", 26, MUTED).move_to([0, -1.35, 0])
        self.play(FadeOut(total), FadeOut(prior),
                  FadeIn(diseased_name), FadeIn(healthy_name),
                  FadeIn(diseased_track), FadeIn(healthy_track),
                  FadeIn(symbolic), run_time=1.15)
        self.wait(0.65)

        operation = label("每组内部，分别筛出阳性", 30, INK).move_to([0, 4.65, 0])
        self.play(Transform(subtitle, operation), run_time=0.45)
        d_positive = segment(left, 2.55, source_width * float(MODEL.sensitivity), ORANGE)
        d_rate = label(words["d_ratio"], 31, ORANGE).move_to([-0.9, 1.65, 0])
        d_badge = label(words["true_positive"], 30, ORANGE, BOLD).move_to([1.7, 1.02, 0])
        self.play(GrowFromEdge(d_positive, LEFT), FadeIn(d_rate), run_time=1.1)
        self.play(FadeIn(d_badge, shift=UP * 0.12), run_time=0.4)
        self.wait(0.65)

        h_positive = segment(left, -0.3, source_width * float(MODEL.false_positive_rate), PURPLE)
        h_rate = label(words["h_ratio"], 31, PURPLE).move_to([-0.8, -1.95, 0])
        pointer = Line([left + 0.035, -0.55, 0], [-2.95, -1.1, 0],
                       color=PURPLE, stroke_width=3)
        h_badge = label(words["false_positive"], 30, PURPLE, BOLD).move_to([1.55, -2.68, 0])
        self.play(GrowFromEdge(h_positive, LEFT), Create(pointer), FadeIn(h_rate), run_time=1.15)
        self.play(FadeIn(h_badge, shift=UP * 0.12), run_time=0.4)
        self.wait(0.7)

        new_subtitle = label("现在只研究阳性者", 31, INK, BOLD).move_to([0, 5.95, 0])
        self.play(Transform(subtitle, new_subtitle), run_time=0.5)
        short_d = label("患病组", 31, ORANGE, BOLD).move_to([-2.45, 3.4, 0])
        short_h = label("未患病组", 31, PURPLE, BOLD).move_to([-2.35, 0.55, 0])
        self.play(Transform(diseased_name, short_d),
                  Transform(healthy_name, short_h),
                  FadeOut(VGroup(d_rate, h_rate, symbolic, pointer)),
                  run_time=0.45)
        # Count labels keep their identity; the two source bars have different
        # denominators and are never moved or joined as area objects.
        d_start, h_start = d_badge.get_center(), h_badge.get_center()
        d_path = CubicBezier(d_start, d_start + [0.3, 0.8, 0],
                             [-2.4, 2.0, 0], [-1.55, 1.25, 0])
        h_path = CubicBezier(h_start, h_start + [0.8, 0.8, 0],
                             [2.4, 0.2, 0], [1.55, 1.25, 0])
        self.play(MoveAlongPath(d_badge, d_path),
                  MoveAlongPath(h_badge, h_path), run_time=1.35)
        sum_label = label(words["sum"], 40, INK, BOLD).move_to([0, -3.7, 0])
        self.play(FadeIn(sum_label, shift=UP * 0.15), run_time=0.45)
        self.wait(0.75)

        pool_title = label(words["pool"], 36, INK, BOLD).move_to([0, 3.25, 0])
        pool_true_bar = segment(pool_left, -0.25, pool_true, ORANGE, 0.78)
        pool_false_bar = segment(pool_left + pool_true, -0.25, pool_false, PURPLE, 0.78)
        scale_note = label(words["pool_note"], 25, MUTED).move_to([0, -1.22, 0])
        self.play(
            FadeOut(VGroup(diseased_name, healthy_name, diseased_track,
                           healthy_track, d_positive, h_positive)),
            FadeIn(pool_title), FadeIn(scale_note), run_time=0.7,
        )
        self.play(GrowFromEdge(pool_true_bar, LEFT), GrowFromEdge(pool_false_bar, LEFT),
                  FadeOut(sum_label),
                  run_time=1.25)
        self.wait(0.75)

        numerator = label(words["numerator"], 30, ORANGE, BOLD).move_to([0, -2.25, 0])
        denominator = label(words["denominator"], 30, INK).move_to([0, -3.0, 0])
        # A pointer outside the data bar cannot widen its visible orange mass.
        focus = numerator_pointer(pool_left, pool_true)
        self.play(Create(focus), FadeIn(numerator), run_time=0.8)
        self.wait(0.45)
        self.play(FadeIn(denominator), run_time=0.5)
        self.wait(0.55)

        formula = MathTex(words["formula_tex"], color=INK, font_size=49)
        formula.move_to([0, -4.3, 0])
        result = label(words["result"], 55, GREEN, BOLD).move_to([0, -5.38, 0])
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
