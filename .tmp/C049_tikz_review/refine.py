from pathlib import Path
root=Path('D:/mathnote');uid=root/'03_conic/C049_ellipse_focal_radius_formula'
p=root/'assets/tikz/C049_focal_radius_main.tex';s=p.read_text(encoding='utf-8')
s=s.replace(r'\node[above left] at (P)',r'\node[above right] at (P)').replace(r'\node[below left] at (Fone)',r'\node[below] at (Fone)').replace(r'\node[below right] at (Ftwo)',r'\node[below] at (Ftwo)')
s=s.replace(r'\node[blue!70!black,above,sloped] at (0,1.6)',r'\path (Fone)--(P) node[midway,blue!70!black,above,sloped]')
s=s.replace(r'\node[orange!85!black,right] at (3,1.6)',r'\node[orange!85!black,left] at (3,1.1)').replace('--(5.8,0)','--(5.3,0)')
p.write_text(s,encoding='utf-8')
p=root/'assets/tikz/C049_focal_radius_three_states.tex';s=p.read_text(encoding='utf-8')
for a,b in [('3.55','3.2'),('2.85','2.6'),('2.25','2.0')]:s=s.replace(','+a+')',','+b+')')
p.write_text(s,encoding='utf-8')
p=root/'assets/tikz/C049_directrix_distances.tex';s=p.read_text(encoding='utf-8').replace('(7.2,1.05)','(7.2,1.4)').replace('(7.2,.45)','(7.2,.5)');p.write_text(s,encoding='utf-8')
p=uid/'05_traps.tex';s=p.read_text(encoding='utf-8').replace('本例椭圆外的点','本例不在椭圆上的点');p.write_text(s,encoding='utf-8')

p=uid/'03_proof.tex';s=p.read_text(encoding='utf-8');idx=s.index(r'\textbf{\textcolor{CProof}{证明三：')
s=s[:idx]+r'''\textbf{\textcolor{CProof}{证明三：常规证明——距离公式＋椭圆方程}}

\textbf{第1步：用椭圆方程消去 $y_0^2$。}
\[
y_0^2=b^2\left(1-\frac{x_0^2}{a^2}\right),\qquad b^2=a^2-c^2.
\]
\textbf{第2步：展开右焦半径的平方，再配方。}
\[
\begin{aligned}
r_2^2&=(x_0-c)^2+y_0^2\\
&=x_0^2-2cx_0+c^2+(a^2-c^2)\left(1-\frac{x_0^2}{a^2}\right)\\
&=a^2-2cx_0+\frac{c^2}{a^2}x_0^2\\
&=\left(a-\frac ca x_0\right)^2=(a-ex_0)^2.
\end{aligned}
\]
\textbf{第3步：说明正性，再开方。} 因为 $|x_0|\le a$、$e=c/a<1$，
\[
a\pm ex_0\ge a-c>0.
\]
所以 $r_2=|a-ex_0|=a-ex_0$。将上面的 $c$ 换成 $-c$，同理得到 $r_1=a+ex_0$。

\textbf{回验：} 两式之和为 $2a$，与第一定义相符；
$x_0=0$ 时 $r_1=r_2=a$；右端点 $P(a,0)$ 处 $r_1=a+c,r_2=a-c$。
特殊值检查符号，一般性由上面的恒等变形保证。

\medskip
\textbf{\textcolor{CProof}{三条路线的联系}}
第一定义给“和”，勾股平方差给“差”；第二定义直接给出每条距离；距离公式则通过消元配方得到同一结果。

\textbf{焦点在纵轴的推广：} 对 $x^2/b^2+y^2/a^2=1$，交换横纵轴，
下、上焦点依次记为 $F_1,F_2$，便有 $r_1=a+ey_0,r_2=a-ey_0$。
\end{proofbox}
'''
p.write_text(s,encoding='utf-8')

(uid/'04_examples.tex').write_text(r'''\clearpage
\begin{examplebox}
\textbf{\textcolor{CExample}{例1：直接求两条距离——右端点检查符号}}

\textbf{题目：} 椭圆 $x^2/25+y^2/16=1$ 上点 $P$ 的横坐标为 $5$，求两条焦半径。

\textbf{解：} $a=5,b=4,c=3,e=3/5$，故
\[
r_1=5+\frac35\cdot5=\boxed8,\qquad r_2=5-\frac35\cdot5=\boxed2.
\]
\textbf{回验：} 此时 $P=(5,0)$，到 $(-3,0)$、$(3,0)$ 的距离确为 $8,2$，和为 $10$。
这正是理解页三态图的右端状态。

\medskip
\textbf{\textcolor{CExample}{例2：由右焦半径反求横坐标}}

\textbf{题目：} 同一椭圆上 $|PF_2|=4$，求横坐标。

\textbf{解：} 右焦半径用减号，
\[
5-\frac35x_0=4\quad\Longrightarrow\quad \boxed{x_0=\frac53}.
\]
\textbf{回验：} 代入椭圆得 $y_0=\pm\frac{8\sqrt2}{3}$，确有上下两个点；
到右焦点的距离平方为 $(5/3-3)^2+128/9=16$，故距离为 $4$。

\medskip
\textbf{\textcolor{CExample}{例3：两条焦半径的乘积最大值}}

\textbf{题目：} 同一椭圆上求 $r_1r_2$ 的最大值。

\textbf{解：} $x_0\in[-5,5]$，所以
\[
r_1r_2=\left(5+\frac35x_0\right)\left(5-\frac35x_0\right)
=25-\frac9{25}x_0^2\le\boxed{25}.
\]
等号当且仅当 $x_0=0$，即 $P=(0,\pm4)$。
\textbf{回验：} 此时两条距离均为 $5$，乘积为 $25$；对应三态图的中间状态。
\end{examplebox}
\clearpage
\begin{examplebox}
\textbf{\textcolor{CExample}{例4：由两焦半径之差反求横坐标}}

\textbf{题目：} 椭圆 $x^2/25+y^2/16=1$ 上一点满足 $r_1-r_2=12/5$，求横坐标。

\textbf{识别：} 第一定义给和 $2a$，平方差法还给出 $r_1-r_2=2ex_0$。
代 $e=3/5$，
\[
\frac{12}{5}=2\cdot\frac35x_0\quad\Longrightarrow\quad\boxed{x_0=2}.
\]
\textbf{回验：} $P=(2,\pm4\sqrt{21}/5)$ 在椭圆上；
$r_1=31/5,r_2=19/5$，差为 $12/5$、和为 $10$。
这也是勾股构造图的左侧状态。

\medskip
\textbf{\textcolor{CExample}{例5：焦点在纵轴——下加上减}}

\textbf{题目：} 椭圆 $x^2/9+y^2/25=1$ 的下、上焦点分别为 $F_1,F_2$。
点 $P$ 的纵坐标 $y_0=5/2$，求两条焦半径。

\textbf{解：} $a=5,b=3,c=4,e=4/5$。焦点在纵轴，用 $y_0$：
\[
r_1=5+\frac45\cdot\frac52=\boxed7,\qquad
r_2=5-\frac45\cdot\frac52=\boxed3.
\]
\textbf{回验：} $P=(\pm3\sqrt3/2,5/2)$ 在椭圆上；
到下焦点 $(0,-4)$ 的距离平方为 $27/4+169/4=49$，
到上焦点 $(0,4)$ 的距离平方为 $27/4+9/4=9$，因此为 $7,3$，且和为 $10$。
\end{examplebox}
''',encoding='utf-8')
p=uid/'06_summary.tex';s=p.read_text(encoding='utf-8');p.write_text('\\clearpage\n'+s,encoding='utf-8')
print('Adjusted labels, preserved three proofs and five examples with concise steps and explicit checks; isolated summary page.')
