"""F031 PDF-only additions. Existing inline figures are preserved separately."""
from pathlib import Path
import json, math

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'assets/tikz'
def save(name,parts):
    (OUT/name).write_text('\n'.join(parts)+'\n',encoding='utf-8')
def frame(height,title):
    return [r'\begin{center}\begin{tikzpicture}[font=\small,>=stealth,line join=round]',
            rf'\draw[draw=teal!45!black,fill=green!3,rounded corners=3pt] (0,0) rectangle (13.8,{height});',
            rf'\node at (6.9,{height-.65}) {{{title}}};']
def end():return [r'\end{tikzpicture}\end{center}']
def dot(x,y,color='F031Min'):
    return rf'\fill[{color}] ({x},{y}) circle(2.6pt);'

def build():
    # Same x/y scales in all four panels: the fixed interval is the solid curve.
    q=frame(12.4,r'$f(x)=(x-t)^2$，固定 $[0,4]$；四图坐标尺度相同')
    for t,ox,oy,titley,cap1,cap2,word in [(-1,1.45,7.2,10.95,6.65,6.20,'左侧'),(1,8.35,7.2,10.95,6.65,6.20,'内部'),(2,1.45,1.6,5.35,1.05,.60,'中点'),(5,8.35,1.6,5.35,1.05,.60,'右侧')]:
        near=min(4,max(0,t));far=[x for x in [0,4] if abs(x-t)==max(abs(t),abs(4-t))]
        center=3.65 if ox<2 else 10.55
        q.extend([rf'\node at ({center},{titley}) {{$t={t}$：轴在{word}}};',
                  rf'\begin{{scope}}[shift={{({ox},{oy})}},x=.65cm,y=.12cm]',
                  r'\draw[gray,->] (-1.35,0)--(5.4,0) node[right] {$x$};',
                  r'\draw[gray,->] (0,0)--(0,26);',
                  rf'\draw[F031Axis,densely dashed] ({t},0)--({t},26);',
                  r'\draw[teal!60!black,very thick] (0,0)--(4,0);',
                  r'\node[below] at (0,-.5) {$0$};\node[below] at (4,-.5) {$4$};',
                  r'\begin{scope}\clip (-1.4,-.2) rectangle (5.5,26);',
                  rf'\draw[gray!60,densely dotted,domain=-1.35:5.35,samples=81] plot(\x,{{(\x-({t}))^2}});',
                  rf'\draw[F031Curve,very thick,domain=0:4,samples=81] plot(\x,{{(\x-({t}))^2}});',
                  r'\end{scope}',dot(near,(near-t)**2)])
        for x in far:q.append(dot(x,(x-t)**2,'F031Max'))
        if t<0 or t>4:q.append(rf'\draw[gray,fill=green!3] ({t},0) circle(2.6pt);')
        q.extend([r'\end{scope}',
                  rf'\node at ({center},{cap2}) {{{{\color{{F031Min}}最小 ${(near-t)**2}$（$x={near}$）}}\quad{{\color{{F031Max}}最大 ${max((x-t)**2 for x in [0,4])}$（$x='+(','.join(str(x) for x in far))+r'$）}};'])
    save('F031_four_moving_axes.tex',q+end())

    q=frame(7.5,r'配方把横向距离变成高度差：$f(x)=(x-1)^2+2$')
    q.extend([r'\begin{scope}[shift={(1.6,1.7)},x=1.32cm,y=.46cm]',
              r'\draw[gray,->] (-.2,0)--(4.4,0) node[right] {$x$};',
              r'\draw[gray,->] (0,0)--(0,10) node[above] {$y$};',
              r'\draw[F031Curve,thick,domain=0:3.6,samples=65] plot(\x,{(\x-1)^2+2});',
              r'\draw[F031Axis,densely dashed] (1,0)--(1,9.5);',
              r'\draw[gray,dotted] (0,2)--(3,2);',
              r'\draw[<->,F031Min,thick] (1,2)--(3,2);',
              r'\draw[<->,F031Max,thick] (3,2)--(3,6);',
              dot(1,2),dot(3,6,'F031Max'),
              r'\node[below] at (1,-.1) {$x_0=1$};\node[below] at (3,-.1) {$x=3$};',
              r'\node[anchor=north] at (2,1.75) {$d=2$};',
              r'\end{scope}',
              r'\node[anchor=west,align=left,text width=4.6cm] at (8.5,4.1) {蓝点：顶点 $(1,2)$\\[10pt]横向距离 $d=|3-1|=2$\\[10pt]橙点：$(3,6)$\\[10pt]高度差 $6-2=2^2=4$};',
              r'\node at (6.9,.6) {$x_0$ 是横坐标；$k=f(x_0)=2$ 是顶点的函数值，两者不能混淆。};'])
    save('F031_complete_square_distance_height.tex',q+end())

    q=frame(7.7,r'端点作差看的是两端高度：$f(x)=(x-x_0)^2$，$[m,n]=[0,4]$')
    for i,t in enumerate([1,2,3]):
        ox=1.0+4.55*i;mid=2.3+4.55*i;delta=(4-t)**2-t*t
        q.extend([rf'\node at ({mid},6.35) {{$x_0={t}$'+(r'$<h$' if t<2 else r'$=h$' if t==2 else r'$>h$')+r'};',
                  rf'\begin{{scope}}[shift={{({ox},2.1)}},x=.68cm,y=.35cm]',
                  r'\draw[gray,->] (-.25,0)--(4.5,0) node[right] {$x$};',
                  rf'\draw[F031Curve,thick,domain=0:4,samples=65] plot(\x,{{(\x-{t})^2}});',
                  rf'\draw[F031Axis,densely dashed] ({t},0)--({t},10);',
                  r'\node[below] at (0,-.1) {$m=0$};\node[below] at (4,-.1) {$n=4$};',
                  dot(t,0)])
        for x in [0,4]:
            y=(x-t)**2
            color='F031Max' if y==max(t*t,(4-t)**2) else 'teal!70!black'
            q.extend([dot(x,y,color),rf'\node[above] at ({x},{y}+.3) {{${y}$}};'])
        q.extend([r'\end{scope}',rf'\node at ({mid},1.2) {{$f(4)-f(0)={delta}$}};',
                  rf'\node at ({mid},.65) {{'+('右端更高' if delta>0 else '两端等高' if delta==0 else '左端更高')+r'};'])
    save('F031_endpoint_height_cases.tex',q+end())

    q=frame(7.6,r'例2：两个端点值在哪里交换大小？')
    q.extend([r'\begin{scope}[shift={(1.3,3.25)},x=3.5cm,y=.55cm]',
              r'\draw[gray,->] (-.05,0)--(2.15,0) node[right] {$a$};',
              r'\draw[gray,->] (0,-3.2)--(0,5.35);',
              r'\draw[F031Curve,thick] (0,5)--(2,-3);',
              r'\draw[teal!70!black,thick,dashed] (0,1)--(2,1);',
              r'\draw[F031Max,very thick] (0,5)--(1,1)--(2,1);',
              r'\draw[F031Axis,densely dashed] (1,-3)--(1,5);',
              dot(1,1,'F031Max'),
              r'\foreach \a in {0,1,2}\node[below] at (\a,-.1) {$\a$};',
              r'\end{scope}',
              r'\node[anchor=west,align=left,text width=3.7cm] at (9.1,4.25) {固定区间 $[0,2]$\\[10pt]斜线：$f(2)=5-4a$\\[10pt]水平线：$f(0)=1$\\[10pt]橙色粗线取较大值\\即 $G(a)$};',
              r'\node at (6.9,.65) {交点 $(a,\text{端点值})=(1,1)$；横轴是参数 $a$，不是自变量 $x$。};'])
    save('F031_example_endpoint_values.tex',q+end())

    q=frame(7.2,r'例3：候选参数必须落在求解时使用的那一段里')
    rows=[(5.4,r'$a<0$',-3,0,r'$g=1\ne-3$，无解'),(3.6,r'$0\le a\le2$',0,2,r'$-2$ 在区间外，舍去；\\$2$ 在闭区间内，保留'),(1.8,r'$a>2$',2,4,r'候选 $2$ 在开边界上，\\不满足 $a>2$，舍去')]
    for row,(y,label,lo,hi,note) in enumerate(rows):
        q.extend([rf'\node[anchor=west] at (.5,{y}) {{{label}}};',
                  rf'\begin{{scope}}[shift={{(5.5,{y})}},x=.85cm]',
                  r'\draw[gray,->] (-3.2,0)--(4.3,0) node[right] {$a$};',
                  rf'\draw[F031Curve,very thick] ({lo},0)--({hi},0);',
                  r'\foreach \a in {0,2} \node[below] at (\a,-.12) {$\a$};'])
        if row==0:q.append(r'\draw[F031Curve,fill=green!3,thick] (0,0) circle(2.5pt);')
        if row==1:
            q.extend([dot(0,0,'F031Curve'),dot(2,0),r'\draw[F031Wrong,thick] (-2,0) circle(3.1pt);\node[F031Wrong,above] at (-2,.14) {候选 $-2$};'])
        if row==2:q.append(r'\draw[F031Wrong,fill=green!3,thick] (2,0) circle(3.1pt);')
        q.extend([r'\end{scope}',rf'\node[anchor=west,align=left,text width=3.65cm] at (9.5,{y}) {{{note}}};'])
    q.append(r'\node[F031Min] at (6.9,.6) {同一个候选 $2$：在 $[0,2]$ 这一段保留，在 $a>2$ 这一段舍去；最终 $a=2$。};')
    save('F031_inverse_parameter_ranges.tex',q+end())

def audit():
    count=0
    for m,n in [(0,4),(0,2),(-3,1),(1,5)]:
        for axis in [m-2,m,(3*m+n)/4,(m+n)/2,(m+3*n)/4,n,n+2]:
            near=min(n,max(m,axis));far=[z for z in [m,n] if abs(z-axis)==max(abs(m-axis),abs(n-axis))]
            for a in [-2,-1,.5,1,3]:
                f=lambda x:a*(x-axis)**2+2
                candidates=[m,n]+([axis] if m<=axis<=n else [])
                expected_min=min(map(f,candidates));expected_max=max(map(f,candidates))
                assert math.isclose(f(near),expected_min if a>0 else expected_max)
                assert all(math.isclose(f(x),expected_max if a>0 else expected_min) for x in far)
                assert math.isclose(f(n)-f(m),a*(n-m)*(m+n-2*axis))
                count+=1
    for a in [-3,-1,0,.5,1,1.5,2,3,4]:
        f=lambda x:x*x-2*a*x+1
        g=1 if a<0 else 1-a*a if a<=2 else 5-4*a
        G=5-4*a if a<=1 else 1
        pts=[0,2]+([a] if 0<=a<=2 else [])
        assert math.isclose(g,min(map(f,pts))) and math.isclose(G,max(map(f,pts)))
        count+=1
    assert (1-2**2)==-3 and (5-4*2)==-3
    assert min([x*x-4*x+1 for x in [0,2]])==-3
    return count

if __name__=='__main__':
    checked=audit();build()
    print(f'PASS: {checked} extrema/endpoint-difference/example checks, including axis boundaries m,n,h; 5 new PDF diagrams.')
