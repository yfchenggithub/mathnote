"""Independent F038 model: fixed x, positive varying base, real exponents."""
import math

def value(base, x):
    if base <= 0 or not math.isfinite(base) or not math.isfinite(x):
        raise ValueError('finite x and positive finite base required')
    return math.exp(math.log(base) * x)

def slope_at_common_point(base):
    if base <= 0:
        raise ValueError('positive base required')
    return math.log(base)

def visible_domain(base, left=-2.2, right=2.2, ceiling=4.8):
    beta = slope_at_common_point(base)
    if abs(beta) < 1e-12:
        return left, right
    cut = math.log(ceiling) / beta
    return (max(left, cut), right) if beta < 0 else (left, min(right, cut))

def category(base):
    if abs(base - 1) < 1e-9:
        return 'a=1：水平线，单列为常数函数'
    return 'a>1：向右递增' if base > 1 else '0<a<1：向右递减'

def shifted(base, x, h, k):
    return value(base, x-h) + k
