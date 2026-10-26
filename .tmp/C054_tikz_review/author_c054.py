from pathlib import Path
import math
d=Path('assets/tikz')
def write(n,s): (d/('C054_'+n+'.tex')).write_text(s.strip()+'\n',encoding='utf-8')
def start(h,t):return '\\begin{tikzpicture}[font=\\small,>=stealth]\n'+f'\\draw[rounded corners=3pt,gray!45] (0,0) rectangle (14.2,{h});\n\\node at (7.1,{h-.55}) {{{t}}};\n'
end='\\end{tikzpicture}\n'

# Two diagrams share exactly the same Euclidean model and scale.
for mapped in [False,True]:
 s=start(12,'再认对应：相似关系保留，只补上抛物线的等距定义' if mapped else '先看初中几何：同一条斜线上的两个直角三角形相似')
 s+=r'\begin{scope}[shift={(1.2,4.7)},scale=1.4]'+'\n'
 s+=r'''
\fill[blue!7] (2,0)--(4,0)--(4,3.464101615)--cycle;
\fill[orange!10] (2,0)--(1.333333333,0)--(1.333333333,-1.154700538)--cycle;
'''
 if mapped:
  s+=r'''
\draw[teal!75!black,thick,samples=120,domain=-1.9:3.9,variable=\t] plot ({1+\t*\t/4},{\t});
\draw[violet,densely dashed] (0,-1.9)--(0,3.95);
\node[violet,rotate=90] at (-.5,1.5) {准线};
\draw[blue!65!black,dashed] (0,3.464101615)--(4,3.464101615);
\draw[orange!85!black,dashed] (0,-1.154700538)--(1.333333333,-1.154700538);
\fill (0,3.464101615) circle(1.5pt) node[left=5pt] {$M$};
\fill (0,-1.154700538) circle(1.5pt) node[left=5pt] {$N$};
\fill (0,0) circle(1.5pt) node[left=5pt] {$Q$};
\draw[gray,dashed] (0,0)--(1.333333333,0);
\node[above=6pt] at (.6,0) {$p$};
'''
 s+=r'''
\draw[gray,dashed] (4,3.464101615)--(4,0);
\draw[gray,dashed] (1.333333333,-1.154700538)--(1.333333333,0);
\draw[blue!75!black,very thick] (2,0)--(4,3.464101615) node[midway,above left=5pt] {$r$};
\draw[orange!85!black,very thick] (2,0)--(1.333333333,-1.154700538) node[midway,below right=6pt] {$s$};
\draw[blue!65!black,thick] (2,0)--(4,0) node[midway,below=7pt] {$u$};
\draw[orange!85!black,thick] (1.333333333,0)--(2,0) node[midway,above=6pt] {$v$};
\draw[gray!80] (3.8,0)--(3.8,.2)--(4,.2);
\draw[gray!80] (1.513333333,0)--(1.513333333,-.18)--(1.333333333,-.18);
\draw[violet] (2.48,0) arc[start angle=0,end angle=60,radius=.48];
\draw[violet] (1.52,0) arc[start angle=180,end angle=240,radius=.48];
\node[violet] at (2.76,.28) {$\alpha$};
\node[violet] at (1.4,-.28) {$\alpha$};
\fill (4,3.464101615) circle(2pt) node[above=8pt] {$A$};
\fill (1.333333333,-1.154700538) circle(2pt) node[below left=6pt] {$B$};
\fill (4,0) circle(1.5pt) node[below right=5pt] {$H$};
\fill (1.333333333,0) circle(1.5pt) node[above left=5pt] {$K$};
'''
 s+=r'\fill (2,0) circle(2pt) node[below right=5pt] {$'+('F' if mapped else 'P')+r'$};'+'\n'+r'\end{scope}'+'\n'
 if mapped:
  s+=r'''
\node[anchor=west,align=left] at (8.5,7.1)
 {普通点 $P\longrightarrow$ 焦点 $F$\\[13pt]
 焦准距 $FQ=p$\\[13pt]
 $\textcolor{blue!75!black}{r=AF=AM=p+u}$\\[10pt]
 $\textcolor{orange!85!black}{s=BF=BN=p-v}$\\[13pt]
 相似比仍是 $u/r=v/s$};
\node at (7.1,1.55) {几何给出比值相等，抛物线定义把投影换成 $r-p$ 与 $p-s$。};
\node at (7.1,.6) {$\displaystyle \frac{r-p}{r}=\frac{p-s}{s}\quad\Longrightarrow\quad\frac1r+\frac1s=\frac2p$};
'''
 else:
  s+=r'''
\node[anchor=west,align=left] at (8.5,7.1)
 {$A,P,B$ 共线\\[11pt]$PH\parallel PK$，$AH\parallel BK$\\[13pt]
 $PA=r,\quad PB=s$\\[10pt]
 $PH=u,\quad PK=v$\\[13pt]
 对应锐角同为 $\alpha$\\[9pt]
 两个直角三角形相似};
\node at (7.1,1.55) {$\triangle PAH\sim\triangle PBK$：比较同类边，不需要先学新曲线。};
\node at (7.1,.6) {$\displaystyle \frac{PH}{PA}=\frac{PK}{PB}\quad\Longrightarrow\quad\frac ur=\frac vs$};
'''
 s+=end
 write('parabola_similarity' if mapped else 'pure_similarity',s)

def graph(cx,cy,scale,theta=None,kind=None):
 s=f'\\begin{{scope}}[shift={{({cx},{cy})}},scale={scale}]\n'
 s+=r'\draw[->,gray] (-1.2,0)--(4.3,0) node[above] {$x$};'+'\n'
 s+=r'\draw[teal!75!black,thick,samples=120,domain=-3.85:3.85,variable=\t] plot ({\t*\t/4},{\t});'+'\n'
 if theta is not None:
  u,v=math.cos(math.radians(theta)),math.sin(math.radians(theta));r=2/(1-u);t=2/(1+u)
  A=(1+r*u,r*v);B=(1-t*u,-t*v)
  s+=f'\\draw[blue!75!black,very thick] (1,0)--({A[0]},{A[1]});\n\\draw[orange!85!black,very thick] (1,0)--({B[0]},{B[1]});\n'
  s+=f'\\fill ({A[0]},{A[1]}) circle(2pt) node[above=8pt] {{$A$}};\n\\fill ({B[0]},{B[1]}) circle(2pt) node[below left=6pt] {{$B$}};\n'
 elif kind==0:
  s+=r'\draw[red!75!black,very thick] (-.6,0)--(4.1,0);\fill (0,0) circle(2pt) node[below left=5pt] {$O$};'+'\n'
 elif kind==2:
  y=2*math.sqrt(2)
  s+=f'\\draw[gray,dashed] (2,{-y})--(1,0)--(2,{y});\n\\draw[blue!75!black,very thick] (2,{-y})--(2,{y});\n\\fill (2,{-y}) circle(2pt);\\fill (2,{y}) circle(2pt);\n'
 s+=r'\fill (1,0) circle(2pt) node['+('above=8pt' if kind==2 else 'above right=5pt' if theta==120 else 'below right=5pt')+r'] {$F$};'+'\n'+r'\end{scope}'+'\n'
 return s

s=start(12.5,'两段长度在变，倒数一增一减：双色条的总长度始终相同')
for cx,theta,a,b in [(1.9,60,.25,.75),(6.3,90,.5,.5),(10.7,120,.75,.25)]:
 s+=f'\\node at ({cx+.65},10.95) {{$\\theta={theta}^\\circ$}};\n'+graph(cx,6.6,.65,theta)
 left=cx-.7;w=3.35;cut=left+w*a
 s+=f'\\fill[blue!28] ({left},2.15) rectangle ({cut},2.55);\n\\fill[orange!35] ({cut},2.15) rectangle ({left+w},2.55);\n\\draw[gray] ({left},2.15) rectangle ({left+w},2.55);\n'
 s+=f'\\node at ({left+w*a/2},1.65) {{$\\textcolor{{blue!75!black}}{{{("1/4" if a==.25 else "1/2" if a==.5 else "3/4")}}}$}};\n'
 s+=f'\\node at ({cut+w*b/2},1.65) {{$\\textcolor{{orange!85!black}}{{{("1/4" if b==.25 else "1/2" if b==.5 else "3/4")}}}$}};\n'
 s+=f'\\node at ({cx+.65},3.25) {{$1/AF+1/BF=1$}};\n'
s+=r'''
\node at (7.1,.75) {$y^2=4x$，$p=2$；蓝色表示 $1/AF$，橙色表示 $1/BF$，总和为 $2/p=1$。};
'''+end
write('reciprocal_comparison',s)

s=start(11.5,'已知一段，另一段怎样变化？先看长度配对的曲线')
s+=r'''
\begin{scope}[shift={(1.1,2.2)},scale=.95]
\draw[->,gray] (0,0)--(7.8,0) node[below=7pt] {$r=AF$};
\draw[->,gray] (0,0)--(0,7.8) node[above right] {$s=BF$};
\draw[violet,densely dashed] (1,0)--(1,7.5);
\draw[violet,densely dashed] (0,1)--(7.5,1);
\draw[teal!75!black,very thick,samples=150,domain=1.155:7.5,variable=\t] plot ({\t},{\t/(\t-1)});
\node[below=5pt] at (0,0) {$0$};
\node[below=5pt,violet] at (1,0) {$1$};
\node[left=5pt,violet] at (0,1) {$1$};
\fill[blue!75!black] (2,2) circle(2.5pt);
\draw[blue!75!black,->] (3.3,4.4)--(2.05,2.1);
\node[blue!75!black,above,align=center] at (3.3,4.4) {通径\\$r=s=2$};
\fill[orange!85!black] (3,1.5) circle(2.5pt);
\draw[orange!85!black,->] (5.45,3.2)--(3.1,1.55);
\node[orange!85!black,above,align=center] at (5.45,3.2) {例1\\$r=3,\ s=3/2$};
\end{scope}
\node[anchor=west,align=left] at (9.3,6.6)
 {$p=2$，$\displaystyle s=\frac r{r-1}$\\[14pt]
 $r>1,\quad s>1$\\[12pt]
 一段变长，另一段变短\\[12pt]
 $r=1$ 没有有限配对\\[10pt]
 虚线只可逼近，不可取到};
\node at (7.1,.8) {图中每个点是一对长度 $(r,s)$，不是抛物线上的端点坐标。};
'''+end
write('length_pair_domain',s)

s=start(11.3,'先认条件：通径、普通竖弦、轴线，只有第一幅能直接用定理')
for cx,kind,title,txt in [(1.9,1,'过焦点的通径',r'$1/2+1/2=1$'),(6.3,2,'不经过焦点的普通弦',r'$1/3+1/3=2/3$'),(10.7,0,'轴线：只有一个交点',r'不构成有限两点弦')]:
 s+=f'\\node at ({cx+.65},9.75) {{{title}}};\n'
 s+=graph(cx,5.5,.65,90 if kind==1 else None,kind)
 s+=f'\\node at ({cx+.65},1.95) {{{txt}}};\n'
s+=r'''
\node at (7.1,.7) {三图同为 $y^2=4x$、$p=2$；普通弦的两端到 $F$ 都是 $3$，不满足倒数和 $1$。};
'''+end
write('validity_comparison',s)

# Explicit orthogonal maps: right, x-reflection, coordinate swap, clockwise rotation.
maps={'right':lambda x,y:(x,y),'left':lambda x,y:(-x,y),'up':lambda x,y:(y,x),'down':lambda x,y:(y,-x)}
s=start(16.7,'同一条焦点弦翻折、转向：长度不变，倒数和也不变')
for name,cx,cy,title in [('right',2.2,11.8,r'$y^2=4x$'),('left',11.9,11.8,r'$y^2=-4x$'),('up',3.4,3.7,r'$x^2=4y$'),('down',10.7,6.5,r'$x^2=-4y$')]:
 top=name in ['right','left'];tx=3.5 if name=='right' else 10.7 if name=='left' else cx
 s+=f'\\node at ({tx},{14.85 if top else 8.3}) {{{title}}};\n\\begin{{scope}}[shift={{({cx},{cy})}},scale=.62]\n'
 pts=[maps[name](t*t/4,t) for t in [(-1.9+i*5.8/120) for i in range(121)]]
 s+='\\draw[teal!75!black,thick] plot coordinates {'+' '.join(f'({x:.8f},{y:.8f})' for x,y in pts)+'};\n'
 F=maps[name](1,0);A=maps[name](3,2*math.sqrt(3));B=maps[name](1/3,-2*math.sqrt(3)/3)
 s+=f'\\draw[blue!75!black,very thick] ({F[0]},{F[1]})--({A[0]},{A[1]});\n\\draw[orange!85!black,very thick] ({F[0]},{F[1]})--({B[0]},{B[1]});\n'
 anchors={'right':['above=8pt','below left=6pt','below right=5pt'],'left':['above=8pt','below right=6pt','below left=5pt'],'up':['above left=6pt','above=10pt','above left=5pt'],'down':['below left=6pt','below=10pt','below left=5pt']}[name]
 for X,l,anc in zip([A,B,F],['A','B','F'],anchors):s+=f'\\fill ({X[0]},{X[1]}) circle(2pt) node[{anc}] {{${l}$}};\n'
 s+='\\end{scope}\n'
s+=r'''
\node at (7.1,9.7) {上排为左右镜像；下排为相应的上下开口。};
\node at (7.1,2.3) {四图同尺度，均有 $p=2,\quad AF=4,\quad BF=4/3$。};
\node at (7.1,1.4) {翻折、旋转保持两段长度；一般焦点弦也同样对应。};
\node at (7.1,.55) {$\displaystyle \frac1{AF}+\frac1{BF}=\frac14+\frac34=1=\frac2p$};
'''+end
write('four_openings',s)
print('Six C054 diagram sources created.')
