from pathlib import Path
import json
root=Path('03_conic/C051_parabola_focal_radius_coordinate')
assets=Path('assets/tikz')
def put(path,text): path.write_text(text.strip()+'\n',encoding='utf-8')

# Three independent views use exactly the same scale and coordinate range.
parts=[r'\begin{tikzpicture}[font=\small,>=stealth]',
r'\draw[rounded corners=3pt,gray!45] (0,0) rectangle (14.2,10.2);',
r'\node at (7.1,9.65) {固定 $y^2=4x$：向右走得越远，焦半径越长};']
for k,(t,u,radius) in enumerate([(0,0,1),(1,2,2),(4,4,5)]):
    cx=2.15+4.65*k
    parts += [rf'\node at ({cx},8.7) {{$x_0={t}$}};',
              rf'\begin{{scope}}[shift={{({cx-.7},4.3)}},scale=.65]',
              r'\draw[->,gray] (-1.5,0)--(4.9,0) node[right] {$x$};',
              r'\draw[red!75!black,thick] (-1,-3.5)--(-1,4.6);',
              r'\draw[teal!75!black,thick,domain=-3.3:4.3,samples=100] plot ({\x*\x/4},\x);',
              r'\fill (1,0) circle(2pt) node[below=5pt] {$F$};']
    if t==0:
        parts += [r'\draw[blue!75!black,very thick] (0,0)--(1,0);',
                  r'\fill (0,0) circle(2pt) node[above=5pt] {$P=O$};']
    else:
        parts += [rf'\draw[orange!85!black,very thick] (-1,{u})--({t},{u});',
                  rf'\draw[blue!75!black,very thick] (1,0)--({t},{u});',
                  rf'\fill ({t},{u}) circle(2pt) node[below right=4pt] {{$P$}};',
                  r'\fill (0,0) circle(1.7pt) node[below left=3pt] {$O$};']
    parts += [r'\end{scope}',
              rf'\node[blue!75!black] at ({cx},1.55) {{$PF={t}+1={radius}$}};']
parts += [r'\node at (7.1,.6) {三图同尺度、焦点不变；$PF=x_0+1\ge1$，只有 $P=O$ 时最短。};',r'\end{tikzpicture}']
put(assets/'C051_position_and_minimum.tex','\n'.join(parts))

put(assets/'C051_coordinate_right_triangle.tex',r'''
% Exact model p=2, P=(4,4), F=(1,0), T=(4,0).
\begin{tikzpicture}[font=\small,>=stealth]
\draw[rounded corners=3pt,gray!45] (0,0) rectangle (14.2,9.8);
\node at (7.1,9.25) {坐标法看这个直角三角形：斜边 $PF$，两直角边 $FT$、$PT$};
\begin{scope}[shift={(2.0,2.8)},scale=1.05]
 \fill[blue!10] (1,0)--(4,0)--(4,4)--cycle;
 \draw[->,gray] (-.5,0)--(5.15,0) node[right] {$x$};
 \draw[->,gray] (0,-.5)--(0,4.7) node[above] {$y$};
 \draw[teal!75!black,thick,domain=0:4.25,samples=90] plot ({\x*\x/4},\x);
 \draw[blue!75!black,very thick] (1,0)--(4,4) node[pos=.55,left=4pt] {$PF=5$};
 \draw[orange!85!black,very thick] (1,0)--(4,0);
 \draw[violet,very thick] (4,0)--(4,4) node[midway,right=5pt] {$PT=4$};
 \draw[violet] (3.75,0)--(3.75,.25)--(4,.25);
 \fill (0,0) circle(2pt) node[below left=3pt] {$O$};
 \fill (1,0) circle(2pt) node[below=4pt] {$F$};
 \fill (4,0) circle(2pt) node[below=4pt] {$T$};
 \fill (4,4) circle(2pt) node[right=4pt] {$P(4,4)$};
 \draw[<->,orange!85!black] (1,-.8)--(4,-.8) node[midway,below] {$FT=4-1=3$};
\end{scope}
\node[anchor=west,align=left] at (9.3,6.4) {$FT=|x_0-p/2|$\\[8pt]$PT=|y_0|$\\[10pt]$PF^2=FT^2+PT^2$\\[8pt]图中：$5^2=3^2+4^2$};
\node at (7.1,1.05) {一般地，$PF^2=(x_0-p/2)^2+y_0^2=(x_0+p/2)^2$。};
\node at (7.1,.45) {代入 $y_0^2=2px_0$ 才能合成完全平方；最后用 $x_0+p/2>0$。};
\end{tikzpicture}
''')

put(assets/'C051_inverse_two_points.tex',r'''
% Exact example 2: y^2=8x, focus=(2,0), P=(4,+/-4sqrt(2)), radius=6.
\begin{tikzpicture}[font=\small,>=stealth]
\draw[rounded corners=3pt,gray!45] (0,0) rectangle (14.2,11.7);
\node at (7.1,11.15) {已知 $PF=6$：先确定竖线 $x=4$，再找上下两个交点};
\begin{scope}[shift={(3.2,5.7)},scale=.72]
 \draw[->,gray] (-2.6,0)--(6.1,0) node[right] {$x$};
 \draw[->,gray] (0,-6.5)--(0,6.5) node[above] {$y$};
 \draw[red!75!black,thick] (-2,-6.1)--(-2,6.1);
 \draw[teal!75!black,thick,domain=-6.15:6.15,samples=120] plot ({\x*\x/8},\x);
 \draw[violet,dashed,thick] (4,-6.2)--(4,6.2);
 \draw[orange!85!black,thick] (-2,{4*sqrt(2)})--(4,{4*sqrt(2)});
 \draw[orange!85!black,thick] (-2,{-4*sqrt(2)})--(4,{-4*sqrt(2)});
 \draw[blue!75!black,very thick] (2,0)--(4,{4*sqrt(2)});
 \draw[blue!75!black,very thick] (2,0)--(4,{-4*sqrt(2)});
 \fill (0,0) circle(2pt) node[below left=4pt] {$O$};
 \fill (2,0) circle(2pt) node[below left=4pt] {$F(2,0)$};
 \fill (4,{4*sqrt(2)}) circle(2pt) node[below right=4pt] {$P_+$};
 \fill (4,{-4*sqrt(2)}) circle(2pt) node[above right=4pt] {$P_-$};
 \node[above right=3pt,violet] at (4,0) {$x=4$};
 \node[left=3pt,red!75!black] at (-2,2.7) {$x=-2$};
\end{scope}
\node[anchor=west,align=left] at (8.7,8.1) {$y^2=8x$，$p/2=2$\\[10pt]$x_0+2=6$\\[5pt]$x_0=4$\\[10pt]$P_+=(4,4\sqrt2)$\\[6pt]$P_-=(4,-4\sqrt2)$\\[10pt]$P_+F=P_-F=6$};
\node at (7.1,.55) {同一横坐标给出同一焦半径；两点关于 $x$ 轴对称，距离相等。};
\end{tikzpicture}
''')

p=root/'02_explanation.tex'; s=p.read_text(encoding='utf-8')
start=s.index('\\textbf{边界也能看见：}')
end=s.index('若写成',start)
s=s[:start]+s[end:]
s+=r'''
\clearpage
\begin{explanationbox}
\textbf{点换位置，焦半径怎样变？}固定同一条抛物线，只改变点的位置。
\begin{center}\input{assets/tikz/C051_position_and_minimum.tex}\end{center}
三个位置分别给出 $1、2、5$。\textbf{决定长度的是沿开口的坐标距离}：
在 $y^2=2px$ 上，$x_0$ 每增加 $1$，焦半径就增加 $1$。
由于 $x_0\ge0$，$PF\ge p/2$；只有 $x_0=0$，即顶点 $P=O$ 时取等号。
上下对称的点横坐标相同，焦半径相同。
\end{explanationbox}
'''
put(p,s)

p=root/'03_proof.tex';s=p.read_text(encoding='utf-8')
marker='  \\textbf{\\textcolor{CProof}{方法三：'
pos=s.index(marker)
# A dedicated page for the coordinate method keeps the triangle and calculation together.
s=s[:pos]+'\\end{proofbox}\n\\clearpage\n\\begin{proofbox}\n'+s[pos:]
s=s.replace('  只利用焦点坐标和曲线上点的方程：',r'''
  过 $P$ 作 $PT\perp x$ 轴，$T=(x_0,0)$。图中取 $p=2$、$P=(4,4)$。
  \begin{center}\input{assets/tikz/C051_coordinate_right_triangle.tex}\end{center}
  一般情况下，$FT=|x_0-p/2|$、$PT=|y_0|$；即使 $T$ 在 $F$ 左侧，平方后仍相同。
  因 $P$ 在曲线上，代入 $y_0^2=2px_0$ 得
''')
# Fewer algebra lines retain each essential implication without an orphan page.
a=s.index('  \\begin{align*}');b=s.index('  最后一步',a)
s=s[:a]+r'''
  \[
  \begin{aligned}
    PF^2&=(x_0-p/2)^2+y_0^2\\
        &=x_0^2-px_0+p^2/4+2px_0=(x_0+p/2)^2,\\
    PF&=|x_0+p/2|=\boxed{x_0+p/2}.
  \end{aligned}
  \]
'''+s[b:]
# Four-direction justification remains explicit but compact.
put(p,s)

p=root/'04_examples.tex';s=p.read_text(encoding='utf-8')
a=s.index('\\textbf{\\textcolor{CExample}{例 2');b=s.index('\\medskip\n\\textbf{\\textcolor{CExample}{例 3',a)
inverse=r'''
\end{examplebox}
\clearpage
\begin{examplebox}
\textbf{\textcolor{CExample}{例 2（由距离反求坐标）}}
在 $y^2=8x$ 上，$PF=6$，求 $x_0$。
\begin{center}\input{assets/tikz/C051_inverse_two_points.tex}\end{center}
\textbf{读图求解：}准线是 $x=-2$，水平距离 $6$ 给出 $x_0=6-2=\boxed{4}$。
若继续求点，则 $y_0^2=32$，所以有上下两个点 $(4,\pm4\sqrt2)$。
\textbf{回验：}两点都有 $PF=\sqrt{(4-2)^2+32}=6$。
一般地，$x_0=r-p/2$：$r>p/2$ 时有两点，$r=p/2$ 时仅顶点，$r<p/2$ 时无解。
\end{examplebox}
\clearpage
\begin{examplebox}
'''
s=s[:a]+inverse+s[b:]
# First example now has a small page of its own; combine it with inverse introductory text instead.
# Put example1 at the end of the preceding short proof page? Keep section responsibility:
# place it before the inverse diagram on the same examples page.
s=s.replace('\\end{examplebox}\n\\clearpage\n\\begin{examplebox}\n\\textbf{\\textcolor{CExample}{例 2', '\\medskip\n\\textbf{\\textcolor{CExample}{例 2',1)
put(p,s)

p=root/'meta.json';m=json.loads(p.read_text(encoding='utf-8'))
m['remarks']+=' 再丰富：新增 assets/tikz/C051_position_and_minimum.tex（三位置同尺度比较与顶点最小值）、C051_coordinate_right_triangle.tex（方法三直角边与完全平方）、C051_inverse_two_points.tex（例2同一焦半径的上下两点及逆求坐标），替代相应变化、坐标构造和反求的口头描述。'
m['meta']['updated_at']='2026-10-25'
put(p,json.dumps(m,ensure_ascii=False,indent=2))
print('C051: 3 new teaching figures, 8 figures total.')
