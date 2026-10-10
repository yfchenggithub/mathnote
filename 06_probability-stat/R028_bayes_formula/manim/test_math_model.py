"""M1–M12 checks for the exact R028 screening animation."""

from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from math_model import MODEL, ScreeningModel


class ScreeningMathTests(unittest.TestCase):
    def test_m1_prior(self):
        self.assertEqual(MODEL.prevalence, Fraction(1, 1000))
        self.assertEqual(MODEL.healthy_prior, Fraction(999, 1000))

    def test_m2_conditional_direction(self):
        self.assertEqual(MODEL.sensitivity, Fraction(99, 100))
        self.assertEqual(MODEL.false_positive_rate, Fraction(1, 100))
        self.assertEqual(1 - MODEL.false_positive_rate, Fraction(99, 100))

    def test_m3_total_probability(self):
        self.assertEqual(MODEL.positive_mass, Fraction(1098, 100000))

    def test_m4_true_positive(self):
        self.assertEqual(MODEL.true_positive_mass, Fraction(99, 100000))

    def test_m5_false_positive(self):
        self.assertEqual(MODEL.false_positive_mass, Fraction(999, 100000))

    def test_m6_posterior(self):
        self.assertEqual(MODEL.posterior, Fraction(99, 1098))
        self.assertEqual(MODEL.posterior, Fraction(11, 122))

    def test_m7_normalization(self):
        self.assertEqual(MODEL.prevalence + MODEL.healthy_prior, 1)
        self.assertEqual(MODEL.true_positive_mass + MODEL.false_positive_mass,
                         MODEL.positive_mass)
        self.assertEqual(MODEL.posterior + MODEL.false_positive_mass / MODEL.positive_mass, 1)
        self.assertNotEqual(MODEL.positive_mass, 1)

    def test_m8_population_integrity(self):
        c = MODEL.exact_counts()
        self.assertEqual(c, {"all": 100000, "diseased": 100, "healthy": 99900,
                             "true_positive": 99, "false_positive": 999,
                             "all_positive": 1098})
        self.assertEqual(c["diseased"] + c["healthy"], c["all"])
        self.assertEqual(c["true_positive"] + c["false_positive"], c["all_positive"])

    def test_m9_official_example_match(self):
        source = (Path(__file__).parents[1] / "04_examples.tex").read_text(encoding="utf-8")
        for literal in ("0.1\\%", "P(A)=0.001", "P(B\\mid A)=0.99",
                        "P(B\\mid \\overline{A})=0.01", "0.01098", "0.0902"):
            self.assertIn(literal, source)

    def test_m10_boundaries(self):
        self.assertEqual(ScreeningModel(Fraction(2, 5), Fraction(1), Fraction(1)).positive_mass, 1)
        self.assertEqual(ScreeningModel(Fraction(2, 5), Fraction(1), Fraction(1)).posterior,
                         Fraction(2, 5))
        with self.assertRaises(ValueError):
            _ = ScreeningModel(Fraction(2, 5), Fraction(0), Fraction(0)).posterior
        self.assertEqual(ScreeningModel(Fraction(0), Fraction(1), Fraction(1)).posterior, 0)
        self.assertEqual(ScreeningModel(Fraction(1), Fraction(1), Fraction(0)).posterior, 1)

    def test_m11_display_rounding(self):
        self.assertEqual(f"{float(MODEL.posterior):.4f}", "0.0902")
        self.assertEqual(f"{float(MODEL.posterior) * 100:.2f}%", "9.02%")

    def test_m12_visual_state_consistency(self):
        c = MODEL.exact_counts()
        self.assertEqual(Fraction(c["true_positive"], c["all_positive"]), MODEL.posterior)
        true_width, false_width = MODEL.positive_pool_widths(7)
        self.assertAlmostEqual(true_width + false_width, 7)
        self.assertAlmostEqual(true_width / 7, float(MODEL.posterior))
        self.assertAlmostEqual(false_width / 7, 1 - float(MODEL.posterior))


if __name__ == "__main__":
    unittest.main()
