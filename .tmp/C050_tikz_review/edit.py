from pathlib import Path
import json

root=Path('D:/mathnote');uid=root/'03_conic/C050_hyperbola_focal_radius'
backup=root/'.tmp/C050_tikz_review/before';backup.mkdir(exist_ok=True)
for name in ['01_statement.tex','02_explanation.tex','03_proof.tex','04_examples.tex','05_traps.tex','06_summary.tex','meta.json']:
    if not (backup/name).exists():(backup/name).write_bytes((uid/name).read_bytes())
asset=root/'assets/tikz/C050_math_audit_geometry.tex'
if not (backup/asset.name).exists():(backup/asset.name).write_bytes(asset.read_bytes())
def frame(title,h):
    return [r'\begin{center}',r'\begin{tikzpicture}[x=1cm,y=1cm,line cap=round,line join=round,font=\small]',
            rf'\draw[black!25,rounded corners=3pt] (0,0) rectangle (14.4,{h});',
            rf'\node[font=\small\bfseries] at (7.2,{h-.5}) {{{title}}};']
def save(name,ls):
    (root/'assets/tikz'/f'C050_{name}.tex').write_text('\n'.join(ls+[r'\end{tikzpicture}',r'\end{center}'])+'\n',encoding='utf-8')
def geometry(ls,center,scale,p,vertical=False):
    ls += [rf'\begin{{scope}}[shift={{({center[0]},{center[1]})}},x={scale}cm,y={scale}cm]',
           r'\draw[black!30,->] (-4.4,0)--(4.5,0) node[right] {$x$};',
           r'\draw[black!30,->] (0,-3.8)--(0,4.1) node[above] {$y$};']
    for sign in [-1,1]:
        expr=rf'({{z}},{{{sign}*2*sqrt(1+z*z/5)}})' if vertical else rf'({{{sign}*2*sqrt(1+z*z/5)}},{{z}})'
        ls.append(r'\draw[black!65,thick,domain=-3.5:3.5,samples=100,variable=\z] plot '+expr+';')
    ls += [rf'\coordinate (P) at {p};',r'\coordinate (Fone) at (0,-3);' if vertical else r'\coordinate (Fone) at (-3,0);',
           r'\coordinate (Ftwo) at (0,3);' if vertical else r'\coordinate (Ftwo) at (3,0);',
           r'\draw[blue!70!black,line width=1.1pt] (Fone)--(P);',r'\draw[orange!85!black,line width=1.1pt] (Ftwo)--(P);',
           r'\foreach \q in {P,Fone,Ftwo} \fill (\q) circle (1.6pt);']

ls=frame('焦半径就是到焦点的距离：右支同侧短、异侧长',9.2)
geometry(ls,(4.5,4.3),.8,'(3,2.5)')
ls += [r'\node[above left] at (P) {$P(3,\frac52)$};',r'\node[below left] at (Fone) {$F_1(-3,0)$};',r'\node[below right] at (Ftwo) {$F_2(3,0)$};',
       r'\path (Fone)--(P) node[pos=.25,above,sloped,blue!70!black] {$d_1=\frac{13}{2}$};',
       r'\node[left,orange!85!black] at (3,1) {$d_2=\frac52$};',r'\end{scope}',
       r'\node[align=left,anchor=north west] at (9.1,7.7) {$\dfrac{x^2}{4}-\dfrac{y^2}{5}=1$\\[1em]$a=2,\ c=3,\ e=\dfrac32$\\[1em]\textcolor{blue!70!black}{$d_1=ex_0+a$}\\[.7em]\textcolor{orange!85!black}{$d_2=ex_0-a$}\\[1em]$d_1-d_2=4=2a$};',
       r'\node at (7.2,.65) {$F_1$ 始终是左焦点，$F_2$ 始终是右焦点；焦点名称不随支改变。};']
save('math_audit_geometry',ls)

ls=frame('左右支对照：焦点名称不变，长短随所在支交换',9.7)
for k,x in enumerate([-3,3]):
    cx=3.6+7.2*k
    geometry(ls,(cx,5.65),.5,f'({x},2.5)')
    ls += [r'\node[above right] at (P) {$P_-$};' if k==0 else r'\node[above left] at (P) {$P_+$};',
           r'\node[below] at (Fone) {$F_1$};',r'\node[below] at (Ftwo) {$F_2$};',r'\end{scope}',
           rf'\node at ({cx},8.65) {{'+('$x_0=-3$，左支' if k==0 else '$x_0=3$，右支')+'};',
           rf'\node[blue!70!black] at ({cx},3.15) {{$d_1='+('5/2' if k==0 else '13/2')+'$};',
           rf'\fill[blue!45] ({cx-1.7},2.55) rectangle ({cx-1.7+.45*(2.5 if k==0 else 6.5)},2.8);',
           rf'\node[orange!85!black] at ({cx},1.85) {{$d_2='+('13/2' if k==0 else '5/2')+'$};',
           rf'\fill[orange!50] ({cx-1.7},1.25) rectangle ({cx-1.7+.45*(6.5 if k==0 else 2.5)},1.5);']
ls += [r'\node at (7.2,.5) {曲线与线段均同尺度；两点互为镜像：同侧距离 $5/2$，异侧距离 $13/2$。};']
save('branch_comparison',ls)

ls=frame('先看允许范围，再看括号正负：绝对值不能直接丢',9.5)
ls += [r'\node at (7.2,8.15) {$e>1\ \Longrightarrow\ 0<a/e<a$；两个零点都落在无曲线点的中间区域。};',
       r'\fill[blue!8] (1,5.85) rectangle (4.8,6.55);',r'\fill[black!7] (4.8,5.85) rectangle (9.6,6.55);',r'\fill[orange!10] (9.6,5.85) rectangle (13.4,6.55);',
       r'\draw[->,black!70] (1,6.2)--(13.5,6.2) node[right] {$x_0$};',
       r'\draw[line width=1.5pt,blue!65] (1.1,6.2)--(4.8,6.2);',r'\draw[line width=1.5pt,orange!85!black] (9.6,6.2)--(13.2,6.2);',
       r'\fill (4.8,6.2) circle(2pt); \fill (9.6,6.2) circle(2pt);',
       r'\node[above] at (4.8,6.55) {$-a$}; \node[above] at (9.6,6.55) {$a$};',
       r'\draw[purple!70] (5.6,6.05)--(5.6,6.35) (8.8,6.05)--(8.8,6.35);',
       r'\node[below] at (5.6,5.8) {$-\dfrac ae$}; \node[below] at (8.8,5.8) {$\dfrac ae$};',
       r'\node at (7.2,4.55) {$-a<x_0<a$：没有双曲线上的点};',
       r'\node at (2.8,7.45) {左支 $x_0\le-a$}; \node at (11.6,7.45) {右支 $x_0\ge a$};',
       r'\node[align=center] at (2.8,3.35) {$a+ex_0<0$\\[.6em]$a-ex_0>0$};',
       r'\node[align=center] at (11.6,3.35) {$a+ex_0>0$\\[.6em]$a-ex_0<0$};',
       r'\node[align=center] at (2.8,1.55) {\textcolor{blue!70!black}{$d_1=-ex_0-a$}\\[.6em]\textcolor{orange!85!black}{$d_2=-ex_0+a$}};',
       r'\node[align=center] at (11.6,1.55) {\textcolor{blue!70!black}{$d_1=ex_0+a$}\\[.6em]\textcolor{orange!85!black}{$d_2=ex_0-a$}};']
save('absolute_value_domains',ls)

ls=frame('把长短两段对齐：平均长度 $t$ 的两侧各差一个 $a$',8.6)
ls += [r'\node at (7.2,7.35) {平移到同一起点，只比较长度；示例 $a=2,\ t=9/2$。};',
       r'\fill[blue!40] (2,6.0) rectangle (11.75,6.2);',r'\node[blue!70!black,above] at (5.3,6.2) {较长 $t+a=13/2$};',
       r'\draw[black!65,dashed,line width=1.2pt] (2,4.6)--(8.75,4.6);',r'\node[above] at (5.3,4.6) {平均长度 $t=9/2$};',
       r'\fill[orange!50] (2,2.9) rectangle (5.75,3.1);',r'\node[orange!85!black,above] at (3.9,3.1) {较短 $t-a=5/2$};',
       r'\draw[black!30,dotted] (2,2.5)--(2,6.6);',r'\draw[purple!65,<->] (8.75,5.35)--(11.75,5.35) node[midway,above] {$a=2$};',
       r'\draw[purple!65,<->] (5.75,3.8)--(8.75,3.8) node[midway,above] {$a=2$};',
       r'\draw[black!60,<->] (5.75,1.8)--(11.75,1.8) node[midway,below] {$2a=4$};',
       r'\draw[black!30,dotted] (5.75,1.7)--(5.75,2.9) (11.75,1.7)--(11.75,6.0);',
       r'\node at (7.2,.55) {$t=\dfrac{\text{长}+\text{短}}2=e|x_0|$；$t$ 是两个长度的平均值，不是焦点连线的中点。};']
save('mean_length_segments',ls)

ls=frame('双曲线准线在两顶点之间；右支点位于两准线右侧',10)
geometry(ls,(5.1,4.5),.9,'(3,2.5)')
ls += [r'\draw[purple!65,dashed] (-1.333333,-3.3)--(-1.333333,3.7);',r'\draw[purple!65,dashed] (1.333333,-3.3)--(1.333333,3.7);',
       r'\coordinate (Kone) at (-1.333333,2.5); \coordinate (Ktwo) at (1.333333,2.5);',
       r'\draw[blue!70!black,dashed,line width=2pt] (Kone)--(P);',r'\draw[orange!85!black,densely dashed,line width=.8pt] (Ktwo)--(P);',
       r'\draw[purple!65] (-1.333333,2.25)--(-1.083333,2.25)--(-1.083333,2.5);',
       r'\draw[purple!65] (1.333333,2.25)--(1.583333,2.25)--(1.583333,2.5);',
       r'\node[below left] at (Kone) {$K_1$}; \node[below right] at (Ktwo) {$K_2$};',
       r'\node[below right] at (P) {$P$};',r'\node[below] at (Fone) {$F_1$}; \node[below] at (Ftwo) {$F_2$};',r'\end{scope}',
       r'\node[purple!65] at (3.9,8.55) {$x=-\dfrac ae$};',r'\node[purple!65] at (6.3,8.55) {$x=\dfrac ae$};',
       r'\node[blue!70!black] at (4.95,7.2) {$x_0+\dfrac ae$};',r'\node[orange!85!black] at (7.2,7.2) {$x_0-\dfrac ae$};',
       r'\node[align=left,anchor=north west] at (10,7.7) {$d_1=e\,PK_1$\\[1em]$d_2=e\,PK_2$\\[1.3em]右支：\\[.6em]$d_1=ex_0+a$\\[.6em]$d_2=ex_0-a$};',
       r'\node at (7.2,.55) {两条水平距离有重合部分，用蓝粗虚线、橙细虚线区分；左支取距离绝对值。};']
save('directrix_geometry',ls)

ls=frame('焦点轴变成纵轴：坐标与分支一起换成 $y_0$',10)
for k in [0,1]:
    cx=3.6+7.2*k
    geometry(ls,(cx,5.3),.6,'(-2.5,3)' if k else '(3,2.5)',bool(k))
    ls += [r'\node[above left] at (P) {$P$};',r'\node[below left] at (Fone) {$F_1$};',r'\node[below right] at (Ftwo) {$F_2$};',r'\end{scope}',
           rf'\node at ({cx},8.9) {{'+('下、上焦点；图示上支' if k else '左、右焦点；图示右支')+'};',
           rf'\node[blue!70!black] at ({cx},1.9) {{$d_1=|a+e'+('y_0' if k else 'x_0')+'|$};',
           rf'\node[orange!85!black] at ({cx},1.2) {{$d_2=|a-e'+('y_0' if k else 'x_0')+'|$};']
ls += [r'\node at (7.2,.5) {两图等比例、同尺度，右图由左图旋转 $90^\circ$ 得到，两条焦半径长度不变。};']
save('focus_axis_comparison',ls)

def write(name,s):(uid/name).write_text(s,encoding='utf-8')
write('02_explanation.tex',r'''\clearpage
\begin{explanationbox}
\textbf{\textcolor{CExplanation}{先看一个真实点：长短相差 $2a$}}

取双曲线 $x^2/4-y^2/5=1$，$a=2,c=3,e=3/2$。
图中 $P=(3,5/2)$ 在右支，两条焦半径分别是 $13/2,5/2$。
\input{assets/tikz/C050_math_audit_geometry}
\textbf{读图：} 连右焦点的橙线较短，连左焦点的蓝线较长，差为 $4=2a$。
把两长度的平均值记作 $t$，就有“短 $=t-a$，长 $=t+a$”。
本例 $t=9/2=e|x_0|$，方法二的实长线段图会把这一步展开。

\textbf{关键区别：} $F_1,F_2$ 的名称始终按左右定义；“同侧、异侧”才随所在支改变。
\end{explanationbox}
\clearpage
\begin{explanationbox}
\textbf{\textcolor{CExplanation}{再把点移到左支：左右焦点不换，长短对调}}
\input{assets/tikz/C050_branch_comparison}
对任一支，令 $t=e|x_0|$，则
\[
\boxed{\text{同侧短}=t-a},\qquad\boxed{\text{异侧长}=t+a}.
\]
所以两条距离的差的绝对值为 $2a$，和为 $2t=2e|x_0|$。
此处 $t\ge ea=c>a$，短的一段仍严格为正。

图中上下翻折 $P(x_0,y_0)\mapsto P'(x_0,-y_0)$ 不改变到横轴上两焦点的距离；
公式不依赖 $y_0$ 的正负，但使用前仍须确认点在曲线上。
\end{explanationbox}
''')
write('03_proof.tex',r'''\clearpage
\begin{proofbox}
\textbf{\textcolor{CProof}{方法一：双曲线定义＋平方差（考场速证）}}

设 $d_1=|PF_1|,d_2=|PF_2|$，由定义有 $|d_1-d_2|=2a$。
两点距离平方相减，共同的 $y_0^2$ 消去：
\[
d_1^2-d_2^2=[(x_0+c)^2+y_0^2]-[(x_0-c)^2+y_0^2]=4cx_0.
\]
因为 $d_1+d_2>0$，平方差的符号就是 $d_1-d_2$ 的符号，故能严格判断哪段较长。

\textbf{右支 $x_0\ge a$：} 平方差为正，所以 $d_1>d_2$，$d_1-d_2=2a$。
\[
d_1+d_2=\frac{4cx_0}{2a}=2ex_0.
\]
由和差求两数：
\[
\boxed{d_1=ex_0+a},\qquad\boxed{d_2=ex_0-a}.
\]
\textbf{左支 $x_0\le-a$：} 平方差为负，所以 $d_1<d_2$，$d_1-d_2=-2a$。
\[
d_1+d_2=\frac{4cx_0}{-2a}=-2ex_0.
\]
于是
\[
\boxed{d_1=-ex_0-a},\qquad\boxed{d_2=-ex_0+a}.
\]
两支统一为 $\boxed{d_1=|a+ex_0|,\ d_2=|a-ex_0|}$。
本法只用定义、两点距离平方差和加减消元，不必代入双曲线方程展开。
\end{proofbox}
\clearpage
\begin{proofbox}
\textbf{\textcolor{CProof}{方法二：先设两长度的平均值 $t$（首推理解）}}

两段差为 $2a$，所以让长、短分别为 $t+a,t-a$，只用一个未知量。
\input{assets/tikz/C050_mean_length_segments}
\textbf{右支：} $d_1=t+a,d_2=t-a$，平方相减有
\[
(t+a)^2-(t-a)^2=4at=4cx_0\ \Longrightarrow\ t=ex_0.
\]
\textbf{左支：} $d_1=t-a,d_2=t+a$，同理
\[
(t-a)^2-(t+a)^2=-4at=4cx_0\ \Longrightarrow\ t=-ex_0.
\]
因此两支都有 $t=e|x_0|$，代回即得“同侧短、异侧长”。
图中的三个长度从同一起点对齐，并非在原焦点三角形中取一个几何中点。
\end{proofbox}
\clearpage
\begin{proofbox}
\textbf{\textcolor{CProof}{方法三：标准方程消元、配方、开方}}

点在双曲线上，故 $y_0^2=\frac{b^2}{a^2}(x_0^2-a^2)$，且 $c^2=a^2+b^2$。
\[
\begin{aligned}
d_1^2&=(x_0+c)^2+y_0^2\\
&=x_0^2+2cx_0+c^2+\frac{b^2}{a^2}x_0^2-b^2\\
&=\frac{c^2}{a^2}x_0^2+2cx_0+a^2=(ex_0+a)^2.
\end{aligned}
\]
把 $c$ 换成 $-c$，同理得 $d_2^2=(ex_0-a)^2$。开方必须保留绝对值：
\[
\boxed{d_1=|ex_0+a|=|a+ex_0|},\qquad
\boxed{d_2=|ex_0-a|=|a-ex_0|}.
\]
\textbf{为什么不能像椭圆那样直接去掉绝对值？}
因为 $e>1,|x_0|\ge a$；右支 $ex_0-a\ge c-a>0$，
左支 $ex_0+a\le a-c<0$。去绝对值前必须先判断所在支。
易错页的数轴图把两个括号的符号一次列清。

\textbf{顶点也成立：} $P=(a,0)$ 时 $(d_1,d_2)=(c+a,c-a)$；
$P=(-a,0)$ 时两者对调。焦半径均非零；仅焦点三角形退化。
\end{proofbox}
\clearpage
\begin{proofbox}
\textbf{\textcolor{CProof}{方法四：焦点—准线第二定义（选学）}}

\textbf{前提：} 已学过并证明第二定义 $|PF|/d(P,\ell)=e$；此处只应用它，不用它循环证明自身。
\input{assets/tikz/C050_directrix_geometry}
与 $F_1,F_2$ 对应的准线依次是 $x=-a/e,x=a/e$，所以
\[
\begin{aligned}
d_1&=e\left|x_0+\frac ae\right|=|ex_0+a|,\\
d_2&=e\left|x_0-\frac ae\right|=|ex_0-a|.
\end{aligned}
\]
右支点位于两条准线右侧，左支点位于两条准线左侧，故水平距离的去绝对值形式不同。
没有学过第二定义时，使用方法一或方法二即可。
\end{proofbox}
''')
write('04_examples.tex',r'''\clearpage
\begin{examplebox}
\textbf{\textcolor{CExample}{例1：已知坐标，直接求焦半径}}

双曲线 $x^2/16-y^2/9=1$ 上点 $P=(5,9/4)$。求两焦半径。

\textbf{解：} $a=4,b=3,c=5,e=5/4$；$25/16-9/16=1$，点确在右支。
\[
d_1=\frac54\cdot5+4=\boxed{\frac{41}{4}},\qquad
d_2=\frac54\cdot5-4=\boxed{\frac94}.
\]
\textbf{回验：} 距离平方为 $10^2+(9/4)^2=(41/4)^2$、$0^2+(9/4)^2$，差为 $8=2a$。

\medskip
\textbf{\textcolor{CExample}{例2：由两焦半径反求双曲线方程}}

焦点在横轴的双曲线右支点 $P=(5,y_0)$ 到左右焦点的距离分别为 $13,3$。求方程。

\textbf{解：} $5e+a=13,5e-a=3$，所以 $a=5,e=8/5,c=8,b^2=39$。
\[
\boxed{\frac{x^2}{25}-\frac{y^2}{39}=1}.
\]
\textbf{回验：} 此时 $x_0=a=5$，$y_0=0$，是右顶点；实际距离为 $8+5=13,8-5=3$。

\medskip
\textbf{\textcolor{CExample}{例3：焦半径之比先决定所在支}}

在 $x^2/16-y^2/9=1$ 上，若 $d_1:d_2=3:1$，求点坐标。

\textbf{解：} $d_1>d_2$，点在右支。
\[
ex_0+a=3(ex_0-a)\ \Longrightarrow\ x_0=2a/e=32/5.
\]
代回曲线得 $y_0^2/9=39/25$，所以
\[
\boxed{P=(32/5,\ \pm3\sqrt{39}/5)}.
\]
\textbf{回验：} $ex_0=8$，距离为 $12,4$，比为 $3:1$；由坐标计算距离平方也分别为 $144,16$。
\end{examplebox}
\clearpage
\begin{examplebox}
\textbf{\textcolor{CExample}{例4：左支同侧短，防止下标与符号写反}}

在 $x^2/9-y^2/16=1$ 上，若 $x_0=-6$，求两焦半径。

\textbf{解：} $a=3,c=5,e=5/3$，点在左支，$t=e|x_0|=10$。
左焦点同侧短，右焦点异侧长，所以
\[
\boxed{d_1=7},\qquad\boxed{d_2=13}.
\]
\textbf{回验：} $y_0=\pm4\sqrt3$，实际距离平方为 $(-6+5)^2+48=49$、$(-6-5)^2+48=169$。
差为 $6=2a$，和为 $20=2t$。

\medskip
\textbf{\textcolor{CExample}{例5：左支由焦半径反推横坐标}}

点在 $x^2/16-y^2/9=1$ 左支且 $d_1=6$，求横坐标。

\textbf{解：} 左焦点同侧短，$6=-\frac54x_0-4$，故 $\boxed{x_0=-8}$。

\textbf{回验：} $P=(-8,\pm3\sqrt3)$ 在曲线上，距离平方分别为 $9+27=36$、$169+27=196$，距离为 $6,14$。

\medskip
\textbf{\textcolor{CExample}{例6：左右顶点检查公式}}

顶点、焦点均在横轴上，直接作一维距离计算：
\[
\begin{array}{c|cc}
P&d_1&d_2\\\hline
(a,0)&c+a&c-a\\
(-a,0)&c-a&c+a
\end{array}
\]
两种状态均差 $2a$、和 $2c=2e|x_0|$。
这里是对公式的回验，不能用两个特殊点替代一般证明。
\end{examplebox}
''')
write('05_traps.tex',r'''\clearpage
\begin{trapbox}
\textbf{\textcolor{CTrap}{易错一、二：丢绝对值，或误把 $F_1$ 永远当作远焦点}}

原式是 $d_1=|a+ex_0|,d_2=|a-ex_0|$。先确认点在曲线上，再按所在支判断括号的正负。
\input{assets/tikz/C050_absolute_value_domains}
\textbf{反例：} 主图右支点 $x_0=3,a=2,e=3/2$，
若错用 $d_2=a-ex_0$，会得到 $-5/2$。距离不可能为负，应取绝对值得 $5/2$。
左支则由 $F_1$ 变成同侧近焦点（见左右支对照图），焦点下标不能按远近重新命名。
\end{trapbox}
\clearpage
\begin{trapbox}
\textbf{\textcolor{CTrap}{易错三：焦点换到纵轴，仍使用横坐标}}
\input{assets/tikz/C050_focus_axis_comparison}
右支图的 $P=(3,5/2)$ 旋转后成为上支点 $P'=(-5/2,3)$。
此时 $F_1$ 是下焦点、$F_2$ 是上焦点，公式中的横坐标改成纵坐标。
本图两种状态的 $d_1,d_2$ 都为 $13/2,5/2$。
\end{trapbox}
\clearpage
\begin{trapbox}
\textbf{\textcolor{CTrap}{易错四：只看横坐标符号，或只检查 $|x_0|\ge a$}}
例如 $a=4$ 时 $x_0=2>0$，仍不可能是双曲线点；
在 $x^2/16-y^2/9=1$ 中，$(5,0)$ 虽满足 $x_0\ge4$，却不在曲线上。
\textbf{纠正：} 范围只是必要条件，必须核对原方程。

\medskip
\textbf{\textcolor{CTrap}{易错五：把 $c^2$ 写成 $a^2-b^2$}}
双曲线始终是 $c^2=a^2+b^2$，因而 $e>1$；先认清曲线，再算参数。

\medskip
\textbf{\textcolor{CTrap}{易错六：平方开方直接丢掉绝对值}}
$\sqrt{(ex_0-a)^2}=|ex_0-a|$。先保留绝对值，或用前面的数轴图判断符号。

\medskip
\textbf{\textcolor{CTrap}{易错七：把椭圆固定和的设法搬来}}
椭圆和为 $2a$，可设 $a+t,a-t$；双曲线差的绝对值为 $2a$，应设 $t+a,t-a$。
用方法二的实长线段图检查：两端分别距平均长度 $a$，总差才是 $2a$。

\medskip
\textbf{\textcolor{CTrap}{易错八：把平均长度 $t$ 当成原图中的几何中点}}
$t=(d_1+d_2)/2$ 是\textbf{两个数的平均值}。原图中两线段不共线，不能据此断言某个几何中点到焦点距离为 $t$。

\medskip
\textbf{考场回验：} 长减短为 $2a$，长加短为 $2e|x_0|$；顶点也应满足这两式。
\end{trapbox}
''')
p=uid/'06_summary.tex';s=p.read_text(encoding='utf-8');write(p.name,'\\clearpage\n'+s)
p=uid/'meta.json';d=json.loads(p.read_text(encoding='utf-8'))
d['remarks']+=' 2026-10-25 TikZ教学补图：完善assets/tikz/C050_math_audit_geometry.tex，保持原a=2,b²=5,c=3,P=(3,5/2)真实模型；新增C050_branch_comparison.tex左右支同尺度对照及实长条、C050_absolute_value_domains.tex定义域与括号符号数轴、C050_mean_length_segments.tex平均长度t±a对齐比较、C050_directrix_geometry.tex准线位置与对应水平距离、C050_focus_axis_comparison.tex旋转90度对照x0/y0。压缩重复说明，保留四种证明与六道原例题，补全欧氏距离回验；总结独立分页。验收见reports/C050_tikz_review_2026-10-25.md。'
d['interactive']['has_diagram']=True;d['meta']['updated_at']='2026-10-25'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Updated C050 main diagram and added five focused diagrams; preserved four proofs and six examples.')
