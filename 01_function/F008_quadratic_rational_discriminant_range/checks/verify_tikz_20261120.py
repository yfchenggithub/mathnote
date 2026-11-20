"""Dependency-free exact Fraction/quadratic-field audit of F008 diagrams."""
from dataclasses import dataclass
from fractions import Fraction as Q
from pathlib import Path
import argparse,json
@dataclass(frozen=True)
class Surd:
 a: Q
 b: Q
 rad: int=5
 def __post_init__(self):
  object.__setattr__(self,'a',Q(self.a));object.__setattr__(self,'b',Q(self.b))
 def coerce(self,v):
  if isinstance(v,Surd):assert self.rad==v.rad;return v
  return Surd(v,0,self.rad)
 def __add__(self,v):
  v=self.coerce(v);return Surd(self.a+v.a,self.b+v.b,self.rad)
 __radd__=__add__
 def __neg__(self):return Surd(-self.a,-self.b,self.rad)
 def __sub__(self,v):return self+-self.coerce(v)
 def __rsub__(self,v):return self.coerce(v)+-self
 def __mul__(self,v):
  v=self.coerce(v);return Surd(self.a*v.a+self.rad*self.b*v.b,self.a*v.b+self.b*v.a,self.rad)
 __rmul__=__mul__
 def __truediv__(self,v):
  v=self.coerce(v);norm=v.a*v.a-self.rad*v.b*v.b;assert norm
  return self*Surd(v.a/norm,-v.b/norm,self.rad)
 def __rtruediv__(self,v):return self.coerce(v)/self
 def __pow__(self,n):
  assert n>=0 and isinstance(n,int);v=Surd(1,0,self.rad)
  for _ in range(n):v=v*self
  return v
 def __eq__(self,v):
  v=self.coerce(v);return self.a==v.a and self.b==v.b
F=lambda x:(x*x+1)/(x*x+2*x+2)
D=lambda x:x*x+2*x+2
G=lambda x:(3*x*x+2*x+1)/(x*x+x+1)
s5=Surd(0,1);L=(3-s5)/2;U=(3+s5)/2;r=(s5-1)/2;t=-(s5+1)/2
labels=[]
def check(label,condition):assert condition,label;labels.append(label)
for root,bound in [(r,L),(t,U)]:
 check('attained standard boundary',F(root)==bound)
 X=D(root);Y=root*root+1
 check('tangent ray through point',Y==bound*X)
 check('tangent ray direction',2*root==bound*(2*root+2))
for sign in [-1,1]:
 pu=sign/s5;pv=sign*2/s5
 check('circle tangent point norm',pu*pu+pv*pv==1)
 check('circle endpoint inverse',pv/(1-pu)-1==(r if sign==1 else t))
s3=Surd(0,1,3)
for root,bound in [(-2+s3,2-2*s3/3),(-2-s3,2+2*s3/3)]:
 check('example three exact boundary',G(root)==bound)
 check('example three derivative numerator',root*root+4*root+1==0)
check('example three y=3',G(Q(-2))==3)
check('3-4-5 right triangle',3**2+4**2==5**2)
for i in range(-240,241):
 x=Q(i,20);q=D(x);v=(2*x+2)/q;u=(q-2)/q
 assert q>0
 assert u*u+v*v==1 and F(x)==Q(3,2)-u/2-v
 assert v/(1-u)-1==x and 1-u>0
 assert (q-(x*x+1)-1)**2==4*x*x
 assert F(x)-L==(1-L)*(x-r)**2/q
 assert U-F(x)==(U-1)*(x-t)**2/q
 assert (2*x*x+3)/(x*x+1)==2+1/(x*x+1)
 assert ((x*x-1)/(x*x+1))**2+(2*x/(x*x+1))**2==1
 assert (2*x*x+3)/(x*x+1)==Q(5,2)-Q(1,2)*(x*x-1)/(x*x+1)
 assert (2*x*x+2)/(x*x+1)==2
 assert (x*x+1)-q==-2*x-1
# Polynomial coefficient expansion in y using exact rational arithmetic.
def mul(a,b):
 c=[Q(0)]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):c[i+j]+=x*y
 return c
for k in range(-12,13):
 a,b,c,d,e,f=[Q(k+z,z+1) for z in range(6)]
 p=mul([b,-e],[b,-e]);q=mul([a,-d],[c,-f]);actual=[p[i]-4*q[i] for i in range(3)]
 assert actual==[b*b-4*a*c,4*a*f+4*c*d-2*b*e,e*e-4*d*f]
check('single crossing coordinates',D(Q(-1,2))==Q(5,4) and F(Q(-1,2))==1)
check('single crossing slope differs',(2*Q(-1,2))/(2*Q(-1,2)+2)==-1)
check('ray start and equation',(Q(0)**2+1)==1 and (2*Q(0)**2+2)==2)
p=argparse.ArgumentParser();p.add_argument('--report',required=True);args=p.parse_args()
r={'status':'PASS','exact_quadratic_field_checks':len(labels),'labels':labels,'exact_rational_parameter_samples':481,'exact_discriminant_coefficient_samples':25,'proof_audit':'General symbolic derivations reviewed manually; exact arithmetic checks supplement the proof.','dependencies':'Python standard library only; no SymPy required.'}
Path(args.report).write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r))
