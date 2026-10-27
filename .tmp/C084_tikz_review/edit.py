from pathlib import Path
import shutil,json,math
root=Path('D:/mathnote'); uid=root/'03_conic/C084_hyperbola_focal_triangle_internal_angle_bisector'
work=root/'.tmp/C084_tikz_review'; (work/'before').mkdir(parents=True,exist_ok=True)
for p in uid.glob('*'):
 if p.is_file(): shutil.copy2(p,work/'before'/p.name)
fig=root/'assets/tikz'; fig.mkdir(parents=True,exist_ok=True)
def frame(name,title,body,h=10):
 s=r'''\begin{center}
\begin{tikzpicture}[font=\small,>=stealth]
\draw[gray!40,rounded corners] (0,0) rectangle (14.2,HEIGHT);
\node[font=\small\bfseries] at (7.1,TITLEY) {TITLE};
BODY
\end{tikzpicture}
\end{center}
'''.replace('HEIGHT',str(h)).replace('TITLEY',str(h-.65)).replace('TITLE',title).replace('BODY',body)
 (fig/f'C084_{name}.tex').write_text(s,encoding='utf8')
def inp(name):return '\\input{assets/tikz/C084_'+name+'}\n'
# All geometric panels use actual Cartesian coordinates and isotropic scaling.
base=r'''
\coordinate (L) at (-5,0); \coordinate (R) at (5,0);
\coordinate (P) at (3.75,3); \coordinate (M) at (2.4,0);
\draw[blue!75!black,thick] (L)--(P);
\draw[orange!85!black,thick] (P)--(R);
\draw[gray] (L)--(R);
\draw[magenta!80!black,very thick] (M)--(P);
\foreach \q in {L,R,P,M} \fill (\q) circle (3pt);
\node[below left] at (L) {$F_1$}; \node[below right] at (R) {$F_2$};
\node[above left] at (P) {$P$}; \node[below left] at (M) {$M$};
'''
frame('first_look','先看主角：内角平分线 PM，也是 P 处切线',r'''
\begin{scope}[shift={(4.5,3.5)},scale=.58]
\draw[->,gray] (-5.8,0)--(6.2,0) node[right] {$x$};
\draw[->,gray] (0,-2)--(0,6.3) node[above] {$y$};
\draw[teal!75!black,thick,domain=-1.05:1.05,samples=90,variable=\t]
 plot ({3*cosh(\t)},{4*sinh(\t)});
\draw[teal!75!black,thick,domain=-1.05:1.05,samples=90,variable=\t]
 plot ({-3*cosh(\t)},{4*sinh(\t)});
BASE
\draw[magenta!80!black,thick] (1.7,-1.5556)--(4.9,5.5556);
\draw[magenta!80!black] (P) ++(-161.075:1.05) arc (-161.075:-114.228:1.05);
\draw[magenta!80!black] (P) ++(-114.228:1.3) arc (-114.228:-67.38:1.3);
\node[fill=white,inner sep=1pt] at (1.6,3.7) {$\alpha$};
\node[fill=white,inner sep=1pt] at (4.05,1.3) {$\alpha$};
\fill (0,0) circle(3pt) node[below left] {$O$};
\fill (3,0) circle(3pt); \draw (3,0)--(3,-1.1) node[below] {$A(a,0)$};
\end{scope}
\node[align=left,anchor=west] at (9.2,6.2) {紫线把顶角\\分成相等两份};
\node[align=left,anchor=west] at (9.2,4.3) {$P=(x_0,y_0)$\\$M=(m,0)$};
\node[align=left,anchor=west] at (9.2,2.4) {$\boxed{x_0m=a^2}$\\[6pt]右支：$0<m<a$};
\node at (7.1,.65) {图取 $a=3,b=4,\ P=(15/4,3)$；左支同样成立。};
'''.replace('BASE',base),10)
frame('elementary_bisector','第一步：只有普通三角形，不需要双曲线',r'''
\begin{scope}[shift={(4.5,3.1)},scale=.62]
\coordinate (A) at (-5,0); \coordinate (B) at (5,0);
\coordinate (C) at (3.75,3); \coordinate (D) at (2.4,0);
\fill[blue!8] (A)--(C)--(D)--cycle;
\fill[orange!12] (B)--(C)--(D)--cycle;
\draw[blue!75!black,very thick] (A)--(C) node[midway,above left] {$u$};
\draw[orange!85!black,very thick] (C)--(B) node[midway,right] {$v$};
\draw[blue!75!black,very thick] (A)--(D) node[midway,below] {$AD$};
\draw[orange!85!black,very thick] (D)--(B) node[midway,below] {$DB$};
\draw[magenta!80!black,very thick] (C)--(D);
\draw (C) ++(-161.075:1) arc (-161.075:-114.228:1);
\draw (C) ++(-114.228:1.2) arc (-114.228:-67.38:1.2);
\foreach \q in {A,B,C,D} \fill (\q) circle(3pt);
\node[below left] at (A) {$A$};\node[below right] at (B) {$B$};
\node[above] at (C) {$C$};\node[below,yshift=-20pt] at (D) {$D$};
\end{scope}
\node[align=left,anchor=west] at (9,5.3) {$\angle ACD=\angle DCB$\\[10pt]$\displaystyle\frac{AD}{DB}=\frac{u}{v}$};
\node[align=center] at (7.1,1) {同色对应：左边对左段，右边对右段。\\下一步只需换名：$A,B,C,D\ \longrightarrow\ F_1,F_2,P,M$。};
''',8)
frame('distance_projections','方法一：两个直角三角形，共用同一条高',r'''
\begin{scope}[shift={(4.4,3.2)},scale=.6]
BASE
\coordinate (H) at (3.75,0);
\draw[dashed,gray] (P)--(H) node[midway,right] {$|y_0|$};
\draw (3.45,0)--(3.45,.3)--(3.75,.3);
\fill (H) circle(3pt);\node[below,yshift=-20pt] at (H) {$H(x_0,0)$};
\draw[blue!75!black,<->] (-5,-1.8)--(3.75,-1.8) node[midway,fill=white] {$x_0+c$};
\draw[orange!85!black,<->] (3.75,-3)--(5,-3);
\node[orange!85!black] at (4.1,-3.7) {$|x_0-c|$};
\node[blue!75!black,above left] at (-.6,1.5) {$r_1$};
\node[orange!85!black,right] at (4.5,1.7) {$r_2$};
\end{scope}
\node[align=left,anchor=west] at (9,5.5) {$r_1^2=(x_0+c)^2+y_0^2$\\[12pt]$r_2^2=(x_0-c)^2+y_0^2$\\[12pt]相减，公共的高消去：\\[6pt]$r_1^2-r_2^2=4cx_0$};
\node at (7.1,.65) {图示 $0<x_0<c$；水平长度取绝对值，平方公式对左右两支均成立。};
'''.replace('BASE',base),9)
frame('incircle_tangent_lengths','方法四：先看三角形的等切线段，再代入焦距差',r'''
\begin{scope}[shift={(4.3,2.7)},scale=.68]
BASE
\coordinate (I) at (3,1.333333);\coordinate (T) at (3,0);
\coordinate (U) at (2.567568,2.594595);\coordinate (V) at (4.230769,1.846154);
\draw[teal!80!black,thick] (I) circle(1.333333);
\draw[teal!80!black,dashed] (I)--(T);
\draw[blue!75!black,very thick] (L)--(U);\draw[blue!75!black,very thick] (L)--(T);
\draw[orange!85!black,very thick] (R)--(V);\draw[orange!85!black,very thick] (R)--(T);
\draw[purple,very thick] (U)--(P)--(V);
\foreach \q in {I,T,U,V} \fill (\q) circle(3pt);
\node[left] at (I) {$I$}; \draw (T)--(3,-1) node[below] {$T$};
\node[above left] at (U) {$U$};\node[right] at (V) {$V$};
\end{scope}
\node[anchor=west,align=left] at (9,5.5) {$F_1U=F_1T$（蓝）\\[8pt]$F_2V=F_2T$（橙）\\[8pt]$PU=PV=\lambda$（紫）};
\node[align=center] at (7.1,1) {$r_1-r_2=F_1T-F_2T$，公共的 $\lambda$ 抵消。\\右支差为 $2a$，所以 $T=(a,0)$；而 $M=(a^2/x_0,0)$。};
'''.replace('BASE',base),8.5)
frame('unit_vector_sum','方法五：先把两条射线各取一段单位长度',r'''
\begin{scope}[shift={(5,5.6)},scale=2]
\coordinate (P) at (0,0); \coordinate (E) at (-.945946,-.324324);
\coordinate (G) at (.384615,-.923077);\coordinate (S) at (-.561331,-1.247401);
\draw[gray] (0,0)--(-1.55,-.53143);\draw[gray] (0,0)--(.61538,-1.47692);
\draw[blue!75!black,very thick,->] (P)--(E) node[midway,above left] {$\boldsymbol u_1$};
\draw[orange!85!black,very thick,->] (P)--(G) node[midway,right] {$\boldsymbol u_2$};
\draw[dashed] (E)--(S)--(G);
\draw[magenta!80!black,very thick,->] (P)--(S);
\foreach \q in {P,E,G,S} \fill (\q) circle(.8pt);
\node[above] at (P) {$P$};\node[left] at (E) {$E$};\node[right] at (G) {$G$};
\node[below] at (S) {$S$};
\end{scope}
\node[anchor=west,align=left] at (9,4.8) {$PE=PG=1$\\[8pt]平行四边形成为菱形\\[8pt]对角线 $PS$ 平分顶角};
\node[align=center] at (7.1,1) {$\overrightarrow{PS}=\boldsymbol u_1+\boldsymbol u_2$ 沿内角平分线。\\$PE$ 指向 $F_1$，$PG$ 指向 $F_2$；单位化后才能直接相加。};
''',8)
frame('branch_reflection','例1与例2：关于 y 轴对称，截距也跟着变号',r'''
\begin{scope}[shift={(7.1,3.3)},scale=.87]
\draw[->,gray] (-6,0)--(6,0) node[right] {$x$};
\draw[->,gray] (0,-1)--(0,4.6) node[above] {$y$};
\draw[teal!75!black,thick,domain=-.85:.85,samples=70,variable=\t] plot ({3*cosh(\t)},{4*sinh(\t)});
\draw[teal!75!black,thick,domain=-.85:.85,samples=70,variable=\t] plot ({-3*cosh(\t)},{4*sinh(\t)});
\draw[blue!60,dashed] (-5,0)--(3.75,3)--(5,0)--(-3.75,3)--cycle;
\draw[magenta!80!black,very thick] (2.4,0)--(3.75,3);
\draw[magenta!80!black,very thick] (-2.4,0)--(-3.75,3);
\fill (3.75,3) circle(2pt) node[above left] {$P(15/4,3)$};
\fill (-3.75,3) circle(2pt) node[above right] {$Q(-15/4,3)$};
\fill (2.4,0) circle(2pt) node[below left] {$M(12/5,0)$};
\fill (-2.4,0) circle(2pt) node[below right] {$N(-12/5,0)$};
\fill (-5,0) circle(2pt) node[below left] {$F_1$};\fill (5,0) circle(2pt) node[below right] {$F_2$};
\end{scope}
\node at (7.1,.75) {$x_0$ 与 $m$ 同号；左右两支都满足 $x_0m=9$。};
''',9)
frame('inverse_two_points','例3：先固定横坐标，再找上下两个交点',r'''
\begin{scope}[shift={(2.2,5.1)},scale=.48]
\draw[->,gray] (-1,0)--(9,0) node[right] {$x$};
\draw[->,gray] (0,-8)--(0,8) node[above] {$y$};
\draw[teal!75!black,thick,domain=-1.38:1.38,samples=100,variable=\t] plot ({3*cosh(\t)},{4*sinh(\t)});
\draw[dashed,orange!85!black] (6,-7.7)--(6,7.7);
\draw[magenta!80!black,thick] (6,6.9282)--(1.5,0)--(6,-6.9282);
\fill (1.5,0) circle(3pt);\node[below left] at (1.5,0) {$M$};
\fill (6,6.9282) circle(3pt);\node[above right] at (6,6.9282) {$P_+$};
\fill (6,-6.9282) circle(3pt);\node[below right] at (6,-6.9282) {$P_-$};
\node[right] at (6,2.4) {$x=6$};
\end{scope}
\node[align=left,anchor=west] at (8.8,6) {$m=3/2$\\[8pt]$x_0=9/m=6$\\[12pt]$P_+=(6,4\sqrt3)$\\[8pt]$P_-=(6,-4\sqrt3)$};
\node at (7.1,.65) {同一个轴交点，通常对应关于 x 轴对称的两个非顶点。};
''',10)
frame('normal_and_degenerate','防混淆：内分线沿切线；顶点处三角形退化',r'''
\begin{scope}[shift={(3.6,4.7)},scale=.4]
BASE
\draw[magenta!80!black] (1.7,-1.5556)--(4.9,5.5556);
\draw[gray,dashed] (0,4.6875)--(7,1.5375);
\node[above] at (6,2.1) {法线};
\end{scope}
\node at (3.7,2.5) {紫实线：内角平分线／切线};
\node at (3.7,1.6) {灰虚线：外角平分线／法线};
\begin{scope}[shift={(10.8,4.7)},scale=.42]
\draw[gray] (-5.8,0)--(6,0);
\draw[teal!75!black,domain=-.55:.55,samples=60,variable=\t] plot ({3*cosh(\t)},{4*sinh(\t)});
\draw[magenta!80!black] (3,-3)--(3,3);
\fill (-5,0) circle(4pt) node[below] {$F_1$};
\fill (5,0) circle(4pt) node[below] {$F_2$};
\fill (3,0) circle(4pt);\node[above left] at (3,0) {$P=A$};
\end{scope}
\node at (10.7,2.5) {$P,F_1,F_2$ 共线：没有三角形};
\node at (10.7,1.6) {顶点切线 $x=a$ 仍存在};
\node at (7.1,.65) {必须保留条件 $y_0\ne0$，才能谈焦点三角形的顶角内分线。};
'''.replace('BASE',base),9)
# Diagrams exist before editing exposition.
p=uid/'01_statement.tex';s=p.read_text(encoding='utf8');cut=s.index('该式对双曲线')
s=s[:cut]+inp('first_look')+'\\end{statementbox}\n\\clearpage\n\\begin{statementbox}\n'+s[cut:];p.write_text(s,encoding='utf8')
(uid/'02_explanation.tex').write_text(r'''\clearpage
\begin{explanationbox}
\textbf{先把双曲线拿掉：熟悉的角平分线定理。}
'''+inp('elementary_bisector')+r'''
\textbf{再把同一结构放回焦点三角形。}
将图中 $A,B,C,D$ 换成 $F_1,F_2,P,M$，令 $PF_1=r_1,PF_2=r_2$。
由于内角平分线交点在底边内部，$F_1M=c+m,MF_2=c-m$，于是
\[
\frac{c+m}{c-m}=\frac{r_1}{r_2}
\quad\Longrightarrow\quad
\boxed{m=c\frac{r_1-r_2}{r_1+r_2}}.
\]
这一步只用初中几何，尚未使用双曲线性质。

\textbf{最后才加入双曲线的两条信息：}
\[
r_1^2-r_2^2=4cx_0,\qquad |r_1-r_2|=2a.
\]
前式来自勾股定理与平方差（见方法一配图），后式来自双曲线定义。
把它们与角平分线所得的式子相乘，即得
\[
\boxed{mx_0=\frac{(r_1-r_2)^2}{4}=a^2}.
\]
先求出交点 $M$，再由 $P,M$ 两点写出直线，便能独立证明它就是切线。
内切圆切点 $T$ 与交点 $M$ 的区别，见方法四配图。
\end{explanationbox}
''',encoding='utf8')
p=uid/'03_proof.tex';s=p.read_text(encoding='utf8');s='\\clearpage\n'+s
s=s.replace('\\textbf{第1步：角平分线定理。}',inp('distance_projections')+'\\textbf{第1步：角平分线定理。}')
for heading in ['方法二：','方法三：','方法四：','方法五：','补充验算：']:
 s=s.replace('\\textbf{'+heading,'\\end{proofbox}\n\\clearpage\n\\begin{proofbox}\n\\textbf{'+heading)
s=s.replace('作 $\\triangle PF_1F_2$ 的内切圆，',inp('incircle_tangent_lengths')+'作 $\\triangle PF_1F_2$ 的内切圆，')
s=s.replace('设两条从 $P$ 指向焦点的',inp('unit_vector_sum')+'设两条从 $P$ 指向焦点的')
s=s.replace('故\n\\[\nF_1T-F_2T',r'令 $\sigma=\operatorname{sgn}(x_0)$，故'+'\n\\[\nF_1T-F_2T')
p.write_text(s,encoding='utf8')
p=uid/'04_examples.tex';s=p.read_text(encoding='utf8');s='\\clearpage\n'+s;s=s.replace('\\textbf{例1',inp('branch_reflection')+'\\textbf{例1',1)
s=s.replace('\\textbf{例3','\\end{examplebox}\n\\clearpage\n\\begin{examplebox}\n'+inp('inverse_two_points')+'\\textbf{例3',1)
s=s.replace('\\textbf{例4','\\end{examplebox}\n\\clearpage\n\\begin{examplebox}\n\\textbf{例4',1);p.write_text(s,encoding='utf8')
p=uid/'05_traps.tex';s=p.read_text(encoding='utf8');s='\\clearpage\n'+s.replace('\\begin{trapbox}','\\begin{trapbox}\n'+inp('normal_and_degenerate'),1)
s=s.replace('椭圆的切线/法线对应关系恰好与此不同。','')
s=s.replace('$T=(\\operatorname{sgn}x_0)a$（分支顶点）','$T=(\\operatorname{sgn}(x_0)a,0)$（分支顶点）');p.write_text(s,encoding='utf8')
p=uid/'06_summary.tex';s=p.read_text(encoding='utf8');s='\\clearpage\n'+s;p.write_text(s,encoding='utf8')
p=uid/'main.tex';s=p.read_text(encoding='utf8').replace('% 不附加 TikZ 图；待单独制作后再插入。','% 教学图由六段正文输入 assets/tikz/C084_*.tex。');p.write_text(s,encoding='utf8')
p=uid/'meta.json';m=json.loads(p.read_text(encoding='utf8'));m['interactive']['has_diagram']=True;m['meta']['updated_at']='2026-10-27';m['remarks']='C084 教学 TikZ：'+', '.join('assets/tikz/'+q.name for q in sorted(fig.glob('C084_*.tex')))+'。先呈现普通三角形角平分线，再映射焦点符号；第一页主图说明切线与内分线重合；投影、等切线段、菱形、左右对称、上下双解及退化图分别解除认知障碍。02_explanation已压缩原五段位置与性质说明，由图和必要公式承担解释。仅构建隔离预览，未覆盖正式PDF。';p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Created 8 TikZ diagrams and updated C084 only.')
