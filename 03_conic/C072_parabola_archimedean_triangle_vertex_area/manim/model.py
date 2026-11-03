from decimal import Decimal, ROUND_HALF_UP

p=1.
def state(t,d):
    A=(t-d,(t-d)**2/(2*p));B=(t+d,(t+d)**2/(2*p))
    P=(t,(t*t-d*d)/(2*p));M=((A[0]+B[0])/2,(A[1]+B[1])/2)
    return A,B,P,M
def area(t,d):
    A,B,P,M=state(t,d)
    return abs((A[0]-P[0])*(B[1]-P[1])-(B[0]-P[0])*(A[1]-P[1]))/2

def midpoint_state(t, d):
    """Compute N from the curve equation, without assuming it bisects PM."""
    if d <= 0:
        raise ValueError('two distinct cut points require d > 0')
    _, _, P, M = state(t, d)
    N = (P[0], P[0] ** 2 / (2 * p))
    return N, N[1] - P[1], M[1] - N[1]

def rounded_for_display(value):
    """Two-place decimal half-up rounding after removing float noise."""
    return float(Decimal(str(round(value, 10))).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP))
