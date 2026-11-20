"""F015 exact symmetry partners; source functions x^2 and x^3."""
def even(x):return x*x
def odd(x):return x*x*x
def pairs(t):return {'even':[(t,even(t)),(-t,even(-t))],'odd':[(t,odd(t)),(-t,odd(-t))]}
def decompose(x):
 f=lambda z:z*z+3*z+2
 return (f(x)+f(-x))/2,(f(x)-f(-x))/2
