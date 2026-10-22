"""Exact coefficient checks and 60-digit plot data for the F003 PDF only.

Run without arguments for verification; --write-plot-data also writes the
UID-specific PGFPlots table. No other UID or published image is touched.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[3]
UID = Path(__file__).resolve().parents[1]
TABLE = ROOT / "assets/tikz/F003_samples.dat"


def mul(a, b, n=8):
    return [sum((a[j] * b[k-j] for j in range(len(a))
                 if 0 <= k-j < len(b)), F(0)) for k in range(n+1)]


def divide(p, q, n=8):
    c = []
    for k in range(n+1):
        c.append(((p[k] if k < len(p) else F(0)) -
                  sum((q[j]*c[k-j] for j in range(1, min(k, len(q)-1)+1)), F(0))) / q[0])
    return c


def trig(x):
    # On |x| <= 1.2 the first omitted term after 70 terms is < 1e-220.
    s, c, a, b = x, D(1), x, D(1)
    for k in range(1, 70):
        a *= -x*x / D((2*k)*(2*k+1))
        b *= -x*x / D((2*k-1)*(2*k))
        s += a
        c += b
    return s, c


def rational(x):
    return ((x*x+6*x+12)/(x*x-6*x+12),
            (3*x*x+6*x)/(x*x+6*x+6),
            6*x/(x*x+6), (12-5*x*x)/(12+x*x), 3*x/(3-x*x))


def verify():
    e = [F(1, factorial(k)) for k in range(9)]
    l = [F(0)] + [F((-1)**(k+1), k) for k in range(1, 9)]
    s = [F((-1)**((k-1)//2), factorial(k)) if k % 2 else F(0) for k in range(9)]
    c = [F((-1)**(k//2), factorial(k)) if k % 2 == 0 else F(0) for k in range(9)]
    t = divide(s, c)
    cases = [(e, [12, 6, 1], [12, -6, 1], 5, F(1,720)),
             (l, [0, 6, 3], [6, 6, 1], 5, F(1,180)),
             (s, [0, 6], [6, 0, 1], 5, -F(7,360)),
             (c, [12, 0, -5], [12, 0, 1], 6, F(1,480)),
             (t, [0, 3], [3, 0, -1], 5, F(1,45))]
    for target, p, q, order, leading in cases:
        approx = divide(list(map(F,p)), list(map(F,q)))
        assert target[:order] == approx[:order]
        assert target[order]-approx[order] == leading

    # Independent exact polynomial verification of both derivative identities.
    P, Q = list(map(F,[12,6,1])), list(map(F,[12,-6,1]))
    PQ = mul(P,Q,4)
    diff = [a-b for a,b in zip(mul([F(6),F(2)],Q,4), mul(P,[F(-6),F(2)],4))]
    assert [a-b for a,b in zip(PQ,diff)] == [0,0,0,0,1]
    den, num = list(map(F,[6,6,1])), list(map(F,[0,6,3]))
    numprime = [a-b for a,b in zip(mul([F(6),F(6)],den,4),mul(num,[F(6),F(2)],4))]
    assert [a-b for a,b in zip(mul(den,den,4),mul([F(1),F(1)],numprime,4))] == [0,0,0,0,1]

    with localcontext() as ctx:
        ctx.prec = 60
        x = D('0.1'); re, rl, _, _, _ = rational(x)
        assert 0 < x.exp()-re < 3*x**5/D(665)
        assert 0 < (1+x).ln()-rl < x**5/D(180)
        assert re.quantize(D('0.0001')) == x.exp().quantize(D('0.0001')) == D('1.1052')
        assert rl.quantize(D('0.0001')) == (1+x).ln().quantize(D('0.0001')) == D('0.0953')
        sn, cs = trig(D('0.2')); rt = rational(D('0.2'))[-1]
        assert abs(rt-sn/cs) > D('0.000007')
        x = D('0.2')
        sm, cm = x-x**3/6, 1-x*x/2
        sp, cp = sm+x**5/120, cm+x**4/24
        assert D('0.20270') < sm/cp < sn/cs < sp/cm < D('0.20273')
        assert (sn/cs).quantize(D('0.0001')) == D('0.2027')
        # Exactness of the two equal-weight samples for monomials of degree <= 3.
        z = D(3); a = z/2-z/(2*D(3).sqrt()); b = z-a
        for k in range(4):
            assert abs(z*(a**k+b**k)/2-z**(k+1)/D(k+1)) < D('1e-55')
        assert abs(z/2*(1/(1+a)+1/(1+b))-rational(z)[1]) < D('1e-55')
        for j in range(-80,81):
            x = D(j)/100
            if not x:
                continue
            re,rl,_,_,_ = rational(x)
            assert (x.exp()-re)*x > 0
            assert ((1+x).ln()-rl)*x > 0
        print('PASS: 5 exact Taylor matches and leading error coefficients; 2 exact derivative identities.')
        print('PASS: certified rounding examples; 2-node area identity and moments; 160 signed-error samples.')


def write_data():
    with localcontext() as ctx:
        ctx.prec = 60
        rows = ['x exp re log rl sin rs cos rc tan rt ee el es ec et t4 e4']
        for j in range(-120, 121):
            x = D(j)/100
            re,rl,rs,rc,rt = rational(x)
            sn,cs = trig(x); ex=x.exp(); ln=(1+x).ln() if x > -1 else D('NaN'); tn=sn/cs
            t4 = D(1) + sum(x**k/D(factorial(k)) for k in range(1,5))
            vals = [x,ex,re,ln,rl,sn,rs,cs,rc,tn,rt,ex-re,ln-rl,sn-rs,cs-rc,tn-rt,t4,ex-t4]
            rows.append(' '.join(format(v,'.24g') for v in vals))
        TABLE.write_text('\n'.join(rows)+'\n',encoding='ascii')
    print('WROTE',TABLE.relative_to(ROOT))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-plot-data',action='store_true')
    args = parser.parse_args()
    verify()
    if args.write_plot_data:
        write_data()
