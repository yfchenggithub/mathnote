from pathlib import Path
import math,json,shutil,re
base=Path('03_conic/C057_hyperbola_focus_chord_reciprocal_sum_diff');work=Path('.tmp/C057_tikz_review')
(work/'before').mkdir(parents=True,exist_ok=True)
for f in list(base.glob('*.tex'))+[base/'meta.json']:shutil.copy2(f,work/'before'/f.name)
def figfile(stem,body,h=12):
 Path(f'assets/tikz/C057_{stem}.tex').write_text(r'\begin{tikzpicture}[font=\small,>=stealth]'+'\n'+rf'\draw[rounded corners=3pt,gray!45] (0,0) rectangle (14.2,{h});'+'\n'+body+'\n'+r'\end{tikzpicture}'+'\n',encoding='utf8')
def xy(pt):return f'({pt[0]:.10f},{pt[1]:.10f})'
sameA=(33/5,16*math.sqrt(6)/5);sameB=(21/5,-8*math.sqrt(6)/5)
q=-math.sqrt(3)/2;p=16/3;e=5/3
ra=p/(1-e*q);rb=p/(-1-e*q)
crossA=(5+ra*q,ra*.5);crossB=(5+rb*q,rb*.5)
def curve(a=3,b=4):
 return rf'''\draw[teal!75!black,thick,samples=110,domain=-1.9:1.9,variable=\t] plot ({{{a}*cosh(\t)}},{{{b}*sinh(\t)}});
\draw[teal!75!black,thick,samples=110,domain=-1.9:1.9,variable=\t] plot ({{-{a}*cosh(\t)}},{{{b}*sinh(\t)}});
'''
def panel(cx,cy,scale,A,B,a=3,b=4):
 c=math.hypot(a,b)
 st=rf'\begin{{scope}}[shift={{({cx},{cy})}},scale={scale}]'+'\n'
 st+=r'\begin{scope}\clip (-10,-9) rectangle (10,9);'+'\n'+curve(a,b)+r'\end{scope}'+'\n'
 st+=r'\draw[->,gray] (-10.2,0)--(10.3,0);'+'\n'
 # AF blue. BF orange; for same-ray geometry keep overlapping AF visible on top.
 st+=rf'\draw[orange!85!black,very thick] ({c},0)--{xy(B)};\draw[blue!75!black,very thick] ({c},0)--{xy(A)};'+'\n'
 st+=rf'\fill {xy(A)} circle(2pt) node[above right=7pt] {{$A$}};\fill {xy(B)} circle(2pt) node['+('below=8pt' if B[1]<0 else 'above left=8pt')+r'] {$B$};'+'\n'
 st+=rf'\fill ({c},0) circle(2pt) node[below right=9pt] {{$F$}};'+'\n'
 return st+r'\end{scope}'+'\n'

st=''
for cx,A,B,title in [(3.6,sameA,sameB,'同支：焦点在中间'),(10.6,crossA,crossB,'异支：焦点在外面')]:
 st+=rf'\node at ({cx},10.45) {{{title}}};'+'\n'+panel(cx,6.1,.28,A,B)
 st+=rf'\node at ({cx},2.6) {{'+(r'$A-F-B$：两条反向射线' if cx<5 else r'$F-A-B$：同一条射线')+r'};'+'\n'
 st+=rf'\node at ({cx},1.55) {{'+(r'倒数\textbf{相加}' if cx<5 else r'倒数\textbf{相减}，取绝对值')+r'};'+'\n'
figfile('statement_comparison',r'\node at (7.1,11.65) {先看站位：双曲线的“过焦点”，说的是整条直线};'+st+r'\node at (7.1,.55) {两图同为 $x^2/9-y^2/16=1$、同尺度；$F=(5,0)$。};',12.2)

figfile('pure_positions',r'''
\node at (7.1,11.55) {先拿掉双曲线：只比较一条直线上的三个点};
\node at (7.1,10.25) {上图：中间点 $P$，两端在相反方向};
\draw[gray] (1.2,8.6)--(12.9,8.6);
\draw[blue!75!black,very thick] (6.2,8.6)--(10.2,8.6);
\draw[orange!85!black,very thick] (6.2,8.6)--(3.2,8.6);
\fill (10.2,8.6) circle(2pt) node[above=9pt] {$A$};
\fill (6.2,8.6) circle(2pt) node[above=9pt] {$P$};
\fill (3.2,8.6) circle(2pt) node[above=9pt] {$B$};
\draw[->,blue!75!black] (6.5,7.9)--(9.7,7.9);
\draw[->,orange!85!black] (5.9,7.9)--(3.7,7.9);
\node at (7.1,6.85) {$AB=PA+PB$，两段的水平位移方向相反。};
\node at (7.1,5.35) {下图：外部点 $P$，两端在同一方向};
\draw[gray] (1.2,3.8)--(12.9,3.8);
\draw[orange!85!black,very thick] (11.2,3.8)--(2.2,3.8);
\draw[blue!75!black,very thick] (11.2,3.8)--(7.2,3.8);
\fill (11.2,3.8) circle(2pt) node[above=9pt] {$P$};
\fill (7.2,3.8) circle(2pt) node[above=9pt] {$A$};
\fill (2.2,3.8) circle(2pt) node[above=9pt] {$B$};
\draw[->,blue!75!black] (10.8,3.1)--(7.7,3.1);
\draw[->,orange!85!black] (10.8,2.6)--(2.7,2.6);
\node at (7.1,1.6) {$AB=PB-PA$，两段的水平位移方向相同。};
\node at (7.1,.55) {此图只认位置和方向；倒数的加减还需要后面的焦半径关系。};''',12.2)

body=r'\node at (7.1,15.65) {再看初中相似：同向的投影比相等，反向的投影比相反};'
for cy,same in [(11.0,True),(4.75,False)]:
 # Unit direction (3/5,4/5) or (-3/5,4/5), lengths 2 and 1 / 1 and 3.
 A=(1.2,1.6) if same else (-.6,.8);B=(-.6,-.8) if same else (-1.8,2.4)
 body+=rf'\node at (7.1,{cy+3.1}) {{'+('反向：普通点 $P$ 在两端中间' if same else '同向：普通点 $P$ 在两端外面')+r'};'+'\n'
 body+=rf'\begin{{scope}}[shift={{(5.2,{cy})}},scale=1.1]'+'\n'
 body+=r'\draw[gray] (-3,0)--(2,0);'+'\n'
 body+=rf'\draw[orange!85!black,very thick] (0,0)--{xy(B)};\draw[blue!75!black,very thick] (0,0)--{xy(A)};'+'\n'
 for pt,label,color in [(A,'A','blue!75!black'),(B,'B','orange!85!black')]:
  body+=rf'\draw[gray,dashed] {xy(pt)}--({pt[0]},0);\fill {xy(pt)} circle(2pt) node['+('above=8pt' if pt[1]>0 else 'below=8pt')+rf'] {{${label}$}};'+'\n'
 body+=r'\fill (0,0) circle(2pt) node[below right=8pt] {$P$};\end{scope}'+'\n'
 formula=r'\dfrac{x_A-x_P}{PA}=-\dfrac{x_B-x_P}{PB}' if same else r'\dfrac{x_A-x_P}{PA}=\dfrac{x_B-x_P}{PB}'
 body+=rf'\node[align=left,anchor=west] at (8.6,{cy+.9}) {{'+('两个直角三角形相似'+r'\\[13pt]水平位移一正一负' if same else '两个直角三角形相似'+r'\\[13pt]水平位移都是负数')+r'};'+'\n'
 body+=rf'\node at (7.1,{cy-1.75}) {{$\displaystyle {formula}$}};'+'\n'
body+=r'\node at (7.1,.6) {所有 $PA,PB$ 都是正长度；分子才是有正负号的水平位移。};'
figfile('pure_projection',body,16.2)

st=panel(4.5,7.5,.37,sameA,sameB)
st+=r'''
\node[anchor=west,align=left] at (9.5,8.3)
 {图取 $a=3,b=4,c=5$\\[13pt]$AF=8,\quad BF=4$\\[13pt]两点都在右支\\[13pt]$F$ 在 $AB$ 内\\[13pt]方向相反};
\node at (7.1,3.65) {$\displaystyle \frac18+\frac14=\frac38=\frac{2a}{b^2}$};
\fill[blue!30] (3,2.25) rectangle (4.4,2.75);
\fill[orange!35] (4.4,2.25) rectangle (7.2,2.75);
\draw[gray] (3,2.25) rectangle (7.2,2.75);
\node[blue!75!black] at (3.7,1.65) {$1/AF=1/8$};
\node[orange!85!black] at (5.8,1.0) {$1/BF=1/4$};
\node[anchor=west] at (8.1,2.5) {两块合起来，才是固定的 $3/8$};
\node at (7.1,.45) {条形图表示倒数；上面的蓝、橙线段表示原长度，两者不能混读。};'''
figfile('same_branch_sum',r'\node at (7.1,12.55) {放回双曲线：同支、反向，两段的倒数相加};'+st,13.2)

A2=(math.sqrt(5),2);B2=(-2*math.sqrt(5),8)
st=panel(4.5,7.1,.37,A2,B2,2,4)
st+=r'''
\node[anchor=west,align=left] at (9.5,8.15)
 {图取 $a=2,b=4$\\[13pt]$AF=3,\quad BF=12$\\[13pt]$A$ 在右支，$B$ 在左支\\[13pt]顺序是 $F-A-B$\\[13pt]右支点 $A$ 更近};
\node at (7.1,3.6) {$\displaystyle \frac13-\frac1{12}=\frac14=\frac{2a}{b^2}$};
\fill[blue!30] (2.8,2.15) rectangle (7.6,2.65);
\fill[orange!40] (6.4,2.15) rectangle (7.6,2.65);
\draw[gray] (2.8,2.15) rectangle (7.6,2.65);
\draw[orange!85!black,thick] (6.4,2.0)--(7.6,2.8) (6.4,2.8)--(7.6,2.0);
\node[blue!75!black] at (4.6,1.45) {剩下 $1/4$};
\node[orange!85!black,anchor=west] at (8.2,2.4) {减掉 $1/BF=1/12$};
\node at (7.1,.6) {整条色条原长是 $1/AF=1/3$；减去橙色部分，留下固定差。};'''
figfile('cross_branch_difference',r'\node at (7.1,12.45) {异支、同向：两点在焦点同侧，较近段的倒数更大};'+st,13.1)

st=''
for y,title,blue,orange,caption in [(9.6,'例1：同支 $AF=3$，另一段 $BF=24$',16/3,2/3,'正的余量'),(6.05,'边界：$AF=8/3$，已占满总量',6,0,'余量为零'),(2.5,'例4：假设同支 $AF=2$，已超过总量',8,0,'不可能有正余量')]:
 st+=rf'\node at (7.1,{y+1.15}) {{{title}}};'+'\n'
 st+=rf'\draw[gray,dashed] (2.2,{y-.2}) rectangle (8.2,{y+.7});\fill[blue!30] (2.2,{y}) rectangle ({2.2+blue},{y+.5});'+'\n'
 if orange:st+=rf'\fill[orange!45] ({2.2+blue},{y}) rectangle (8.2,{y+.5});'+'\n'
 st+=rf'\draw[violet,dashed] (8.2,{y-.25})--(8.2,{y+.85});\node[anchor=west] at (10.7,{y+.25}) {{{caption}}};'+'\n'
 st+=rf'\node at (5.2,{y-.55}) {{'+({9.6:r'$1/3+1/24=3/8$',6.05:r'$1/BF=0$：没有有限另一段',2.5:r'$1/2>3/8$：所设同支情形无解'}[y])+r'};'+'\n'
figfile('reciprocal_feasibility',r'\node at (7.1,12.2) {同支时：两块倒数都为正，才能拼成固定总量 $3/8$};'+st+r'\node at (7.1,.55) {虚框宽度表示 $K=3/8$；色条画的是倒数，不是原线段长度。};',12.8)

st=''
for cx,kind,title in [(2.35,'axis','水平：异支两点'),(7.1,'parallel','平行渐近线：仅一点'),(11.85,'vertical','竖直：同支两点')]:
 st+=rf'\node at ({cx},10.2) {{{title}}};\begin{{scope}}[shift={{({cx},6)}},scale=.18]'+'\n'
 st+=r'\begin{scope}\clip (-10,-9) rectangle (10,9);'+'\n'+curve()
 if kind=='parallel':st+=r'\draw[gray,dashed] (-8,-10.6667)--(8,10.6667);\draw[blue!75!black,very thick] (-2,-9.3333333)--(12,9.3333333);'
 if kind=='axis':st+=r'\draw[blue!75!black,very thick] (-10,0)--(10,0);'
 if kind=='vertical':st+=r'\draw[blue!75!black,very thick] (5,-9)--(5,9);'
 st+=r'\end{scope}\draw[->,gray] (-10.5,0)--(10.5,0);\fill (5,0) circle(2pt);\node at (1,-1.5) {$F$};\draw[gray] (2.5,-1.0)--(4.8,-.05);'
 pts={'axis':[(-3,0),(3,0)],'parallel':[(17/5,-32/15)],'vertical':[(5,16/3),(5,-16/3)]}[kind]
 for pt in pts:st+=rf'\fill[red!75!black] {xy(pt)} circle(2.5pt);'
 st+='\n'+r'\end{scope}'+'\n'
 caption={'axis':r'$k=0$\\[13pt]可以用倒数差','parallel':r'$k=b/a=4/3$\\[13pt]不能虚设第二点','vertical':r'$x=c=5$\\[13pt]可以用倒数和'}[kind]
 st+=rf'\node[align=center] at ({cx},2.7) {{{caption}}};'+'\n'
figfile('intersection_boundary',r'\node at (7.1,11.45) {先数有限交点：斜率不存在，与仅有一个交点是两回事};'+st+r'\node at (7.1,1.1) {三图同一双曲线、同尺度；红点为有限交点，灰虚线为渐近线。};\node at (7.1,.45) {$k=-b/a$ 与中图上下对称，也只有一个有限交点。};')

# Diagrams precede prose edits. Preserve all mathematics and examples.
def fig(stem):return '\\begin{center}\\input{assets/tikz/C057_'+stem+'.tex}\\end{center}\n'
def box(kind,body):return '\\clearpage\n\\begin{'+kind+'box}\n'+body+'\n\\end{'+kind+'box}\n'
old=(base/'01_statement.tex').read_text(encoding='utf8')
tail=old[old.index(r'  \textbf{\textcolor{CStatement}{核心结论}}'):]
first=r'''设双曲线 $x^2/a^2-y^2/b^2=1$，$a,b>0$，$c^2=a^2+b^2$。直线过所选焦点 $F(\pm c,0)$，并有两个不同的有限交点 $A,B$。这里不要求焦点在线段 $AB$ 内。
'''+fig('statement_comparison')+r'''\[
 \boxed{\text{同支：}\ \frac1{|AF|}+\frac1{|BF|}=\frac{2a}{b^2}},\qquad
 \boxed{\text{异支：}\ \left|\frac1{|AF|}-\frac1{|BF|}\right|=\frac{2a}{b^2}}.
\]
同支看两点所在的分支，异支看焦点位于延长线上；所有距离均为正。
'''
(base/'01_statement.tex').write_text(r'\begin{statementbox}'+'\n'+first+'\n'+r'\end{statementbox}\clearpage\begin{statementbox}'+'\n'+tail,encoding='utf8')
ex=box('explanation',r'\textbf{第一步，只看熟悉的线段位置。}用普通点 $P$ 暂代焦点，先分清两端在它的两侧还是同侧。'+fig('pure_positions')+r'不要把“直线经过一个点”理解成“线段一定包含这个点”。上图是两条反向射线，下图是同一条射线。')
ex+=box('explanation',r'\textbf{第二步，看相似三角形的投影比。}仍然没有双曲线、焦点和新公式；横向位移可以为负，点到点的长度始终为正。'+fig('pure_projection')+r'竖直线的水平位移都是零，比值关系仍成立；水平线虽没有非退化直角三角形，也可直接核对位移与长度的比例。')
ex+=box('explanation',r'\textbf{第三步，普通点 $P$ 对应右焦点 $F$。先看同支。}两点都在右支，焦点在中间；蓝段与橙段方向相反。'+fig('same_branch_sum')+r'''令 $r_A=|AF|$、$r_B=|BF|$，$e=c/a$、$p=b^2/a$。右支焦半径关系 $r=ex-a$ 给出 $x-c=(r-p)/e$。
把它代入上一页的反向比例，便得到
\[
 \frac{r_A-p}{er_A}=-\frac{r_B-p}{er_B}
 \quad\Longrightarrow\quad \frac1{r_A}+\frac1{r_B}=\frac2p.
\]
倒数来自“水平位移除以线段长”；不是额外猜出来的形式。''')
ex+=box('explanation',r'\textbf{第四步，再看异支。}从右焦点向同一方向走，先到右支 $A$，再到左支 $B$。焦点在弦外，不能画成两点夹住焦点。'+fig('cross_branch_difference')+r'''两支的焦半径关系不同：右支 $x_A-c=(r_A-p)/e$，左支 $x_B-c=(-r_B-p)/e$。代入同向比例，得到
\[
 \frac{r_A-p}{er_A}=\frac{-r_B-p}{er_B}
 \quad\Longrightarrow\quad \frac1{r_A}-\frac1{r_B}=\frac2p>0.
\]
因此右支点 $A$ 更近。若没有规定哪点叫 $A$，倒数差外面保留绝对值。''')
(base/'02_explanation.tex').write_text(ex,encoding='utf8')

proof=(base/'03_proof.tex').read_text(encoding='utf8')
# Split only at existing method headings, retaining full original derivations.
for marker in [r'  \textbf{\textcolor{CProof}{证明一',r'  \textbf{\textcolor{CProof}{证明二',r'  \textbf{\textcolor{CProof}{证明三']:
 pos=proof.index(marker);proof=proof[:pos]+r'\end{proofbox}\clearpage\begin{proofbox}'+'\n'+proof[pos:]
proof='\\clearpage\n'+proof
(base/'03_proof.tex').write_text(proof,encoding='utf8')
examples=(base/'04_examples.tex').read_text(encoding='utf8')
for marker in [r'  \textbf{\textcolor{CExample}{例2',r'  \textbf{\textcolor{CExample}{例3',r'  \textbf{\textcolor{CExample}{例4',r'  \textbf{\textcolor{CExample}{例5']:
 pos=examples.index(marker);examples=examples[:pos]+r'\end{examplebox}\clearpage\begin{examplebox}'+'\n'+examples[pos:]
examples=examples.replace(r'  \textbf{\textcolor{CExample}{例4',fig('reciprocal_feasibility')+r'  \textbf{\textcolor{CExample}{例4')
examples=examples.replace(r'  \textbf{\textcolor{CExample}{例5',fig('intersection_boundary')+r'  \textbf{\textcolor{CExample}{例5')
(base/'04_examples.tex').write_text('\\clearpage\n'+examples,encoding='utf8')
for name in ['05_traps.tex','06_summary.tex']:
 f=base/name;f.write_text('\\clearpage\n'+f.read_text(encoding='utf8'),encoding='utf8')
meta=json.loads((base/'meta.json').read_text(encoding='utf8'))
meta['remarks']+=' 新增七幅TikZ（assets/tikz/）：C057_statement_comparison.tex（第一页同支异支）、C057_pure_positions.tex（普通线段内外点）、C057_pure_projection.tex（纯几何投影相似）、C057_same_branch_sum.tex（同支倒数和）、C057_cross_branch_difference.tex（异支倒数差）、C057_reciprocal_feasibility.tex（倒数条形图解释可行性）、C057_intersection_boundary.tex（水平、渐近线方向、竖直线有限交点对比）。围绕图形压缩重复空间描述，保留三种证明、五道例题及易错清单；main/source及原正式PDF不覆盖。'
meta['interactive']['has_diagram']=True;meta['meta']['updated_at']='2026-10-26'
(base/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('C057: seven diagrams authored; proofs and five examples retained.')
