AXIS=2
def f(x):return (x-AXIS)**2+1
def state(t):
 if not .4<=t<=1.9:raise ValueError("t outside storyboard")
 return {"left":AXIS-t,"right":AXIS+t,"height":t*t+1}
