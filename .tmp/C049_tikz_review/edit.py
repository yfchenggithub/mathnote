from pathlib import Path
import json

root=Path('D:/mathnote');uid=root/'03_conic/C049_ellipse_focal_radius_formula'
# Save this task's starting versions, including the user's existing edits.
backup=root/'.tmp/C049_tikz_review/before';backup.mkdir(exist_ok=True)
for name in ['01_statement.tex','02_explanation.tex','03_proof.tex','04_examples.tex','05_traps.tex','06_summary.tex','meta.json']:
    dest=backup/name
    if not dest.exists():dest.write_bytes((uid/name).read_bytes())

def frame(title,h):
    return [r'\begin{center}',r'\begin{tikzpicture}[x=1cm,y=1cm,line cap=round,line join=round,font=\small]',
            rf'\draw[black!25,rounded corners=3pt] (0,0) rectangle (14.4,{h});',
            rf'\node[font=\small\bfseries] at (7.2,{h-.5}) {{{title}}};']
def save(name,ls):
    (root/'assets/tikz'/f'C049_{name}.tex').write_text('\n'.join(ls+[r'\end{tikzpicture}',r'\end{center}'])+'\n',encoding='utf-8')
def axes(ls,scale,center,vertical=False):
    ls.append(rf'\begin{{scope}}[shift={{({center[0]},{center[1]})}},x={scale}cm,y={scale}cm]')
    rx,ry=(4,5) if vertical else (5,4)
    ls += [rf'\draw[black!35,->] (-{rx+.7},0)--({rx+.8},0) node[right] {{$x$}};',
           rf'\draw[black!35,->] (0,-{ry+.5})--(0,{ry+.6}) node[above] {{$y$}};',
           rf'\draw[black!65,thick] (0,0) ellipse ({rx} and {ry});']
def focals(ls,p,vertical=False):
    ls += [rf'\coordinate (P) at {p};',r'\coordinate (Fone) at (0,-3);' if vertical else r'\coordinate (Fone) at (-3,0);',
           r'\coordinate (Ftwo) at (0,3);' if vertical else r'\coordinate (Ftwo) at (3,0);',
           r'\draw[blue!70!black,line width=1.1pt] (Fone)--(P);',r'\draw[orange!85!black,line width=1.1pt] (Ftwo)--(P);',
           r'\foreach \q in {P,Fone,Ftwo} \fill (\q) circle (1.6pt);']

ls=frame('两条焦半径：蓝色连左焦点，橙色连右焦点',9.4)
axes(ls,.7,(4.7,4.7));focals(ls,'(3,3.2)')
ls += [r'\node[above left] at (P) {$P(3,\frac{16}{5})$};',r'\node[below left] at (Fone) {$F_1(-3,0)$};',r'\node[below right] at (Ftwo) {$F_2(3,0)$};',
       r'\node[below left] at (0,0) {$O$};',r'\node[blue!70!black,above,sloped] at (0,1.6) {$r_1=\frac{34}{5}$};',
       r'\node[orange!85!black,right] at (3,1.6) {$r_2=\frac{16}{5}$};',r'\end{scope}',
       r'\node[anchor=north west,align=left] at (9.1,7.9) {$\dfrac{x^2}{25}+\dfrac{y^2}{16}=1$\\[1em]$a=5,\ c=3,\ e=\dfrac35$\\[1em]\textcolor{blue!70!black}{$r_1=a+ex_0$}\\[.5em]\textcolor{orange!85!black}{$r_2=a-ex_0$}\\[1em]$r_1+r_2=10=2a$};',
       r'\node at (7.2,.65) {“左加右减”指所连焦点的位置；$x_0$ 保留正负号，不换成 $|x_0|$。};']
save('focal_radius_main',ls)

ls=frame('从左端到右端：蓝色变长、橙色变短，总长度不变',8.8)
for k,(x,y,r1,r2) in enumerate([(-5,0,2,8),(0,4,5,5),(5,0,8,2)]):
    cx=2.4+4.8*k
    ls += [rf'\begin{{scope}}[shift={{({cx},5.1)}},x=.36cm,y=.36cm]',r'\draw[black!25] (-5.5,0)--(5.5,0);',r'\draw[black!60] (0,0) ellipse (5 and 4);']
    focals(ls,f'({x},{y})')
    ls += [r'\node[below] at (Fone) {$F_1$};',r'\node[below] at (Ftwo) {$F_2$};',r'\node[above] at (P) {$P$};',r'\end{scope}',
           rf'\node at ({cx},3.55) {{$x_0={x}$}};',rf'\node[blue!70!black] at ({cx},2.85) {{$r_1={r1}$}};',rf'\node[orange!85!black] at ({cx},2.25) {{$r_2={r2}$}};',
           rf'\fill[blue!45] ({cx-1.8},1.35) rectangle ({cx-1.8+.36*r1},1.7);',rf'\fill[orange!50] ({cx-1.8+.36*r1},1.35) rectangle ({cx+1.8},1.7);',
           rf'\node at ({cx},.7) {{$r_1r_2={r1*r2}$}};']
ls += [r'\node at (7.2,7.6) {同一椭圆 $x^2/25+y^2/16=1$，三图与下方长度条均保持同尺度。};']
save('focal_radius_three_states',ls)

ls=frame('准线法：焦半径等于对应水平距离乘以 $e$',9.5)
axes(ls,.55,(7.2,4.5));focals(ls,'(3,3.2)')
ls += [r'\draw[purple!65,dashed] (-8.333333,-5)--(-8.333333,5.4);',r'\draw[purple!65,dashed] (8.333333,-5)--(8.333333,5.4);',
       r'\coordinate (Kone) at (-8.333333,3.2); \coordinate (Ktwo) at (8.333333,3.2);',
       r'\draw[blue!65,dashed] (Kone)--(P); \draw[orange!85!black,dashed] (P)--(Ktwo);',
       r'\draw[purple!65] (-8.333333,2.9)--(-8.033333,2.9)--(-8.033333,3.2);',
       r'\draw[purple!65] (8.333333,2.9)--(8.033333,2.9)--(8.033333,3.2);',
       r'\node[above] at (P) {$P(x_0,y_0)$};',r'\node[below left] at (Fone) {$F_1$};',r'\node[below right] at (Ftwo) {$F_2$};',
       r'\node[left] at (Kone) {$K_1$}; \node[right] at (Ktwo) {$K_2$};',
       r'\node[blue!70!black,above] at (-3.6,3.45) {$x_0+\dfrac{a^2}{c}$};',
       r'\node[orange!85!black,above] at (6.1,3.45) {$\dfrac{a^2}{c}-x_0$};',r'\end{scope}',
       r'\node[purple!65] at (2.62,8.2) {$x=-\dfrac{a^2}{c}$};',r'\node[purple!65] at (11.78,8.2) {$x=\dfrac{a^2}{c}$};',
       r'\node at (7.2,1.05) {$-\dfrac{a^2}{c}<-a\le x_0\le a<\dfrac{a^2}{c}$};',
       r'\node at (7.2,.45) {准线在顶点外侧，所以两条水平距离始终为正。};']
save('directrix_distances',ls)

ls=frame('勾股构造：垂足可以在焦点之间，也可以在焦点外侧',8.8)
for k,(x,y) in enumerate([(2,'{4*sqrt(21)/5}'),(4,'2.4')]):
    cx=3.6+7.2*k
    axes(ls,.44,(cx,5.15));focals(ls,f'({x},{y})')
    ls += [rf'\coordinate (H) at ({x},0);',r'\draw[purple!75,dashed] (P)--(H);',rf'\draw[purple!75] ({x-.25},0)--({x-.25},.25)--({x},.25);',
           r'\node[above left] at (P) {$P$};',r'\node[below left] at (Fone) {$F_1$};',
           (r'\node[below right] at (Ftwo) {$F_2$}; \node[below left] at (H) {$H$};' if k==0 else r'\node[below left] at (Ftwo) {$F_2$}; \node[below right] at (H) {$H$};'),
           r'\end{scope}',rf'\node at ({cx},2.6) {{'+('$-c<x_0<c$' if k==0 else '$x_0>c$')+'};',
           rf'\node at ({cx},1.9) {{$HF_1=x_0+c,\quad HF_2='+('c-x_0' if k==0 else 'x_0-c')+'$};']
ls += [r'\node at (7.2,1.05) {一般长度为 $HF_1=|x_0+c|,\ HF_2=|x_0-c|,\ PH=|y_0|$。};',
       r'\node at (7.2,.45) {平方后统一为 $r_1^2=(x_0+c)^2+y_0^2,\quad r_2^2=(x_0-c)^2+y_0^2$。};']
save('pythagoras_foot_positions',ls)

ls=frame('先看焦点轴：横轴用 $x_0$，纵轴用 $y_0$',10)
for k in [0,1]:
    cx=3.6+7.2*k
    axes(ls,.48,(cx,5.15),bool(k));focals(ls,'(-3.2,3)' if k else '(3,3.2)',bool(k))
    ls += [r'\node[above left] at (P) {$P$};',r'\node[below left] at (Fone) {$F_1$};',r'\node[below right] at (Ftwo) {$F_2$};',r'\end{scope}',
           rf'\node at ({cx},8.65) {{'+('焦点在 $y$ 轴' if k else '焦点在 $x$ 轴')+'};',
           rf'\node[blue!70!black] at ({cx},1.8) {{$r_1=a+e'+('y_0' if k else 'x_0')+'$};',
           rf'\node[orange!85!black] at ({cx},1.15) {{$r_2=a-e'+('y_0' if k else 'x_0')+'$};']
ls += [r'\node at (7.2,.45) {同一椭圆旋转 $90^\circ$：左右焦点变为下上焦点，距离保持不变。};']
save('focus_axis_comparison',ls)

def write(name,text):
    (uid/name).write_text(text,encoding='utf-8',newline='\n')
write('02_explanation.tex',r'''\clearpage
\begin{explanationbox}
\textbf{\textcolor{CExplanation}{先认清：焦半径就是两条连向焦点的线段}}

取椭圆 $x^2/25+y^2/16=1$，$a=5,c=3,e=3/5$。图中 $P=(3,16/5)$ 确实在椭圆上。
\input{assets/tikz/C049_focal_radius_main}
\textbf{读图：} 蓝线连左焦点，长 $5+\frac35\cdot3=\frac{34}{5}$；
橙线连右焦点，长 $5-\frac35\cdot3=\frac{16}{5}$。
和为 $10$，与椭圆定义相符。

\textbf{推广到任意椭圆上的点：}
\[
\textcolor{blue!70!black}{r_1=a+ex_0},\qquad
\textcolor{orange!85!black}{r_2=a-ex_0},\qquad r_1+r_2=2a.
\]
这里的“加、减”对应\emph{焦点位置}；不是把两条线段的长短永远固定。
例如 $x_0<0$ 时 $ex_0<0$，左焦半径反而较短。
\end{explanationbox}
\clearpage
\begin{explanationbox}
\textbf{\textcolor{CExplanation}{再看变化：一条增、一条减，和保持不变}}
\input{assets/tikz/C049_focal_radius_three_states}
三幅真实状态直接检验“左加右减”。随着 $x_0$ 从 $-a$ 增到 $a$，
$r_1$ 从 $a-c$ 增到 $a+c$，$r_2$ 反向变化，每条都为正。

\textbf{长度条还告诉我们：} 两条之和相同，长度相等时乘积最大；在两端时乘积最小。
一般地
\[
r_1r_2=a^2-e^2x_0^2\in[b^2,a^2].
\]
最大值在 $x_0=0$（两个短轴端点）取得；最小值在 $x_0=\pm a$（两个长轴端点）取得。

\textbf{理解不等于证明：} 三态图用来理解、验算符号；下面用准线或勾股平方差证明\emph{所有点}都成立。
\end{explanationbox}
''')
p=uid/'03_proof.tex';s=p.read_text(encoding='utf-8')
s='\\clearpage\n'+s
s=s.replace('利用第二定义，直接有','\\input{assets/tikz/C049_directrix_distances}\n利用第二定义，直接有')
s=s.replace('\\medskip\n\\textbf{\\textcolor{CProof}{证明二：','\\end{proofbox}\n\\clearpage\n\\begin{proofbox}\n\\textbf{\\textcolor{CProof}{证明二：')
s=s.replace('过 $P$ 向 $x$ 轴作垂足 $H(x_0,0)$。对两个直角三角形分别使用勾股定理：','过 $P$ 向 $x$ 轴作垂足 $H(x_0,0)$。先看垂足的两种位置：\n\\input{assets/tikz/C049_pythagoras_foot_positions}\n长度取绝对值，平方后无须分段；勾股定理统一写为：')
s=s.replace('\\textbf{第三步（平方差除以和，求出差）：}','\\end{proofbox}\n\\clearpage\n\\begin{proofbox}\n\\textbf{\\textcolor{CProof}{证明二（续）：由和、差分别求出两条焦半径}}\n\n\\textbf{第三步（平方差除以和，求出差）：}')
s=s.replace('\\medskip\n\\textbf{\\textcolor{CProof}{证明三：','\\end{proofbox}\n\\clearpage\n\\begin{proofbox}\n\\textbf{\\textcolor{CProof}{证明三：')
write('03_proof.tex',s)
write('05_traps.tex',r'''\clearpage
\begin{trapbox}
\textbf{\textcolor{CTrap}{易错一：焦点换到纵轴，仍机械代入横坐标}}
\input{assets/tikz/C049_focus_axis_comparison}
\textbf{错因与纠正：} 横轴图用 $x_0$，纵轴图用 $y_0$；先定位焦点，再写“左加右减”或“下加上减”。
本图左侧 $P=(3,16/5)$，右侧旋转后 $P'=(-16/5,3)$；两图均有 $r_1=34/5,r_2=16/5$。

\textbf{\textcolor{CTrap}{易错二：加减号写反，或擅自把 $x_0$ 换成 $|x_0|$}}
这样会把左、右两条焦半径对调。用理解页的左右端点检查：
右端点 $P(a,0)$ 应有 $r_1=a+c,r_2=a-c$；左端点正好反过来。
\end{trapbox}
\clearpage
\begin{trapbox}
\textbf{\textcolor{CTrap}{易错三：只检查坐标范围，就对任意点套公式}}
例如本例椭圆外的点 $(0,0)$ 虽满足 $x_0\in[-5,5]$，但到两焦点的距离均为 $3$，并非公式给出的 $5$。
\textbf{正确做法：} 必须确认 $P$ 在椭圆上；范围条件只是必要条件。

\medskip
\textbf{\textcolor{CTrap}{易错四：准线距离直接去绝对值，不说明依据}}
右准线距离本为 $|x_0-a^2/c|$。因为 $P$ 在椭圆上且 $a^2/c>a$，
才可写为 $a^2/c-x_0$。准线图中两条准线都在长轴端点外侧。

\medskip
\textbf{\textcolor{CTrap}{易错五：由平方相等直接开方，漏掉正性}}
由 $r_2^2=(a-ex_0)^2$ 先得 $r_2=|a-ex_0|$；
再由 $|x_0|\le a,e<1$ 知 $a\pm ex_0\ge a-c>0$，才能去掉绝对值。

\medskip
\textbf{\textcolor{CTrap}{易错六：仅用三个特殊位置替代一般证明}}
三态图可以检查符号、观察极值，但不能证明全椭圆上的公式。
一般证明仍需准线定义、第一定义加勾股平方差，或代入椭圆方程配方。
\end{trapbox}
''')
# Connect the existing extrema example to the actual endpoint states.
p=uid/'04_examples.tex';s=p.read_text(encoding='utf-8')
s=s.replace('最大值为 $25$。','最大值为 $25$。此时 $P=(0,\\pm4)$，两条距离均为 $5$（见理解页三态图的中间状态）。',1)
write('04_examples.tex',s)
p=uid/'meta.json';d=json.loads(p.read_text(encoding='utf-8'))
d['remarks']='2026-10-25 C049 TikZ教学补图：assets/tikz/C049_focal_radius_main.tex将两条真实焦半径与a±ex0对应；C049_focal_radius_three_states.tex用同尺度左端/短轴上端/右端与实长条显示左增右减、总长不变和乘积极值；C049_directrix_distances.tex显示两条准线与水平距离；C049_pythagoras_foot_positions.tex对照垂足在焦点之间/右焦点外侧，解释绝对值长度与平方统一；C049_focus_axis_comparison.tex按90度旋转对照x0/y0，替代焦点轴混淆的纯文字提醒。理解页删除原重复说明，证明保留三种路径并就近配图，例3补齐等号点。数学与逐页视觉验收见reports/C049_tikz_review_2026-10-25.md。'
d['meta']['updated_at']='2026-10-25';d['interactive']['has_diagram']=True
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Added 5 exact TikZ diagrams; edited explanation, proof, example equality, traps, metadata.')
