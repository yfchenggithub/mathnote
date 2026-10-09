"""Independent numerical checks for the T021 point transformations."""

import itertools
import math
import unittest


def first_path(t, a, omega, phi):
    """Move a point left by phi, scale its x coordinate, then scale its y."""
    x, y = t, math.sin(t)
    x -= phi
    x /= omega
    y *= a
    return x, y


def second_path(t, a, omega, phi):
    """Scale x first, then move left by phi/omega, then scale y."""
    x, y = t, math.sin(t)
    x /= omega
    x -= phi / omega
    y *= a
    return x, y


class T021TransformMathTests(unittest.TestCase):
    def test_point_paths_and_target_curve_parameter_matrix(self):
        samples = [-2.3, -math.pi / 2, -0.41, 0.0, 0.37, math.pi / 2, 2.8]
        for a, omega, phi, t in itertools.product(
            [-2.0, 2.0], [0.5, 1.0, 2.0],
            [-math.pi / 4, 0.0, math.pi / 4], samples,
        ):
            with self.subTest(a=a, omega=omega, phi=phi, t=t):
                x1, y1 = first_path(t, a, omega, phi)
                x2, y2 = second_path(t, a, omega, phi)
                self.assertAlmostEqual(x1, x2, places=13)
                self.assertAlmostEqual(y1, y2, places=13)
                self.assertAlmostEqual(y1, a * math.sin(omega * x1 + phi), places=13)

    def test_negative_a_original_counterexample(self):
        a, omega, phi, x = -2.0, 2.0, math.pi / 4, math.pi / 8
        t = omega * x + phi
        self.assertAlmostEqual(first_path(t, a, omega, phi)[1], -2.0)
        self.assertAlmostEqual(second_path(t, a, omega, phi)[1], -2.0)
        self.assertAlmostEqual(abs(a) * math.sin(t), 2.0)  # old error
        self.assertEqual(abs(a), 2.0)  # amplitude is nonnegative

    def test_signed_shifts_equality_and_scaling_regimes(self):
        for omega, phi, equal in [
            (1.0, math.pi / 4, True),
            (2.0, 0.0, True),
            (1.0, 0.0, True),
            (2.0, math.pi / 4, False),
            (0.5, -math.pi / 4, False),
        ]:
            with self.subTest(omega=omega, phi=phi):
                self.assertEqual(math.isclose(abs(phi), abs(phi / omega)), equal)
                self.assertEqual(math.copysign(1, phi), math.copysign(1, phi / omega))
        self.assertLess(1 / 2.0, 1.0)  # compression
        self.assertEqual(1 / 1.0, 1.0)  # unchanged
        self.assertGreater(1 / 0.5, 1.0)  # stretch

    def test_adjusted_composition_and_noncommutation(self):
        t, omega, phi = 0.37, 2.0, math.pi / 4
        scale_after_shift = (t - phi) / omega
        shift_after_scale_adjusted = t / omega - phi / omega
        shift_after_scale_unadjusted = t / omega - phi
        self.assertAlmostEqual(scale_after_shift, shift_after_scale_adjusted)
        self.assertNotAlmostEqual(scale_after_shift, shift_after_scale_unadjusted)

    def test_former_and_new_worked_examples(self):
        cases = [
            (3.0, 2.0, math.pi / 4),
            (2.0, 3.0, -math.pi / 2),
            (4.0, 2.0, -math.pi / 3),
            (-2.0, 2.0, math.pi / 4),
            (2.0, 1.0, math.pi / 4),
            (2.0, 2.0, 0.0),
            (2.0, 0.5, -math.pi / 4),
        ]
        for a, omega, phi in cases:
            for x in [-1.0, 0.0, math.pi / 8, 1.27]:
                with self.subTest(a=a, omega=omega, phi=phi, x=x):
                    t = omega * x + phi
                    p1 = first_path(t, a, omega, phi)
                    p2 = second_path(t, a, omega, phi)
                    self.assertAlmostEqual(p1[0], x)
                    self.assertAlmostEqual(p2[0], x)
                    self.assertAlmostEqual(p1[1], a * math.sin(omega * x + phi))
                    self.assertAlmostEqual(p2[1], a * math.sin(omega * x + phi))


if __name__ == "__main__":
    unittest.main()
