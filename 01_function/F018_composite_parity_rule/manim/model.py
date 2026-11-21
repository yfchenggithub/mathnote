def inner(x):
    return x*x

def outer(u):
    return 2**u

def composite(x):
    return outer(inner(x))

def state(t):
    if not .4 <= t <= 1.4:raise ValueError("t outside model interval")
    return {"u_plus":inner(t),"u_minus":inner(-t),"value":composite(t)}
