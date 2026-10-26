from pathlib import Path
import math,json,shutil
base=Path('03_conic/C056_ellipse_focal_chord_ratio');work=Path('.tmp/C056_tikz_review')
(work/'before').mkdir(parents=True,exist_ok=True)
for f in list(base.glob('*.tex'))+[base/'meta.json']:shutil.copy2(f,work/'before'/f.name)
def figfile(stem,body,height=12):
 Path(f'assets/tikz/C056_{stem}.tex').write_text(r'\begin{tikzpicture}[font=\small,>=stealth]'+'\n'+rf'\draw[rounded corners=3pt,gray!45] (0,0) rectangle (14.2,{height});'+'\n'+body+'\n'+r'\end{tikzpicture}'+'\n',encoding='utf8')
def point(deg,left=False):
 q=math.cos(math.radians(deg));v=math.sin(math.radians(deg));f=-4 if left else 4
 r=9/(5+(-4 if left else 4)*q);s=9/(5-(-4 if left else 4)*q)
 return (f+r*q,r*v),(f-s*q,-s*v),r,s
def xy(pt):return f'({pt[0]:.10f},{pt[1]:.10f})'
def panel(cx,cy,scale,deg,left=False,axes=True):
 A,B,r,s=point(deg,left);f=-4 if left else 4
 st=rf'\begin{{scope}}[shift={{({cx},{cy})}},scale={scale}]'+'\n'
 if axes:st+=r'\draw[->,gray] (-5.6,0)--(5.7,0);'+'\n'
 st+=r'\draw[teal!75!black,thick] (0,0) ellipse (5 and 3);'+'\n'
 st+=rf'\draw[blue!75!black,very thick] ({f},0)--{xy(A)};\draw[orange!85!black,very thick] ({f},0)--{xy(B)};'+'\n'
 st+=rf'\fill {xy(A)} circle(2pt) node[above=8pt] {{$A$}};\fill {xy(B)} circle(2pt) node[below=8pt] {{$B$}};'+'\n'
 # Keep the focus name away from the steep chord.
 anchor='below right=7pt' if deg<90 else 'above right=7pt'
 st+=rf'\fill ({f},0) circle(2pt) node[{anchor}] {{$'+('F_1' if left else 'F')+r'$};'+'\n'
 return st,A,B,r,s

A,B,r,s=point(60)
st,A,B,r,s=panel(4.5,5.4,.68,60)
st+=r'''
\draw[->,violet,thick] (4,0)--(5.2,{1.2*sqrt(3)});
\draw[violet] (4.8,0) arc[start angle=0,end angle=60,radius=.8];
\draw[gray,thin] (4.8,.45)--(6,1.1);
\node[violet,anchor=west] at (6.1,1.2) {$\theta$};
\end{scope}
\node[anchor=west,align=left] at (9.5,6.25)
 {先从右焦点 $F$ 出发\\[12pt]
 $\textcolor{blue!75!black}{FA=r>0}$：沿 $\theta$\\[12pt]
 $\textcolor{orange!85!black}{FB=s>0}$：反方向\\[15pt]
 图中 $\theta=60^\circ$\\[12pt]
 $r=9/7,\quad s=3$\\[12pt]
 $r/s=3/7<1$};
\node at (7.1,1.6) {蓝段与橙段组成整条弦：$AB=r+s$；$r,s$ 都是正长度。};
\node at (7.1,.6) {图取 $a=5,b=3,c=4$；端点方向一经规定，比值的分子分母才能确定。};'''
figfile('statement_overview',r'\node at (7.1,11.45) {第一眼先认方向：蓝色为正向端 $A$，橙色为反向端 $B$};'+st)

# Pure projection: no ellipse, focus or directrix.
figfile('pure_projection',r'''
\node at (7.1,11.45) {先看熟悉的投影：斜边乘余弦，就是水平位移};
\begin{scope}[shift={(5.2,6.1)},scale=1.55]
\draw[gray] (-2.1,0)--(1.65,0);
\draw[blue!75!black,very thick] (0,0)--(.6428571429,1.1134612334) node[midway,left=8pt] {$r$};
\draw[orange!85!black,very thick] (0,0)--(-1.5,-2.5980762114) node[midway,right=8pt] {$s$};
\draw[gray,dashed] (.6428571429,1.1134612334)--(.6428571429,0);
\draw[gray,dashed] (-1.5,-2.5980762114)--(-1.5,0);
\draw[blue!65!black,thick] (0,0)--(.6428571429,0);
\draw[orange!85!black,thick] (-1.5,0)--(0,0);
\draw[gray] (.5,0)--(.5,.14)--(.6428571429,.14);
\draw[gray] (-1.35,0)--(-1.35,-.15)--(-1.5,-.15);
\draw[violet] (.45,0) arc[start angle=0,end angle=60,radius=.45];
\node[violet] at (.83,.3) {$\theta$};
\fill (0,0) circle(2pt) node[below right=6pt] {$P$};
\fill (.6428571429,1.1134612334) circle(2pt) node[above=8pt] {$A$};
\fill (-1.5,-2.5980762114) circle(2pt) node[below=8pt] {$B$};
\node[above=9pt,orange!85!black] at (-.75,0) {$s\cos\theta$};
\node[below right=8pt,blue!75!black] at (.6428571429,0) {$r\cos\theta$};
\end{scope}
\node[anchor=west,align=left] at (9.1,7.2)
 {图中为锐角\\[14pt]从 $P$ 到 $A$：向右\\[12pt]水平位移 $+r\cos\theta$\\[18pt]
 从 $P$ 到 $B$：向左\\[12pt]水平位移 $-s\cos\theta$};
\node at (7.1,1.2) {先只认“走多远”和“横向走多远”，不需要椭圆的新知识。};
\node at (7.1,.5) {钝角时余弦为负，位移式仍成立；不要把位移的负号当成长度为负。};''')

# Full ellipse and corresponding right directrix, with two horizontal distances.
st,A,B,r,s=panel(4.2,6.25,.62,60)
st+=rf'''
\draw[violet,dashed] (6.25,-4.2)--(6.25,4.6);
\node[violet,above=7pt] at (6.25,4.6) {{$\ell$}};
\draw[blue!65!black,dashed] {xy(A)}--(6.25,{A[1]});
\draw[orange!85!black,dashed] {xy(B)}--(6.25,{B[1]});
\fill (6.25,{A[1]}) circle(1.4pt) node[right=6pt] {{$M$}};
\fill (6.25,{B[1]}) circle(1.4pt) node[right=6pt] {{$N$}};
\end{{scope}}
\node[anchor=west,align=left] at (9.5,7.6)
 {{$\ell:x=a^2/c>a$\\[12pt]
 $x_A=c+r\cos\theta$\\[12pt]$x_B=c-s\cos\theta$\\[15pt]
 $AF=e\,AM$\\[12pt]$BF=e\,BN$\\[15pt]
 正向、反向的投影\\[8pt]符号正好相反}};
\node at (7.1,2.8) {{$\textcolor{{blue!75!black}}{{AM=\dfrac{{b^2}}{{c}}-r\cos\theta}}$}};
\node at (7.1,1.65) {{$\textcolor{{orange!85!black}}{{BN=\dfrac{{b^2}}{{c}}+s\cos\theta}}$}};
\node at (7.1,.55) {{先保留投影结构，再用第二定义；准线在整个椭圆的右侧。}};
'''
figfile('directrix_projection',r'\node at (7.1,12.05) {再放回椭圆：从“横向位移”看清“到准线距离”};'+st,12.6)

# Both focal triangles, explicitly separate, with the same ellipse and scale.
tri=''
for cy,which in [(11.75,'A'),(5.55,'B')]:
 pt=A if which=='A' else B
 tri+=rf'\begin{{scope}}[shift={{(4.4,{cy})}},scale=.65]'+'\n'
 tri+=r'\draw[teal!60!black] (0,0) ellipse (5 and 3);'+'\n'
 color='blue!75!black' if which=='A' else 'orange!85!black'
 tri+=rf'\fill[{color},opacity=.07] (-4,0)--(4,0)--{xy(pt)}--cycle;\draw[gray,thick] (-4,0)--(4,0);\draw[{color},very thick] (4,0)--{xy(pt)};\draw[violet,thick] (-4,0)--{xy(pt)};'+'\n'
 tri+=rf'\fill (-4,0) circle(2pt) node[below=8pt] {{$F_1$}};\fill (4,0) circle(2pt) node[below right=7pt] {{$F$}};\fill {xy(pt)} circle(2pt) node['+('above=9pt' if which=='A' else 'below=9pt')+rf'] {{${which}$}};'+'\n'
 if which=='A':
  tri+=r'\draw[violet] (4.85*.0+4.75*.0+4.5,0) ++(0,0);'+'\n' if False else ''
  tri+=r'\draw[violet] (4.4,.692820323) arc[start angle=60,end angle=180,radius=.8];\node[violet] at (3.25,1.05) {$\pi-\theta$};'+'\n'
 else:tri+=r'\draw[violet] (3.2,0) arc[start angle=180,end angle=240,radius=.8];\node[violet] at (2.8,-.45) {$\theta$};'+'\n'
 tri+=r'\node[above=8pt] at (0,0) {$2c$};\end{scope}'+'\n'
 legend=(r'$AF=r$\\[12pt]$AF_1=2a-r$\\[15pt]夹角 $\pi-\theta$\\[12pt]余弦 $-\cos\theta$' if which=='A' else r'$BF=s$\\[12pt]$BF_1=2a-s$\\[15pt]夹角 $\theta$\\[12pt]余弦 $+\cos\theta$')
 tri+=rf'\node[anchor=west,align=left] at (9.2,{cy}) {{{legend}}};'+'\n'
figfile('two_focal_triangles',r'''\node at (7.1,16.45) {不用准线：分别看两个焦点三角形，夹角的余弦变号};
\node at (7.1,15.35) {上图只看 $F_1FA$：另一条边由椭圆定义补成 $2a-r$};'''+tri+r'''
\node at (7.1,8.7) {下图只看 $F_1FB$：另一条边补成 $2a-s$};
\node at (7.1,1.6) {两图同一椭圆、同一条弦、同一尺度；只切换正在使用的三角形。};
\node at (7.1,.6) {图取 $\theta=60^\circ$；一般 $0<\theta<\pi$ 时，两个夹角仍分别为 $\pi-\theta,\theta$。};''',17)

st=''
for cx,deg,cap in [(2.35,60,r'$AF<BF$'),(7.1,90,r'$AF=BF$'),(11.85,120,r'$AF>BF$')]:
 piece,_,_,_,_=panel(cx,6.4,.37,deg)
 st+=rf'\node at ({cx},10.6) {{$\theta={deg}^\circ$}};'+'\n'+piece+r'\end{scope}'+'\n'
 st+=rf'\node at ({cx},3.7) {{{cap}}};'+'\n'
 ratio={60:r'\dfrac37<1',90:'1',120:r'\dfrac73>1'}[deg]
 st+=rf'\node at ({cx},2.55) {{$AF/BF={ratio}$}};'+'\n'
figfile('angle_comparison',r'\node at (7.1,11.8) {只改变倾斜角：锐角短比长，直角等长，钝角长比短};'+st+r'\node at (7.1,1.1) {$a=5,b=3,c=4$ 固定；三图同尺度，蓝色始终表示 $FA$。};\node at (7.1,.45) {端点按方向命名，不按“左端”或“短段”命名。};',12.4)

st=''
for cx,deg,title in [(3.6,0,'最长：长轴'),(10.6,90,'最短：通径')]:
 piece,_,_,_,_=panel(cx,6.0,.5,deg)
 # Horizontal focus label above the axis; endpoints outside their vertices.
 if deg==0:
  piece=piece.replace('node[above=8pt] {$A$}','node[right=8pt] {$A$}').replace('node[below=8pt] {$B$}','node[left=8pt] {$B$}')
 st+=rf'\node at ({cx},10.2) {{{title}}};'+'\n'+piece+r'\end{scope}'+'\n'
 st+=rf'\node at ({cx},3.3) {{$AB='+('2a=10' if deg==0 else r'2b^2/a=18/5')+r'$};'+'\n'
figfile('chord_extremes',r'\node at (7.1,11.35) {焦点弦的两端边界：水平最长，竖直最短};'+st+r'\node at (7.1,1.6) {两图同尺度：焦点弦的两段之和通常不等于 $2a$。};\node at (7.1,.6) {$\displaystyle \frac{2b^2}{a}\le AB\le2a$；左端在通径取到，右端在长轴取到。};',12)

st=''
for cx,left,title in [(3.6,False,'从右焦点出发'),(10.6,True,'从左焦点出发')]:
 piece,_,_,_,_=panel(cx,6,.5,60,left)
 st+=rf'\node at ({cx},10.5) {{{title}}};'+'\n'+piece+r'\end{scope}'+'\n'
 ratio=r'AF/BF=3/7' if not left else r'AF_1/BF_1=7/3'
 st+=rf'\node at ({cx},3.15) {{${ratio}$}};'+'\n'
 denominator=r'AF=\dfrac{b^2}{a+c\cos\theta}' if not left else r'AF_1=\dfrac{b^2}{a-c\cos\theta}'
 st+=rf'\node at ({cx},1.95) {{${denominator}$}};'+'\n'
figfile('left_right_focus',r'\node at (7.1,11.65) {角度和端点规则不变，只换焦点：正向一段的长短反过来};'+st+r'\node at (7.1,.6) {两图均取 $a=5,b=3,c=4,\theta=60^\circ$，尺度相同。};',12.2)

# Diagrams are ready; adapt the surrounding text and paginate without shrinking.
def fig(stem):return '\\begin{center}\\input{assets/tikz/C056_'+stem+'.tex}\\end{center}\n'
def box(kind,body):return '\\clearpage\n\\begin{'+kind+'box}\n'+body+'\n\\end{'+kind+'box}\n'
statement=r'''设椭圆 $x^2/a^2+y^2/b^2=1$，$a>b>0$，$c^2=a^2-b^2$，$e=c/a\in(0,1)$；取右焦点 $F=(c,0)$。倾斜角 $0\le\theta<\pi$ 从 $x$ 轴正向逆时针量起。
'''+fig('statement_overview')+r'''\textbf{方向约定：}$A=F+r(\cos\theta,\sin\theta)$，$B=F-s(\cos\theta,\sin\theta)$，$r=AF>0,s=BF>0$。先定方向，再写比值：
\[
 \boxed{\frac{AF}{BF}=\frac{a-c\cos\theta}{a+c\cos\theta}=\frac{1-e\cos\theta}{1+e\cos\theta}}.
\]
交换 $A,B$ 后，比值必须取倒数。
'''
statement+=r'\end{statementbox}\clearpage\begin{statementbox}'+'\n'+r'''\textbf{两段长度与整条弦长}
\[
 \boxed{AF=\frac{b^2}{a+c\cos\theta}},\qquad
 \boxed{BF=\frac{b^2}{a-c\cos\theta}}.
\]
\[
 \boxed{AB=AF+BF=\frac{2ab^2}{a^2-c^2\cos^2\theta}}.
\]
$a>c>0$ 且 $|\cos\theta|\le1$，全部分母恒正。两段都是正长度，不是有向线段；焦点在弦内，所以弦长用两段相加。

\medskip
\textbf{方向与边界速查}
\[
 \theta=0:\ AF=a-c,\ BF=a+c;\qquad
 \theta=\frac\pi2:\ AF=BF=\frac{b^2}{a}.
\]
当 $\theta$ 为钝角时，正向端 $A$ 位于向左的射线，$AF>BF$。
'''
(base/'01_statement.tex').write_text(r'\begin{statementbox}'+'\n'+statement+'\n'+r'\end{statementbox}'+'\n',encoding='utf8')
ex=box('explanation',r'\textbf{第一步，先认普通斜线的水平投影。}暂时拿掉椭圆、焦点和准线，只看从中间点 $P$ 沿相反方向走到两端。'+fig('pure_projection')+r'两段长度 $r,s$ 都为正；向右的水平位移是正数，向左是负数。这里的正负属于位移，不属于长度。')
ex+=box('explanation',r'\textbf{第二步，再把这个结构放入椭圆。}普通点 $P$ 对应右焦点 $F(c,0)$；先写出横坐标，再看准线距离。'+fig('directrix_projection')+r'''右准线在 $x=a^2/c>a$，因此距离是“准线横坐标减端点横坐标”。结合第二定义：
\[
 r=e\left(\frac{b^2}{c}-r\cos\theta\right),\quad
 s=e\left(\frac{b^2}{c}+s\cos\theta\right).
\]
代入 $e=c/a$ 后，分别得到 $r(a+c\cos\theta)=b^2$、$s(a-c\cos\theta)=b^2$。尚未学习准线时，可直接使用后面的第一定义证明。''')
ex+=box('explanation',r'\textbf{第三步，看角度变化，不要把 $A$ 固定记成短段。}三图保留同一个椭圆和右焦点，只改变直线方向。'+fig('angle_comparison')+r'''锐角时 $\cos\theta>0$，$AF$ 的分母较大，蓝段较短；钝角时余弦为负，蓝段反而较长。
\[
 \frac{AF}{BF}=\frac{a-c\cos\theta}{a+c\cos\theta}.
\]
图形用于观察和验算，一般证明在下一节给出。水平长轴 $\theta=0$ 是最方便的符号检查：朝右只剩 $a-c$，所以 $AF$ 的分母必须用加号。''')
(base/'02_explanation.tex').write_text(ex,encoding='utf8')
proof=(base/'03_proof.tex').read_text(encoding='utf8')
proof=proof.replace(r'\begin{proofbox}',r'\clearpage'+'\n'+r'\begin{proofbox}')
needle=r'\textbf{第 1 步：为什么只设 $r,s$？}'
insert=box('proof',r'\textbf{方法二的图形准备：两个端点各有自己的焦点三角形。}先用定义补出第三边，再对照夹角。'+fig('two_focal_triangles')+r'上、下两图分别对应后文的两次余弦定理，不能只画 $AF$ 而让 $BF$ 靠想象。')
method2=proof.index(r'\textbf{方法二｜')
boxstart=proof.rfind(r'\clearpage',0,method2)
proof=proof[:boxstart]+insert+proof[boxstart:]
proof=proof.replace(needle,r'\textbf{先补齐水平情形：}$\theta=0$ 时端点为 $(a,0),(-a,0)$，两段为 $a-c,a+c$，公式直接成立。以下余弦定理推导取 $0<\theta<\pi$。'+'\n'+needle)
# Remove the old negative vertical spacing; use natural page layout.
proof=proof.replace(r'故\vspace{-5pt}',r'故')
(base/'03_proof.tex').write_text(proof,encoding='utf8')
examples=(base/'04_examples.tex').read_text(encoding='utf8').replace(r'\begin{examplebox}',r'\clearpage'+'\n'+r'\begin{examplebox}')
examples=examples.replace(r'\textbf{例 4｜',fig('chord_extremes')+r'\textbf{例 4｜')
examples=examples.replace(r'\textbf{例 5｜',fig('left_right_focus')+r'\textbf{例 5｜')
(base/'04_examples.tex').write_text(examples,encoding='utf8')
(base/'05_traps.tex').write_text('\\clearpage\n'+(base/'05_traps.tex').read_text(encoding='utf8'),encoding='utf8')
(base/'06_summary.tex').write_text('\\clearpage\n'+(base/'06_summary.tex').read_text(encoding='utf8'),encoding='utf8')
meta=json.loads((base/'meta.json').read_text(encoding='utf8'))
meta['interactive']['has_diagram']=True;meta['meta']['updated_at']='2026-10-26'
meta['remarks']+=' 新增七幅独立TikZ：assets/tikz/C056_statement_overview.tex（第一页方向主图）、C056_pure_projection.tex（先看普通线段投影）、C056_directrix_projection.tex（再引入椭圆与准线距离）、C056_two_focal_triangles.tex（AF/BF两次余弦定理完整配图）、C056_angle_comparison.tex（锐角直角钝角同比例比较）、C056_chord_extremes.tex（水平最长竖直最短）、C056_left_right_focus.tex（换焦点的符号变化）。替换原理解图输入并压缩重复空间口述，原图源及source.tex不覆盖；保留三种证明、准线补充和五道例题。'
(base/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('C056: seven teaching diagrams authored; all proofs and five examples retained.')
