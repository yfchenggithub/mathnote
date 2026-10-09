"""Pixel-space collision and deterministic placement regression cases."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from scripts.static_cards.canvas import CardCanvas, MathFrame
from scripts.static_cards.labels import (CollisionFailure, LayoutFailure, CurveLabel, LabelLayout,
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
        self.assertNotEqual(first.artist.get_position(), second.artist.get_position())
        second.artist.set_position(first.artist.get_position())
        renderer = self.canvas.fig.canvas.get_renderer()
        lines, points = self.layout._geometry()
        hits = self.layout._collisions(second, second.artist.get_window_extent(renderer),
                                       lines, points, renderer)
        self.assertTrue(any(hit["type"] == "label" for hit in hits))

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

    def test_unregistered_plot_text_blocks_pass(self):
        self.canvas.label("plain note", 540, 700, 20)
        with self.assertRaises(LayoutFailure) as context:
            self.layout.coverage()
        self.assertEqual(context.exception.report["status"], "LAYOUT_FAIL")
        self.assertEqual(len(context.exception.report["uncovered_text"]), 1)
        self.assertTrue(any(entry["text"] == "plain note" and entry["zone"] == "plot"
                            for entry in self.canvas.text_coverage_report))

    def test_plain_text_vs_curve_and_asymptote(self):
        for name in ("curve", "asymptote"):
            with self.subTest(obstacle=name):
                line = self.frame.segment((-2, -2), (2, 2), name=name)
                text = self.canvas.label("plain note", 540, 760, 20)
                with self.assertRaises(CollisionFailure) as context:
                    self.layout.coverage()
                self.assertTrue(any(hit["object"] == name for hit in
                                    context.exception.report["collisions"]))
                text.remove()
                line.remove()

    def test_anchor_distance_gate(self):
        self.frame.point((0, 0), "", object_name="point P")
        self.layout.add(PointLabel("P", "point P", (0, 0), candidates=("E",),
                                   max_anchor_distance=5))
        with self.assertRaises(LayoutFailure) as context:
            self.layout.resolve()
        self.assertTrue(any(item["type"] == "anchor_distance" for attempt in
                            context.exception.report["attempted"]
                            for item in attempt["association"]))

    def test_wrong_object_association(self):
        self.frame.point((0, 0), "", object_name="point P")
        self.frame.segment((2, -2), (2, 2), name="wrong curve")
        label = self.layout.add(PointLabel("P", "point P", (0, 0),
                                           max_anchor_distance=120))
        x, y = self.frame.xy(1.4, 0)
        label.artist = self.canvas.math("P", x, y, 25, ha="center")
        with self.assertRaises(LayoutFailure) as context:
            self.layout.audit()
        self.assertTrue(any(item["type"] == "wrong_object" and
                            item["object"] == "wrong curve"
                            for item in context.exception.report["association"]))

    def test_safe_leader_is_drawn_and_checked(self):
        self.frame.point((0, 0), "", object_name="point P")
        label = self.layout.add(PointLabel("P", "point P", (0, 0), candidates=("E",),
                                           max_anchor_distance=5, allow_leader=True))
        self.layout.resolve()
        self.assertIsNotNone(label.leader_artist)
        self.assertIsNotNone(self.layout.report[0]["leader"])
        self.layout.audit()

    def test_unsafe_leader_fails(self):
        self.frame.point((0, 0), "", object_name="point P")
        x, _ = self.frame.xy(0.34, 0)
        self.canvas.line(x, 650, x, 870, name="leader obstacle")
        self.layout.add(PointLabel("P", "point P", (0, 0), candidates=("E",),
                                   max_anchor_distance=5, allow_leader=True))
        with self.assertRaises(LayoutFailure) as context:
            self.layout.resolve()
        self.assertEqual(context.exception.report["status"], "LAYOUT_FAIL")
        self.assertTrue(any(any(hit["object"] == "leader obstacle" for hit in
                                attempt.get("leader_collisions", []))
                            for attempt in context.exception.report["attempted"]))

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

    def test_builder_refuses_uncovered_plot_text(self):
        import json
        from scripts.static_cards import build

        self.canvas.label("unregistered", 540, 700, 20)
        self.canvas.label_layout = self.layout
        cards = SimpleNamespace(SPECS={"002": {"uid": "C999"}},
                                validate_content=lambda _: "PASS",
                                draw_card=lambda _: self.canvas,
                                LABEL_GATE_REQUIRED={"002": set()})
        model = SimpleNamespace(validation_results=lambda: {"geometry": "PASS"})
        with TemporaryDirectory(dir=build.ROOT / ".build" / "static_cards") as directory:
            output = Path(directory) / "C999"
            with patch.object(build, "load_source", return_value=(cards, model)), \
                 patch.object(build, "verify_sources", return_value=({}, {})):
                with self.assertRaises(LayoutFailure):
                    build.main(["--uid", "C999", "--source-dir", "unused/C999_test",
                                "--card", "002", "--output", str(output)])
            report = json.loads((output / "build_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["render_gate"], "LAYOUT_FAIL")
            self.assertEqual(report["uncovered_text"][0]["text"], "unregistered")


if __name__ == "__main__":
    unittest.main()
