from math import sqrt,cos,sin,cosh,sinh,hypot
KIND='ellipse'
def parameters(b):
    a=3. if KIND=='ellipse' else 2.
    c=sqrt(a*a-b*b) if KIND=='ellipse' else sqrt(a*a+b*b)
    return a,b,c
def triangle(b):
    a,b,c=parameters(b)
    return ((0,0),(c,0),(0,b)) if KIND=='ellipse' else ((0,0),(a,0),(a,b))
