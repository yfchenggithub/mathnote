"""Independent checks of C032 formulas, actual TikZ coordinates and examples.

Sampling cross-checks the general proofs; it does not replace those proofs.
Run from any working directory with Python's standard library only.
"""
from pathlib import Path
from fractions import Fraction as F
import math
import re
import json

ROOT = Path(__file__).resolve().parents[3]
UID = ROOT / '03_conic/C032_apollonius_circle_ratio'

def close(a, b):
    assert math.isclose(a, b, rel_tol=2e-8, abs_tol=2e-8), (a, b)

def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def norm2(a): return dot(a,a)
def ratio(P,A,B,k):
    assert math.dist(P,B)>1e-9
    close(math.dist(P,A)/math.dist(P,B),k)

def verify():
    paths=sorted((ROOT/'assets/tikz').glob('C032_*.tex'))
    assert len(paths)==13
    for path in paths:
        s=path.read_text(encoding='utf-8')
        m={k:(float(x),float(y)) for k,x,y in re.findall(
            r'\\coordinate \((\w+)\) at \(([-\d.]+),([-\d.]+)\);',s)}
        A,B=m['A'],m['B']
        if 'unit_ratio' in path.name:
            ratio(m['P'],A,B,1);continue
        if 'coordinate_proof' in path.name:
            P,H=m['P'],m['H']
            ratio(P,A,B,2)
            close(P[0],H[0]);close(H[1],0)
            close(math.dist(P,A)**2,(P[0]+1)**2+P[1]**2)
            close(math.dist(P,B)**2,(P[0]-1)**2+P[1]**2)
            assert A[0]<B[0]<H[0] and P[1]>0
            continue
        C=m['C'];r=math.dist(A,B)*2/3
        if 'center_radius_quick' in path.name:
            close(math.dist(C,A)/math.dist(C,B),4)
            close(r*r,math.dist(C,A)*math.dist(C,B))
            close((8.4-5.0666666667)/1.25,math.dist(C,A))
            close((8.4-7.5666666667)/1.25,math.dist(C,B))
        close(C[0],(A[0]-4*B[0])/-3)
        close(C[1],(A[1]-4*B[1])/-3)
        for k in ('P','Q','D','E','U','V'):
            if k in m:
                ratio(m[k],A,B,2);close(math.dist(m[k],C),r)
        radii=[float(x) for x in re.findall(r'\(C\) circle \(([\d.]+)\)',s)]
        if 'projection_proof' not in path.name and 'vector_proof' not in path.name:
            assert radii
        for value in radii: close(value,r)
        if 'projection_proof' in path.name:
            H,P=m['H'],m['P']
            close(H[0],P[0]);close(H[1],0)
            t=dot(sub(P,C),sub(A,C))/math.dist(C,A)
            close(t,math.dist(C,H))
            close(math.dist(P,A)**2,math.dist(P,C)**2+math.dist(C,A)**2-2*math.dist(C,A)*t)
            close(math.dist(P,B)**2,math.dist(P,C)**2+math.dist(C,B)**2-2*math.dist(C,B)*t)
        if 'vector_proof' in path.name:
            for i in (0,1):
                close(A[i]-C[i],4*(B[i]-C[i]))
                close(m['P'][i]-A[i],(m['P'][i]-C[i])-(A[i]-C[i]))
                close(m['P'][i]-B[i],(m['P'][i]-C[i])-(B[i]-C[i]))
        if 'D' in m and 'E' in m:
            D,E=m['D'],m['E']
            close(math.dist(D,E)/2,r)
            for i in (0,1): close((D[i]+E[i])/2,C[i])
        if 'bisectors' in path.name:
            P=m['P'];v=sub(m['D'],P);w=sub(m['E'],P)
            close(dot(v,w),0)
            inner=tuple(sub(A,P)[i]/math.dist(A,P)+sub(B,P)[i]/math.dist(B,P) for i in (0,1))
            close(v[0]*inner[1]-v[1]*inner[0],0)
            close(sub(m['T'],P)[0]*sub(P,A)[1]-sub(m['T'],P)[1]*sub(P,A)[0],0)
            assert dot(sub(m['T'],P),sub(P,A))>0
            arcs=[tuple(map(float,groups)) for groups in re.findall(
                r'\(([-\d.]+),([-\d.]+)\) arc\[start angle=([-\d.]+),delta angle=([-\d.]+),radius=([-\d.]+)\]',s)]
            assert len(arcs)==4
            for (x,y,a,delta,radius),(start,end) in zip(arcs,[('A','D'),('D','B'),('B','E'),('E','T')]):
                close(x,P[0]+radius*math.cos(math.radians(a)))
                close(y,P[1]+radius*math.sin(math.radians(a)))
                for theta,key in [(a,start),(a+delta,end)]:
                    v=sub(m[key],P);close(math.cos(math.radians(theta)),v[0]/math.hypot(*v));close(math.sin(math.radians(theta)),v[1]/math.hypot(*v))
            close(arcs[0][3],arcs[1][3]);close(arcs[2][3],arcs[3][3]);close(arcs[0][3]+arcs[2][3],90)
        if 'reciprocal' in path.name:
            assert '(-1.6666666667,0) circle (1.3333333333)' in s
            for t in range(0,360,10):
                ratio((-5/3+4/3*math.cos(math.radians(t)),4/3*math.sin(math.radians(t))),A,B,.5)
        if 'circle_not_disk' in path.name: ratio(C,A,B,4)
        if 'intersection' in path.name:
            close(m['U'][0],m['U'][1]);close(m['V'][0],m['V'][1])
            assert m['U'][0]<m['V'][0]
    samples=0
    for A,B in [((-1,0),(1,0)),((0,0),(4,2)),((-3,2),(2,-4))]:
        L=math.dist(A,B)
        for k in (.1,.5,.9,1.1,2.,10.):
            C=tuple((A[i]-k*k*B[i])/(1-k*k) for i in (0,1));r=k*L/abs(1-k*k)
            for deg in range(360):
                P=(C[0]+r*math.cos(math.radians(deg)),C[1]+r*math.sin(math.radians(deg)))
                ratio(P,A,B,k);samples+=1
            for P in [(0,0),(2,3),(-4,1)]:
                close(norm2(sub(P,A))-k*k*norm2(sub(P,B)),(1-k*k)*(norm2(sub(P,C))-r*r))
            # Signed projection identities must also hold beyond both endpoints.
            direction=tuple((A[i]-C[i])/math.dist(A,C) for i in (0,1))
            for t0 in (-5.,0.,.2,3.,20.):
                P=tuple(C[i]+t0*direction[i]+.7*(-direction[1] if i==0 else direction[0]) for i in (0,1))
                t=dot(sub(P,C),direction)
                close(t,t0)
                ph2=norm2(sub(P,C))-t*t
                close(ph2,.49)
                close(norm2(sub(P,A)),(math.dist(C,A)-t)**2+ph2)
                close(norm2(sub(P,B)),(math.dist(C,B)-t)**2+ph2)
                close(-2*math.dist(C,A)*t+2*k*k*math.dist(C,B)*t,0)
            D=tuple((A[i]+k*B[i])/(1+k) for i in (0,1))
            E=tuple((A[i]-k*B[i])/(1-k) for i in (0,1))
            ratio(D,A,B,k);ratio(E,A,B,k)
            close(math.dist(D,E),2*r)
            for i in (0,1): close((D[i]+E[i])/2,C[i])
        midpoint=tuple((A[i]+B[i])/2 for i in (0,1));v=sub(B,A)
        for t in (-2,0,3):
            P=(midpoint[0]-t*v[1],midpoint[1]+t*v[0]);ratio(P,A,B,1)
    k=F(2);a=F(1);D=a*(k-1)/(k+1);E=a*(k+1)/(k-1)
    assert D==F(1,3) and E==3 and (D+E)/2==F(5,3) and (E-D)/2==F(4,3)
    assert F(16,3)**2+F(8,3)**2-F(80,3)==F(80,9)
    ca,cb,t,ph=F(8,3),F(2,3),F(16,15),F(4,5)
    assert (ca-t)**2+ph**2==F(16,5)
    assert (cb-t)**2+ph**2==F(4,5)
    assert t*t+ph*ph==ca*cb==F(16,9)
    meta=json.loads((UID/'meta.json').read_text(encoding='utf-8'))
    refs=re.findall(r'assets/tikz/C032_[a-z_]+\.tex',meta['remarks'])
    assert len(refs)==13 and all((ROOT/p).is_file() for p in refs)
    assert meta['meta']['updated_at']=='2026-10-28' and meta['interactive']['has_diagram'] is True
    for rid in meta['relations']['related_ids']: assert len(list((ROOT/'03_conic').glob(rid+'_*')))==1
    proof=(UID/'03_proof.tex').read_text(encoding='utf-8')
    for name in ['coordinate_proof','projection_proof','bisectors','vector_proof']:
        assert f'assets/tikz/C032_{name}.tex' in proof
    print(f'PASS: 13 actual TikZ models, projections, vectors and angle arcs; {samples} sampled circle points; general identity, endpoints, examples, unit ratio, proof coverage and metadata.')

if __name__=='__main__':verify()
