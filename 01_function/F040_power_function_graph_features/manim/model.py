"""F040 independent model. Uniform real powers are evaluated only for x>0."""
import math
def power(x,alpha):
 if x<=0:raise ValueError('The uniform real-exponent model requires x > 0')
 return math.exp(alpha*math.log(x))
def slope(x,alpha):return alpha*power(x,alpha-1)
def category(alpha):
 if alpha>1+1e-9:return '上升，越来越陡'
 if abs(alpha-1)<=1e-9:return '直线，斜率为1'
 if alpha>1e-9:return '上升，越来越平'
 if abs(alpha)<=1e-9:return '高度不变，恒为1'
 return '下降，越来越平'
def fractional_even(x):
 if x==0:raise ValueError('x=0 is outside the domain')
 return abs(x)**(-2/3)
def example_four_inequality(a):
 if a in [-1,3]:return None
 return fractional_even(a+1)>fractional_even(3-a)
