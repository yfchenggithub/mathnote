"""Independent coordinate/length checks for the P036 PDF figures.

Run from any cwd. Sampling is a regression check, not a replacement for proof.
"""
from pathlib import Path
from fractions import Fraction as F
import math
import re

ROOT = Path(__file__).resolve().parents[3]


def model(p, q, a):
    assert abs(p-q) < a < p+q
    x = (p*p-q*q+a*a)/(2*a)
    y = math.sqrt(p*p-x*x)
    return {'A': (x, y), 'B': (0., 0.), 'C': (a, 0.),
            'D': (a*p/(p-q), 0.)} if p != q else {
                'A': (x, y), 'B': (0., 0.), 'C': (a, 0.)}


def distance(p, q):
    return math.hypot(p[0]-q[0], p[1]-q[1])


def projection(p, a, b):
    v = (b[0]-a[0], b[1]-a[1])
    t = ((p[0]-a[0])*v[0]+(p[1]-a[1])*v[1])/(v[0]**2+v[1]**2)
    return a[0]+t*v[0], a[1]+t*v[1]


def area(a, b, c):
    return abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2


def near(a, b):
    assert math.isclose(a, b, rel_tol=2e-8, abs_tol=2e-8), (a, b)


def check_model(p, q, a, m):
    A, B, C = [m[k] for k in 'ABC']
    near(distance(A,B), p); near(distance(A,C), q); near(distance(B,C), a)
    if p == q:
        near(A[0], a/2)
        return
    D = m['D']
    bd, cd = distance(B,D), distance(C,D)
    near(bd/cd, p/q); near(abs(bd-cd), a)
    assert (D[0] > a) if p > q else (D[0] < 0)
    M, N = projection(D,A,B), projection(D,A,C)
    near(distance(D,M), distance(D,N))
    near(area(A,B,D)/area(A,C,D), bd/cd)
    near(area(A,B,D)/area(A,C,D), p/q)
    # External direction: difference of the two unit side vectors.
    w = ((B[0]-A[0])/p-(C[0]-A[0])/q,
         (B[1]-A[1])/p-(C[1]-A[1])/q)
    near((D[0]-A[0])*w[1]-(D[1]-A[1])*w[0], 0)
    # At D the rays to B and C point the SAME way.
    near((B[0]-D[0])*(C[1]-D[1])-(B[1]-D[1])*(C[0]-D[0]), 0)
    assert (B[0]-D[0])*(C[0]-D[0])+(B[1]-D[1])*(C[1]-D[1]) > 0


def verify():
    figs = list((ROOT/'assets/tikz').glob('P036_*.tex'))
    assert len(figs) == 10
    checked = 0
    for fig in figs:
        text = fig.read_text(encoding='utf-8')
        match = re.search(r'% MODEL ([\d.]+) ([\d.]+) ([\d.]+)', text)
        if not match:
            assert fig.stem == 'P036_near_isosceles'
            continue
        p,q,a = map(float, match.groups())
        m = {name:(float(x),float(y)) for name,x,y in re.findall(
            r'\\coordinate \((\w+)\) at \(([-\d.]+),([-\d.]+)\);', text)}
        check_model(p,q,a,m)
        A,B,C = [m[k] for k in 'ABC']
        if 'M' in m:
            for foot, end in [('M',B),('N',C)]:
                point=projection(m['D'],A,end)
                near(distance(point,m[foot]),0)
        if 'F' in m:
            near(distance(A,m['F']),q)
            near((m['F'][0]-C[0])*(m['D'][1]-A[1])-
                 (m['F'][1]-C[1])*(m['D'][0]-A[0]),0)
        if 'E' in m:
            near(distance(B,m['E'])/distance(C,m['E']),p/q)
            near(sum((m['D'][i]-A[i])*(m['E'][i]-A[i]) for i in (0,1)),0)
        if 'W' in m:
            near(distance(B,m['W'])/distance(C,m['W']),q/p)
            assert m['W'][0] < 0 < C[0] < m['D'][0]
        if 'H' in m:
            near(m['H'][0],A[0]);near(m['H'][1],0)
        # Read the actual drawn arc angles, rather than just their labels.
        arcs=list(map(float,re.findall(r'delta angle=([-\d.]+)',text)))
        if fig.stem in ['P036_left_external','P036_right_external',
                        'P036_area_from_d','P036_parallel_proof']:
            assert len(arcs)==2
            near(arcs[0],arcs[1])
        if fig.stem=='P036_sine_angles':
            assert len(arcs)==3
            near(arcs[0]+arcs[1],180)
        checked += 1
    samples=0
    for p in range(2,17):
        for q in range(2,17):
            for a in range(abs(p-q)+1,p+q):
                check_model(p,q,a,model(p,q,a));samples+=1
    # Exact arithmetic for all three examples, including point order.
    assert F(4,6)==F(8,12) and 12-8==4 and abs(6-4)<4<6+4
    assert F(5,3)==F(10,6) and 10-6==4
    assert F(4,2)==F(2,1)==F(6,3) and 6-2==4
    # Signed segment convention: B=0,C=a, oriented BD/DC < 0 externally.
    for p,q,a in [(4,6,4),(5,3,4),(6,4,5)]:
        d=F(a*p,p-q)
        assert d/F(a-d)==-F(p,q)
    print(f'PASS: {checked} figure coordinate models; {samples} triangle cases; exact examples and signed ratios.')


if __name__ == '__main__':
    verify()
