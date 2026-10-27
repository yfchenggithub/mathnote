import json,math,unittest
from pathlib import Path
from model import Configuration,screen,familiar_points,SCALE


class ModelTests(unittest.TestCase):
    def check_config(self,m):
        a,b,c=m.a,m.b,m.c;F,M,N=m.F,m.M,m.N
        self.assertGreater(M[0],a)
        self.assertLess(N[0],M[0]);self.assertLess(M[0],F[0])
        self.assertAlmostEqual(M[0]**2/a**2-M[1]**2/b**2,1,places=9)
        self.assertAlmostEqual(M[1],b/a*(M[0]-c),places=9)
        self.assertAlmostEqual(N[1],-b/a*N[0],places=9)
        self.assertAlmostEqual(N[1],b/a*(N[0]-c),places=9)
        self.assertAlmostEqual(math.dist(F,M),b*b/(2*a),places=9)
        self.assertAlmostEqual(math.dist(M,N),a/2,places=9)
        self.assertAlmostEqual(math.dist(F,M)/math.dist(M,N),m.e*m.e-1,places=9)
        self.assertAlmostEqual(m.t/(c/2-m.t),m.ratio,places=9)
        self.assertAlmostEqual(math.dist(screen(M),screen(N)),SCALE*a/2,places=9)

    def test_full_motion_domain(self):
        for i in range(481):self.check_config(Configuration(3,2.25+1.75*i/480))

    def test_parameter_generalization_and_reflections(self):
        for a in [.5,2,3,6]:
            for b in [.2,2.25,3,4,9]:
                m=Configuration(a,b);self.check_config(m)
                for sx,sy in [(1,1),(1,-1),(-1,1),(-1,-1)]:
                    tr=lambda P:(sx*P[0],sy*P[1])
                    self.assertAlmostEqual(math.dist(tr(m.F),tr(m.M))/math.dist(tr(m.M),tr(m.N)),m.ratio,places=9)

    def test_key_states_and_familiar_mapping(self):
        m=Configuration();self.assertEqual(m.c,5)
        self.assertAlmostEqual(m.M[0],17/5);self.assertAlmostEqual(m.M[1],-32/15)
        self.assertAlmostEqual(m.N[0],5/2);self.assertAlmostEqual(m.N[1],-10/3)
        self.assertAlmostEqual(m.fm,8/3);self.assertEqual(m.mn,1.5)
        F,M,N=familiar_points()
        self.assertAlmostEqual(math.dist(F,M)/math.dist(M,N),16/9)
        for i in range(61):
            q=i/60
            states=[tuple((1-q)*s+q*t for s,t in zip(P,screen(Q))) for P,Q in zip((F,M,N),(m.F,m.M,m.N))]
            self.assertAlmostEqual(math.dist(states[0],states[1])/math.dist(states[1],states[2]),16/9)

    def test_curve_and_labels_stay_in_graph_area(self):
        for i in range(121):
            m=Configuration(3,2.25+1.75*i/120)
            for j in range(81):
                P=m.curve(-3.8+6.3*j/80)
                self.assertAlmostEqual(P[0]**2/9-P[1]**2/m.b**2,1,places=9)
                x,y,_=screen(P);self.assertTrue(-4<x<4 and -2.5<y<5)

    def test_invalid_parameters(self):
        for a,b in [(0,1),(1,0),(-1,2),(2,-1)]:
            with self.assertRaises(ValueError):Configuration(a,b)


if __name__=='__main__':unittest.main()
