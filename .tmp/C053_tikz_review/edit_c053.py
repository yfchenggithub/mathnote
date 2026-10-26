from pathlib import Path
import json
base=Path('03_conic/C053_parabola_focal_chord_length_inclination')
def get(n):return (base/n).read_text(encoding='utf-8')
def put(n,s):(base/n).write_text(s,encoding='utf-8')

put('02_explanation.tex',r'''\clearpage
\begin{explanationbox}
\textbf{先用一条真实的弦认清所有字母。}图中 $y^2=4x$，故 $p=2$；直线以 $60^\circ$ 穿过焦点。
\begin{center}\input{assets/tikz/C053_focal_chord_notation.tex}\end{center}
蓝段是 $FA=r$，橙段是 $FB=s$。两端到准线的水平距离分别等于这两段长度，故
\[
 L=r+s=AM+BN=x_A+x_B+p.
\]
图中两段为 $4$ 与 $4/3$，所以整弦是 $16/3$，不能只算一段或任意倍增。
\end{explanationbox}
\clearpage
\begin{explanationbox}
\textbf{只改变方向，弦长怎样变化？}保持抛物线、焦点和绘图尺度相同，看两端的变化。
\begin{center}\input{assets/tikz/C053_angle_comparison.tex}\end{center}
中间是竖直通径，两侧的焦半径相等，弦长最短；两边的弦关于 $x$ 轴对称，长短两段互换，总长相同。
\[
 L=\frac{2p}{\sin^2\theta}\ge2p,\qquad
 \sin^2(\pi-\theta)=\sin^2\theta.
\]
\textbf{读图要点：}越接近 $90^\circ$ 越短；不是角度越大就越短。
下面分别画出正向、反向的投影，解释公式中的两个分母从哪里来。
\end{explanationbox}
''')

s=get('03_proof.tex')
i2=s.index(r'\textbf{\textcolor{CProof}{方法二')
i3=s.index(r'\textbf{\textcolor{CProof}{方法三')
i4=s.index(r'\textbf{\textcolor{CProof}{方法四')
tail=s[i4:]
mirror=tail.index(r'\textbf{\textcolor{CProof}{左右开口统一性')
endmirror=tail.index(r'\textbf{\textcolor{CProof}{通径最短的证明')
tail=tail[:mirror]+r'''\begin{center}\input{assets/tikz/C053_opening_reflection.tex}\end{center}
左右开口的图形关于 $y$ 轴镜像；长度不变，倾斜角变为 $\pi-\theta$，正弦平方不变。
因此左右开口均有 $L=2p/\sin^2\theta$，$p$ 都取正数。
\medskip
'''+tail[endmirror:]
method2=s[i2:i3].rstrip().removesuffix(r'\medskip').rstrip()
method3=s[i3:i4].rstrip().removesuffix(r'\medskip').rstrip()
method3=method3.replace('若交点对应 $t_1,t_2$，就有 $L=|t_1-t_2|$。','两个交点对应 $t_1>0>t_2$，与前图一致：$t_1=r$、$t_2=-s$，故 $L=t_1-t_2=r+s$。')
prefix=r'''\clearpage
\begin{proofbox}
\textbf{\textcolor{CProof}{方法一：焦点准线定义＋两端投影（先求正向一段）}}

取右开口 $y^2=2px$，$F=(p/2,0)$，准线 $x=-p/2$。
沿 $(\cos\theta,\sin\theta)$ 到 $A$，反向到 $B$，令 $r=FA$、$s=FB$。
\begin{center}\input{assets/tikz/C053_forward_projection.tex}\end{center}
\textbf{先看 $AF$：}图中 $H$ 在 $F$ 的正上方，$MH=p$，$HA=r\cos\theta$。
由抛物线定义 $FA=AM$，一般地按有向投影写成
\[
 r=p+r\cos\theta\quad\Longrightarrow\quad
 \boxed{r=\frac{p}{1-\cos\theta}}.
\]
两张投影图取 $p=2,\theta=60^\circ$ 便于观察；公式用有向分量，对任意 $0<\theta<\pi$ 均成立。
\end{proofbox}
\clearpage
\begin{proofbox}
\textbf{\textcolor{CProof}{方法一（续）：补齐反向一段，再把两段相加}}
\begin{center}\input{assets/tikz/C053_backward_projection.tex}\end{center}
\textbf{再看 $BF$：}图中 $K$ 在 $F$ 的正下方，$NK=p$，$BK=s\cos\theta$。
到准线的距离是 $BN=NK-BK$，由 $FB=BN$ 得
\[
 s=p-s\cos\theta\quad\Longrightarrow\quad
 \boxed{s=\frac{p}{1+\cos\theta}}.
\]
两分母在 $0<\theta<\pi$ 内均为正；焦点处于两个交点之间，故
\[
 L=r+s=\frac p{1-\cos\theta}+\frac p{1+\cos\theta}
 =\frac{2p}{1-\cos^2\theta}=\boxed{\frac{2p}{\sin^2\theta}}.
\]
\textbf{记忆：}正向减余弦，反向加余弦；两段相加，平方差给出正弦平方。
\end{proofbox}
\clearpage
\begin{proofbox}
'''
put('03_proof.tex',prefix+method2+'\n\\end{proofbox}\n\\clearpage\n\\begin{proofbox}\n'+method3+'\n\\end{proofbox}\n\\clearpage\n\\begin{proofbox}\n'+tail)

s=get('04_examples.tex')
s='\\clearpage\n'+s
for title in ['例4（左开口，公式不换号）','例6（坐标核验：检查图像是否真的准确）']:
    key=r'\textbf{\textcolor{CExample}{'+title
    s=s.replace(key,'\\end{examplebox}\n\\clearpage\n\\begin{examplebox}\n'+key)
s=s.replace(r'\textbf{这一例可以同时用来检查图：先定交点，再画线和抛物线，保证两点确在图上。}',r'\textbf{回看理解说明的总览图：}蓝段 $FA=4$，橙段 $FB=4/3$，与坐标距离所得 $16/3$ 完全一致。')
put('04_examples.tex',s)

s=get('05_traps.tex')
prefix=r'''\clearpage
\begin{trapbox}
\textbf{先看反例：方向相同，也不能保证弦长相同。}
\begin{center}\input{assets/tikz/C053_validity_comparison.tex}\end{center}
左图轴线仅交于顶点，不能当作两端点不同的焦点弦；中、右两图同为竖直弦，右图不经过焦点，所以长度不同。
\textbf{正确做法：}先验“过焦点、两个不同交点”，再套弦长公式。
当 $\theta\to0^+$ 或 $\pi^-$ 时弦长趋于无穷大，是极限现象；$\theta=0$ 本身没有这条有限焦点弦。
\end{trapbox}
\clearpage
\begin{trapbox}
\textbf{开口方向变了，先看角从哪条轴量。}
\begin{center}\input{assets/tikz/C053_vertical_axis_angle.tex}\end{center}
左右开口、角从 $x$ 轴量时用 $\sin^2\theta$；上下开口、角仍从 $x$ 轴量时改用 $\cos^2\theta$。
图中的弦长是 $16/3$，不能把 $30^\circ$ 直接代进分母 $\sin^2\theta$。
最短的始终是垂直于对称轴的通径：上下开口时为水平弦。
\end{trapbox}
\clearpage
'''
put('05_traps.tex',prefix+s)
put('06_summary.tex','\\clearpage\n'+get('06_summary.tex'))

m=json.loads(get('meta.json'))
m['remarks']='2026-10-26补充七幅正式教学TikZ：assets/tikz/C053_focal_chord_notation.tex（焦准距、两段与坐标）、C053_forward_projection.tex（正向投影）、C053_backward_projection.tex（反向投影）、C053_angle_comparison.tex（通径最短与互补角）、C053_opening_reflection.tex（开口镜像）、C053_validity_comparison.tex（轴线、通径与普通弦）、C053_vertical_axis_angle.tex（上下开口计角）。替换原理解说明中条件加载的小型通径图，压缩重复投影文字，四种证明与原有例题均保留。原有两份图源不覆盖。'
m['interactive']['has_diagram']=True
m['meta']['updated_at']='2026-10-26'
put('meta.json',json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print('C053 proof methods and examples preserved; diagram-led explanation and pitfalls updated.')
