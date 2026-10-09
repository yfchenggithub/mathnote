"""Independent checks for V2 mathematical copy and drawing geometry."""

import json
from pathlib import Path
import unittest

from scripts.static_cards.v2.build import ROOT, load_file, source_data


SOURCE = ROOT / "03_conic" / "C043_hyperbola_abc_relation"


class C043V2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = load_file("_c043_v2_test_cards", SOURCE / "static_cards_v2" / "cards.py")
        cls.model = load_file("_c043_v2_test_model", SOURCE / "static_cards" / "model.py")

    def test_source_agreement_and_example(self):
        _, texts = source_data(SOURCE)
        self.assertTrue(all(v == "PASS" for v in self.cards.validate_content(texts).values()))
        self.assertEqual(self.model.Hyperbola(4, 3).c_squared, 25)
        self.assertEqual(self.model.Hyperbola(4, 3).foci, ((-5, 0), (5, 0)))
        self.assertEqual(self.model.Hyperbola(4, 3).asymptote_y(4), 3)

    def test_auxiliary_corner_and_focus_are_distinct(self):
        m = self.model.Hyperbola(3, 4)
        self.assertEqual(m.c_squared, 25)
        self.assertEqual(m.equation_value((3, 4)), 0)
        self.assertNotEqual((3, 4), (m.c, 0))
        self.assertEqual(m.asymptote_y(3), 4)
        canvas = self.cards.draw_card("002", self.model.Hyperbola)
        labels = {x["label"] for x in canvas.layout_report if x["status"] == "PASS"}
        self.assertEqual(labels, self.cards.LABEL_GATE_REQUIRED["002"])
        self.assertTrue(all(x["actual_clearance_px"] >= x["minimum_required_px"]
                            for x in canvas.layout_report))
        entries = canvas.label_layout.finalize()
        self.assertEqual(len([x for x in entries if x["zone"] == "plot"]), 8)
        self.assertTrue(all(x["registered"] and not x["collisions"]
                            for x in entries if x["zone"] == "plot"))
        self.assertEqual(canvas.text_collision_audit()["text_overlap"], 0)
        canvas.fig.clear()

    def test_all_card_copy_retains_required_conditions(self):
        expected = {
            "001": ("$c^2=a^2+b^2$", "a > 0，b > 0，c > 0", "不是双曲线在 y 轴上的截距"),
            "002": ("$\\frac{x^2}{a^2}-\\frac{y^2}{b^2}=1$", "$OB=OF_2=c$", "也不是焦点"),
            "003": ("$9x^2-16y^2=144$", "$a=4,\\quad b=3,\\quad c=\\sqrt{16+9}=5$",
                    "$y=\\pm\\frac{3}{4}x$"),
        }
        for number, tokens in expected.items():
            with self.subTest(card=number):
                canvas = self.cards.draw_card(number, self.model.Hyperbola)
                copy = "\n".join(text.get_text() for text in canvas.ax.texts)
                self.assertTrue(all(token in copy for token in tokens))
                self.assertEqual(canvas.text_collision_audit()["text_overlap"], 0)
                canvas.fig.clear()


if __name__ == "__main__":
    unittest.main()
