"""A1–A8 regressions for the R028 positive-population polish."""

from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from math_model import MODEL
from scene import ORANGE, PURPLE, display_labels, numerator_pointer, segment


class PositivePopulationPolishTests(unittest.TestCase):
    def setUp(self):
        self.c = MODEL.exact_counts()

    def test_a1_positive_population_conservation(self):
        self.assertEqual(self.c["true_positive"] + self.c["false_positive"],
                         self.c["all_positive"])
        self.assertEqual((self.c["true_positive"], self.c["false_positive"]),
                         (99, 999))

    def test_a2_original_conditional_ratios(self):
        self.assertEqual(Fraction(self.c["true_positive"], self.c["diseased"]),
                         MODEL.sensitivity)
        self.assertEqual(Fraction(self.c["false_positive"], self.c["healthy"]),
                         MODEL.false_positive_rate)

    def test_a3_posterior_ratio(self):
        self.assertEqual(Fraction(self.c["true_positive"], self.c["all_positive"]),
                         MODEL.posterior)
        self.assertAlmostEqual(float(MODEL.posterior), 0.0901639344, places=9)

    def test_a4_actual_segment_geometry(self):
        width = 7.0
        tp, fp = MODEL.positive_pool_widths(width)
        true_bar = segment(-width / 2, -0.25, tp, ORANGE, 0.78)
        false_bar = segment(-width / 2 + tp, -0.25, fp, PURPLE, 0.78)
        self.assertAlmostEqual(true_bar.width / width, float(Fraction(99, 1098)), places=12)
        self.assertAlmostEqual(false_bar.width / width, float(Fraction(999, 1098)), places=12)

    def test_a5_full_bar_conservation(self):
        for width in (1.0, 7.0, 100.0):
            tp, fp = MODEL.positive_pool_widths(width)
            self.assertAlmostEqual(tp + fp, width, places=12)

    def test_a6_common_denominator_transition(self):
        self.assertEqual(Fraction(self.c["true_positive"], self.c["diseased"]),
                         Fraction(99, 100))
        self.assertEqual(Fraction(self.c["false_positive"], self.c["healthy"]),
                         Fraction(1, 100))
        self.assertEqual(Fraction(self.c["true_positive"], self.c["all_positive"])
                         + Fraction(self.c["false_positive"], self.c["all_positive"]), 1)
        self.assertNotEqual(Fraction(99, 100), Fraction(99, 1098))

    def test_a7_display_labels_from_model(self):
        labels = display_labels(MODEL)
        self.assertEqual(labels["prior_tex"], r"P(D)=0.1\%")
        self.assertEqual(labels["formula_tex"],
                         r"P(D\mid +)=\frac{P(D\cap +)}{P(+)}=\frac{99}{1098}")
        self.assertEqual(labels["d_group"], "患病组 · 共 100 人")
        self.assertEqual(labels["h_group"], "未患病组 · 共 99,900 人")
        self.assertEqual(labels["d_ratio"], "99 / 100 = 99%")
        self.assertEqual(labels["h_ratio"], "999 / 99,900 = 1%")
        self.assertEqual(labels["sum"], "99 + 999 = 1,098 人")
        self.assertEqual(labels["pool"], "阳性新总体  1,098 人")
        self.assertEqual(labels["result"], "≈ 9.02%")

    def test_a8_visual_state_integrity(self):
        labels = display_labels(MODEL)
        self.assertIn(str(self.c["true_positive"]), labels["true_positive"])
        self.assertIn(str(self.c["false_positive"]), labels["false_positive"])
        self.assertIn(str(self.c["all_positive"]), labels["sum"].replace(",", ""))
        width = 7.0
        tp, _ = MODEL.positive_pool_widths(width)
        true_bar = segment(-width / 2, -0.25, tp, ORANGE, 0.78)
        pointer = numerator_pointer(-width / 2, tp)
        self.assertGreater(pointer.get_bottom()[1], true_bar.get_top()[1])


if __name__ == "__main__":
    unittest.main()
