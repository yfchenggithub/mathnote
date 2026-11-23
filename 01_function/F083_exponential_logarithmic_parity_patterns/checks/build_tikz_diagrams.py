"""F083 only: exact-formula samples, parity audit, and PDF-only TikZ figures."""
from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/tikz'

def expdiff(x,a): return a**x-a**(-x)
def expsum(x,a): return a**x+a**(-x)
def fraction(x,a): return math.tanh(x*math.log(a)/2)
def reciprocal_fraction(x,a): return 1/math.tanh(x*math.log(a)/2)
def logratio(x,s): return math.log((x-s)/(x+s))
def rootlog(x,a): return math.asinh(x)/math.log(a)
def hidden(x,_): return x*(.5+1/math.expm1(x*math.log(2)))

# Each catalog entry produces one separate file, in the same order as the source.
CATALOG = [
 ('odd_01_exp_difference',r'奇1：$y=a^x-a^{-x}$',expdiff,[-2,2,-5,5],[-2,2],1,'odd',[(2,'blue','solid'),(.5,'orange!85!black','dashed')],
  r'蓝实线：$a=2$\\[8pt]橙虚线：$a=\frac12$\\[14pt]两种底数下，\\点对均关于原点对称。',r'$D=\mathbb R$；$f(0)=0$。指数互换后，差变号。'),
 ('odd_02_exp_fraction',r'奇2：$y=\dfrac{a^x-1}{a^x+1}$',fraction,[-4,4,-1.3,1.3],[-4,4],1,'odd',[(2,'blue','solid'),(.5,'orange!85!black','dashed')],
  r'蓝实线：$a=2$\\[8pt]橙虚线：$a=\frac12$\\[14pt]两图都经过原点。\\[8pt]靠近 $y=\pm1$，\\但取不到这两个值。',r'$D=\mathbb R$；分母始终为正，$f(0)=0$。'),
 ('odd_03_exp_reciprocal_fraction',r'奇3：$y=\dfrac{a^x+1}{a^x-1}$',reciprocal_fraction,[-4,4,-5,5],[-4,0,4],1,'odd',[(2,'blue','solid'),(.5,'orange!85!black','dashed')],
  r'蓝实线：$a=2$\\[8pt]橙虚线：$a=\frac12$\\[14pt]左右分支关于原点对称。\\[8pt]$x=0$ 为竖直渐近线；\\图像不经过原点。',r'$D=\mathbb R\setminus\{0\}$；$x=0$ 无定义，仍然是奇函数。'),
 ('odd_04_log_ratio_minus',r'奇4：$y=\ln\dfrac{kx-b}{kx+b}$',logratio,[-4,4,-4,4],[-4,-1,1,4],2,'odd',[(1,'blue','solid'),(-1,'orange!85!black','dashed')],
  r'固定 $k=1$。\\[8pt]蓝实线：$b=1$\\[8pt]橙虚线：$b=-1$\\[14pt]阴影内没有函数值。\\两条边界均不能取。',r'$k,b\ne0$；$D=\{x:|x|>|b/k|\}$。图中禁区为 $[-1,1]$。'),
 ('odd_05_log_ratio_plus',r'奇5：$y=\ln\dfrac{kx+b}{kx-b}$',lambda x,s:-logratio(x,s),[-4,4,-4,4],[-4,-1,1,4],2,'odd',[(1,'blue','solid'),(-1,'orange!85!black','dashed')],
  r'固定 $k=1$。\\[8pt]蓝实线：$b=1$\\[8pt]橙虚线：$b=-1$\\[14pt]同一组 $k,b$ 下，\\本式与奇4互为相反数。',r'$k,b\ne0$；$D=\{x:|x|>|b/k|\}$。取倒数后，对数反号。'),
 ('odd_06_root_log_plus',r'奇6：$y=\log_a\!\bigl(x+\sqrt{x^2+1}\bigr)$',rootlog,[-3,3,-3.2,3.2],[-3,3],1,'odd',[(2,'blue','solid'),(.5,'orange!85!black','dashed')],
  r'蓝实线：$a=2$\\[8pt]橙虚线：$a=\frac12$\\[14pt]每一条曲线都\\关于原点对称。\\[8pt]$x=0$ 时真数为 $1$。',r'$D=\mathbb R$；$\sqrt{x^2+1}>|x|$，故真数始终为正，$f(0)=0$。'),
 ('odd_07_root_log_minus',r'奇7：$y=\log_a\!\bigl(\sqrt{x^2+1}-x\bigr)$',lambda x,a:-rootlog(x,a),[-3,3,-3.2,3.2],[-3,3],1,'odd',[(2,'blue','solid'),(.5,'orange!85!black','dashed')],
  r'蓝实线：$a=2$\\[8pt]橙虚线：$a=\frac12$\\[14pt]同一底数下，本式\\与奇6上下互为相反数。\\每条曲线也原点对称。',r'$D=\mathbb R$；两个根式真数互为倒数，取对数后互为相反数。'),
 ('even_01_exp_sum',r'偶1：$y=a^x+a^{-x}$',expsum,[-2,2,0,8.5],[-2,2],1,'even',[(2,'blue','solid'),(3,'orange!85!black','dashed')],
  r'蓝实线：$a=2$\\[8pt]橙虚线：$a=3$\\[14pt]左右同高，关于 $y$ 轴对称。\\[8pt]两图最低点都是 $(0,2)$。',r'$D=\mathbb R$；$f(x)\ge2$。把底数换成 $1/a$，整条曲线不变。'),
 ('even_02_exp_absolute',r'偶2：$y=a^{|x|}$',lambda x,a:a**abs(x),[-2.5,2.5,0,6],[-2.5,2.5],1,'even',[(2,'blue','solid'),(.5,'orange!85!black','dashed')],
  r'蓝实线：$a=2$\\[8pt]橙虚线：$a=\frac12$\\[14pt]两图都关于 $y$ 轴对称。\\[8pt]$a>1$ 时中间最低；\\$0<a<1$ 时中间最高。',r'$D=\mathbb R$；$f(0)=1$。保留指数函数右半图，再向左翻折。'),
 ('even_03_exp_negative_square',r'偶3：$y=a^{-x^2}$',lambda x,a:a**(-x*x),[-2,2,0,5],[-2,2],1,'even',[(2,'blue','solid'),(.5,'orange!85!black','dashed')],
  r'蓝实线：$a=2$\\[8pt]橙虚线：$a=\frac12$\\[14pt]正负输入给出同一指数。\\[8pt]底数改变峰谷形状，\\不改变左右对称。',r'$D=\mathbb R$；$f(0)=1$。$a>1$ 时 $0<f\le1$；$0<a<1$ 时 $f\ge1$。'),
 ('even_04_log_absolute',r'偶4：$y=\log_a|x|$',lambda x,a:math.log(abs(x))/math.log(a),[-4,4,-3,3],[-4,0,4],2,'even',[(2,'blue','solid'),(.5,'orange!85!black','dashed')],
  r'蓝实线：$a=2$\\[8pt]橙虚线：$a=\frac12$\\[14pt]每条曲线左右同高。\\[8pt]经过 $(-1,0)$、$(1,0)$；\\$x=0$ 不能代入。',r'$D=\mathbb R\setminus\{0\}$；纵轴是渐近线，定义域仍然左右成对。'),
 ('even_05_hidden_product',r'偶5：$y=x\left(\dfrac12+\dfrac1{2^x-1}\right)$',hidden,[-4,4,0,2.9],[-4,0,4],2,'even',[(2,'blue','solid')],
  r'没有可变底数参数。\\[14pt]$f(-2)=f(2)=\frac53$。\\[14pt]左右同高，是偶函数；\\中间空点不能补入。',r'$D=\mathbb R\setminus\{0\}$；括号内是奇函数，乘上奇函数 $x$ 后为偶函数。'),
]

def valid(key,x):
    if key.startswith(('odd_04','odd_05')): return abs(x)>1
    if key.startswith(('odd_03','even_04','even_05')): return x!=0
    return True

def points(fn,parameter,interval,bounds,key):
    xmin,xmax,ymin,ymax=bounds
    low,high=interval
    segments=[]; segment=[]
    for i in range(601):
        x=low+(high-low)*i/600
        if not valid(key,x): y=None
        else:
            try:y=fn(x,parameter)
            except (ValueError,ZeroDivisionError,OverflowError):y=None
        if y is not None and math.isfinite(y) and ymin<=y<=ymax:
            segment.append((x,y))
        elif segment:
            if len(segment)>1:segments.append(segment)
            segment=[]
    if len(segment)>1:segments.append(segment)
    return segments

def create(item):
    key,title,fn,bounds,breaks,t,parity,curves,note,footer=item
    xmin,xmax,ymin,ymax=bounds
    xs=6.8/(xmax-xmin);ys=4.5/(ymax-ymin)
    ox=1.0-xmin*xs;oy=1.65-ymin*ys
    parts=[r'\begin{center}\begin{tikzpicture}[font=\small,>=stealth,line join=round]',
           r'\draw[gray!40,rounded corners=3pt] (0,0) rectangle (14.2,8.4);',
           r'\node at (7.1,7.75) {'+title+r'};',
           rf'\begin{{scope}}[shift={{({ox:.6f},{oy:.6f})}},x={xs:.6f}cm,y={ys:.6f}cm]']
    if key.startswith(('odd_04','odd_05')):
        parts.append(rf'\fill[gray!12] (-1,{ymin}) rectangle (1,{ymax});')
        for x in [-1,1]:parts.append(rf'\draw[gray,dashed] ({x},{ymin})--({x},{ymax});')
    if key.startswith(('odd_02','odd_03')):
        for y in [-1,1]:
            parts.append(rf'\draw[gray,dotted] ({xmin},{y})--({xmax},{y});')
            parts.append(rf'\node[anchor=east] at ({xmin}-.08/{xs:.6f},{y}) {{${y}$}};')
    parts.extend([rf'\draw[->,gray] ({xmin},0)--({xmax},0) node[right] {{$x$}};',
                  rf'\draw[->,gray] (0,{ymin})--(0,{ymax}) node[above] {{$y$}};'])
    if key.startswith(('odd_04','odd_05')):
        for x in [-1,1]:
            parts.append(rf'\node[anchor=north] at ({x},{ymin}-.07/{ys:.6f}) {{${x}$}};')
    for x in [-t,t]:
        parts.append(rf'\draw[gray] ({x},-.035/{ys:.6f})--({x},.035/{ys:.6f});')
        parts.append(rf'\node[anchor=north] at ({x},-.07/{ys:.6f}) {{${x:g}$}};')
    parts.append(r'\begin{scope}')
    parts.append(rf'\clip ({xmin},{ymin}) rectangle ({xmax},{ymax});')
    total=0
    for parameter,color,style in curves:
        for low,high in zip(breaks,breaks[1:]):
            for segment in points(fn,parameter,(low,high),bounds,key):
                coordinates=' '.join(f'({x:.7f},{y:.7f})' for x,y in segment)
                parts.append(rf'\draw[{color},thick,{style}] plot coordinates {{{coordinates}}};')
                total+=len(segment)
    value=fn(t,curves[0][0]);negative=fn(-t,curves[0][0])
    parts.append(rf'\draw[violet!75!black,densely dotted] (-{t},{negative:.7f})--({t},{value:.7f});')
    for x,y in [(-t,negative),(t,value)]:parts.append(rf'\fill[violet!75!black] ({x},{y:.7f}) circle(2.3pt);')
    if key.startswith('even_05'):
        parts.append(rf'\draw[blue,fill=white,thick] (0,{1/math.log(2):.8f}) circle(2.7pt);')
    parts.extend([r'\end{scope}',r'\end{scope}',
                  r'\node[anchor=west,align=left,text width=4.35cm] at (8.9,4.4) {'+note+r'};',
                  r'\node[text width=12.8cm,align=center] at (7.1,.65) {'+footer+r'};',
                  r'\end{tikzpicture}\end{center}'])
    name='F083_'+key+'.tex'
    (OUT/name).write_text('% Formula-based samples; see F083 checks/build_tikz_diagrams.py.\n'+'\n'.join(parts)+'\n',encoding='utf-8')
    return name,total

def audit():
    checks=0
    for item in CATALOG:
        key,_,fn,_,_,_,parity,curves,_,_=item
        for parameter,_,_ in curves:
            for x in [0.013,0.1,0.5,0.99,1.01,1.2,2,3,4]:
                if not valid(key,x):continue
                y,z=fn(x,parameter),fn(-x,parameter)
                expected=-y if parity=='odd' else y
                assert math.isclose(z,expected,abs_tol=2e-11,rel_tol=2e-11),(key,x)
                checks+=1
    for a in [.2,.5,2,3]:
        for x in [-4,-1,-.1,0,.1,1,4]:
            u=x+math.sqrt(x*x+1);v=math.sqrt(x*x+1)-x
            assert u>0 and v>0 and math.isclose(u*v,1,abs_tol=1e-12)
            assert math.isclose(rootlog(x,a),math.log(u)/math.log(a),abs_tol=1e-12)
            if x:assert math.isclose(hidden(x,2),x*(2**x+1)/(2*(2**x-1)),abs_tol=1e-12)
    for k,b in [(1,1),(1,-1),(-2,3),(-2,-3),(2,-3)]:
        for x in [-4,-2,-.5,0,.5,2,4]:
            if k*x+b==0:continue
            ratio=(k*x-b)/(k*x+b)
            assert (ratio>0)==(abs(x)>abs(b/k))
    return checks

def supplementary_figures():
    """Two different cognitive tasks: allowed inputs, and positive reciprocals."""
    parts=[r'\begin{center}\begin{tikzpicture}[font=\small,>=stealth]',
           r'\draw[gray!40,rounded corners=3pt] (0,0) rectangle (14.2,8.4);',
           r'\node at (7.1,7.75) {绝对值改变了定义域：两幅图用相同坐标尺度};']
    for ox,absolute,title in [(3.65,False,r'$y=\log_2x$'),(10.65,True,r'$y=\log_2|x|$')]:
        parts.append(rf'\node at ({ox},6.8) {{{title}}};')
        parts.append(rf'\begin{{scope}}[shift={{({ox},3.85)}},x=.82cm,y=.75cm]')
        if not absolute:parts.append(r'\fill[gray!12] (-3,-2.6) rectangle (0,2.6);')
        parts.extend([r'\draw[->,gray] (-3,0)--(3,0) node[right] {$x$};',r'\draw[->,gray] (0,-2.6)--(0,2.6) node[above] {$y$};'])
        for lo,hi in ([(-3,-.17),(.17,3)] if absolute else [(.17,3)]):
            coords=' '.join(f'({lo+(hi-lo)*i/160:.7f},{math.log2(abs(lo+(hi-lo)*i/160)):.7f})' for i in range(161))
            parts.append(r'\draw[blue,thick] plot coordinates {'+coords+'};')
        parts.append(r'\end{scope}')
        caption=r'$D=(0,+\infty)$，不成对' if not absolute else r'$D=\mathbb R\setminus\{0\}$，成对'
        parts.append(rf'\node at ({ox},1.25) {{{caption}}};')
    parts.extend([r'\node at (7.1,.55) {左图没有负数输入；右图把正半图复制到左侧，但两图都不能代入 $0$。};',r'\end{tikzpicture}\end{center}'])
    (OUT/'F083_log_domain_compare.tex').write_text('\n'.join(parts)+'\n',encoding='utf-8')
    parts=[r'\begin{center}\begin{tikzpicture}[font=\small,>=stealth]',
           r'\draw[gray!40,rounded corners=3pt] (0,0) rectangle (14.2,8.4);',
           r'\node at (7.1,7.75) {两个根式真数都为正；互为倒数，取对数后才互为相反数};',
           r'\begin{scope}[shift={(4.4,1.8)},x=1.2cm,y=.75cm]',
           r'\draw[->,gray] (-2.8,0)--(2.8,0) node[right] {$x$};',
           r'\draw[->,gray] (0,0)--(0,6) node[above] {$y$};',
           r'\draw[gray,dotted] (-2.8,1)--(2.8,1);']
    for sign,color,style in [(1,'blue','solid'),(-1,'orange!85!black','dashed')]:
        coords=' '.join(f'({x:.7f},{math.sqrt(x*x+1)+sign*x:.7f})' for x in [-2.7+5.4*i/240 for i in range(241)])
        parts.append(rf'\draw[{color},thick,{style}] plot coordinates {{{coords}}};')
        value=math.sqrt(2)+sign
        parts.append(rf'\fill[{color}] (1,{value:.7f}) circle(2.3pt);')
    parts.extend([r'\draw[violet,densely dotted] (1,0)--(1,2.41421356);',
                  r'\node[anchor=north] at (1,-.1) {$1$};',r'\end{scope}',
                  r'\node[anchor=west,align=left,text width=4.5cm] at (8.9,4.3) {蓝实线：\\[4pt]$U(x)=\sqrt{x^2+1}+x$\\[10pt]橙虚线：\\[4pt]$V(x)=\sqrt{x^2+1}-x$\\[14pt]$U(1)=\sqrt2+1$\\[10pt]$V(1)=\sqrt2-1$};',
                  r'\node at (7.1,.65) {$U(x)>0$、$V(x)>0$，且 $U(-x)=V(x)=1/U(x)$。};',r'\end{tikzpicture}\end{center}'])
    (OUT/'F083_root_positive_reciprocals.tex').write_text('\n'.join(parts)+'\n',encoding='utf-8')

if __name__=='__main__':
    count=audit();generated=[create(item) for item in CATALOG];supplementary_figures()
    (HERE/'checks/diagram_manifest.json').write_text(json.dumps({'parity_checks':count,'diagrams':[{'path':'assets/tikz/'+n,'sample_points':c} for n,c in generated],'supplementary_diagrams':['assets/tikz/F083_log_domain_compare.tex','assets/tikz/F083_root_positive_reciprocals.tex']},indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {count} parity checks, conjugate/domain/hidden-product identities; {len(generated)} dedicated diagrams.')
