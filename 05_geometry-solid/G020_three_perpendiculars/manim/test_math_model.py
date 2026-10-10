"""Independent checks for G020 world geometry and camera-independent facts."""

import math
import unittest

from math_model import G020State, INITIAL, PERPENDICULAR, RAISED, dot, norm, project_alpha, subtract


class G020Mathematics(unittest.TestCase):
    def test_m1_preconditions(self):
        for kwargs in (dict(a=0, height=2, line_angle_deg=90),
                       dict(a=2, height=0, line_angle_deg=90),
                       dict(a=2, height=float("nan"), line_angle_deg=90)):
            with self.assertRaises(ValueError):
                G020State(**kwargs)

    def test_m2_initial_world_geometry(self):
        s = INITIAL
        self.assertEqual(s.O, (0, 0, 0))
        self.assertEqual(s.A, (2.8, 0, 0))
        self.assertEqual(s.P, (0, 0, 1.6))
        self.assertEqual(project_alpha(s.P), s.O)
        self.assertEqual(project_alpha(s.A), s.A)
        self.assertAlmostEqual(dot(s.PO, s.OA), 0)
        self.assertAlmostEqual(s.point_on_l(1)[2], 0)

    def test_m3_projection_and_dot_identity_at_intermediate_states(self):
        for height in (0.2, 0.9, 1.6, 2.3, 3.0):
            for angle in (0, 20, 48, 73, 90, 117):
                s = G020State(2.8, height, angle)
                for t in (0, .2, .5, .8, 1):
                    q = s.projected_point_on_PA(t)
                    self.assertAlmostEqual(q[0], 2.8 * t)
                    self.assertAlmostEqual(q[1], 0)
                    self.assertAlmostEqual(q[2], 0)
                # Independent coordinate expansion: AP=(a,0,-h), d=(cos θ,sin θ,0).
                expected = 2.8 * math.cos(math.radians(angle))
                self.assertAlmostEqual(s.plane_dot, expected, places=12)
                self.assertAlmostEqual(s.space_dot, expected, places=12)

    def test_m4_both_directions_and_negative_case(self):
        self.assertFalse(INITIAL.is_perpendicular())
        self.assertGreater(abs(INITIAL.plane_dot), 1)
        self.assertTrue(PERPENDICULAR.is_perpendicular())
        self.assertTrue(RAISED.is_perpendicular())
        for angle in (30, 60, 89, 91, 120):
            s = G020State(2.8, 2, angle)
            self.assertFalse(s.is_perpendicular())

    def test_m5_height_motion_preserves_true_relation(self):
        for i in range(41):
            h = 1.6 + (3.0 - 1.6) * i / 40
            s = G020State(2.8, h, 90)
            self.assertEqual(s.OA, PERPENDICULAR.OA)
            self.assertAlmostEqual(norm(s.AP), math.hypot(2.8, h))
            self.assertAlmostEqual(s.space_dot, 0, places=12)

    def test_m6_relevant_boundaries(self):
        near = G020State(2.8, 1e-6, 90)
        self.assertTrue(near.is_perpendicular())
        self.assertNotEqual(near.P, near.O)
        with self.assertRaises(ValueError):
            G020State(2.8, 0, 90)
        with self.assertRaises(ValueError):
            G020State(0, 1.6, 90)

    def test_m7_rigid_view_change_cannot_change_dot_products(self):
        s = RAISED
        # An independently written rigid z-axis rotation changes coordinates,
        # as a different world basis or camera view would, but preserves dots.
        yaw = math.radians(37)
        def rotate(v):
            x, y, z = v
            return (x * math.cos(yaw) - y * math.sin(yaw),
                    x * math.sin(yaw) + y * math.cos(yaw), z)
        self.assertAlmostEqual(dot(rotate(s.line_direction), rotate(s.AP)), s.space_dot)
        self.assertAlmostEqual(dot(rotate(s.line_direction), rotate(s.OA)), s.plane_dot)

    def test_m8_true_right_angle_markers(self):
        for world_space in (False, True):
            b, c, d = RAISED.right_angle_corners(world_space)
            self.assertAlmostEqual(dot(subtract(b, RAISED.A), subtract(d, RAISED.A)), 0, places=12)
            self.assertAlmostEqual(norm(subtract(b, RAISED.A)), .32)
            self.assertAlmostEqual(norm(subtract(d, RAISED.A)), .32)
            self.assertAlmostEqual(norm(subtract(c, b)), .32)
        with self.assertRaises(ValueError):
            INITIAL.right_angle_corners(False)

    def test_m9_world_labels_and_final_conclusion(self):
        s = RAISED
        self.assertEqual(s.point_on_l(0), s.A)
        self.assertEqual(s.projected_point_on_PA(0), s.O)
        self.assertEqual(s.projected_point_on_PA(1), s.A)
        self.assertEqual(s.P[2], 3.0)
        self.assertTrue(s.is_perpendicular())


if __name__ == "__main__":
    unittest.main()
