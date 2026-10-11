"""Mathematics, visible copy and mobile type gates for C043 polish previews."""

import unittest

from cards import (card_001, card_002, card_003, mathematical_checks,
                   validate_visible_copy)


class PolishTests(unittest.TestCase):
    def test_formal_and_model_facts(self):
        self.assertEqual(len(mathematical_checks()), 11)

    def test_recall_geometry_and_copy(self):
        card = card_001()
        self.assertEqual(validate_visible_copy("001", card), "PASS")
        plot = [item for item in card.label_layout.finalize() if item["zone"] == "plot"]
        self.assertEqual(sum(item["registered"] for item in plot), 6)
        self.assertTrue(all(not item["collisions"] for item in plot))
        self.assertEqual(card.audit_text()["text_overlap"], 0)

    def test_explanation_geometry_and_copy(self):
        card = card_002()
        self.assertEqual(validate_visible_copy("002", card), "PASS")
        plot = [item for item in card.label_layout.finalize() if item["zone"] == "plot"]
        self.assertEqual(sum(item["registered"] for item in plot), 7)
        self.assertTrue(all(not item["collisions"] for item in plot))
        self.assertEqual(card.audit_text()["text_overlap"], 0)

    def test_worked_example_steps_and_results(self):
        card = card_003()
        self.assertEqual(validate_visible_copy("003", card), "PASS")
        self.assertEqual(card.audit_text()["text_overlap"], 0)

    def test_mobile_type_floor_for_essential_content(self):
        for card in (card_001(), card_002(), card_003()):
            essential = [artist for artist in card.ax.texts if
                         artist.get_text().startswith("$\\frac{x^2}") or
                         artist.get_text().startswith("$c^2=") or
                         artist.get_text().startswith("一眼")]
            self.assertTrue(essential)
            self.assertGreaterEqual(min(item.get_fontsize() for item in essential), 31)


if __name__ == "__main__":
    unittest.main()
