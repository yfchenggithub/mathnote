import math
import random
import unittest
from model import Rotation, LESSON, MOTIONS


class RotationModelTests(unittest.TestCase):
    def assertPair(self,a,b):
        for x,y in zip(a,b): self.assertAlmostEqual(x,y,places=10)

    def test_named_key_states(self):
        rt=math.sqrt(2)
        for angle,want in [(0,(4,2)),(45,(1+rt,1+2*rt)),
                           (90,(0,4)),(-45,(1+2*rt,1-rt)),
                           (180,(-2,0)),(360,(4,2))]:
            self.assertPair(LESSON.image(angle),want)

    def test_random_rigid_rotations_and_components(self):
        rng=random.Random(40)
        for _ in range(1000):
            model=Rotation(tuple(rng.uniform(-9,9) for _ in range(2)),
                           tuple(rng.uniform(-9,9) for _ in range(2)))
            angle=rng.uniform(-1080,1080)
            u,v=model.relative; s,t=model.rotated_relative(angle)
            h,k=model.components(angle); radius2=u*u+v*v
            self.assertAlmostEqual(s*s+t*t,radius2,places=9)
            self.assertAlmostEqual(u*s+v*t,radius2*math.cos(math.radians(angle)),places=9)
            self.assertAlmostEqual(u*t-v*s,radius2*math.sin(math.radians(angle)),places=9)
            self.assertAlmostEqual(h[0]*k[0]+h[1]*k[1],0,places=9)
            self.assertPair(model.image(angle),(model.center[0]+h[0]+k[0],model.center[1]+h[1]+k[1]))

    def test_center_point_and_origin(self):
        for angle in [-720,-90,0,45,90,1080]:
            self.assertPair(Rotation((2,-1),(2,-1)).image(angle),(2,-1))
        self.assertPair(Rotation((0,0),(3,1)).image(90),(-1,3))

    def test_all_motion_samples_stay_in_chart(self):
        angles=[0,45]
        previous=0
        for target,duration,hold,caption in MOTIONS:
            self.assertGreater(duration,0); self.assertGreaterEqual(hold,0)
            angles.extend(previous+(target-previous)*i/240 for i in range(241))
            previous=target
        angles.extend(45*i/240 for i in range(241))
        for angle in angles:
            x,y=LESSON.image(angle)
            self.assertTrue(-3<x<5 and -3<y<5)
            self.assertAlmostEqual(math.dist(LESSON.center,(x,y)),math.sqrt(10),places=11)


if __name__=='__main__': unittest.main()
