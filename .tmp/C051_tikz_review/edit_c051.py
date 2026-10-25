from pathlib import Path
import json

root = Path('03_conic/C051_parabola_focal_radius_coordinate')
tikz = Path('assets/tikz')
def put(name, text):
    Path(name).write_text(text.strip()+'\n', encoding='utf-8')

put(tikz/'C051_focus_directrix_split.tex', r'''
% Exact representative: p=2, P=(4,4), F=(1,0), PF=PQ=5.
\begin{tikzpicture}[>=stealth,font=\small]
\draw[rounded corners=3pt,gray!45] (0,0) rectangle (14.2,10.4);
\node at (7.1,9.85) {斜线换水平线：$PF=PQ=QH+HP$};
\begin{scope}[shift={(3.3,3.4)},scale=0.88]
  \draw[->,gray] (-1.8,0)--(5.9,0) node[right] {$x$};
  \draw[->,gray] (0,-2.6)--(0,5.5) node[above] {$y$};
  \draw[red!75!black,thick] (-1,-2.4)--(-1,5.3);
  \draw[teal!75!black,thick,domain=-2.3:4.6,samples=100] plot ({\x*\x/4},\x);
  \draw[blue!75!black,very thick] (1,0)--(4,4) node[pos=.48,right=3pt] {$PF$};
  \draw[violet,very thick] (-1,4)--(0,4);
  \draw[orange!85!black,very thick] (0,4)--(4,4);
  \draw[gray,dashed] (4,0)--(4,4);
  \draw[red!75!black] (-1,3.7)--(-.7,3.7)--(-.7,4);
  \draw[<->,violet] (-1,4.75)--(0,4.75) node[midway,above] {$p/2$};
  \draw[<->,orange!85!black] (0,4.75)--(4,4.75) node[midway,above] {$x_0$};
  \fill (-1,4) circle(2pt) node[left=3pt] {$Q$};
  \fill (0,4) circle(2pt) node[below left=2pt] {$H$};
  \fill (4,4) circle(2pt) node[right=4pt] {$P(x_0,y_0)$};
  \fill (0,0) circle(2pt) node[below left=3pt] {$O$};
  \fill (1,0) circle(2pt) node[below=4pt] {$F$};
  \node[below=4pt] at (4,0) {$x_0$};
  \node[left,align=center] at (-1,-1.5) {准线 $l$\\$x=-p/2$};
\end{scope}
\node[align=left,anchor=west] at (10.2,6.6) {$P$ 在抛物线上\\[6pt]$\color{blue!75!black}PF=PQ$\\[12pt]$QH=p/2$\\[6pt]$HP=x_0$};
\node at (7.1,1.15) {$\displaystyle PF=\textcolor{violet}{\frac p2}+\textcolor{orange!85!black}{x_0}$};
\node at (7.1,.5) {图取 $y^2=4x$、$P(4,4)$：两段 $1+4$，焦半径就是 $5$。};
\end{tikzpicture}
''')

put(tikz/'C051_math_audit_geometry.tex', r'''
% Exact representative: y^2=4x, p=2; latus rectum endpoints (1,+/-2).
\begin{tikzpicture}[>=stealth,font=\small]
\draw[rounded corners=3pt,gray!45] (0,0) rectangle (14.2,9.9);
\node at (7.1,9.35) {看清三种长度：$OF=p/2$，焦准距 $p$，通径 $2p$};
\begin{scope}[shift={(4.4,5.2)},scale=1.05]
 \draw[->,gray] (-1.8,0)--(3.7,0) node[right] {$x$};
 \draw[->,gray] (0,-2.6)--(0,2.8) node[above] {$y$};
 \draw[red!75!black,thick] (-1,-2.4)--(-1,2.6);
 \draw[teal!75!black,thick,domain=-2.7:2.7,samples=90] plot ({\x*\x/4},\x);
 \draw[blue!75!black,very thick] (0,0)--(1,0);
 \draw[orange!85!black,very thick] (1,-2)--(1,2);
 \fill (0,0) circle(2pt) node[below left=3pt] {$O$};
 \fill (1,0) circle(2pt) node[right=4pt] {$F$};
 \fill (-1,0) circle(2pt) node[below left=3pt] {$D$};
 \fill (1,2) circle(2pt) node[above right=3pt] {$A$};
 \fill (1,-2) circle(2pt) node[below right=3pt] {$B$};
 \draw[<->,blue!75!black] (0,-.8)--(1,-.8) node[midway,below] {$p/2$};
 \draw[gray,dotted] (-1,-2.4)--(-1,-3.1);
 \draw[gray,dotted] (1,-2.4)--(1,-3.1);
 \draw[<->,violet] (-1,-3)--(1,-3) node[midway,below] {$DF=p$};
 \draw[gray,dotted] (1,2)--(2.8,2);
 \draw[gray,dotted] (1,-2)--(2.8,-2);
 \draw[<->,orange!85!black] (2.6,-2)--(2.6,2) node[midway,right=3pt] {$AB=2p$};
 \node[left] at (-1,2) {准线};
\end{scope}
\node[anchor=west,align=left] at (9.5,6) {$y^2=4x$，$p=2$\\[8pt]$OF=1$\\[5pt]$DF=2$\\[5pt]$AF=FB=2$\\[5pt]$AB=4$};
\node at (7.1,1.15) {公式加的是蓝段 $OF=p/2$，不是半通径 $AF=p$。};
\node at (7.1,.5) {当 $P$ 到达顶点 $O$，沿开口的距离变为 $0$，焦半径最短为 $OF$。};
\end{tikzpicture}
''')

put(tikz/'C051_area_height.tex', r'''
% Exact example 3: P=(4,4), F=(1,0), triangle area 2.
\begin{tikzpicture}[>=stealth,font=\small]
\draw[rounded corners=3pt,gray!45] (0,0) rectangle (14.2,8.7);
\node at (7.1,8.15) {例 3：先由 $PF=5$ 求坐标，再找 $\triangle OFP$ 的底和高};
\begin{scope}[shift={(2.2,2.3)},scale=1.05]
 \fill[blue!12] (0,0)--(1,0)--(4,4)--cycle;
 \draw[->,gray] (-.6,0)--(5.2,0) node[right] {$x$};
 \draw[->,gray] (0,-.5)--(0,4.8) node[above] {$y$};
 \draw[teal!75!black,thick,domain=-.9:4.25,samples=90] plot ({\x*\x/4},\x);
 \draw[blue!75!black,thick] (0,0)--(4,4)--(1,0);
 \draw[blue!75!black,very thick] (0,0)--(1,0);
 \draw[violet,thick,dashed] (4,0)--(4,4) node[midway,right=4pt] {高 $4$};
 \draw[violet] (3.75,0)--(3.75,.25)--(4,.25);
 \fill (0,0) circle(2pt) node[below left=3pt] {$O$};
 \fill (1,0) circle(2pt) node[below=4pt] {$F(1,0)$};
 \fill (4,0) circle(2pt) node[below=4pt] {$H(4,0)$};
 \fill (4,4) circle(2pt) node[right=4pt] {$P(4,4)$};
 \draw[<->,blue!75!black] (0,-.9)--(1,-.9) node[midway,below] {底 $1$};
\end{scope}
\node[anchor=west,align=left] at (9.4,5.1) {$x_0=5-1=4$\\[8pt]$|y_0|=4$\\[10pt]$\displaystyle S=\frac12\cdot1\cdot4=2$};
\node at (7.1,.55) {高落在底边的延长线上也成立；取 $P(4,-4)$，面积仍为 $2$。};
\end{tikzpicture}
''')

# Rotate the entire exact model, including the directrix, focus and perpendicular.
parts=[r'\begin{tikzpicture}[>=stealth,font=\small]',
 r'\draw[rounded corners=3pt,gray!45] (0,0) rectangle (14.2,13.6);',
 r'\node at (7.1,13.05) {四种开口，同一件事：焦半径等于到准线的垂直距离};']
panels=[(3.6,10,0,'向右：$y^2=2px$',r'PF=x_0+\frac p2'),
        (10.6,10,180,'向左：$y^2=-2px$',r'PF=-x_0+\frac p2'),
        (3.6,4,90,'向上：$x^2=2py$',r'PF=y_0+\frac p2'),
        (10.6,4,270,'向下：$x^2=-2py$',r'PF=-y_0+\frac p2')]
for cx,cy,angle,title,formula in panels:
    # Label directions remain readable while points rotate mathematically.
    parts += [rf'\node at ({cx},{cy+2.05}) {{{title}}};',
              rf'\begin{{scope}}[shift={{({cx},{cy-.2})}},scale=.64]',
              r'\draw[->,gray] (-2.7,0)--(2.7,0) node[right] {$x$};',
              r'\draw[->,gray] (0,-2.7)--(0,2.7) node[above] {$y$};',
              rf'\begin{{scope}}[rotate={angle}]',
              r'\draw[teal!75!black,thick,domain=-2.45:2.45,samples=90] plot ({\x*\x/4},\x);',
              r'\draw[red!75!black,thick] (-1,-2.5)--(-1,2.5);',
              r'\draw[orange!85!black,very thick] (-1,2)--(1,2);',
              r'\draw[blue!75!black,very thick] (1,0)--(1,2);',
              r'\draw[red!75!black] (-1,1.7)--(-.7,1.7)--(-.7,2);',
              r'\fill (1,2) circle(2pt) node[above right=2pt] {$P$};',
              r'\fill (-1,2) circle(2pt) node[above left=2pt] {$Q$};',
              r'\fill (1,0) circle(2pt) node[below right=2pt] {$F$};',
              r'\fill (0,0) circle(1.7pt) node[below left=2pt] {$O$};',
              r'\end{scope}\end{scope}',
              rf'\node at ({cx},{cy-2.5}) {{$\displaystyle {formula}$}};']
parts += [r'\node at (7.1,.65) {四图均取 $p=2$；橙段 $PQ$ 与蓝段 $PF$ 都长 $2$，红线为准线。};',r'\end{tikzpicture}']
put(tikz/'C051_four_openings.tex','\n'.join(parts))

parts=[r'\begin{tikzpicture}[>=stealth,font=\small]',
 r'\draw[rounded corners=3pt,gray!45] (0,0) rectangle (14.2,9.6);',
 r'\node at (7.1,9.05) {横坐标相同，也必须先检查点是否在抛物线上};']
for offset,valid in [(2.2,True),(9.2,False)]:
    parts += [rf'\begin{{scope}}[shift={{({offset},3.6)}},scale=.78]',
              r'\draw[->,gray] (-1.6,0)--(4.6,0) node[right] {$x$};',
              r'\draw[->,gray] (0,-1.2)--(0,4.9) node[above] {$y$};',
              r'\draw[red!75!black,thick] (-1,-1.1)--(-1,4.8);',
              r'\draw[teal!75!black,thick,domain=-1:4.1,samples=90] plot ({\x*\x/4},\x);',
              r'\fill (0,0) circle(1.7pt) node[below left=2pt] {$O$};',
              r'\fill (1,0) circle(2pt) node[below=3pt] {$F$};']
    if valid:
        parts += [r'\draw[orange!85!black,very thick] (-1,{sqrt(12)})--(3,{sqrt(12)});',
                  r'\draw[blue!75!black,very thick] (1,0)--(3,{sqrt(12)});',
                  r'\fill (3,{sqrt(12)}) circle(2pt) node[above right=2pt] {$P$};',
                  r'\fill (-1,{sqrt(12)}) circle(2pt) node[left=2pt] {$Q$};',
                  r'\draw[gray,dashed] (3,0)--(3,{sqrt(12)});',
                  r'\node[below] at (3,0) {$3$};']
    else:
        parts += [r'\draw[orange!85!black,very thick] (-1,0)--(3,0);',
                  r'\draw[blue!75!black,very thick] (1,0)--(3,0);',
                  r'\draw[<->,orange!85!black] (-1,-1.6)--(3,-1.6) node[midway,below] {$RQ=4$};',
                  r'\draw[<->,blue!75!black] (1,1)--(3,1) node[midway,above] {$RF=2$};',
                  r'\fill (3,0) circle(2pt) node[below right=3pt] {$R(3,0)$};',
                  r'\fill (-1,0) circle(2pt) node[below left=2pt] {$Q$};']
    parts += [r'\end{scope}']
    if valid:
        parts += [rf'\node[align=center] at ({offset+1},1.55) {{$P(3,2\sqrt3)$ 在 $y^2=4x$ 上\\[6pt]$PF=PQ=3+1=4$}};']
    else:
        parts += [rf'\node[align=center] at ({offset+1},1.05) {{$R(3,0)$ 不在 $y^2=4x$ 上\\[6pt]$RF\ne RQ$，不能套公式}};']
parts += [r'\end{tikzpicture}']
put(tikz/'C051_on_curve_requirement.tex','\n'.join(parts))

put(root/'02_explanation.tex', r'''
\clearpage
\begin{explanationbox}
\textbf{先看一个真点：}$y^2=4x$ 上的 $P(4,4)$，焦点为 $F(1,0)$。
从 $P$ 向准线作垂线，垂足为 $Q$；与 $y$ 轴交于 $H$。
\begin{center}\input{assets/tikz/C051_focus_directrix_split.tex}\end{center}
\textbf{只看两件事：}点在抛物线上，所以蓝色焦半径 $PF=PQ$；水平的 $PQ$ 又恰好分成紫段 $p/2$ 和橙段 $x_0$。
\[
  \boxed{PF=PQ=QH+HP=\frac p2+x_0}.
\]
图取 $p=2$，但分段关系对任意 $p>0$、任意曲线上点都成立（顶点处 $H=P$）。
\textbf{记忆动作：}遇到焦半径，先找准线，再量沿开口方向的距离。
\end{explanationbox}
\clearpage
\begin{explanationbox}
\textbf{公式里为什么加 $p/2$？}顶点在焦点与准线的正中间。
\begin{center}\input{assets/tikz/C051_math_audit_geometry.tex}\end{center}
\textbf{参数不混淆：}$DF=p$，$DO=OF=p/2$；通径 $AB=2p$，半通径 $AF=FB=p$。
因此公式中的常数是 $OF$，不是半通径。

\medskip
\textbf{边界也能看见：}$PF=x_0+p/2\ge p/2$，且只有 $P=O$ 时取等号。
已知 $PF=r$ 时可逆求 $x_0=r-p/2$，须有 $r\ge p/2$。
若写成 $y^2=4ax$，则 $a=p/2$，公式相应为 $PF=x_0+a$。
\end{explanationbox}
''')

# Keep all three mathematically correct methods; shorten duplicated verbal construction.
proof=(root/'03_proof.tex').read_text(encoding='utf-8')
start=proof.index('  \\textbf{只看水平线：}')
end=proof.index('  \\medskip', start)
proof=proof[:start]+r'''
  直接使用理解说明主图中的 $Q(-p/2,y_0)$、$H(0,y_0)$：
  $Q,H,P$ 从左至右排列（允许 $H=P$），因此
  \[
    PF=PQ=QH+HP=\frac p2+x_0.
  \]
  其中 $PF=PQ$ 用抛物线定义，最后一步用两段水平长度相加。

'''+proof[end:]
put(root/'03_proof.tex', '\\clearpage\n'+proof)

# Retain user's seven examples, compacting repetitive prose in the first three.
examples=(root/'04_examples.tex').read_text(encoding='utf-8')
tail=examples[examples.index('  \\medskip\n  \\textbf{\\textcolor{CExample}{例 4'):]
put(root/'04_examples.tex', r'''
\clearpage
\begin{examplebox}
\textbf{\textcolor{CExample}{例 1（由坐标求距离）}}
在 $y^2=4x$ 上，$P$ 的横坐标为 $3$，求 $PF$。
\textbf{解：}$2p=4$，故 $p/2=1$，$PF=3+1=\boxed{4}$。
\textbf{回验：}$y_0^2=12$，用两点距离得 $\sqrt{(3-1)^2+12}=4$。

\medskip
\textbf{\textcolor{CExample}{例 2（由距离反求坐标）}}
在 $y^2=8x$ 上，$PF=6$，求 $x_0$。
\textbf{解：}$p/2=2$，$x_0+2=6$，所以 $x_0=\boxed{4}$。
\textbf{回验：}$y_0^2=32$，$\sqrt{(4-2)^2+32}=6$，且 $x_0\ge0$。

\medskip
\textbf{\textcolor{CExample}{例 3（焦半径转坐标，再求面积）}}
在 $y^2=4x$ 上，$PF=5$，求 $\triangle OFP$ 的面积。
\begin{center}\input{assets/tikz/C051_area_height.tex}\end{center}
\textbf{解：}$F(1,0)$；由 $x_0+1=5$ 得 $x_0=4$。
代回 $y_0^2=4x_0=16$，得 $y_0=\pm4$。
底 $OF=1$，高 $|y_0|=4$，所以 $S=\frac12\cdot1\cdot4=\boxed{2}$。
\textbf{回验：}$PF=\sqrt{(4-1)^2+4^2}=5$。
\end{examplebox}
\clearpage
\begin{examplebox}
'''+tail)

put(root/'05_traps.tex', r'''
\clearpage
\begin{trapbox}
\textbf{\textcolor{CTrap}{误区一：换开口方向，还照抄 $x_0+p/2$。}}
左右开口量水平距离，上下开口量竖直距离；向左、向下时相应坐标非正，须取相反数。
\begin{center}\input{assets/tikz/C051_four_openings.tex}\end{center}
四式的共同结构都是 $PF=t+p/2$，$t\ge0$。
不能把有正负号的坐标直接当作长度；主图的分段也说明向右应当加 $p/2$，不能减。
\end{trapbox}
\clearpage
\begin{trapbox}
\textbf{\textcolor{CTrap}{误区二：任意点都能用焦半径公式。}}
两图用同一条曲线、同一焦点、同一尺度，且两点横坐标都是 $3$。
\begin{center}\input{assets/tikz/C051_on_curve_requirement.tex}\end{center}
\textbf{为什么错：}$R$ 不满足 $y^2=4x$，所以没有定义所保证的 $RF=RQ$。
\textbf{正确替代：}先代入检验点在曲线上；不在曲线上，就使用两点距离公式。

\medskip
\textbf{\textcolor{CTrap}{误区三：把 $p/2$ 当作半通径，或读错方程系数。}}
由参数图，半通径是 $p$；公式常数为 $p/2$。
若 $y^2=kx$（$k>0$），则 $k=2p=4a$，公式常数为 $k/4=a$。
通径端点 $x_0=p/2$ 的焦半径是 $p$，可用来回验。

\medskip
\textbf{三问防错：}点在曲线上吗？开口朝哪里？方程系数对应 $2p$ 还是 $4a$？
\end{trapbox}
''')

summary=(root/'06_summary.tex').read_text(encoding='utf-8')
put(root/'06_summary.tex','\\clearpage\n'+summary)
meta=json.loads((root/'meta.json').read_text(encoding='utf-8'))
meta['remarks']='2026-10-25：保留三种证明与七道例题；新增 assets/tikz/C051_focus_directrix_split.tex（PF=PQ 与 p/2+x0 分段，替代重复路线描述）、C051_four_openings.tex（四方向同尺度对照，替代开口脑补）、C051_area_height.tex（例3底高与延长线）、C051_on_curve_requirement.tex（同横坐标曲线上/外对照）；重绘 C051_math_audit_geometry.tex，区分 p/2、p、2p 并显示顶点最短焦半径。'
meta['meta']['updated_at']='2026-10-25'
put(root/'meta.json',json.dumps(meta,ensure_ascii=False,indent=2))
print('C051: 5 TikZ files and scoped text/metadata updated')
