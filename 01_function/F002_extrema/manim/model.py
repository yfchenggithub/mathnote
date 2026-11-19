def peak(x):return 1-x*x
def stationary(x):return x**3
def corner(x):return abs(x)
def audit():
    for i in range(1,151):
        h=i/100
        assert peak(h)<peak(0) and peak(-h)<peak(0)
        assert stationary(-h)<stationary(0)<stationary(h)
        assert corner(-h)>corner(0) and corner(h)>corner(0)
    assert (corner(.1)-corner(0))/.1==1
    assert (corner(-.1)-corner(0))/(-.1)==-1
    return 152
