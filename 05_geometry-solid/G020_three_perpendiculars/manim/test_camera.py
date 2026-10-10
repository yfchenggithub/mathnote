"""Actual Manim camera projections of the same verified G020 world state."""

import math
import unittest

import numpy as np
from manim import DEGREES, ThreeDCamera

from math_model import RAISED


class G020CameraAudit(unittest.TestCase):
    def camera(self, phi, theta):
        return ThreeDCamera(
            phi=phi * DEGREES, theta=theta * DEGREES, zoom=1.4,
            frame_center=np.array((1.6, 0, .2)),
        )

    def test_m7_three_views_preserve_world_truth_and_visible_points(self):
        s = RAISED
        for phi, theta in ((45, -35), (15, -35), (78, -20)):
            camera = self.camera(phi, theta)
            projected = [camera.project_point(np.array(p)) for p in (s.O, s.A, s.P)]
            self.assertTrue(all(np.isfinite(q).all() for q in projected))
            self.assertGreater(np.linalg.norm(projected[2][:2] - projected[0][:2]), .8)
            self.assertGreater(np.linalg.norm(projected[1][:2] - projected[0][:2]), 1.0)
            # The camera does not enter the world-coordinate dot products.
            self.assertTrue(s.is_perpendicular())
            self.assertAlmostEqual(s.plane_dot, s.space_dot, places=12)

    def test_m8_formal_oblique_camera_keeps_key_geometry_in_portrait_frame(self):
        camera = self.camera(45, -35)
        corners = ((-.25,-1.85,0), (4.1,-1.85,0),
                   (4.1,1.85,0), (-.25,1.85,0))
        points = corners + (RAISED.O, RAISED.A, RAISED.P,
                            RAISED.point_on_l(-1.9), RAISED.point_on_l(1.9))
        for point in points:
            x, y, _ = camera.project_point(np.array(point))
            self.assertLess(abs(x), 4.5)
            self.assertLess(abs(y), 5.0)  # keep clear of fixed header/footer


if __name__ == "__main__":
    unittest.main()
