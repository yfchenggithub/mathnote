"""C097: vertex secants in two orientations; no reciprocal of an undefined slope."""
def horizontal(t,p=1.):
    if p==0:raise ValueError('p must be nonzero')
    return (t*t/(2*p),t)

def vertical(t,p=1.):
    if p==0:raise ValueError('p must be nonzero')
    return (t,t*t/(2*p))

def slope(A,B):
    dx=B[0]-A[0]
    return None if abs(dx)<1e-12 else (B[1]-A[1])/dx

def inverse_direction(A,B):
    return (B[0]-A[0])/(B[1]-A[1])

def state(b,vertical_axis=False):
    P=vertical if vertical_axis else horizontal
    if b==0 or b==2:raise ValueError('Distinct nonvertex points required')
    return P(2.),P(b)

def audit():
    count=0;O=(0.,0.)
    for p in [-3.,-1.,.5,1.,2.]:
      for i in range(361):
        b=-2.6+1.8*i/360;A=horizontal(2,p);B=horizontal(b,p)
        k1=slope(O,A);k2=slope(O,B);q=inverse_direction(A,B)
        assert abs(1/k1+1/k2-q)<1e-10
        kab=slope(A,B)
        if kab is not None:assert abs(1/kab-q)<1e-10
        U=vertical(2,p);V=vertical(b,p)
        assert abs(slope(O,U)+slope(O,V)-slope(U,V))<1e-10
        assert U==(A[1],A[0]) and V==(B[1],B[0])
        count+=1
    A,B=state(-2);assert slope(A,B) is None and inverse_direction(A,B)==0
    A,B=state(-2,True);assert slope(A,B)==0
    for b in [0,2]:
        try:state(b)
        except ValueError:pass
        else:raise AssertionError('Boundary accepted')
    return count+4
