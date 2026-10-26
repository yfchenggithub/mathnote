from pathlib import Path
root=Path('03_conic/C052_ellipse_focal_chord_length');assets=Path('assets/tikz')
def put(p,s):p.write_text(s.strip()+'\n',encoding='utf-8')
put(root/'01_statement.tex',r'''
\begin{statementbox}
\textbf{\textcolor{CStatement}{条件}}
椭圆 $x^2/a^2+y^2/b^2=1$，$a>b>0$，$c=\sqrt{a^2-b^2}$；
焦点为 $F_1(-c,0)$、$F_2(c,0)$。直线经过其中一个焦点，与椭圆交于 $A,B$。
记倾斜角 $\theta\in[0,\pi)$（相对 $x$ 轴正方向），弦长 $L=AB$。

\medskip
\textbf{\textcolor{CStatement}{焦点弦长}}
\[
 \boxed{L=\frac{2ab^2}{a^2-c^2\cos^2\theta}
 =\frac{2h}{1-e^2\cos^2\theta}},\qquad e=\frac ca,\quad h=\frac{b^2}{a}.
\]
$a$ 是半长轴，$c$ 是半焦距，$e$ 是离心率，$h$ 是半通径。
左、右焦点使用同一弦长公式，且分母至少为 $b^2>0$。

\medskip
\textbf{\textcolor{CStatement}{两侧焦半径}}
取右焦点 $F_2$，将 $A$ 选在方向 $(\cos\theta,\sin\theta)$ 一侧，
$B$ 在相反一侧。令 $r=F_2A$、$s=F_2B$，则
\[
 r=\frac{b^2}{a+c\cos\theta},\qquad
 s=\frac{b^2}{a-c\cos\theta},\qquad \boxed{L=r+s}.
\]
两分母均为正（$a>c$），两段通常不等，垂直长轴时相等。

\medskip
\textbf{\textcolor{CStatement}{通径及最值}}
\[
 \boxed{\frac{2b^2}{a}\le L\le2a}.
\]
最小值在 $\theta=90^\circ$ 时取得，是过焦点且垂直长轴的通径；
最大值在 $\theta=0^\circ$ 时取得，是长轴弦。

\medskip
\textbf{\textcolor{CStatement}{斜率与长轴方向}}
有限斜率 $k$ 满足 $\cos^2\theta=1/(1+k^2)$，故
\[
 L=\frac{2ab^2(1+k^2)}{a^2(1+k^2)-c^2}.
\]
竖直线直接用通径。长轴在 $y$ 轴时，改用弦与长轴的角 $\varphi$：
\[
 L=\frac{2ab^2}{a^2-c^2\cos^2\varphi}.
\]
其中 $a$ 始终是半长轴；若仍给相对 $x$ 轴的倾斜角 $\theta$，则 $\cos^2\varphi=\sin^2\theta$。
\end{statementbox}
''')
p=assets/'C052_focal_chord_split.tex';s=p.read_text(encoding='utf-8').replace(r'$\theta=60^\circ$',r'$\theta$');put(p,s)
p=assets/'C052_three_directions.tex';s=p.read_text(encoding='utf-8').replace(r' node[above] {$x$};',';');put(p,s)
p=assets/'C052_left_right_focus.tex';s=p.read_text(encoding='utf-8').replace('(-1.6000000,1.0392305) circle(2pt) node[above right=4pt]','(-1.6000000,1.0392305) circle(2pt) node[above left=4pt]');put(p,s)
p=assets/'C052_supplementary_angles.tex';s=p.read_text(encoding='utf-8').replace('(1.6000000,-1.0392305) circle(2pt) node[below left=4pt]','(1.6000000,-1.0392305) circle(2pt) node[below right=4pt]');put(p,s)
p=assets/'C052_definition_pythagoras.tex';s=p.read_text(encoding='utf-8').replace('(2.15,0) node[below]','(2.15,0) node[above]').replace('(-1,-.3)--(-1,-2.25)','(-1,-.7)--(-1,-2.25)');put(p,s)
p=assets/'C052_vertical_major_axis_angle.tex';s=p.read_text(encoding='utf-8').replace(r'\end{scope}',r'''\node[violet] at (1.9,4.2) {$\theta$};
\node[orange!85!black] at (.6,5.55) {$\varphi$};
\end{scope}''');put(p,s)
p=root/'03_proof.tex';s=p.read_text(encoding='utf-8')
a=s.index('\\[\n r=FA>0');b=s.index('\\]',a)+2
s=s[:a]+r'''
\[
\begin{gathered}
 r=FA>0,\quad s=FB>0,\quad u=\cos\theta,\\
 A=(c+ru,r\sin\theta),\qquad B=(c-su,-s\sin\theta).
\end{gathered}
\]
'''+s[b:];put(p,s)
p=root/'04_examples.tex';s=p.read_text(encoding='utf-8')
s=s.replace('\\end{examplebox}\n\\clearpage\n\\begin{examplebox}\n\\textbf{\\textcolor{CExample}{例2','\\medskip\n\\textbf{\\textcolor{CExample}{例2',1)
# Compact direct example; the following inverse example supplies its own diagram.
a=s.index('\\textbf{题目：}');b=s.index('\\textbf{\\textcolor{CExample}{例2',a)
s=s[:a]+r'''
\textbf{题目：}椭圆 $x^2/4+y^2/3=1$，过右焦点的弦倾斜角为 $60^\circ$，求弦长。
\textbf{解：}$a=2,b^2=3,c^2=1$，故
$L=12/(4-1/4)=\boxed{16/5}$。
\textbf{核验：}主图两段 $6/5+2=16/5$，且通径 $3<L<4$（长轴弦）。
\medskip
'''+s[b:];put(p,s)
p=root/'05_traps.tex';s=p.read_text(encoding='utf-8');a=s.index('% C052 / 05_traps.tex')
s=s[:a]+r'''
\begin{trapbox}
\textbf{\textcolor{CTrap}{十个错误，各用一个动作纠正}}
\begin{enumerate}[leftmargin=*,itemsep=.65em,topsep=.5em]
\item \textbf{普通弦也套公式：}先验是否过 $(\pm c,0)$。上页对照图中左弦不满足条件，应联立求交点。
\item \textbf{把 $c$ 当 $a$：}$a$ 是半长轴，$c$ 是半焦距，始终有 $a^2=b^2+c^2$。
\item \textbf{漏掉余弦平方：}分母来自 $(a+cu)(a-cu)=a^2-c^2u^2$，其中 $u=\cos\theta$。
\item \textbf{只算一条焦半径：}按分段主图写 $AB=AF+FB$；通常 $AF\ne FB$，也不能直接倍增其中一段。
\item \textbf{通径系数记反：}令 $x=c$，得 $y=\pm b^2/a$，上下相加为 $2b^2/a$。
\item \textbf{长轴在 $y$ 轴仍用横轴角：}例8中的橙色角 $\varphi$ 才是公式用角；$\cos^2\varphi=\sin^2\theta$。
\item \textbf{把斜率 $k$ 当余弦：}有限斜率用 $\cos^2\theta=1/(1+k^2)$；竖直线无有限斜率，用通径。
\item \textbf{反求角漏一解：}由 $\cos^2\theta=1/4$ 得 $\cos\theta=\pm1/2$，例2两图对应 $60^\circ$、$120^\circ$。
\item \textbf{担心零分母：}$a^2-c^2\cos^2\theta\ge a^2-c^2=b^2>0$。
\item \textbf{最长最短颠倒：}三方向图显示长轴弦 $2a$ 最长，通径 $2b^2/a$ 最短；比较范围仅限焦点弦。
\end{enumerate}
\medskip
\textbf{15秒自检：}弦是否过焦点？角度是否相对长轴？两段是否相加？结果是否落在 $[2b^2/a,2a]$？
\end{trapbox}
''';put(p,s)
print('Refined statement pagination, proof display and diagram labels; consolidated repeated traps.')
