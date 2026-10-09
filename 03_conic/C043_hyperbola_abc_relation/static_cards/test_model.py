"""C043 mathematics, source agreement, and card geometry checks."""

from fractions import Fraction
from math import isclose
import unittest

from model import Hyperbola, validation_results
from scripts.static_cards.build import ROOT, load_source, verify_sources
from matplotlib.transforms import Bbox
from scripts.static_cards.canvas import MathFrame
from scripts.static_cards.labels import LabelLayout, PointLabel, SegmentLabel


class HyperbolaTests(unittest.TestCase):
    def test_card_002_layout_and_constructed_collisions(self):
        source = ROOT / "03_conic" / "C043_hyperbola_abc_relation"
        cards, _ = load_source(source, "C043")
        canvas = cards.draw_card("002")
        self.assertEqual({item["label"] for item in canvas.layout_report},
                         cards.LABEL_GATE_REQUIRED["002"])
        self.assertTrue(all(item["actual_clearance_px"] >= item["minimum_required_px"]
                            for item in canvas.layout_report))
        coverage = canvas.label_layout.finalize()
        plot_text = [item for item in coverage if item["zone"] == "plot"]
        self.assertEqual(len(plot_text), 8)
        self.assertTrue(all(item["registered"] and not item["collisions"]
                            for item in plot_text))
        b_label = next(item for item in canvas.layout_report if item["label"] == "B")
        self.assertLessEqual(b_label["anchor_distance_px"], 42)
        self.assertIsNone(b_label["leader"])
        self.assertFalse(any("辅助矩形角点不在曲线上" == t.get_text()
                             for t in canvas.ax.texts))
        frame = MathFrame(canvas, 420, 772, 49)
        gate = LabelLayout(canvas, frame, (103, 479, 978, 1056))
        canvas.fig.canvas.draw()
        renderer = canvas.fig.canvas.get_renderer()
        lines, points = gate._geometry()
        # A's original placement cuts the right branch and auxiliary edge.
        ax, ay = frame.xy(3, 0)
        old_a = PointLabel("A", "point A", (3, 0))
        old_a.artist = canvas.math("A", ax - 3, ay + 33, 25)
        old_box = old_a.artist.get_window_extent(renderer)
        self.assertTrue(any(hit["type"] == "path" for hit in
                            gate._collisions(old_a, old_box, lines, points, renderer)))
        old_a.artist.remove()
        # A label centred on AB is rejected even though its anchor is valid.
        bx, by = frame.xy(3, 2)
        blocked_b = SegmentLabel("b", "AB", (3, 0), endpoint=(3, 4))
        blocked_b.artist = canvas.math("b", bx, by, 25, ha="center")
        b_box = blocked_b.artist.get_window_extent(renderer)
        self.assertTrue(any(hit["object"] == "AB" for hit in
                            gate._collisions(blocked_b, b_box, lines, points, renderer)))
        canvas.fig.clear()

    def test_parameter_gate(self):
        self.assertTrue(all(value == "PASS" for value in validation_results().values()))
        for a, b in ((0, 2), (-1, 2), (2, 0)):
            with self.subTest(a=a, b=b), self.assertRaises(ValueError):
                Hyperbola(a, b)

    def test_two_branches_and_vertices(self):
        model = Hyperbola(3, 4)
        self.assertEqual(model.vertices, ((-3, 0), (3, 0)))
        for side in (-1, 1):
            self.assertEqual(model.exact_branch_point(side, Fraction(1)), (side * 3, 0))
            for u in (Fraction(1, 3), Fraction(1, 2), Fraction(2), Fraction(3)):
                x, y = model.exact_branch_point(side, u)
                self.assertEqual(model.equation_value((x, y)), 1)
                self.assertEqual(x > 0, side > 0)
        self.assertNotEqual(model.exact_branch_point(-1, 2),
                            model.exact_branch_point(1, 2))

    def test_auxiliary_geometry_distinguished_from_curve(self):
        model = Hyperbola(3, 4)
        origin, vertex, corner, focus = (0, 0), (3, 0), (3, 4), (5, 0)
        self.assertEqual(model.c_squared, 25)
        self.assertEqual((vertex[0] - origin[0]) ** 2, 9)
        self.assertEqual((corner[1] - vertex[1]) ** 2, 16)
        self.assertEqual(corner[0] ** 2 + corner[1] ** 2, 25)
        self.assertNotEqual(corner, focus)
        self.assertEqual(model.equation_value(corner), 0)
        self.assertEqual(model.equation_value((0, 4)), -1)
        self.assertEqual(model.equation_value((0, -4)), -1)
        self.assertEqual(model.asymptote_y(3), 4)
        self.assertEqual(model.asymptote_y(-3), -4)

    def test_asymptotic_trend(self):
        model = Hyperbola(3, 4)
        for sign in (-1, 1):
            small = model.branch_point(sign, 1.0)
            large = model.branch_point(sign, 4.0)
            self.assertLess(abs(large[1] / large[0] - sign * 4 / 3),
                            abs(small[1] / small[0] - sign * 4 / 3))

    def test_formal_example_and_content(self):
        source = ROOT / "03_conic" / "C043_hyperbola_abc_relation"
        cards, _ = load_source(source, "C043")
        _, texts = verify_sources(source, cards.SPECS)
        self.assertEqual(cards.validate_content(texts), "PASS")
        model = Hyperbola(4, 3)
        self.assertEqual(model.c, 5)
        self.assertEqual(model.foci, ((-5, 0), (5, 0)))
        self.assertEqual(model.asymptote_y(4), 3)
        self.assertTrue(isclose(model.c / 4, 1.25))

    def test_diagram_panel_and_focus_label_clearance(self):
        source = ROOT / "03_conic" / "C043_hyperbola_abc_relation"
        cards, _ = load_source(source, "C043")
        for number in ("001", "002"):
            with self.subTest(card=number):
                canvas = cards.draw_card(number)
                canvas.fig.canvas.draw()
                panel = next(p for p in canvas.ax.patches if p.get_x() == 85
                             and p.get_height() > 600)
                for line in canvas.ax.lines:
                    if line.get_linewidth() not in (4, 5) or len(line.get_xdata()) < 100:
                        continue
                    self.assertGreater(min(line.get_xdata()), panel.get_x() + 12)
                    self.assertLess(max(line.get_xdata()), panel.get_x() + panel.get_width() - 12)
                    self.assertGreater(min(line.get_ydata()), panel.get_y() + 12)
                    self.assertLess(max(line.get_ydata()), panel.get_y() + panel.get_height() - 12)
                if number == "001":
                    renderer = canvas.fig.canvas.get_renderer()
                    label = next(t for t in canvas.ax.texts if t.get_text() == "$OF_2=c$")
                    bounds = label.get_window_extent(renderer)
                    padded = Bbox.from_extents(bounds.x0 - 5, bounds.y0 - 5,
                                               bounds.x1 + 5, bounds.y1 + 5)
                    for line in canvas.ax.lines:
                        if line.get_color() == "#176dcb" and len(line.get_xdata()) > 100:
                            path = line.get_path().transformed(line.get_transform())
                            self.assertFalse(path.intersects_bbox(padded, filled=False))
                canvas.fig.clear()


if __name__ == "__main__":
    unittest.main()
