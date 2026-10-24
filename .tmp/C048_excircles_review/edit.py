from pathlib import Path
import math, json
root=Path('D:/mathnote')
uid=root/'03_conic/C048_hyperbola_focus_triangle_area'
q=math.sqrt(7)
A=(-2,0); B=(2.5,1.5*q); C=(2,0)
def pt(v): return '('+','.join(f'{x:.8f}' for x in v)+')'
def frame(title,h=10):
    return [r'\begin{center}',r'\begin{tikzpicture}[x=1cm,y=1cm,line cap=round,line join=round,font=\small]',
            rf'\draw[black!25,rounded corners=3pt] (0,0) rectangle (14.4,{h});',
            rf'\node[font=\small\bfseries] at (7.2,{h-.5}) {{{title}}};']
def end(lines,name):
    lines += [r'\end{tikzpicture}',r'\end{center}']
    (root/'assets/tikz'/name).write_text('\n'.join(lines)+'\n',encoding='utf-8')
def geom(lines,I,R,feet,scale,shift,lab):
    lines += [rf'\begin{{scope}}[shift={{{pt(shift)}}},x={scale}cm,y={scale}cm]']
    for key,v in dict(A=A,B=B,C=C,I=I,T=feet[0],U=feet[1],V=feet[2]).items():
        lines.append(rf'\coordinate ({key}) at {pt(v)};')
    lines += [rf'\fill[green!4] (I) circle ({R:.8f});',rf'\draw[green!45!black,thick] (I) circle ({R:.8f});',
              r'\fill[red!7] (A)--(B)--(C)--cycle;',r'\draw[red!75!black,thick] (A)--(B)--(C)--cycle;']
    # Three supporting-line portions extend only to their actual tangency feet.
    for f,(v,w) in zip(feet,[(B,C),(A,B),(A,C)]):
        den=sum((w[k]-v[k])**2 for k in range(2))
        t=sum((f[k]-v[k])*(w[k]-v[k]) for k in range(2))/den
        if t<0: lines.append(rf'\draw[red!65!black,dashed] {pt(v)}--{pt(f)};')
        elif t>1: lines.append(rf'\draw[red!65!black,dashed] {pt(w)}--{pt(f)};')
    # Foot ordering above is only for I1. Other circles supply explicit extensions below.
    for nm,f in zip('TUV',feet):
        lines.append(rf'\draw[purple!75,dashed] (I)--({nm});')
        e=((I[0]-f[0])/R,(I[1]-f[1])/R); t=(-e[1],e[0]); z=.13/scale
        corner=[(f[0]+z*t[0],f[1]+z*t[1]),(f[0]+z*(t[0]+e[0]),f[1]+z*(t[1]+e[1])),(f[0]+z*e[0],f[1]+z*e[1])]
        lines.append(r'\draw[purple!75] '+'--'.join(pt(v) for v in corner)+';')
    for nm,txt,pos in [('A',r'F_1','below left'),('B','P','above left'),('C',r'F_2','below right'),('I',lab,'above right')]:
        lines.append(rf'\fill ({nm}) circle (1.5pt); \node[{pos}] at ({nm}) {{$'+txt+r'$};')
    for nm,pos in zip('TUV',['left','above left','below']):
        lines.append(rf'\fill[purple!75] ({nm}) circle (1.5pt); \node[{pos},fill=white,inner sep=1pt] at ({nm}) {{$'+nm+r'$};')
    lines.append(r'\end{scope}')

# Same exact 6-4-4 triangle in every panel. Each panel is uniformly scaled.
specs=[
 ('C048_excircle_opposite_f1.tex','① 对应 $F_1$：与边 $PF_2$ 相切（本法选它）',(5,q),q,[(19/8,9*q/8),(13/4,7*q/4),(5,0)],1.02,(3.0,2.2),'I_1',
  r'$T\in\overline{PF_2}$；$U$ 越过 $P$；$V$ 越过 $F_2$',r'$r_1=\sqrt7,\quad PT=PU=1=c-a$'),
 ('C048_excircle_opposite_p.tex','② 对应 $P$：与边 $F_1F_2$ 相切',(-1,-q),q,[(-1,0),(-11/4,-q/4),(13/8,-9*q/8)],.95,(7,5.5),'I_P',
  r'$T\in\overline{F_1F_2}$；$U$ 越过 $F_1$；$V$ 越过 $F_2$',r'$r_P=\sqrt7$（本例等腰，恰有 $r_P=r_1$）'),
 ('C048_excircle_opposite_f2.tex','③ 对应 $F_2$：与边 $F_1P$ 相切',(-5,3*q),3*q,[(1/4,3*q/4),(23/8,21*q/8),(-5,0)],.46,(8.6,1.8),'I_2',
  r'$T\in\overline{F_1P}$；$U$ 越过 $P$；$V$ 越过 $F_1$',r'$r_2=3\sqrt7$（大圆仍完整画出）')]
# Explicit supporting segments for each local naming convention.
segments=[ [('B','U'),('C','V')], [('A','U'),('C','V')], [('B','U'),('A','V')] ]
for idx,(name,title,I,R,feet,scale,shift,lab,caption,formula) in enumerate(specs):
    ls=frame(title,10.5)
    # Generic extension mapping is replaced with the actual named sides below.
    start=len(ls);geom(ls,I,R,feet,scale,shift,lab)
    ls=[v for i,v in enumerate(ls) if not (i>=start and v.startswith(r'\draw[red!65!black,dashed]'))]
    insert=next(i for i,v in enumerate(ls) if v.startswith(r'\draw[purple!75,dashed]'))
    ls[insert:insert]=[rf'\draw[red!65!black,dashed] ({x})--({y});' for x,y in segments[idx]]
    ls += [rf'\node at (7.2,1.15) {{{caption}}};',rf'\node at (7.2,.55) {{{formula}}};']
    end(ls,name)

ls=frame('外角半角局部图：$PI$ 平分外角，不是内角',8.8)
ls += [r'\begin{scope}[shift={(4,2.3)},x=1.65cm,y=1.65cm]',
        r'\coordinate (P) at (0,0); \coordinate (T) at (1,0);',rf'\coordinate (I) at (1,{q:.8f});',rf'\coordinate (U) at (-.75,{q/4:.8f});',
        r'\fill[green!6] (P)--(T)--(I)--cycle;',r'\draw[red!75!black,thick] (P)--(1.7,0) (P)--(U);',
        r'\draw[black!50,->] (P)--(-41.409622:1.5) node[right] {指向 $F_1$};',
        r'\draw[green!45!black,thick,dashed] (P)--(I);',r'\draw[purple!75,thick] (I)--(T);',
        r'\draw[purple!75] (.86,0)--(.86,.14)--(1,.14);',
        r'\draw[green!45!black] (.52,0) arc(0:69.295189:.52);',
        r'\draw[green!45!black] (69.295189:.69) arc(69.295189:138.590378:.69);',
        r'\node at (.67,.45) {$\alpha$}; \node at (-.25,.88) {$\alpha$};',
        r'\draw[red!75!black] (-41.409622:.83) arc(-41.409622:0:.83);',
        r'\node at (1.02,-.42) {$\theta$};',
        r'\node[below left] at (P) {$P$}; \node[below right] at (T) {$T$};',
        r'\node[above left] at (I) {$I=I_1$}; \node[above left] at (U) {$U$};',
        r'\node[right] at (1,1.6) {$r$};',r'\node at (.5,-.85) {$PT=c-a$};',r'\end{scope}',
        r'\node[align=left,anchor=north west] at (9,6.7) {$2\alpha+\theta=\pi$\\[1em]$\alpha=\dfrac{\pi-\theta}{2}$\\[1em]$\dfrac r{PT}=\tan\alpha$\\[1em]$\phantom{\dfrac r{PT}}=\cot\dfrac\theta2$};',
        r'\node at (7.2,.55) {只保留原图的局部关系，经旋转、放大；$PU$ 与 $PF_1$ 方向相反。};']
end(ls,'C048_excircle_half_angle.tex')

ls=frame('面积分解：加上前两块，再减去重复的一块',8)
for k,(vertices,col,caption) in enumerate([('ABI','blue',r'$+\,\frac12 mr$'),('ACI','green',r'$+\,\frac12(2c)r$'),('BCI','red',r'$-\,\frac12 nr$')]):
    ls += [rf'\begin{{scope}}[shift={{({1.4+k*4.8},3)}},x=.44cm,y=.44cm]']
    for nm,v in dict(A=A,B=B,C=C,I=(5,q),T=(19/8,9*q/8),U=(13/4,7*q/4),V=(5,0)).items():ls.append(rf'\coordinate ({nm}) at {pt(v)};')
    ls += [rf'\fill[{col}!16] '+'--'.join('('+v+')' for v in vertices)+'--cycle;',
           rf'\draw[{col}!60!black,thick] '+'--'.join('('+v+')' for v in vertices)+'--cycle;',
           r'\draw[red!75!black] (A)--(B)--(C)--cycle;']
    foot=['U','V','T'][k]
    if k==0:ls.append(r'\draw[black!50,dashed] (B)--(U);')
    if k==1:ls.append(r'\draw[black!50,dashed] (C)--(V);')
    ls.append(rf'\draw[purple!75,dashed] (I)--({foot}) node[midway,right] {{$r$}};')
    for nm,txt,pos in [('A',r'F_1','below left'),('B','P','above left'),('C',r'F_2','below'),('I','I','right')]:ls.append(rf'\node[{pos}] at ({nm}) {{$'+txt+r'$};')
    ls += [r'\end{scope}',rf'\node at ({2.4+k*4.8},2.25) {{{caption}}};']
ls += [r'\node at (7.2,6.65) {三幅均为同一三角形、同一尺度；紫色虚线是对应底边所在直线的高。};',
       r'\node at (7.2,1.3) {$S_{F_1PF_2}=S_{IF_1P}+S_{IF_1F_2}-S_{IPF_2}$};',
       r'\node at (7.2,.55) {$S=\dfrac r2(m+2c-n)=(a+c)r$};']
end(ls,'C048_excircle_area_decomposition.tex')

p=uid/'03_proof.tex'; original=p.read_bytes(); txt=original.decode('utf-8')
marker='\\clearpage\r\n\\begin{proofbox}\r\n\\textbf{\\textcolor{CProof}{方法五：'
if marker not in txt:marker=marker.replace('\r\n','\n')
prefix=txt[:txt.index(marker)]
tail=r'''\clearpage
\begin{proofbox}
\textbf{\textcolor{CProof}{方法五：纯几何法——先认清三个旁切圆（不使用余弦定理）}}

把离 $P$ 较远的焦点记为 $F_1$，较近的记为 $F_2$。设
\[
PF_1=m,\quad PF_2=n,\quad m-n=2a,\quad F_1F_2=2c,
\qquad s=\frac{m+n+2c}{2}.
\]
\textbf{先补充旁切圆性质。} 每个非退化三角形\textbf{恰有三个旁切圆}，分别对应三个顶点。
每个圆与该顶点的\textbf{对边线段}及另外两边的\textbf{延长线}相切。
圆心位于该顶点的内角平分线及另两个顶点的外角平分线上；到三边所在直线的距离都等于半径。
同一点向同一圆所引的两条切线段等长，且半径垂直于切线。

\textbf{① 本法选 $F_1$ 对应的旁切圆。} 记圆心 $I_1$、半径 $r_1$。
\input{assets/tikz/C048_excircle_opposite_f1}
图中 $T$ 在 $PF_2$ 上；$U,V$ 分别在越过 $P,F_2$ 的延长线上。
后文简记 $I=I_1,\ r=r_1$，不与另外两个圆的半径混用。
\end{proofbox}

\clearpage
\begin{proofbox}
\textbf{\textcolor{CProof}{方法五（预备知识续）：另外两个旁切圆}}

\textbf{② $P$ 对应的旁切圆：} 与边 $F_1F_2$ 相切，圆心记为 $I_P$，半径记为 $r_P$。
\input{assets/tikz/C048_excircle_opposite_p}
它的圆心在 $P$ 的\textbf{内角平分线}上；因此不能把本法使用的外半角关系直接套给它。

\textbf{三图均用同一个边长为 $6,4,4$ 的三角形。} 三图缩放不同，各自均等比例绘制；
比较半径请看数值，不按印在纸上的大小比较。本例等腰，两个旁切圆半径相等，但仍是两个不同的圆。
\end{proofbox}

\clearpage
\begin{proofbox}
\textbf{\textcolor{CProof}{方法五（预备知识续）：第三个旁切圆与面积关系}}

\textbf{③ $F_2$ 对应的旁切圆：} 与边 $F_1P$ 相切，圆心记为 $I_2$，半径记为 $r_2$。
\input{assets/tikz/C048_excircle_opposite_f2}
\textbf{统一记法：} 对边长为 $d$ 的旁切圆半径 $\rho$ 满足 $S=(s-d)\rho$。
这是把三边作底、半径作高，两个三角形面积相加再减一个得到的（后面画出本法所用的分解）。因此
\[
\begin{array}{c|c|c}
\text{对应顶点}&\text{实际相切的边}&\text{面积关系}\\ \hline
F_1&PF_2=n&S=(s-n)r_1=(a+c)r_1\\
P&F_1F_2=2c&S=(s-2c)r_P\\
F_2&PF_1=m&S=(s-m)r_2=(c-a)r_2
\end{array}
\]
\textbf{选择理由：} 本法用 $I_1$，是为了让切线长得到 $c-a$、面积因子得到 $c+a$，两者相乘恰是 $b^2$。
\end{proofbox}

\clearpage
\begin{proofbox}
\textbf{\textcolor{CProof}{方法五（正式推导）：等切线先给出 $c-a$}}

\textbf{第1步：回到第①图，只用同点切线等长。}
\[
PT=PU=x,\quad F_2T=F_2V=n-x,\quad F_1U=F_1V.
\]
由延长线上的线段相加，
\[
\underbrace{m+x}_{F_1U}=\underbrace{2c+n-x}_{F_1V}
\quad\Longrightarrow\quad
\boxed{PT=x=c-a}.
\]
\textbf{第2步：外角平分线给出半径。} $PU$ 与 $PF_1$ 反向，故外角为 $\pi-\theta$。
\input{assets/tikz/C048_excircle_half_angle}
在直角三角形 $PIT$ 中，$\angle IPT=(\pi-\theta)/2$，所以
\[
\frac r{PT}=\tan\frac{\pi-\theta}{2}=\cot\frac\theta2,
\qquad \boxed{r=(c-a)\cot\frac\theta2}.
\]
这里用的是\textbf{外角的一半}，不是 $\theta/2$。
\end{proofbox}

\clearpage
\begin{proofbox}
\textbf{\textcolor{CProof}{方法五（完成）：面积“加、加、减”给出 $c+a$}}

\textbf{第3步：三个底边所在直线到 $I$ 的距离都是 $r$。}
连 $IF_1,IP,IF_2$：沿 $IF_1$ 分割四边形 $F_1PIF_2$ 得到下面前两块；
沿 $PF_2$ 分割同一四边形，得到原三角形与第三块。所以第三块必须减去。
\input{assets/tikz/C048_excircle_area_decomposition}
\[
S=\frac12 mr+\frac12(2c)r-\frac12 nr
 =\frac r2(m-n+2c)=\boxed{(a+c)r}.
\]
\textbf{第4步：代入半径，认出 $b^2$。}
\[
S=(a+c)(c-a)\cot\frac\theta2
=(c^2-a^2)\cot\frac\theta2
=\boxed{b^2\cot\frac\theta2}.
\]
\textbf{记忆：} 等切线找 $c-a$，面积分解找 $c+a$，乘起来就是 $b^2$。

\textbf{适用范围：} $P$ 在任一分支且不是实轴顶点时均成立；只需先按距离远近重标 $F_1,F_2$。
顶点处三角形退化，本旁切圆构造不适用；面积公式仍可按极限延拓为 $0$。
\end{proofbox}
'''
p.write_bytes((prefix+tail.replace('\n','\r\n')).encode('utf-8'))
p=uid/'meta.json'; data=json.loads(p.read_text(encoding='utf-8'))
data['content']['derivation'].append('方法五：按距离远近标记焦点，选F1对应旁切圆；同点切线等长给PT=c-a，外角半角给r=(c-a)cot(θ/2)，面积加加减给S=(a+c)r，合得b²cot(θ/2)。非退化三角形有三个旁切圆，不能混用其半径。')
data['remarks']+=' 2026-10-24 方法五内补充三个旁切圆性质与面积关系，新增C048_excircle_opposite_f1/p/f2三图（不同缩放、各自等比例），C048_excircle_half_angle外半角局部图及C048_excircle_area_decomposition面积加加减图；替代原方法五的切点位置列表及纯文字半角、面积说明。原C048_excircle_exact.tex保留。验收见reports/C048_excircles_review_2026-10-24.md。'
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Wrote 5 TikZ files, method-five-only proof replacement, and metadata.')
