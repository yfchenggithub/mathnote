CENTER=(2,3)
def f(x):return (x-2)**3+3
def state(t):
 if not .4<=t<=1.5:raise ValueError("outside storyboard")
 return ((2-t,f(2-t)),(2+t,f(2+t)))
