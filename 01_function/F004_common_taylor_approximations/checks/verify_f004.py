"""F004: exact coefficient checks, 60-digit numerical audit, PGFPlots data.

Run from any directory; --write-data regenerates only F004_samples.dat.
Numerical sampling supplements the analytic proofs; it is not their proof.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[3]


def trig(x):
    s, c, a, b = x, D(1), x, D(1)
    for k in range(1, 90):
        a *= -x*x / D((2*k)*(2*k+1))
        b *= -x*x / D((2*k-1)*(2*k))
        s += a
        c += b
    return s, c


def multiply(a, b, n):
    return [sum((a[i]*b[k-i] for i in range(len(a))
                 if 0 <= k-i < len(b)), F(0)) for k in range(n+1)]


def verify(write_data=False):
    # tan(x) cos(x) = sin(x), through degree four.
    assert multiply([F(0), F(1), F(0), F(1, 3)],
                    [F(1), F(0), F(-1, 2), F(0), F(1, 24)], 4) == [
                        F(0), F(1), F(0), F(-1, 6), F(0)]
    # (1+x)(1-x+x²) = 1+x³: exact finite log identity.
    assert multiply([F(1), F(1)], [F(1), F(-1), F(1)], 3) == [1, 0, 0, 1]
    # ln(1+sin x) = sin x - (sin x)²/2 + O(x³).
    assert multiply([F(0), F(1), F(0)], [F(0), F(1), F(0)], 2) == [0, 0, 1]
    rows = []
    count = 0
    with localcontext() as ctx:
        ctx.prec = 60
        for j in range(-120, 201):
            x = D(j)/100
            s, c = trig(x)
            e = x.exp()
            pe = 1+x+x*x/2
            ps = x-x**3/6+x**5/120
            pc = 1-x*x/2+x**4/24
            pt = x+x**3/3
            log = (1+x).ln() if x > -1 else D('NaN')
            pl = x-x*x/2+x**3/3
            comp = (1+s).ln() if 1+s > 0 else D('NaN')
            er = (e-1-x)/x**2 if x else D('NaN')
            cr = (c-1+x*x/2)/x**4 if x else D('NaN')
            if abs(x) <= D('.8'):
                assert abs(e-pe) <= abs(x)**3*D('.8').exp()/6 + D('1e-55')
                assert abs(log-pl) <= abs(x)**4/(4*(1-D('.8'))) + D('1e-55')
                assert log <= pl + D('1e-55')
                assert abs(s-ps) <= abs(x)**7/5040 + D('1e-55')
                assert abs(c-pc) <= abs(x)**6/720 + D('1e-55')
                count += 5
            if 0 < abs(x) <= D('.5'):
                assert abs((s/c-pt)/x**5) < D('.15')
                count += 1
            vals = [x, e, 1+x, pe, log, pl, s, ps, c, pc, s/c, pt,
                    x-x**3/6, x+x**3/6, comp, x-x*x/2, er, cr,
                    abs(s-(x-x**3/6)), abs(s-ps), x**3/(1+x) if x>-1 else D('NaN')]
            rows.append(' '.join('nan' if v.is_nan() else f'{v:.35g}'
                                 for v in map(D, vals)))
        x = D('.2')
        s, _ = trig(x)
        p = x-x**3/6+x**5/120
        bound = x**7/5040
        assert D('.19865') < p-bound < s < p < D('.19875')
        assert bound < D('2.54e-9')
        assert F(1,5)-F(1,5)**3/6+F(1,5)**5/120 == F(74501,375000)
        for x in [D('1e-4'), D('-1e-4')]:
            _, c = trig(x)
            assert abs((c-1+x*x/2)/x**4 - D(1)/24) < D('1.4e-11')
        print(f'PASS: exact identities; {count} sampled error checks; rounding interval; two-sided residual limit checks.')
        print(f'sin(0.2)={s}; T5={p}; error bound={bound}')
        if write_data:
            dest = ROOT/'assets/tikz/F004_samples.dat'
            dest.write_text('x exp line pe log pl sin ps cos pc tan pt s3 wrong composite q2 er cr es3 es5 logder\n'
                            + '\n'.join(rows)+'\n', encoding='ascii')
            print(f'Wrote {len(rows)} rows: {dest}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--write-data', action='store_true')
    verify(ap.parse_args().write_data)
