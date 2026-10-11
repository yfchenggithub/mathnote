"""C043 Rose Premium content, diagram and formula-region regression tests."""

import hashlib
import unittest
from fractions import Fraction
from pathlib import Path

import matplotlib.pyplot as plt

from cards import card_001, card_003, validate_visible_content
from quality import FormulaRegionError, check_formula_regions
from static_cards_ab_experiment.cards import card_002, mathematical_checks
from static_cards_ab_experiment.formula_spacing import check_standard_equation
from scripts.static_cards.style_a import P
from model import Hyperbola


ROOT = Path(__file__).resolve().parents[3]
SELECTED = ROOT / ".build/static_cards_ab_experiment_fix/C043/B_rose"
DEST = ROOT / ".build/static_cards_rose_premium/C043"


class RoseThreeCardTests(unittest.TestCase):
    def test_001_recall_facts_and_triangle(self):
        canvas = card_001()
        try:
            self.assertEqual(validate_visible_content("001", canvas), "PASS")
            self.assertEqual(len(check_formula_regions(canvas)), 2)
            model = Hyperbola(3, 4)
            self.assertEqual(model.c_squared, 25)
            self.assertEqual(model.equation_value((3, 4)), 0)
            self.assertNotEqual((3, 4), model.foci[1])
            self.assertEqual({x["label"]: x["object"] for x in canvas.layout_report},
                             {"O": "point O", "A": "point A", "B": "point B",
                              "a": "OA", "b": "AB", "c": "OB"})
            plot = [x for x in canvas.label_layout.finalize() if x["zone"] == "plot"]
            self.assertEqual(sum(x["registered"] for x in plot), 6)
            self.assertTrue(all(not x["collisions"] for x in plot))
            colors = {getattr(x, "_mathnote_name", None): x.get_color()
                      for x in canvas.ax.lines}
            self.assertEqual([colors[k] for k in ("OA", "AB", "OB")],
                             [P.blue, P.teal, P.amber])
            self.assertEqual(canvas.audit_text()["text_overlap"], 0)
        finally:
            plt.close(canvas.fig)

    def test_003_exact_example_and_formula_regions(self):
        canvas = card_003()
        try:
            self.assertEqual(validate_visible_content("003", canvas), "PASS")
            self.assertEqual(len(check_formula_regions(canvas)), 4)
            self.assertEqual(Fraction(9, 144), Fraction(1, 16))
            self.assertEqual(Fraction(16, 144), Fraction(1, 9))
            model = Hyperbola(4, 3)
            self.assertEqual((model.a, model.b, model.c), (4, 3, 5))
            self.assertEqual(model.foci, ((-5, 0), (5, 0)))
            self.assertEqual(model.asymptote_y(4), 3)
            self.assertEqual(model.asymptote_y(-4), -3)
            self.assertEqual(canvas.audit_text()["text_overlap"], 0)
        finally:
            plt.close(canvas.fig)

    def test_new_capsule_formula_collisions_fail(self):
        for make, region_index in ((card_001, 1), (card_003, 1)):
            canvas = make()
            try:
                region = canvas.formula_regions[region_index]
                region["capsule"].set_y(region["capsule"].get_y()+20)
                region["title"].set_y(region["title"].get_position()[1]+20)
                with self.assertRaisesRegex(FormulaRegionError,
                                            "capsule background / formula"):
                    check_formula_regions(canvas)
            finally:
                plt.close(canvas.fig)

    def test_selected_002_model_spacing_and_byte_identity(self):
        self.assertEqual(len(mathematical_checks()), 11)
        canvas = card_002("B_rose")
        try:
            self.assertGreaterEqual(check_standard_equation(canvas)["capsule_formula_gap_px"], 8)
            plot = [x for x in canvas.label_layout.finalize() if x["zone"] == "plot"]
            self.assertEqual(sum(x["registered"] for x in plot), 7)
        finally:
            plt.close(canvas.fig)
        for filename in ("002.png", "002.svg", "002_mobile_360.png",
                         "002_mobile_390.png"):
            self.assertEqual(hashlib.sha256((SELECTED/filename).read_bytes()).hexdigest(),
                             hashlib.sha256((DEST/filename).read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
