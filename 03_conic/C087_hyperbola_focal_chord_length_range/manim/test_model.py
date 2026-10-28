import json
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import snapshot, screen, sampling_angles, CRITICAL


class ModelTests(unittest.TestCase):
    def check_state(self, s):
        a,b,c,t = (s[k] for k in ('a','b','c','theta'))
        for x,y in s['points']:
            self.assertAlmostEqual(x*x/(a*a)-y*y/(b*b), 1, delta=2e-8)
            self.assertAlmostEqual((x-c)*math.sin(t)-y*math.cos(t), 0, delta=2e-9)
        if s['kind']=='boundary':
            self.assertEqual(len(s['points']),1)
            self.assertIsNone(s['length'])
            return
        L=s['length']
        self.assertAlmostEqual(L,2*a*b*b/abs(a*a-c*c*math.cos(t)**2),delta=1e-7)
        if s['kind']=='opposite':
            xs=sorted(x for x,y in s['points'])
            self.assertLessEqual(xs[0],-a+1e-9)
            self.assertGreaterEqual(xs[1],a-1e-9)
            self.assertGreaterEqual(L+1e-9,2*a)
        else:
            self.assertTrue(all(x>=a-1e-9 for x,y in s['points']))
            self.assertGreaterEqual(L+1e-9,2*b*b/a)
        for p in s['points']:
            x,y,_=screen(p,s['scale'])
            self.assertLessEqual(abs(x),3.1000001)
            self.assertLessEqual(abs(y-1.2),3.1000001)

    def test_all_motion_samples(self):
        for t in sampling_angles():
            self.check_state(snapshot(t))

    def test_general_parameters_and_reflections(self):
        for a,b in [(1,1),(4,2),(2,5),(3,4)]:
            critical=math.atan2(b,a)
            for t in [0,critical*.3,critical*.95,(critical+math.pi/2)/2,math.pi/2]:
                for angle in [t,-t,math.pi-t]:
                    self.check_state(snapshot(angle,a,b))

    def test_minima_and_boundary(self):
        self.assertAlmostEqual(snapshot(0)['length'],6)
        self.assertAlmostEqual(snapshot(math.pi/2)['length'],32/3)
        for t in [CRITICAL,math.pi-CRITICAL]:
            self.check_state(snapshot(t))
        p=snapshot(CRITICAL)['points'][0]
        self.assertAlmostEqual(p[0],17/5)
        self.assertAlmostEqual(p[1],-32/15)

    def test_unbounded_from_both_sides(self):
        for sign in [-1,1]:
            lengths=[snapshot(CRITICAL+sign*e)['length'] for e in [.1,.01,.001]]
            self.assertTrue(lengths[0]<lengths[1]<lengths[2])

    def test_rendered_audit_if_present(self):
        root=Path(__file__).resolve().parents[3]
        path=root/'build/manim/C087/focal_chord_range/audit.json'
        if not path.exists():
            self.skipTest('render audit not yet produced')
        rows=json.loads(path.read_text(encoding='utf8'))
        self.assertGreater(len(rows),400)
        for row in rows:
            self.check_state(row)
            self.assertLessEqual(row['bounds'][2],4.15)
            self.assertGreaterEqual(row['bounds'][0],-4.15)
            self.assertLessEqual(row['bounds'][3],5.2)
            self.assertGreaterEqual(row['bounds'][1],-2.7)


if __name__=='__main__':
    unittest.main(verbosity=2)
