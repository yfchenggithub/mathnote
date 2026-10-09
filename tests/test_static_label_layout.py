"""Pixel-space collision and deterministic placement regression cases."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from scripts.static_cards.canvas import CardCanvas, MathFrame
from scripts.static_cards.labels import (CollisionFailure, CurveLabel, LabelLayout,
                                         LineLabel, PointLabel, SegmentLabel)


class LabelLayoutTests(unittest.TestCase):
    def setUp(self):
        self.canvas = CardCanvas("TEST", "002", "test", "Layout", "Geometry")
        self.frame = MathFrame(self.canvas, 540, 760, 50)
        self.layout = LabelLayout(self.canvas, self.frame, (180, 430, 900, 1100))

    def tearDown(self):
        import matplotlib.pyplot as plt
        plt.close(self.canvas.fig)

    def _segment(self, start, end, direction=None):
        self.frame.segment(start, end, width=5)
        label = SegmentLabel("s", "segment", start, endpoint=end,
                             candidates=(direction,) if direction else (), clearance=8)
        self.layout.add(label)
        self.layout.resolve()
        self.assertEqual(self.layout.report[0]["status"], "PASS")
        self.assertGreaterEqual(len(label.attempted), 1)
        return label

    def test_horizontal_segment(self):
        self._segment((-2, 0), (2, 0))

    def test_vertical_segment(self):
        self._segment((0, -2), (0, 2))

    def test_slanted_segment(self):
        self._segment((-2, -1), (2, 1))

    def test_curve_near_point(self):
        xs = [v / 20 for v in range(-60, 61)]
        ys = [0.4 * x * x for x in xs]
        px, py = zip(*(self.frame.xy(x, y) for x, y in zip(xs, ys)))
        self.canvas.ax.plot(px, py, lw=5)
        self.frame.point((0, 0), "")
        label = self.layout.add(PointLabel("P", "curve point", (0, 0), clearance=8))
        self.layout.resolve()
        self.assertFalse(self.layout.audit())
        self.assertTrue(any(a["collisions"] for a in label.attempted))

    def test_axes_intersection(self):
        self.frame.segment((-4, 0), (4, 0))
        self.frame.segment((0, -4), (0, 4))
        self.frame.point((0, 0), "")
        self.layout.add(PointLabel("O", "origin", (0, 0), clearance=8))
        self.layout.resolve()
        self.assertEqual(self.layout.report[0]["status"], "PASS")

    def test_two_near_labels(self):
        self.frame.point((0, 0), "")
        self.frame.point((0.5, 0), "")
        first = self.layout.add(PointLabel("A", "first", (0, 0), priority=2))
        second = self.layout.add(PointLabel("B", "second", (0.5, 0), priority=1))
        self.layout.resolve()
        self.assertTrue(any(any(h["type"] == "label" for h in a["collisions"])
                            for a in second.attempted))
        self.assertNotEqual(first.artist.get_position(), second.artist.get_position())

    def test_multiple_candidates_blocked(self):
        self.frame.point((0, 0), "")
        self.frame.segment((0.5, 0.2), (2, 1.7))
        self.frame.segment((0.5, -0.2), (2, -1.7))
        label = self.layout.add(PointLabel("P", "blocked point", (0, 0), clearance=8))
        self.layout.resolve()
        self.assertGreater(sum(bool(a["collisions"]) for a in label.attempted), 1)
        self.assertEqual(self.layout.report[0]["status"], "PASS")

    def test_all_candidates_unsafe(self):
        # At 25 pt the measured glyph cannot fit into this valid plot region.
        self.layout.bounds = (538, 758, 542, 762)
        self.layout.add(LineLabel("x", "axis", (0, 0)))
        with self.assertRaises(CollisionFailure) as context:
            self.layout.resolve()
        failure = context.exception.report
        self.assertEqual(failure["status"], "COLLISION_FAIL")
        self.assertTrue(failure["attempted"])
        self.assertTrue(all(a["collisions"] for a in failure["attempted"]))

    def test_exact_ink_collision_is_detected(self):
        self.frame.segment((-2, 0), (2, 0), width=5)
        label = self.layout.add(SegmentLabel("s", "segment", (-2, 0), endpoint=(2, 0)))
        self.canvas.fig.canvas.draw()
        renderer = self.canvas.fig.canvas.get_renderer()
        label.artist = self.canvas.math("s", *self.frame.xy(0, 0), 25)
        box = label.artist.get_window_extent(renderer)
        lines, points = self.layout._geometry()
        hits = self.layout._collisions(label, box, lines, points, renderer)
        self.assertTrue(any(hit["type"] == "path" for hit in hits))

    def test_curve_label_and_line_label_types(self):
        self.assertEqual(CurveLabel("C", "curve", (0, 0)).kind, "curve")
        self.assertEqual(LineLabel("x", "axis", (0, 0)).kind, "line")

    def test_builder_records_collision_fail(self):
        import json
        from scripts.static_cards import build
        failure = {"uid": "C999", "card": "002", "label": "P",
                   "collisions": [{"object": "curve", "type": "path"}],
                   "attempted": [{"candidate": "NE"}], "status": "COLLISION_FAIL"}

        def reject(_):
            raise CollisionFailure(failure)

        cards = SimpleNamespace(SPECS={"002": {"uid": "C999"}},
                                validate_content=lambda _: "PASS", draw_card=reject)
        model = SimpleNamespace(validation_results=lambda: {"geometry": "PASS"})
        with TemporaryDirectory(dir=build.ROOT / ".build" / "static_cards") as directory:
            output = Path(directory) / "C999"
            with patch.object(build, "load_source", return_value=(cards, model)), \
                 patch.object(build, "verify_sources", return_value=({}, {})):
                with self.assertRaises(CollisionFailure):
                    build.main(["--uid", "C999", "--source-dir", "unused/C999_test",
                                "--card", "002", "--output", str(output)])
            report = json.loads((output / "build_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["render_gate"], "COLLISION_FAIL")
            self.assertEqual(report["label_layout"][0]["attempted"][0]["candidate"], "NE")


if __name__ == "__main__":
    unittest.main()
