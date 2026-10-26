import math,json
from pathlib import Path

def eq(a,b):
    assert math.isclose(a,b,rel_tol=2e-10,abs_tol=2e-10),(a,b)

maps=[lambda x,y:(x,y),lambda x,y:(-x,y),lambda x,y:(y,x),lambda x,y:(y,-x)]
states=0
for p in [.5,2,6]:
    for deg in range(1,180):
        theta=math.radians(deg);dx,dy=math.cos(theta),math.sin(theta)
        # Independently solve intersection F+t*(dx,dy) with y^2=2px.
        a,b,c=dy*dy,-2*p*dx,-p*p
        root=math.sqrt(b*b-4*a*c)
        q=-.5*(b+math.copysign(root,b))
        ts=sorted([q/a,c/q],reverse=True)
        assert ts[0]>0>ts[1]
        for transform in maps:
            focus=transform(p/2,0)
            points=[transform(p/2+t*dx,t*dy) for t in ts]
            r,s=[math.dist(focus,q) for q in points]
            eq(1/r+1/s,2/p);eq(2*r*s,p*(r+s))
            assert r>p/2 and s>p/2 and r+s>=2*p-1e-9
            eq(s*(2*r-p),p*r) # Cross multiplication avoids amplification near the asymptote.
            for t in ts: eq(abs(t),p+t*dx)
            states+=1

# Pure geometry: arbitrary similar right triangles, then diagram coordinates.
for alpha in [15,30,60,80]:
    for r,s in [(4,4/3),(2,5),(7,3)]:
        u,v=r*math.cos(math.radians(alpha)),s*math.cos(math.radians(alpha))
        eq(u/r,v/s)
F=(2,0);A=(4,math.sqrt(12));B=(4/3,-math.sqrt(4/3))
eq(math.dist(A,F),4);eq(math.dist(B,F),4/3)
for x,y in [A,B]:eq(y*y,4*(x-1));eq(math.dist((x,y),F),x)
for transform in maps:
    f=transform(1,0);a=transform(3,math.sqrt(12));b=transform(1/3,-math.sqrt(4/3))
    eq(math.dist(f,a),4);eq(math.dist(f,b),4/3)

# Numerical examples, including transfer exercise.
for p,r,s in [(2,3,1.5),(4,8,8/3),(2,4,4/3),(6,5,7.5),(3,3,3)]:
    eq(1/r+1/s,2/p)
eq(8+8/3,32/3);eq(5+7.5,25/2)
eq(1+0,1) # p=2,r=1 would force reciprocal of s to be zero.
eq(math.hypot(2-1,math.sqrt(8)),3) # Ordinary vertical chord counterexample.
for r in [1.01,1.2,2,3,7.5,100]:
    s=r/(r-1);eq(1/r+1/s,1);assert s>1

# Coordinate and parameter proofs.
for p in [.5,2,6]:
    for m in [-5,-1,0,.3,4]:
        ys=[p*m+p*math.sqrt(m*m+1),p*m-p*math.sqrt(m*m+1)]
        rs=[m*y+p for y in ys]
        eq(sum(rs),2*p*(1+m*m));eq(math.prod(rs),p*p*(1+m*m))
    for t in [-4,-.2,.3,1,8]:
        t2=-1/t;eq(t*t2,-1)
        eq(2/p/(1+t*t)+2/p/(1+t2*t2),2/p)

base=Path('03_conic/C054_parabola_focal_chord_reciprocal_sum')
json.loads((base/'meta.json').read_text(encoding='utf8'))
figures=['pure_similarity','parabola_similarity','reciprocal_comparison','length_pair_domain','validity_comparison','four_openings']
for stem in figures:
    txt=Path(f'assets/tikz/C054_{stem}.tex').read_text(encoding='utf8')
    assert '\\tiny' not in txt and '\\scriptsize' not in txt
proof=(base/'03_proof.tex').read_text(encoding='utf8')
assert proof.count('begin{proofbox}')==4
examples=(base/'04_examples.tex').read_text(encoding='utf8')
for marker in ['例1','例2','例3','例4','例5','迁移训练']:assert marker in examples
result={'status':'PASS','intersection_states':states,'openings':4,'parameter_values':[.5,2,6],'angles_degrees':'1..179','figures':6,'proofs':4,'examples':5,'transfer_exercises':1}
Path('.tmp/C054_tikz_review/math_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
