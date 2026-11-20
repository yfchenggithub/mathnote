FIXED=2.0
def state(x):
 if not 2<x<10:raise ValueError('second input must remain greater than 2 and below 10')
 return {'blue':(2.0,8.0,2.0),'orange':(float(x),10-float(x),float(x)),'g_slope':-1,'f_slope':-1,'composite_slope':1}
def signed_composition(sg,sf,x):return sf*(sg*x)
