"""V009: nondegenerate triangle, incenter and perpendicular feet."""
import numpy as np

def geometry(t=0):
    A = np.array([-0.7 + 1.65*np.sin(t), 3.9-0.65*(1-np.cos(t)), 0.])
    B = np.array([-3., -0.8, 0.])
    C = np.array([3., -0.8, 0.])
    vertices = [A, B, C]
    sides = np.array([np.linalg.norm(C-B), np.linalg.norm(A-C), np.linalg.norm(B-A)])
    I = sum(s*p for s,p in zip(sides, vertices))/sum(sides)
    feet = []
    for P,Q in [(B,C),(C,A),(A,B)]:
        feet.append(P+np.dot(I-P,Q-P)/np.dot(Q-P,Q-P)*(Q-P))
    r = np.linalg.norm(I-feet[0])
    return vertices, sides, I, feet, r
