def f(x):return x*x
def state(t,b=1.5):
    if not 1<=t<=2.6:raise ValueError("t outside storyboard")
    return {"a":-t,"mirror":t,"b":b,"fa":f(-t),"fb":f(b),"gap":f(-t)-f(b)}
