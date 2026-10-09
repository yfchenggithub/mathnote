"""Independent numerical regression for T021 animation states; no Manim import."""

import itertools
import math
import unittest

from math_model import (
    DEMO, TRACKED_T, Parameters, amplitude_scale, baseline, first_scale,
    first_shift, horizontal_result, reflection, second_scale, second_shift,
)


class T021ModelTests(unittest.TestCase):
    def test_conditions_and_demo(self):
        for a, omega in [(0, 2), (2, 0), (-2, -1)]:
            with self.assertRaises(ValueError):
                Parameters(a, omega, 0)
        self.assertAlmostEqual(DEMO.first_shift_distance, math.pi / 2)
        self.assertAlmostEqual(DEMO.second_shift_distance, math.pi / 4)
        self.assertAlmostEqual(first_shift(DEMO, 1).point(TRACKED_T)[0], 0)
        self.assertAlmostEqual(second_scale(DEMO, 1).point(TRACKED_T)[0], math.pi / 4)
        self.assertAlmostEqual(first_scale(DEMO, 1).point(TRACKED_T)[0], 0)
        self.assertAlmostEqual(second_shift(DEMO, 1).point(TRACKED_T)[0], 0)
        self.assertAlmostEqual(reflection(DEMO, 1).point(TRACKED_T)[1], -2)

    def test_all_path_endpoints_and_curve_values(self):
        samples = [-2.3, -math.pi / 2, -0.43, 0, 0.37, math.pi / 2, 2.8]
        for a, omega, phi, t in itertools.product(
            [-2, 2], [0.5, 1, 2], [-math.pi / 4, 0, math.pi / 2], samples,
        ):
            with self.subTest(a=a, omega=omega, phi=phi, t=t):
                p = Parameters(a, omega, phi)
                one = first_scale(p, 1).point(t)
                two = second_shift(p, 1).point(t)
                expected_x = (t - phi) / omega
                self.assertAlmostEqual(one[0], expected_x)
                self.assertAlmostEqual(two[0], expected_x)
                self.assertAlmostEqual(one[1], math.sin(t))
                self.assertAlmostEqual(two[1], math.sin(t))
                final = reflection(p, 1) if a < 0 else amplitude_scale(p, 1)
                x, y = final.point(t)
                self.assertAlmostEqual(x, expected_x)
                self.assertAlmostEqual(y, a * math.sin(t))
                self.assertAlmostEqual(final.value(x), p.target(x))
                self.assertAlmostEqual(p.amplitude, abs(a))
                self.assertAlmostEqual(p.period, 2 * math.pi / omega)

    def test_interpolation_curve_and_marked_point_agree(self):
        phases = (first_shift, first_scale, second_scale, second_shift,
                  amplitude_scale, reflection)
        for phase, u, t in itertools.product(
            phases, [0, 0.2, 0.5, 0.8, 1], [-2.1, 0.17, TRACKED_T, 2.4],
        ):
            with self.subTest(phase=phase.__name__, u=u, t=t):
                state = phase(DEMO, u)
                x, y = state.point(t)
                self.assertGreater(state.scale, 0)
                self.assertAlmostEqual(state.value(x), y)
        self.assertEqual(baseline().point(TRACKED_T), (TRACKED_T, 1.0))

    def test_independent_stage_coordinates_and_noncommutation(self):
        p, t = DEMO, 0.37
        self.assertAlmostEqual(first_shift(p, 1).point(t)[0], t - p.phi)
        self.assertAlmostEqual(first_scale(p, 1).point(t)[0], (t - p.phi) / p.omega)
        self.assertAlmostEqual(second_scale(p, 1).point(t)[0], t / p.omega)
        self.assertAlmostEqual(second_shift(p, 1).point(t)[0], t / p.omega - p.phi / p.omega)
        self.assertNotAlmostEqual((t - p.phi) / p.omega, t / p.omega - p.phi)

    def test_negative_a_historic_counterexample(self):
        p = Parameters(-2, 2, math.pi / 4)
        x = math.pi / 8
        self.assertAlmostEqual(p.target(x), -2)
        self.assertAlmostEqual(abs(p.a) * math.sin(p.omega * x + p.phi), 2)
        t = p.omega * x + p.phi
        self.assertAlmostEqual(reflection(p, 1).point(t)[1], -2)
        self.assertAlmostEqual(amplitude_scale(p, 1).point(t)[1], 2)

    def test_shift_equalities_and_directions(self):
        for omega, phi, same in [
            (1, math.pi / 4, True), (2, 0, True), (1, 0, True),
            (2, math.pi / 4, False), (0.5, -math.pi / 4, False),
        ]:
            p = Parameters(2, omega, phi)
            self.assertEqual(math.isclose(p.first_shift_distance,
                                          p.second_shift_distance), same)
            self.assertAlmostEqual(first_shift(p, 1).shift, -phi)
            self.assertAlmostEqual(second_shift(p, 1).shift, -phi / omega)
        self.assertLess(1 / 2, 1)  # omega > 1: compress
        self.assertEqual(1 / 1, 1)
        self.assertGreater(1 / 0.5, 1)  # omega < 1: stretch


if __name__ == "__main__":
    unittest.main()
