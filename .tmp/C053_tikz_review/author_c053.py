from pathlib import Path
import math,json

base=Path('03_conic/C053_parabola_focal_chord_length_inclination')
out=Path('assets/tikz')
def write(name,s):
    (out/('C053_'+name+'.tex')).write_text(s.strip()+'\n',encoding='utf-8')
def start(h,title):
    return '\\begin{tikzpicture}[font=\\small,>=stealth]\n'+f'\\draw[rounded corners=3pt,gray!45] (0,0) rectangle (14.2,{h});\n\\node at (7.1,{h-.55}) {{{title}}};\n'
end='\\end{tikzpicture}\n'
def curve(lo=-2.3,hi=4.15):
    return f'\\draw[teal!75!black,thick,samples=120,domain={lo}:{hi},variable=\\t] plot ({{\\t*\\t/4}},{{\\t}});\n'
def axes(xmax=4.5):
    return f'\\draw[->,gray] (-1.5,0)--({xmax},0) node[above] {{$x$}};\n'
def focus():
    return r'\fill (1,0) circle(2pt) node[below right=5pt] {$F$};'+'\n'
def chord(theta,labels=True):
    q=math.radians(theta);u,v=math.cos(q),math.sin(q)
    r=2/(1-u);s=2/(1+u);A=(1+r*u,r*v);B=(1-s*u,-s*v)
    a=f'({A[0]:.9f},{A[1]:.9f})';b=f'({B[0]:.9f},{B[1]:.9f})'
    z=f'\\draw[blue!75!black,very thick] (1,0)--{a};\n\\draw[orange!85!black,very thick] (1,0)--{b};\n'
    z+=f'\\fill {a} circle(2pt)'+(r' node[above right=4pt] {$A$}' if labels else '')+';\n'
    z+=f'\\fill {b} circle(2pt)'+(r' node[below right=4pt] {$B$}' if labels else '')+';\n'
    return z

# 1: complete notation, two equal-distance constructions, coefficient meaning.
s=start(12,'先认图：焦点在弦内，两段焦半径相加才是整条弦')
s+=r'\begin{scope}[shift={(3.8,5.6)},scale=1.1]'+'\n'+axes()+curve()
s+=r'''
\draw[violet,densely dashed] (-1,-2.4)--(-1,4.2);
\node[rotate=90,violet] at (-1.4,1.6) {准线 $x=-1$};
\draw[blue!65!black,dashed] (-1,3.464101615)--(3,3.464101615);
\draw[orange!85!black,dashed] (-1,-1.154700538)--(.333333333,-1.154700538);
\fill (-1,3.464101615) circle(1.5pt) node[left=4pt] {$M$};
\fill (-1,-1.154700538) circle(1.5pt) node[left=4pt] {$N$};
\draw[gray,dotted] (1,.5)--(1,4.15);
\draw[<->,violet] (-1,4.1)--(1,4.1) node[midway,above] {$p=2$};
'''+chord(60)+focus()+r'''
\node[below left=4pt] at (0,0) {$O$};
\draw[violet,->] (1.65,0) arc[start angle=0,end angle=60,radius=.65];
\node[violet] at (1.94,.42) {$\theta$};
\end{scope}
\node[anchor=west,align=left] at (9.3,7.2)
 {$y^2=4x$，$p=2$\\[9pt]$F=(1,0)$\\[12pt]
 $\textcolor{blue!75!black}{r=FA=AM=4}$\\[9pt]
 $\textcolor{orange!85!black}{s=FB=BN=4/3}$\\[12pt]
 $L=r+s=16/3$};
\node at (7.1,2.1) {定义：到焦点的距离 $=$ 到准线的垂直距离。};
\node at (7.1,1.3) {$A=(3,2\sqrt3),\quad B=(1/3,-2\sqrt3/3),\quad\theta=60^\circ$。};
\node at (7.1,.5) {$p$ 是焦点到准线的距离；方程系数与通径长度都是 $2p=4$。};
'''+end
write('focal_chord_notation',s)

# 2: AF projection, same coordinates and scale as the notation figure.
s=start(12,r'先看正方向：到准线的距离 $AM=p+r\cos\theta$')
s+=r'\begin{scope}[shift={(3.8,5.6)},scale=1.1]'+'\n'+axes()+curve()
s+=r'''
\draw[violet,densely dashed] (-1,-2.3)--(-1,4.2);
\node[rotate=90,violet] at (-1.4,1.5) {准线};
\fill[blue!7] (1,0)--(1,3.464101615)--(3,3.464101615)--cycle;
\draw[gray,dashed] (1,0)--(1,3.464101615);
\draw[orange!85!black,thick,dashed] (-1,3.464101615)--(1,3.464101615);
\draw[blue!75!black,thick,dashed] (1,3.464101615)--(3,3.464101615)
 node[midway,above=5pt] {$r\cos\theta$};
\draw[blue!75!black,very thick] (1,0)--(3,3.464101615) node[midway,below right=5pt] {$r$};
\fill (3,3.464101615) circle(2pt) node[above right=4pt] {$A$};
\fill (-1,3.464101615) circle(1.5pt) node[left=4pt] {$M$};
\fill (1,3.464101615) circle(1.5pt) node[above left=4pt] {$H$};
\draw[gray,dotted] (1,3.8)--(1,4.2);
\draw[<->,orange!85!black] (-1,4.15)--(1,4.15) node[midway,above] {$MH=p$};
\draw[blue!75!black] (1,3.25)--(1.21,3.25)--(1.21,3.464101615);
\draw[violet,->] (1.65,0) arc[start angle=0,end angle=60,radius=.65];
\node[violet] at (1.94,.42) {$\theta$};
'''+focus()+r'''
\end{scope}
\node[anchor=west,align=left] at (9.3,7)
 {$\textcolor{blue!75!black}{FA=r}$\\[10pt]$AM=FA=r$\\[12pt]
 $MH=p$\\[9pt]$HA=r\cos\theta$\\[12pt]$AM=MH+HA$};
\node at (7.1,1.6) {同一模型：$y^2=4x$，$\theta=60^\circ$；蓝色三角形给水平投影。};
\node at (7.1,.65) {$\displaystyle r=p+r\cos\theta\quad\Longrightarrow\quad r=\frac{p}{1-\cos\theta}$};
'''+end
write('forward_projection',s)

# 3: BF projection, explicitly draw the other endpoint rather than imply it.
s=start(12,r'再看反方向：从 $p$ 中减去水平投影，$BN=p-s\cos\theta$')
s+=r'\begin{scope}[shift={(3.8,5.6)},scale=1.1]'+'\n'+axes()+curve(-1.65)
s+=r'''
\draw[violet,densely dashed] (-1,-3.2)--(-1,4.15);
\node[rotate=90,violet] at (-1.4,1.5) {准线};
\fill[orange!10] (1,0)--(1,-1.154700538)--(.333333333,-1.154700538)--cycle;
\draw[gray,dashed] (1,0)--(1,-1.154700538);
\draw[orange!85!black,thick,dashed] (-1,-1.154700538)--(.333333333,-1.154700538);
\draw[blue!65!black,dashed] (.333333333,-1.154700538)--(1,-1.154700538);
\draw[orange!85!black,very thick] (1,0)--(.333333333,-1.154700538);
\fill (.333333333,-1.154700538) circle(2pt) node[below left=5pt] {$B$};
\fill (-1,-1.154700538) circle(1.5pt) node[left=4pt] {$N$};
\fill (1,-1.154700538) circle(1.5pt) node[right=5pt] {$K$};
\draw[blue!65!black] (.82,-1.154700538)--(.82,-.974700538)--(1,-.974700538);
\draw[gray,dotted] (.333333333,-1.6)--(.333333333,-2.1);
\draw[gray,dotted] (1,-1.55)--(1,-3.05);
\draw[gray,dotted] (-1,-1.5)--(-1,-3.05);
\draw[<->,blue!65!black] (.333333333,-2.05)--(1,-2.05) node[midway,below] {$BK=s\cos\theta$};
\draw[<->,violet] (-1,-3)--(1,-3) node[midway,below] {$NK=p$};
'''+focus()+r'''
\end{scope}
\node[anchor=west,align=left] at (9.3,7)
 {$\textcolor{orange!85!black}{FB=s}$\\[10pt]$BN=FB=s$\\[12pt]
 $NK=p$\\[9pt]$BK=s\cos\theta$\\[12pt]$BN=NK-BK$};
\node at (7.1,1.25) {与上一图同一椭圆以外的模型：同一抛物线、同一方向、同一尺度。};
\node at (7.1,.5) {$\displaystyle s=p-s\cos\theta\quad\Longrightarrow\quad s=\frac{p}{1+\cos\theta}$};
'''+end
s=s.replace('与上一图同一椭圆以外的模型：','与上一图对照：')
write('backward_projection',s)

# 4: controlled comparison, exact same parabola and drawing scale.
s=start(11,'只转动过焦点的直线：越接近竖直越短，互补角等长')
for cx,theta,L in [(2.0,60,'16/3'),(6.6,90,'4'),(11.2,120,'16/3')]:
    s+=f'\\node at ({cx+.6},9.5) {{$\\theta={theta}^\\circ$}};\n'
    s+=f'\\begin{{scope}}[shift={{({cx},5.2)}},scale=.68]\n'+axes(4.4)+curve(-4,4)+chord(theta)+focus()+r'\end{scope}'+'\n'
    s+=f'\\node at ({cx+.6},1.65) {{$L={L}$}};\n'
s+=r'''
\node at (7.1,.65) {三图均为 $y^2=4x$、$F=(1,0)$，同尺度；通径 $L_{\min}=2p=4$。};
'''+end
write('angle_comparison',s)

# 5: reflect whole geometry, not merely a formula box.
s=start(10.7,'左右开口互为镜像：焦点换边，弦长保持不变')
for cx,sign,title in [(2.4,1,r'右开口 $y^2=4x$'),(11.8,-1,r'左开口 $y^2=-4x$')]:
    s+=f'\\node at ({3.6 if sign==1 else 10.6},9.3) {{{title}}};\n'
    s+=f'\\begin{{scope}}[shift={{({cx},5.2)}},scale=.85]\n'
    s+=r'\draw[->,gray] (-1.1,0)--(1.1,0);'+'\n'
    s+=f'\\draw[teal!75!black,thick,samples=120,domain=-2.2:4,variable=\\t] plot ({{{sign}*\\t*\\t/4}},{{\\t}});\n'
    s+=f'\\draw[blue!75!black,very thick] ({sign},0)--({3*sign},3.464101615);\n'
    s+=f'\\draw[orange!85!black,very thick] ({sign},0)--({sign/3},-1.154700538);\n'
    for x,y,l,anchor in [(sign,0,'F','below right' if sign==1 else 'below left'),(3*sign,3.464101615,'A','above right' if sign==1 else 'above left'),(sign/3,-1.154700538,'B','below right' if sign==1 else 'below left')]:
        s+=f'\\fill ({x},{y}) circle(2pt) node[{anchor}=4pt] {{${l}$}};\n'
    s+=r'\end{scope}'+'\n'
    s+=f'\\node at ({3.6 if sign==1 else 10.6},2.3) {{$\\theta={60 if sign==1 else 120}^\\circ,\\quad L=16/3$}};\n'
s+=r'''
\node at (7.1,1.2) {$\sin^2(180^\circ-\theta)=\sin^2\theta$，镜像前后长度相同。};
\node at (7.1,.5) {两边都取 $p=2>0$；开口向左，不代表长度带负号。};
'''+end
write('opening_reflection',s)

# 6: boundary and missing-focus counterexample at the same scale.
s=start(10.8,'先检查直线：轴线只有一个交点；竖直弦也必须经过焦点')
for cx,kind,title in [(2,0,'轴线：不构成焦点弦'),(6.6,1,'通径：合法且最短'),(11.2,2,'普通弦：不能套公式')]:
    s+=f'\\node at ({cx+.6},9.3) {{{title}}};\n'
    s+=f'\\begin{{scope}}[shift={{({cx},5.3)}},scale=.68]\n'+axes(4.4)+curve(-3.7,3.7)
    if kind==0:
        s+=r'\draw[red!75!black,very thick] (-.6,0)--(4.1,0);\fill (0,0) circle(2pt) node[below left=5pt] {$O$};'+'\n'
    else:
        x=kind;y=2*math.sqrt(x)
        s+=f'\\draw[blue!75!black,very thick] ({x},{-y})--({x},{y});\n'
        s+=f'\\fill ({x},{y}) circle(2pt);\\fill ({x},{-y}) circle(2pt);\n'
    s+=focus()+r'\end{scope}'+'\n'
    txt=[r'$\theta=0$，仅顶点 $O$',r'$x=1,\quad L=4$',r'$x=2,\quad L=4\sqrt2$'][kind]
    s+=f'\\node at ({cx+.6},1.85) {{{txt}}};\n'
s+=r'''
\node at (7.1,.65) {三图均为 $y^2=4x$，同尺度；后两条直线同为竖直，只有中图过 $F$。};
'''+end
write('validity_comparison',s)

# 7: rotate the model; theta remains measured from positive x.
s=start(12,r'开口向上时：角仍从横轴量，分母就要改用 $\cos^2\theta$')
s+=r'''
\begin{scope}[shift={(4.4,3.3)},scale=1.05]
\draw[->,gray] (-2.4,0)--(4.3,0) node[above] {$x$};
\draw[->,gray] (0,-.4)--(0,4.8) node[left] {$y$};
\draw[teal!75!black,thick,samples=120,domain=-2.2:4.1,variable=\t] plot ({\t},{\t*\t/4});
\draw[blue!75!black,very thick] (0,1)--(3.464101615,3);
\draw[orange!85!black,very thick] (0,1)--(-1.154700538,.333333333);
\draw[gray,dashed] (0,1)--(2,1);
\draw[violet,->] (.8,1) arc[start angle=0,end angle=30,radius=.8];
\node[violet] at (1.3,1.28) {$\theta$};
\draw[orange!85!black,->] (.95262794,1.55) arc[start angle=30,end angle=90,radius=1.1];
\node[orange!85!black] at (.62,2.34) {$\varphi$};
\fill (0,1) circle(2pt) node[above left=5pt] {$F$};
\fill (3.464101615,3) circle(2pt) node[above left=5pt] {$A$};
\fill (-1.154700538,.333333333) circle(2pt) node[above left=5pt] {$B$};
\node[below left=4pt] at (0,0) {$O$};
\end{scope}
\node[anchor=west,align=left] at (9.4,7)
 {$x^2=4y$，$F=(0,1)$\\[12pt]
 $\textcolor{violet}{\theta=30^\circ}$（从横轴量）\\[9pt]
 $\textcolor{orange!85!black}{\varphi=60^\circ}$（与竖轴）\\[12pt]
 $\sin^2\varphi=\cos^2\theta$\\[9pt]
 $L=4/\cos^230^\circ=16/3$};
\node at (7.1,1.5) {先认对称轴，再认角度：图中 $\theta+\varphi=90^\circ$。};
\node at (7.1,.65) {通用记法：用弦与对称轴的夹角 $\varphi$，总有 $L=2p/\sin^2\varphi$。};
'''+end
write('vertical_axis_angle',s)

print('Seven C053 diagram sources created.')
