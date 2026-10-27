from pathlib import Path
r=Path('D:/mathnote');f=r/'assets/tikz'
def edit(name,pairs):
 p=f/f'C084_{name}.tex';s=p.read_text(encoding='utf8')
 for a,b in pairs:
  assert a in s,a
  s=s.replace(a,b)
 p.write_text(s,encoding='utf8')
edit('first_look',[
 ('domain=-1.05:1.05','domain=-.65:1.05'),
 ('(1.6,3.7)','(2.15,1.85)'),('(4.05,1.3)','(3.9,1.1)'),
 ('(3,0)--(3,-1.1) node[below]','(3,0)--(4,-1.7) node[right,fill=white,inner sep=1pt]')])
edit('distance_projections',[
 ('(P)--(H) node[midway,right] {$|y_0|$}','(P)--(H)'),
 ('\\node[below,yshift=-20pt] at (H) {$H(x_0,0)$}','\\node[below] at (H) {$H$}'),
 ('(4.5,1.7)','(5.2,1.7)'),
 ('(3.75,-3)--(5,-3)','(3.75,-2.7)--(5,-2.7)'),
 ('(4.1,-3.7)','(5.6,-2.7)'),
 ('\\node at (7.1,.65)','\\node[anchor=west] at (9,2.3) {$H=(x_0,0),\\quad PH=|y_0|$};\n\\node at (7.1,.65)')])
edit('branch_reflection',[
 ('domain=-.85:.85','domain=-.55:.85'),
 ('\\fill (2.4,0) circle(2pt) node[below left] {$M(12/5,0)$};','\\fill (2.4,0) circle(2pt);\\draw (2.4,0)--(3,-1.25) node[below] {$M(12/5,0)$};'),
 ('\\fill (-2.4,0) circle(2pt) node[below right] {$N(-12/5,0)$};','\\fill (-2.4,0) circle(2pt);\\draw (-2.4,0)--(-3,-1.25) node[below] {$N(-12/5,0)$};')])
# Replace a nearly empty spill page with a concise, diagram-referenced checklist.
p=r/'03_conic/C084_hyperbola_focal_triangle_internal_angle_bisector/05_traps.tex'
p.write_text(r'''\clearpage
\begin{trapbox}
\input{assets/tikz/C084_normal_and_degenerate}
\begin{itemize}
\item \textbf{内角与外角混淆：}内角平分线沿切线，外角平分线沿法线；两者垂直，见上图。
\item \textbf{比值方向颠倒：}必须同侧对应：$F_1M/MF_2=PF_1/PF_2$，见普通三角形配图。
\item \textbf{把左支的截距写正：}$x_0$ 与 $m$ 同号，统一用 $x_0m=a^2$；且 $0<|m|<a<c$，见例1、例2对称图。
\item \textbf{混淆切点与交点：}$T=(\operatorname{sgn}(x_0)a,0)$ 是圆的轴上切点，$M=(a^2/x_0,0)$ 是角平分线的轴上交点。非顶点时 $T\ne M$，见方法四图。
\item \textbf{漏掉非退化条件：}必须 $y_0\ne0$。顶点处不能套三角形角平分线定理；顶点切线仍存在，见上图。
\item \textbf{循环论证：}方法三引用已知切线性质，只适合快速求截距；独立证明应走方法一，再由 $P,M$ 写出切线方程。
\item \textbf{坐标或焦距关系写错：}$P=(x_0,y_0)$、$M=(m,0)$ 满足乘积关系 $x_0m=a^2$；双曲线用 $c^2=a^2+b^2$。
\end{itemize}
\end{trapbox}
''',encoding='utf8')
print('Refined curve extents, angle labels, dimension labels and trap pagination.')
