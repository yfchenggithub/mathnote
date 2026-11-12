import numpy as np

GENERAL=np.array([-1.5,3.8,0.])
EQUILATERAL=np.array([0.,-.7+2.6*np.sqrt(3),0.])
RIGHT_TRIANGLE=np.array([-2.6,3.2,0.])

def centers(A):
    V=np.array([A,[-2.6,-.7,0.],[2.6,-.7,0.]])
    a,b,c=[np.linalg.norm(V[(j+1)%3]-V[(j+2)%3]) for j in range(3)]
    weights=np.array([a,b,c])/(a+b+c)
    G=V.mean(axis=0); I=weights@V
    r=I[1]+.7
    return V,weights,G,I,r

def blended_point(A,t):
    V,w,G,I,r=centers(A)
    weights=(1-t)*np.ones(3)/3+t*w
    return weights@V
