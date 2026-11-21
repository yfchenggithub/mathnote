import math
A=2
def f(x):return math.sin(math.pi*x/2)
def state(x):
 return {"center":x,"left":x-A,"right":x+A,"left_height":f(x-A),"right_height":f(x+A),"gap":2*A}
