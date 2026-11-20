"""F003-only exact matching checks and high-precision exponential plot data.

Run with --write-plot-data to create the new PDF table. Existing tables are not
overwritten unless their bytes already match the independently regenerated data.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / 'assets/tikz/F003_exp_design_samples.dat'


def mul(p, q):
    out = [F(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i+j] += a*b
    return out


def sub(p, q):
    return [(p[i] if i < len(p) else F(0)) -
            (q[i] if i < len(q) else F(0)) for i in range(max(len(p),len(q)))]


def derivative(p):
    return [i*p[i] for i in range(1,len(p))]


def verify_and_table():
    # Independent coefficient arithmetic: the slope at zero does not depend on b.
    for b in [F(0),F(1,12),F(1,5),F(-1,7)]:
        n, d = [F(1),F(1,2),b], [F(1),F(-1,2),b]
        numer = sub(mul(derivative(n),d),mul(n,derivative(d)))
        assert n[0]/d[0] == 1 and numer[0]/d[0]**2 == 1
        residual = sub(numer,mul(n,d))
        assert residual == [0,0,F(1,4)-3*b,0,-b*b]
    n,d = [F(1),F(1,2)],[F(1),F(-1,2)]
    residual1=sub(sub(mul(derivative(n),d),mul(n,derivative(d))),mul(n,d))
    assert residual1==[0,0,F(1,4)]

    with localcontext() as ctx:
        ctx.prec=70
        lines=['x exp r1 r2 err1 err2']
        observations=[]
        for i in range(-200,201):
            x=D(i)/200
            ex=x.exp();r1=(2+x)/(2-x);r2=(x*x+6*x+12)/(x*x-6*x+12)
            e1=abs(r1-ex);e2=abs(ex-r2)
            assert 2-x>0 and x*x-6*x+12>0
            if x>0:
                assert r1>ex>r2 and e2<=e1/49
            elif x<0:
                assert r1<ex<r2
            else:
                assert ex==r1==r2==1 and e1==e2==0
            lines.append(' '.join([str(x)]+[format(v,'.20E') for v in [ex,r1,r2,e1,e2]]))
            if x in [D('.1'),D('.5'),D(1)]:
                observations.append({'x':str(x),'R1_error':str(e1),'R2_error':str(e2),
                                     'error_reduction_factor':str(e1/e2)})
        # Differentiate the weighted deviations, then compare their derivatives.
        for i in range(1,201):
            x=D(i)/200;Q=x*x-6*x+12
            assert Q>=7 and 0<x*(2-x)<=1
            v1prime=(-x).exp()*x*x/(2-x)**2
            v2prime=(-x).exp()*x**4/Q**2
            assert v1prime>0 and 0<v2prime<=v1prime/49
        return '\n'.join(lines)+'\n',observations


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--write-plot-data',action='store_true')
    parser.add_argument('--report')
    args=parser.parse_args()
    text,observations=verify_and_table()
    if args.write_plot_data:
        if TABLE.exists():
            assert TABLE.read_text(encoding='ascii')==text,'Existing plot table differs; not overwritten.'
        else:
            TABLE.write_text(text,encoding='ascii')
    result={'status':'PASS','precision_digits':70,'data_rows':401,
            'matching_at_zero':'R2(0)=1 and R2_prime(0)=2a=1 for any b once a=1/2',
            'residuals':'R1_prime-R1=x^2/(2-x)^2; R2_prime-R2=-x^4/(x^2-6x+12)^2',
            'uniform_error_comparison':'0<=exp(x)-R2(x)<=(R1(x)-exp(x))/49 on [0,1]',
            'observations':observations}
    if args.report:
        p=Path(args.report);p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
