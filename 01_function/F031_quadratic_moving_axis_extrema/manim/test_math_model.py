"""F031 boundary and independent-candidate regression tests."""

from __future__ import annotations

import random
import unittest

from math_model import (
    QuadraticSpec,
    analytic_state,
    assert_independent_agreement,
    candidate_extrema,
)


class F031MathTest(unittest.TestCase):
    def test_invalid_conditions(self) -> None:
        for left, right, a in [(1, 1, 1), (2, 1, 1), (-2, 2, 0)]:
            with self.assertRaises(ValueError):
                QuadraticSpec(left, right, a, 0)

    def test_all_seven_regions_both_openings(self) -> None:
        positions = [-3, -2, -1, 0, 1, 2, 3]
        cases = [
            "left", "at_left", "left_half", "midpoint",
            "right_half", "at_right", "right",
        ]
        for a in (0.25, -0.25):
            for h, case in zip(positions, cases):
                with self.subTest(a=a, h=h):
                    spec = QuadraticSpec(-2, 2, a, h, 1)
                    state = analytic_state(spec)
                    self.assertEqual(state.axis_case, case)
                    self.assertTrue(all(-2 <= x <= 2 for x in
                                        state.minimum_points + state.maximum_points))
                    assert_independent_agreement(spec)

    def test_threshold_sides(self) -> None:
        eps = 1e-6
        for a in (0.25, -0.25):
            for boundary in (-2, 0, 2):
                for offset in (-eps, 0, eps):
                    with self.subTest(a=a, boundary=boundary, offset=offset):
                        assert_independent_agreement(
                            QuadraticSpec(-2, 2, a, boundary + offset))

    def test_midpoint_tie_and_endpoint_uniqueness(self) -> None:
        up = analytic_state(QuadraticSpec(-2, 2, 0.25, 0))
        down = analytic_state(QuadraticSpec(-2, 2, -0.25, 0, 3))
        self.assertEqual(up.maximum_points, (-2, 2))
        self.assertEqual(up.minimum_points, (0,))
        self.assertEqual(down.minimum_points, (-2, 2))
        self.assertEqual(down.maximum_points, (0,))
        for h, expected in [(-2, (-2,)), (2, (2,))]:
            self.assertEqual(
                analytic_state(QuadraticSpec(-2, 2, 0.25, h)).minimum_points,
                expected)

    def test_vertex_outside_never_marked_extremum(self) -> None:
        for h in (-3, 3):
            for a in (-0.25, 0.25):
                state = analytic_state(QuadraticSpec(-2, 2, a, h))
                self.assertNotIn(h, state.minimum_points + state.maximum_points)

    def test_endpoints_and_random_cross_check(self) -> None:
        rng = random.Random(31014)
        for _ in range(300):
            left = rng.uniform(-4, 0)
            right = rng.uniform(0.5, 5)
            h = rng.uniform(left - 2, right + 2)
            a = rng.choice((-1, 1)) * rng.uniform(.1, 2)
            k = rng.uniform(-3, 3)
            spec = QuadraticSpec(left, right, a, h, k)
            assert_independent_agreement(spec)
            state = analytic_state(spec)
            self.assertAlmostEqual(state.left_value, spec.value(left))
            self.assertAlmostEqual(state.right_value, spec.value(right))
            self.assertAlmostEqual(state.vertex[1], k)
            for i in range(101):
                x = left + (right - left) * i / 100
                self.assertLessEqual(state.minimum_value - 1e-9, spec.value(x))
                self.assertLessEqual(spec.value(x), state.maximum_value + 1e-9)

    def test_candidate_method_separate_from_classification(self) -> None:
        spec = QuadraticSpec(-2, 2, 0.25, 0)
        low, min_points, high, max_points = candidate_extrema(spec)
        self.assertEqual((low, min_points, high, max_points),
                         (0, (0,), 1, (-2, 2)))


if __name__ == "__main__":
    unittest.main()
