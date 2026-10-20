from math import pi,cos,sin,sqrt
ROTATION_AXIS='y'
A,B=3.,2.
def profile(t,phi):
    if ROTATION_AXIS=='x': return (A*cos(t), B*sin(t)*cos(phi), B*sin(t)*sin(phi))
    return (A*cos(t)*cos(phi),B*sin(t),A*cos(t)*sin(phi))
def disk(q,t):
    if ROTATION_AXIS=='x':
        r=B*sqrt(max(0,1-q*q/A**2)); return (q,r*cos(t),r*sin(t))
    r=A*sqrt(max(0,1-q*q/B**2)); return (r*cos(t),q,r*sin(t))
def section_area(q):
    return pi*(B*B*(1-q*q/A**2) if ROTATION_AXIS=='x' else A*A*(1-q*q/B**2))
def volume(): return 4*pi/3*(A*B*B if ROTATION_AXIS=='x' else A*A*B)
