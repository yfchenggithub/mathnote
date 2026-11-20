"""F014: independently model the join of two increasing affine branches."""
def value(x,c):return x if x<=0 else x+c
def join_height(c):return c
def globally_strict_increasing(c):return c>=0
def witness(c):
 if c>=0:return None
 return min(1,-c/2)
