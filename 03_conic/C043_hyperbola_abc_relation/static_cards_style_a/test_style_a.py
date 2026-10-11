"""Content and geometry assertions specific to the selected C043 Style A set."""

import unittest

from cards import (card_001, card_003, validate_card_copy, validate_formal_sources,
                   validate_selected_copy)
from style_lab import style_a


class StyleATests(unittest.TestCase):
    def test_formal_facts_for_three_card_scope(self):
        self.assertEqual(set(validate_formal_sources().values()), {"PASS"})

    def test_recall_triangle_and_copy(self):
        canvas = card_001()
        self.assertEqual(validate_card_copy("001", canvas), "PASS")
        coverage = canvas.label_layout.finalize()
        plot = [entry for entry in coverage if entry["zone"] == "plot"]
        self.assertEqual(len(plot), 6)
        self.assertTrue(all(item["registered"] and not item["collisions"] for item in plot))
        self.assertEqual(canvas.audit_text()["text_overlap"], 0)

    def test_worked_example_displayed_steps(self):
        canvas = card_003()
        self.assertEqual(validate_card_copy("003", canvas), "PASS")
        self.assertEqual(canvas.audit_text()["text_overlap"], 0)

    def test_selected_explanation_displayed_facts(self):
        canvas = style_a()
        self.assertEqual(validate_selected_copy(canvas), "PASS")
        self.assertEqual(canvas.audit_text()["text_overlap"], 0)


if __name__ == "__main__":
    unittest.main()
