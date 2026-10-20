from math import sin,cos
a,b=3.,1.5
def transform(P,s):return P[0],s*P[1]
def point(t,s):return transform((a*cos(t),b*sin(t)),s)
triangle=((-1.,-.6),(1.4,.6),(-.2,1.1))
def area(points):
    A,B,C=points;return abs((B[0]-A[0])*(C[1]-A[1])-(B[1]-A[1])*(C[0]-A[0]))/2
