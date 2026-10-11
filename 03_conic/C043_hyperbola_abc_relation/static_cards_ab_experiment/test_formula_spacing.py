"""Regression for the standard equation capsule covering MathText numerators."""

import unittest

from build_fix import reconstructed_old_layout
from cards import card_002
from formula_spacing import FormulaSpacingError, check_standard_equation, measure_standard_equation


class FormulaSpacingTests(unittest.TestCase):
    def test_both_themes_have_full_size_equation_and_clearance(self):
        measurements = []
        for theme in ("A_blue", "B_rose"):
            canvas = card_002(theme)
            result = check_standard_equation(canvas)
            self.assertEqual(result["formula_font_pt"], 40)
            self.assertGreaterEqual(result["capsule_formula_gap_px"], 8)
            self.assertGreaterEqual(result["title_formula_gap_px"], 8)
            self.assertGreaterEqual(result["formula_bottom_panel_clearance_px"], 3)
            self.assertEqual(result["capsule_formula_bbox_overlap_px2"], 0)
            self.assertEqual(result["title_formula_bbox_overlap_px2"], 0)
            self.assertEqual(canvas.audit_text()["text_overlap"], 0)
            measurements.append(result)
        self.assertEqual(measurements[0], measurements[1])

    def test_prior_numerator_obstruction_is_rejected_for_both_themes(self):
        for theme in ("A_blue", "B_rose"):
            canvas = reconstructed_old_layout(theme)
            measured = measure_standard_equation(canvas)
            self.assertLess(measured["capsule_formula_gap_px"], 0)
            self.assertGreater(measured["capsule_formula_bbox_overlap_px2"], 0)
            # The previous text-only gate passed, showing the exact blind spot.
            self.assertEqual(canvas.audit_text()["text_overlap"], 0)
            with self.assertRaisesRegex(FormulaSpacingError,
                                        "capsule background / MathText formula"):
                check_standard_equation(canvas)


if __name__ == "__main__":
    unittest.main()
