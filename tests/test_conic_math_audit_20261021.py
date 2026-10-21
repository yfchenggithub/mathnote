"""Independent geometric regression checks for the October 2026 source repairs.

Run: .venv-manim/Scripts/python.exe -B -m unittest discover -s tests
     -p test_conic_math_audit_20261021.py
No renderer or animation model is imported: distances and intersections are
reconstructed from the original curve equations.
"""
import json
import math
import re
from fractions import Fraction as F
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ConicMathAudit(unittest.TestCase):
    def close(self, a, b, tol=1e-9):
        self.assertLessEqual(abs(a-b), tol*max(1, abs(a), abs(b)))

    def test_right_focus_chord_orientation_and_curve_residuals(self):
        for a,b in ((5,3),(2,math.sqrt(3)),(3,2),(1,.15)):
            c=math.sqrt(a*a-b*b)
            for j in range(181):
                theta=j*math.pi/181
                u=(math.cos(theta),math.sin(theta))
                # Quadratic roots reconstructed directly from the ellipse.
                qa=u[0]**2/a**2+u[1]**2/b**2
                qb=2*c*u[0]/a**2
                qc=c*c/a**2-1
                discr=qb*qb-4*qa*qc
                tpos=(-qb+math.sqrt(discr))/(2*qa)
                tneg=(-qb-math.sqrt(discr))/(2*qa)
                self.assertGreater(tpos,0);self.assertLess(tneg,0)
                for t in (tpos,tneg):
                    x,y=c+t*u[0],t*u[1]
                    self.close(x*x/a**2+y*y/b**2,1)
                self.close(tpos,b*b/(a+c*u[0]))
                self.close(-tneg,b*b/(a-c*u[0]))
                self.close(tpos/-tneg,(1-c/a*u[0])/(1+c/a*u[0]))

    def test_focal_angle_and_focal_radius_distance_product(self):
        for a,b in ((5,3),(2,math.sqrt(3)),(3,2)):
            c=math.sqrt(a*a-b*b)
            for j in range(1,360):
                t=j*math.pi/180;x,y=a*math.cos(t),b*math.sin(t)
                r1,r2=math.hypot(x+c,y),math.hypot(x-c,y)
                dot=(c*c-x*x-y*y)*-1 # (F1-P) dot (F2-P)
                cosangle=max(-1,min(1,dot/(r1*r2)))
                theta=math.acos(cosangle)
                self.close(math.tan(theta/2),c*abs(y)/b**2,2e-8)
                d=1/math.hypot(x/a**2,y/b**2)
                self.close(math.sqrt(r1*r2)*d,a*b)

    def test_optical_internal_bisectors_using_oriented_unit_rays(self):
        for j in range(1,180):
            t=j*math.pi/180
            # Ellipse normal must be parallel to unit focal ray sum.
            x,y=2*math.cos(t),math.sqrt(3)*math.sin(t)
            u=((-1-x)/math.hypot(x+1,y),-y/math.hypot(x+1,y))
            v=((1-x)/math.hypot(x-1,y),-y/math.hypot(x-1,y))
            self.close((u[0]+v[0])*y/3-(u[1]+v[1])*x/4,0)
        for branch in (-1,1):
            for j in (-20,-10,-1,1,10,20):
                t=j/10;x,y=branch*math.cosh(t),math.sqrt(3)*math.sinh(t)
                u=((-2-x)/math.hypot(x+2,y),-y/math.hypot(x+2,y))
                v=((2-x)/math.hypot(x-2,y),-y/math.hypot(x-2,y))
                self.close((u[0]+v[0])*x-(u[1]+v[1])*y/3,0)
        for p in (.5,2,5):
            for j in range(-30,31):
                y=j/5;x=y*y/(2*p);r=math.hypot(p/2-x,y)
                u=((p/2-x)/r,-y/r);h=(1,0)
                # unit ray sum is normal, orthogonal to the actual derivative.
                self.close((u[0]+h[0])*y+(u[1]+h[1])*p,0)
                if j:
                    tangent=(y,p)
                    self.assertGreater(abs((u[0]+1)*tangent[1]-u[1]*tangent[0]),1e-9)

    def test_hyperbola_midpoint_existence_and_branch_classification(self):
        a,b=2.,3.
        for ix in range(-20,21):
            for iy in range(-20,21):
                if not iy:continue
                x0,y0=ix/5,iy/5
                q=x0*x0/a**2-y0*y0/b**2
                k=b*b*x0/(a*a*y0);m=y0-k*x0
                qa=1/a**2-k*k/b**2;qb=-2*k*m/b**2;qc=-m*m/b**2-1
                disc=qb*qb-4*qa*qc
                exists=q< -1e-10 or q>1+1e-10
                self.assertEqual(disc>1e-9 and abs(qa)>1e-10,exists)
                if exists:
                    x1=(-qb+math.sqrt(disc))/(2*qa);x2=(-qb-math.sqrt(disc))/(2*qa)
                    y1,y2=k*x1+m,k*x2+m
                    self.close((x1+x2)/2,x0);self.close((y1+y2)/2,y0)
                    self.assertEqual(x1*x2<0,q<0)
        self.assertTrue(0 < F(2)**2/4-F(1)**2/9 < 1)
        self.assertTrue(0 < F(1,5)**2/4-F(1,5)**2/9 < 1)
        # Slopes 2 through Q=(1,2) do not make a central chord.
        self.assertLess(1/4-4/9,0)

    def test_contact_chord_existence_including_asymptote_and_vertex(self):
        # Count real contacts by solving the polar with the original hyperbola.
        a,b=2.,3.
        for ix in range(-12,13):
            for iy in range(-12,13):
                x0,y0=ix/4,iy/4;q=x0*x0/a**2-y0*y0/b**2
                if abs(y0)>1e-12:
                    k=b*b*x0/(a*a*y0);m=-b*b/y0
                    qa=1/a**2-k*k/b**2;qb=-2*k*m/b**2;qc=-m*m/b**2-1
                    if abs(qa)<1e-10:count=1 if abs(qb)>1e-10 else 0
                    else:
                        discr=qb*qb-4*qa*qc
                        count=2 if discr>1e-9 else 1 if abs(discr)<1e-9 else 0
                elif x0:
                    yy=b*b*((a*a/x0)**2/a**2-1)
                    count=2 if yy>1e-9 else 1 if abs(yy)<1e-9 else 0
                else:count=0
                self.assertEqual(count==2,q<1-1e-10 and abs(q)>1e-10)
        for p in (1,2,3):
            for x0,y0 in ((-1,0),(1,0),(0,0),(1,2),(3,-1)):
                disc=(-2*y0)**2-4*2*p*x0
                self.assertEqual(disc>0,y0*y0-2*p*x0>0)

    def test_corrected_numeric_examples(self):
        self.assertEqual(1/(F(1,2)/4),8)
        for x,y in ((F(3),F(5,2)),(F(-3),F(-5,2))):
            self.assertEqual(x*x/4-y*y/5,1)
            self.assertEqual(y/(x+2)+y/(x-2),3)
        self.assertEqual(F(3,2)**2/3+F(1,4),1)
        # Midpoints with slope 2 on y²=4x cover exactly x>1/4.
        for t in (.01,.2,1,10):
            y1,y2=1+t,1-t;x1,x2=y1*y1/4,y2*y2/4
            self.assertGreater((x1+x2)/2,.25)
            self.close((y1-y2)/(x1-x2),2)

    def test_asymptote_parallel_unique_point(self):
        for a,b in ((2,3),(3,1),(1,2)):
            for d in (-3,-.2,.5,4):
                for sign in (-1,1):
                    x=-a*(b*b+d*d)/(2*sign*b*d);y=sign*b/a*x+d
                    self.close(x*x/a**2-y*y/b**2,1)

    def test_parabola_four_openings_and_noncoincident_midpoint_line(self):
        for p in (.5,2,5):
            for m in (-3,-1,0,2):
                y1=p*m+p*math.sqrt(m*m+1);y2=p*m-p*math.sqrt(m*m+1)
                x1,x2=y1*y1/(2*p),y2*y2/(2*p)
                self.close(x1*x2,p*p/4);self.close(y1*y2,-p*p)
                self.close(1/(x1+p/2)+1/(x2+p/2),2/p)
                self.close((p/y1)*(p/y2),-1)
                xM=y1*y2/(2*p);xN=(x1+x2)/2
                self.close(xN-xM,(y1-y2)**2/(4*p))
                self.assertGreater(xN-xM,0)
                # Reflection and swapping axes preserve all lengths/products.
                self.close((-x1)*(-x2),p*p/4)

    def test_ramanujan_rounding_and_independent_arc_integral(self):
        def approx(a,b):
            h=((a-b)/(a+b))**2
            return math.pi*(a+b)*(1+3*h/(10+math.sqrt(4-3*h)))
        for a,b,expected in ((5,3,25.527),(5,4,28.362),(10,6,51.054),(9,7,50.462)):
            self.assertEqual(round(approx(a,b),3),expected)
            # Composite Simpson integration is independent of the approximation.
            n=20000;step=(math.pi/2)/n
            def f(i):return math.hypot(a*math.sin(i*step),b*math.cos(i*step))
            exact=4*step/3*(f(0)+f(n)+4*sum(f(i) for i in range(1,n,2))+2*sum(f(i) for i in range(2,n,2)))
            self.assertLess(abs(approx(a,b)-exact)/exact,1e-9)
        self.close(1-14*math.pi/44,.0004023374941569)

    def test_confocal_signed_denominators(self):
        a,b=5,3;c=4
        for lam in (-24,-20,-10,-8,0,15):
            dx,dy=a*a+lam,b*b+lam
            self.assertGreater(dx,0);self.assertNotEqual(dy,0)
            self.close(dx-dy,c*c)
            if dy<0:self.close(math.sqrt(dx+(-dy)),c)
            else:self.close(math.sqrt(dx-dy),c)

    def test_actual_tikz_tangent_segments_match_their_contact_points(self):
        source=(ROOT/'assets/tikz/C073_math_audit_geometry.tex').read_text(encoding='utf-8')
        segments=re.findall(r'\\draw\[orange,thick\] \(([^)]+)\)--\(([^)]+)\);',source)
        self.assertEqual(len(segments),2)
        matched=[]
        for start,end in segments:
            x1,y1=map(float,start.split(','));x2,y2=map(float,end.split(','))
            k=(y2-y1)/(x2-x1);m=y1-k*x1
            # Independently recover contact coordinate on y²=4x from slope.
            y0=2/k;x0=y0*y0/4
            self.close(y0,k*x0+m)
            matched.append((round(x0,8),round(y0,8)))
        self.assertEqual(set(matched),{(1.,2.),(1.,-2.)})
        for uid in (59,60):
            source=(ROOT/f'assets/tikz/C{uid:03d}_math_audit_geometry.tex').read_text(encoding='utf-8')
            segments=re.findall(r'\\draw\[(?:teal,thick|orange,dashed,thick)\] \(([^)]+)\)--\(([^)]+)\);',source)
            self.assertEqual(len(segments),2)
            for start,end in segments:
                x1,y1=map(float,start.split(','));x2,y2=map(float,end.split(','))
                self.close(x1*x1/4+y1*y1,1)
                self.close(x2*x2/4+y2*y2,1)
                self.close(x1+x2,0);self.close(y1+y2,0)

    def test_all_83_metadata_parse_and_corrected_source_search_formulas(self):
        folders=sorted((ROOT/'03_conic').glob('C[0-9][0-9][0-9]_*'))
        self.assertEqual(len(folders),83)
        for path in folders:json.loads((path/'meta.json').read_text(encoding='utf-8'))
        c3=json.loads(next((ROOT/'03_conic').glob('C003_*')).joinpath('meta.json').read_text(encoding='utf-8'))
        self.assertNotIn('c/y',json.dumps(c3))
        c74=json.loads(next((ROOT/'03_conic').glob('C074_*')).joinpath('meta.json').read_text(encoding='utf-8'))
        self.assertNotIn('抛物线切线平分',json.dumps(c74,ensure_ascii=False))


if __name__ == '__main__':
    unittest.main(verbosity=2)
