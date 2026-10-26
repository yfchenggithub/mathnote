from pathlib import Path
import json
b=Path('03_conic/C054_parabola_focal_chord_reciprocal_sum')
def put(n,s): (b/n).write_text(s.strip()+'\n',encoding='utf-8')
put('01_statement.tex',r'''
\begin{statementbox}
\textbf{\textcolor{CStatement}{条件与符号}}

抛物线 $y^2=2px$，$p>0$；焦点 $F(p/2,0)$，准线 $x=-p/2$。
过 $F$ 的直线与抛物线相交于两个不同的有限点 $A,B$。
记两段正长度 $r=AF$、$s=BF$；焦点在线段 $AB$ 内，故 $AB=r+s$。

\par\medskip
\textbf{\textcolor{CStatement}{核心结论：倒数之和不随弦的方向改变}}
\[
 \boxed{\frac1r+\frac1s=\frac2p},\qquad
 \boxed{2rs=p(r+s)}.
\]
这里 $p$ 是焦点到准线的距离；$2p$ 是方程中 $x$ 项的系数，也是通径长。

\par\medskip
\textbf{\textcolor{CStatement}{三条直接推论}}
\[
 AB=r+s=\frac{2rs}{p}\ge2p,
 \qquad AB=2p\iff r=s=p\quad\text{（通径）}.
\]
\[
 \boxed{s=\frac{pr}{2r-p}},\qquad r>\frac p2,\quad s>\frac p2.
\]
$p/2$ 是每一段长度的严格下界，不能由有限焦点弦取到。

\par\medskip
\textbf{\textcolor{CStatement}{与倾斜角的联系}}

若把上方端点叫作 $A$、下方端点叫作 $B$，直线倾斜角为 $0<\theta<\pi$，则
\[
 r=\frac p{1-\cos\theta},\quad
 s=\frac p{1+\cos\theta},\quad
 AB=\frac{2p}{\sin^2\theta}.
\]
交换端点时，两段公式随之交换；倒数和始终不变。

\par\medskip
\textbf{\textcolor{CStatement}{适用范围}}

四种标准开口 $y^2=\pm2px$、$x^2=\pm2py$，若均以正数 $p$ 表示焦准距，长度倒数和都为 $2/p$。
必须是过焦点的有限两点弦；对称轴只有一个交点，不属于此情形。
\end{statementbox}
''')

put('02_explanation.tex',r'''
\clearpage
\begin{explanationbox}
\textbf{第一步，先只看两个熟悉的直角三角形。}
普通点 $P$ 在斜线段 $AB$ 内；$H,K$ 是两端向过 $P$ 的水平直线所作垂足。
\begin{center}\input{assets/tikz/C054_pure_similarity.tex}\end{center}
两个直角相等，$P$ 处两个锐角又是对顶角，所以 $\triangle PAH\sim\triangle PBK$。
对应的水平边与斜边之比相等：$u/r=v/s$。
\textbf{先看懂这个比；它来自相似，不需要背新的公式。}
\end{explanationbox}
\clearpage
\begin{explanationbox}
\textbf{第二步，把同一结构放回本题。}图形和尺度保持不变；把普通点 $P$ 对应为焦点 $F$，再补上曲线与准线。
\begin{center}\input{assets/tikz/C054_parabola_similarity.tex}\end{center}
准线在左边，焦准距是 $p$。由等距定义，蓝段 $r=p+u$，橙段 $s=p-v$。
\[
 \frac ur=\frac vs
 \ \Longrightarrow\ \frac{r-p}{r}=\frac{p-s}{s}
 \ \Longrightarrow\ 1-\frac pr=\frac ps-1.
\]
于是 $p/r+p/s=2$。\textbf{倒数来自“水平边除以斜边”，再用定义把水平边换掉。}
\end{explanationbox}
\clearpage
\begin{explanationbox}
\textbf{第三步，转动焦点弦，看倒数怎样互相补偿。}这里统一按上下标号：上端为 $A$，下端为 $B$。
\begin{center}\input{assets/tikz/C054_reciprocal_comparison.tex}\end{center}
图中蓝、橙两段通常不等，取倒数后也不同；但两块条形合起来始终为 $1$。
这三条弦用于观察和核验，下一节再给出任意焦点弦的证明。
\[
 \frac1r=\frac{1-\cos\theta}{p},\qquad
 \frac1s=\frac{1+\cos\theta}{p}.
\]
一增一减的部分相加抵消，留下固定的 $2/p$。通径只是其中 $r=s=p$ 的对称情形。
\end{explanationbox}
''')

put('03_proof.tex',r'''
\clearpage
\begin{proofbox}
\textbf{\textcolor{CProof}{证明一：初中相似法——先用几何，再补抛物线定义}}

\textbf{先约定正长度。}对非竖直焦点弦，本证明把右端记为 $A$、左端记为 $B$。
令 $r=AF$、$s=BF$，并令 $u=x_A-p/2>0$、$v=p/2-x_B>0$。
它们正是上一节图中的两条水平边。

\par\medskip
\textbf{第1步：只用两个直角三角形相似。}
从两端向水平线作垂线，垂足为 $H,K$。
因 $A,F,B$ 共线，两个直角三角形在 $F$ 处锐角相等，故
\[
 \boxed{\frac{FH}{FA}=\frac{FK}{FB}},\qquad \frac ur=\frac vs.
\]
负斜率时把图关于水平线翻折，水平距离与相似关系都不变。

\par\medskip
\textbf{第2步：用到焦点等于到准线，把水平边换成斜边。}
准线 $x=-p/2$，所以
\[
 r=x_A+\frac p2=p+u,\quad
 s=x_B+\frac p2=p-v;
 \qquad u=r-p,\quad v=p-s.
\]

\par\medskip
\textbf{第3步：代入相似比，倒数自然出现。}
\[
\begin{aligned}
 \frac{r-p}{r}&=\frac{p-s}{s},\\
 1-\frac pr&=\frac ps-1,\\
 p\left(\frac1r+\frac1s\right)&=2,\\
 \boxed{\frac1r+\frac1s}&=\boxed{\frac2p}.
\end{aligned}
\]
\textbf{为何要除以斜边？}相似三角形给的就是这个比，不是为了凑倒数。

\par\medskip
\textbf{补齐竖直弦：}此时 $x_A=x_B=p/2$，由定义 $r=s=p$，所以倒数和也为 $2/p$。
\end{proofbox}

\clearpage
\begin{proofbox}
\textbf{\textcolor{CProof}{证明二：最快余弦法——把相似比换成三角函数}}

本证明改按上下标号：$A$ 为上端、$B$ 为下端；交换标号不影响倒数和。
令 $r=AF>0$、$s=BF>0$，倾斜角 $0<\theta<\pi$。
沿两条反向射线走到端点，横坐标为
\[
 x_A=\frac p2+r\cos\theta,\qquad
 x_B=\frac p2-s\cos\theta.
\]
抛物线定义给出 $AF=x_A+p/2$、$BF=x_B+p/2$，故
\[
 r=p+r\cos\theta,\qquad s=p-s\cos\theta.
\]
移项后分别除以 $pr$、$ps$：
\[
 \frac1r=\frac{1-\cos\theta}{p},\qquad
 \frac1s=\frac{1+\cos\theta}{p}.
\]
相加，余弦项相消：
\[
 \boxed{\frac1r+\frac1s}
 =\frac{1-\cos\theta+1+\cos\theta}{p}
 =\boxed{\frac2p}.
\]
这与相似法是同一原理：斜线两侧有相同的倾斜程度，水平分量符号相反。
若已经记住焦半径角度公式，考场上可以直接从两个倒数相加开始。
\end{proofbox}

\clearpage
\begin{proofbox}
\textbf{\textcolor{CProof}{证明三：坐标韦达法——只求两段长度的和与积}}

设过焦点的直线为 $x=my+p/2$，$m\in\mathbb R$。
$m=0$ 包含竖直通径；水平轴线不在这一族中，但它只有一个交点，本来不属于有限两点弦。

\par\medskip
\textbf{第1步：联立抛物线，得到一元二次式。}
\[
 y^2=2p\left(my+\frac p2\right)
 \ \Longrightarrow\ y^2-2pmy-p^2=0.
\]
两根为 $y_1,y_2$，于是
\[
 y_1+y_2=2pm,\qquad y_1y_2=-p^2.
\]
\textbf{第2步：用定义写焦半径。}
由 $x_i=my_i+p/2$ 得
\[
 r=my_1+p,\qquad s=my_2+p.
\]
\textbf{第3步：要算 $(r+s)/(rs)$，就分别算和、积。}
\[
\begin{aligned}
 r+s&=m(y_1+y_2)+2p=2p(1+m^2),\\
 rs&=m^2y_1y_2+mp(y_1+y_2)+p^2\\
   &=-p^2m^2+2p^2m^2+p^2=p^2(1+m^2).
\end{aligned}
\]
\textbf{第4步：通分相除，参数自动消掉。}
\[
 \frac1r+\frac1s=\frac{r+s}{rs}
 =\frac{2p(1+m^2)}{p^2(1+m^2)}=\boxed{\frac2p}.
\]
倒数和对两端交换不敏感，正好由韦达给出的和、积来求，无需解出交点根式。
\end{proofbox}

\clearpage
\begin{proofbox}
\textbf{\textcolor{CProof}{证明四：参数法——两端参数互为负倒数}}

取抛物线上参数点 $P(t)=(pt^2/2,pt)$，代入即满足 $y^2=2px$。
设不同两点 $A=P(t_1)$、$B=P(t_2)$。
由两点坐标消元可得弦所在直线
\[
 x=\frac{t_1+t_2}{2}\,y-\frac p2t_1t_2.
\]
代入焦点 $F(p/2,0)$，得到充要条件
\[
 \boxed{t_1t_2=-1}.
\]
定义给出
\[
 r=\frac p2(1+t_1^2),\qquad s=\frac p2(1+t_2^2).
\]
于是 $t_2=-1/t_1$，$t_1\ne0$，
\[
\begin{aligned}
 \frac1r+\frac1s
 &=\frac2p\left(\frac1{1+t_1^2}+\frac1{1+1/t_1^2}\right)\\
 &=\frac2p\left(\frac1{1+t_1^2}+\frac{t_1^2}{1+t_1^2}\right)
 =\boxed{\frac2p}.
\end{aligned}
\]
同一分母下的两项恰好补成 $1$，与前面的双色条形图含义一致。

\par\medskip
\textbf{继续推出长度界限与最短弦。}由倒数和式可得
\[
 s=\frac{pr}{2r-p},\quad r>p/2;
 \qquad 2rs=p(r+s).
\]
又 $(r+s)^2\ge4rs=2p(r+s)$，除以正数 $r+s$ 得 $r+s\ge2p$。
等号当且仅当 $r=s=p$，即通径。
\end{proofbox}
''')

put('04_examples.tex',r'''
\clearpage
\begin{examplebox}
\textbf{\textcolor{CExample}{例1：已知一段，求另一段}}

\textbf{题目：}$y^2=4x$，焦点弦满足 $AF=3$，求 $BF$。
\begin{center}\input{assets/tikz/C054_length_pair_domain.tex}\end{center}
由 $2p=4$ 得 $p=2$。令 $BF=s$，则
\[
 \frac13+\frac1s=1\quad\Longrightarrow\quad
 \frac1s=\frac23\quad\Longrightarrow\quad\boxed{s=\frac32}.
\]
图中橙点就是配对 $(3,3/2)$。回验 $1/3+2/3=1$，且两段均大于 $p/2=1$。
\end{examplebox}

\clearpage
\begin{examplebox}
\textbf{\textcolor{CExample}{例2：给倾角，分别求倒数和与弦长}}

\textbf{题目：}$y^2=8x$ 的焦点弦倾斜角为 $60^\circ$，求倒数和及 $AB$。
由 $p=4$，倒数和为 $\boxed{2/p=1/2}$，与角度无关。
按上、下端标号，
\[
 AF=\frac4{1-1/2}=8,\quad BF=\frac4{1+1/2}=\frac83,
 \quad\boxed{AB=\frac{32}3}.
\]
回验 $1/8+3/8=1/2$，且 $AB=2p/\sin^260^\circ=32/3$。

\par\medskip
\textbf{\textcolor{CExample}{例3：给比例，只设一个未知数}}

\textbf{题目：}$y^2=4x$ 的焦点弦满足 $AF:BF=3:1$，求倒数和及 $AB$。
$p=2$，故倒数和为 $1$。设 $AF=3t$、$BF=t$，$t>0$，则
\[
 \frac1{3t}+\frac1t=1\quad\Longrightarrow\quad t=\frac43.
\]
所以 $\boxed{AF=4,\ BF=4/3,\ AB=16/3}$。
这正是前面相似图的两段；回验 $1/4+3/4=1$。

\par\medskip
\textbf{\textcolor{CExample}{迁移训练：比例换成 $2:3$}}

\textbf{题目：}$y^2=12x$ 的焦点弦满足 $AF:BF=2:3$，求两段及弦长。
$p=6$，设 $AF=2t$、$BF=3t$，则
\[
 \frac1{2t}+\frac1{3t}=\frac13
 \quad\Longrightarrow\quad t=\frac52.
\]
故 $\boxed{AF=5,\ BF=15/2,\ AB=25/2}$。
回验 $1/5+2/15=1/3=2/p$。
\end{examplebox}

\clearpage
\begin{examplebox}
\textbf{\textcolor{CExample}{例4：由倒数和推出通径最短}}

\textbf{题目：}对 $y^2=6x$，证明通径最短，并求其长度。
由 $p=3$，记 $r=AF,s=BF$，则 $1/r+1/s=2/3$。
\[
 (r+s)\left(\frac1r+\frac1s\right)
 =2+\frac rs+\frac sr\ge4.
\]
故 $\boxed{r+s\ge4/(2/3)=6}$。
等号要求 $r=s$，再由倒数和得 $r=s=3$；这正是通径。
\textbf{回验：}竖直线 $x=3/2$ 的端点为 $(3/2,\pm3)$，弦长为 $6$。

\par\medskip
\textbf{\textcolor{CExample}{例5：检查“已知长度”是否可能}}

\textbf{题目：}$y^2=4x$ 是否存在有限焦点弦使 $AF=1$？
此时 $p=2$。若 $AF=1$，则
\[
 1+\frac1{BF}=1\quad\Longrightarrow\quad\frac1{BF}=0,
\]
不可能由有限的正长度 $BF$ 满足，所以\textbf{不存在}。
一般地，$1/s=2/p-1/r>0$，因此
\[
 \boxed{r>p/2},\qquad \boxed{s>p/2}.
\]
回看例1配对曲线的两条虚线：长度可以无限接近下界，不能取到。
注意 $p/2$ 是\textbf{严格下界}，不是可取得的最小值。
\end{examplebox}
''')

put('05_traps.tex',r'''
\clearpage
\begin{trapbox}
\textbf{先看结构差异，再决定能不能套定理。}
\begin{center}\input{assets/tikz/C054_validity_comparison.tex}\end{center}
中图也是竖直弦，但不经过焦点，倒数和为 $2/3$；右图只有顶点一个交点。
\textbf{正确检查：}必须经过焦点，且有两个不同的有限交点。
左图通径只能核验定理的特例，不能代替对所有倾斜弦的证明。
\end{trapbox}

\clearpage
\begin{trapbox}
\textbf{改变开口时，长度定值为什么保持不变？}
\begin{center}\input{assets/tikz/C054_four_openings.tex}\end{center}
四图给出同一几何结构的对应；翻折、旋转保持距离，故任意对应的焦点弦都有相同倒数和。
统一用正数 $p$ 表示焦准距，不能给左开口或下开口的长度定值加负号。
\end{trapbox}

\clearpage
\begin{trapbox}
\textbf{八项易错，各用一个动作纠正}
\begin{enumerate}[leftmargin=*,itemsep=.65em]
\item \textbf{用通径代替一般证明：}通径只验证 $r=s=p$；一般性依靠相似、余弦或联立韦达。
\item \textbf{焦半径写成 $x-p/2$：}先写准线 $x=-p/2$，点到它的水平距离是 $x+p/2$。
\item \textbf{端点标号和正负余弦不对应：}证明一按左右标号；角度式按上下标号。
若 $A$ 在上，则 $r=p/(1-\cos\theta)$，$s=p/(1+\cos\theta)$；交换端点要连公式一起换，倒数和不变。
\item \textbf{斜截式漏掉通径：}用 $x=my+p/2$，$m=0$ 就是竖直通径；水平轴线本来不是有限两点弦。
\item \textbf{忽略正且有限：}两段都须大于 $p/2$；由单段反求 $s=pr/(2r-p)$ 时，先检查 $2r-p>0$。
\item \textbf{混淆系数：}$y^2=2px$ 中 $p$ 是焦准距；若写作 $y^2=4ax$，则 $p=2a$，倒数和为 $1/a$，不是 $2/a$。
\item \textbf{开口改变就给长度定值换号：}四种标准式均取 $p>0$；倒数和仍为 $2/p$。
单段的三角表达式才需要重新约定轴向和射线方向。
\item \textbf{普通弦也套公式：}先确认 $F\in AB$，并有不同的有限端点；反例图中的平行弦长度与倒数和都不同。
\end{enumerate}
\textbf{自检三问：}焦准距找对了吗？确实过焦点吗？求出的单段长度大于 $p/2$ 吗？
\end{trapbox}
''')

put('06_summary.tex',r'''
\clearpage
\begin{summarybox}
\textbf{\textcolor{CSummary}{从熟悉结构走到新结论}}

先看两个相似的直角三角形：$u/r=v/s$。
再补上抛物线定义：$r=p+u$、$s=p-v$。
把水平边换掉，就自然得到
\[
 \frac{r-p}{r}=\frac{p-s}{s}
 \quad\Longrightarrow\quad\boxed{\frac1r+\frac1s=\frac2p}.
\]
\textbf{相似给比值，定义给等量；倒数来自除以斜边。}

\par\medskip
\textbf{\textcolor{CSummary}{三条速查}}
\[
 AB=r+s=\frac{2rs}{p}\ge2p,\qquad
 AB=2p\iff r=s=p.
\]
\[
 s=\frac{pr}{2r-p},\qquad r>p/2,\ s>p/2.
\]
按上下端标号且角度从横轴量，右开口时
\[
 \frac1r=\frac{1-\cos\theta}{p},\qquad
 \frac1s=\frac{1+\cos\theta}{p}.
\]

\par\medskip
\textbf{\textcolor{CSummary}{四种证明怎样选}}

理解来源用\textbf{相似法}；已知倾角用\textbf{余弦法}；综合坐标约束用\textbf{韦达法}，只算 $r+s$ 与 $rs$；
研究端点参数时用\textbf{参数法}，过焦点的条件是 $t_1t_2=-1$。

\par\medskip
\textbf{\textcolor{CSummary}{最后检查}}
\begin{itemize}[leftmargin=*,itemsep=.35em]
\item 是过焦点的两点有限弦吗？焦点是否处于两端之间？
\item $p$ 是正的焦准距吗？方程系数是否为 $2p$？
\item 已知比例时，是否只设一个正参数？
\item 单段是否大于 $p/2$，总长是否至少为 $2p$？
\end{itemize}
四种标准开口的倒数和相同；先看熟悉的结构，再认新概念，最后用公式。
\end{summarybox}
''')
m=json.loads((b/'meta.json').read_text(encoding='utf-8'))
m['remarks']='2026-10-26新增六幅精确TikZ，图源均在 assets/tikz/：C054_pure_similarity.tex（无圆锥曲线概念的初中相似）、C054_parabola_similarity.tex（同形同尺度映射到抛物线）、C054_reciprocal_comparison.tex（方向变化及倒数补偿）、C054_length_pair_domain.tex（已知一段反求与严格下界）、C054_validity_comparison.tex（通径、普通弦、轴线反例）、C054_four_openings.tex（四种开口距离不变）。替换原理解说明的小型通径图输入，原图源不覆盖。保留四种证明、五道例题和迁移训练，压缩重复空间口述；相似法左右标号和角度式上下标号明确区分。'
m['interactive']['has_diagram']=True;m['meta']['updated_at']='2026-10-26'
(b/'meta.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('C054 updated: four proofs, five examples and transfer exercise retained.')
