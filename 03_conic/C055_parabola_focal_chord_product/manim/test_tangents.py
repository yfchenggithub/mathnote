"""Numerically audit the actual geometry used by C055TangentPerpendicular."""

import math
import unittest

from model_tangents import right_angle_vertices, tangent_state, unit_from_to


class TangentTests(unittest.TestCase):
    def test_curve_chord_tangent_and_directrix_over_parameters(self):
        for p in (0.5, 1.0, 2.0, 5.0):
            for index in range(601):
                m = -3 + index / 100
                state = tangent_state(m, p)
                tx, ty = state.intersection
                for x, y in (state.a, state.b):
                    self.assertAlmostEqual(y * y, 2 * p * x)
                    self.assertAlmostEqual(x, m * y + p / 2)
                    self.assertAlmostEqual(y * ty, p * (tx + x))
                    # Substitution of the tangent into the curve is (y-y0)^2=0.
                    self.assertAlmostEqual((2 * y) ** 2 - 4 * 2 * p * x, 0)
                self.assertGreater(state.a[1], 0)
                self.assertLess(state.b[1], 0)
                self.assertAlmostEqual(state.a[1] * state.b[1], -p * p)
                self.assertAlmostEqual(state.slope_a * state.slope_b, -1)
                self.assertAlmostEqual(tx, -p / 2)
                self.assertAlmostEqual(ty, (state.a[1] + state.b[1]) / 2)
                u = unit_from_to(state.intersection, state.a)
                v = unit_from_to(state.intersection, state.b)
                self.assertAlmostEqual(u[0] * v[0] + u[1] * v[1], 0)

    def test_right_angle_marker_and_rendered_range(self):
        for index in range(1501):
            state = tangent_state(-0.75 + 1.5 * index / 1500)
            q1, q2, q3 = right_angle_vertices(state)
            self.assertAlmostEqual(math.dist(q1, q2), 0.24)
            self.assertAlmostEqual(math.dist(q2, q3), 0.24)
            for x, y in (state.a, state.b, state.intersection, q1, q2, q3):
                self.assertTrue(-1.5 <= x <= 4.9)
                self.assertTrue(-4.3 <= y <= 4.3)

    def test_reference_states_and_invalid_inputs(self):
        state = tangent_state(0.75)
        self.assertEqual(state.a, (4, 4))
        self.assertEqual(state.b, (0.25, -1))
        self.assertEqual(state.intersection, (-1, 1.5))
        self.assertEqual((state.slope_a, state.slope_b), (0.5, -2))
        vertical = tangent_state(0)
        self.assertEqual((vertical.a, vertical.b), ((1, 2), (1, -2)))
        self.assertEqual(vertical.intersection, (-1, 0))
        reflected = tangent_state(-0.75)
        self.assertEqual((reflected.a, reflected.b), ((0.25, 1), (4, -4)))
        for m, p in ((0, 0), (0, -1), (math.inf, 2), (0, math.nan)):
            with self.assertRaises(ValueError):
                tangent_state(m, p)


if __name__ == "__main__":
    unittest.main()
