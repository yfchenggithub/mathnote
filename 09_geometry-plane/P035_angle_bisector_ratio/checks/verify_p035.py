"""P035: audit the actual coordinates and angle arcs drawn in the PDF."""
from pathlib import Path
from fractions import Fraction as F
import math,re

ROOT=Path(__file__).resolve().parents[3]

def triangle(p,q,a):
    assert abs(p-q)<a<p+q
    x=(p*p-q*q+a*a)/(2*a)
    return {'A':(x,math.sqrt(p*p-x*x)),'B':(0.,0.),'C':(a,0.),
            'D':(a*p/(p+q),0.)}

def distance(a,b):return math.dist(a,b)
def project(P,A,B):
    v=(B[0]-A[0],B[1]-A[1])
    t=sum((P[i]-A[i])*v[i] for i in (0,1))/sum(z*z for z in v)
    return tuple(A[i]+t*v[i] for i in (0,1))
def close(a,b):
    assert math.isclose(a,b,rel_tol=3e-8,abs_tol=3e-8),(a,b)
def area(A,B,C):return abs((B[0]-A[0])*(C[1]-A[1])-(B[1]-A[1])*(C[0]-A[0]))/2
def audit(p,q,a,m):
    A,B,C,D=[m[k] for k in 'ABCD']
    close(distance(A,B),p);close(distance(A,C),q);close(distance(B,C),a)
    assert 0<D[0]<a and D[1]==0
    close(distance(B,D)/distance(D,C),p/q)
    close(distance(B,D)+distance(D,C),a)
    u=tuple((B[i]-A[i])/p+(C[i]-A[i])/q for i in (0,1))
    close((D[0]-A[0])*u[1]-(D[1]-A[1])*u[0],0)
    close(area(A,B,D)/area(A,C,D),p/q)
    close(distance(D,project(D,A,B)),distance(D,project(D,A,C)))

def verify():
    figs=list((ROOT/'assets/tikz').glob('P035_*.tex'))
    assert len(figs)==12
    for fig in figs:
        s=fig.read_text(encoding='utf-8')
        p,q,a=map(float,re.search(r'% MODEL ([\d.]+) ([\d.]+) ([\d.]+)',s).groups())
        m={k:(float(x),float(y)) for k,x,y in re.findall(r'\\coordinate \((\w+)\) at \(([-\d.]+),([-\d.]+)\);',s)}
        audit(p,q,a,m);A,B,C,D=[m[k] for k in 'ABCD']
        if 'G' in m:
            close(distance(m['G'],project(D,A,B)),0)
            close(distance(m['K'],project(D,A,C)),0)
        if 'H' in m:close(m['H'][0],A[0]);close(m['H'][1],0)
        if 'M' in m:close(m['M'][0],a/2);close(m['M'][1],0)
        if 'E' in m:
            close(distance(A,m['E']),q)
            assert m['E'][1]>A[1]
            close((m['E'][0]-C[0])*(D[1]-A[1])-(m['E'][1]-C[1])*(D[0]-A[0]),0)
        if 'W' in m:close(distance(B,m['W'])/distance(m['W'],C),q/p)
        if 'X' in m:
            assert m['X'][0]>a
            close(distance(B,m['X'])/distance(m['X'],C),p/q)
        if 'A0' in m:
            close(distance(m['A0'],m['B0']),9)
            close(distance(m['A0'],m['C0']),6)
            close(distance(m['B0'],m['C0']),15)
            close(area(m['A0'],m['B0'],m['C0']),0)
        arcs=list(map(float,re.findall(r'delta angle=([-\d.]+)',s)))
        if fig.stem in ['P035_weighted_split','P035_equal_distances','P035_parallel_proof']:
            assert len(arcs)==2;close(arcs[0],arcs[1])
        if fig.stem=='P035_sine_proof':
            assert len(arcs)==4
            close(arcs[0],arcs[1]);close(arcs[2]+arcs[3],180)
    n=0
    for p in range(2,17):
        for q in range(2,17):
            for a in range(abs(p-q)+1,p+q):audit(p,q,a,triangle(p,q,a));n+=1
    assert F(10*9,9+6)==6 and F(10*6,9+6)==4
    assert 9+6==15 and not abs(9-6)<15<9+6
    assert F(10,6)==F(15,9) and 10-6==4 and 10+6==16
    assert 5*5+12*12==13*13 and F(12*5,5+13)==F(10,3)
    assert F(10,3)/F(26,3)==F(5,13)
    print(f'PASS: {len(figs)} actual figure models; {n} triangle cases; converse, exact examples and degeneracy checks.')

if __name__=='__main__':verify()
