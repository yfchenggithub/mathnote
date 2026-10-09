"""Exact geometry checks independent of rendered pixels."""

from fractions import Fraction
from pathlib import Path
import unittest

from model import Parabola, validation_results
from scripts.static_cards.build import load_source, ROOT
from scripts.static_cards.canvas import BLUE
from scripts.static_cards.canvas import GOLD
from matplotlib.transforms import Bbox


class ParabolaTests(unittest.TestCase):
    def test_all_cases(self):
        self.assertTrue(all(v == "PASS" for v in validation_results().values()))

    def test_example_and_symmetry(self):
        model = Parabola(Fraction(2))
        upper = model.check_geometry((Fraction(4), Fraction(4)))
        lower = model.check_geometry((Fraction(4), Fraction(-4)))
        self.assertEqual((upper["PF"], lower["PF"]), (5, 5))
        self.assertEqual(upper["H"], (Fraction(-1), Fraction(4)))

    def test_focus_directrix_and_vertex(self):
        model = Parabola(Fraction(2))
        self.assertEqual(model.focus, (Fraction(1), Fraction(0)))
        self.assertEqual(model.directrix_x, Fraction(-1))
        self.assertEqual(model.point(0), (Fraction(0), Fraction(0)))
        self.assertEqual(model.check_geometry(model.point(0))["PF"], Fraction(1))

    def test_perpendicular_foot_and_distances(self):
        model = Parabola(Fraction(2))
        result = model.check_geometry((Fraction(4), Fraction(4)))
        self.assertEqual(result["H"][0], model.directrix_x)
        self.assertEqual(result["H"][1], result["P"][1])
        self.assertEqual(result["PH"], result["PF"])
        self.assertEqual(result["PF"], result["P"][0] + model.p / 2)

    def test_formal_example_one(self):
        model = Parabola(Fraction(2))
        x0 = Fraction(3)
        self.assertEqual(2 * model.p, 4)
        self.assertEqual(2 * model.p * x0, 12)  # y²=12 has real curve points.
        self.assertEqual(x0 + model.p / 2, 4)

    def test_reject_invalid_inputs(self):
        with self.assertRaises(ValueError):
            Parabola(Fraction(-1))
        with self.assertRaises(ValueError):
            Parabola(Fraction(2)).check_geometry((Fraction(4), Fraction(3)))

    def test_drawn_curve_continues_beyond_p(self):
        source = ROOT / "03_conic" / "C051_parabola_focal_radius_coordinate"
        cards, _ = load_source(source, "C051")
        points = cards.curve_points()
        self.assertEqual(points[400], cards.POINT)
        self.assertGreater(points[-1][1], cards.POINT[1])
        self.assertTrue(all(y * y == 2 * cards.MODEL.p * x for x, y in points))

    def test_diagram_label_clearances(self):
        source = ROOT / "03_conic" / "C051_parabola_focal_radius_coordinate"
        cards, _ = load_source(source, "C051")
        for number in ("001", "002"):
            with self.subTest(card=number):
                canvas = cards.draw_card(number)
                canvas.fig.canvas.draw()
                renderer = canvas.fig.canvas.get_renderer()
                directrix = next(line for line in canvas.ax.lines if line.get_linestyle() == "--")
                line_x = directrix.get_xdata()[0]
                for label in canvas.ax.texts:
                    if label.get_text() == "准线" or label.get_text().startswith("$x=-"):
                        self.assertGreater(line_x - label.get_window_extent(renderer).x1, 12)
                p_label = next(label for label in canvas.ax.texts
                               if label.get_text().startswith("$P(x_0"))
                curve = next(line for line in canvas.ax.lines
                             if line.get_color() == BLUE and line.get_linewidth() == 5)
                path = curve.get_path().transformed(curve.get_transform())
                self.assertFalse(path.intersects_bbox(p_label.get_window_extent(renderer), filled=False))
                pf_label = next(label for label in canvas.ax.texts if label.get_text() == "$PF$")
                pf_box = pf_label.get_window_extent(renderer)
                padded = Bbox.from_extents(pf_box.x0 - 7, pf_box.y0 - 7,
                                           pf_box.x1 + 7, pf_box.y1 + 7)
                pf_segment = next(line for line in canvas.ax.lines
                                  if line.get_color() == GOLD and line.get_linewidth() == 5)
                pf_path = pf_segment.get_path().transformed(pf_segment.get_transform())
                self.assertFalse(pf_path.intersects_bbox(padded, filled=False))
                self.assertFalse(path.intersects_bbox(padded, filled=False))
                for other in canvas.ax.texts:
                    if other is not pf_label:
                        self.assertFalse(pf_box.overlaps(other.get_window_extent(renderer)))
                panel = next(patch for patch in canvas.ax.patches if patch.get_x() == 84)
                self.assertGreater(min(curve.get_ydata()), panel.get_y() + 20)
                self.assertLess(max(curve.get_ydata()), panel.get_y() + panel.get_height() - 20)
                self.assertLess(max(curve.get_xdata()), panel.get_x() + panel.get_width() - 20)
                canvas.fig.clear()


if __name__ == "__main__":
    unittest.main()
