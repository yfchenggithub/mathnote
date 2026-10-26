from pathlib import Path
import json,re,shutil
base=Path('03_conic/C055_parabola_focal_chord_product')
work=Path('.tmp/C055_tikz_review');(work/'before').mkdir(parents=True,exist_ok=True)
for f in base.glob('*.tex'):shutil.copy2(f,work/'before'/f.name)
shutil.copy2(base/'meta.json',work/'before/meta.json')

def write(stem,body,height=12):
    Path(f'assets/tikz/C055_{stem}.tex').write_text(r'\begin{tikzpicture}[font=\small,>=stealth]'+'\n'+rf'\draw[rounded corners=3pt,gray!45] (0,0) rectangle (14.2,{height});'+'\n'+body+'\n'+r'\end{tikzpicture}'+'\n',encoding='utf8')

geometry=r'''
\fill[blue!7] (1,0)--(4,0)--(4,4)--cycle;
\fill[orange!10] (1,0)--(.25,0)--(.25,-1)--cycle;
\draw[blue!75!black,very thick] (1,0)--(4,4);
\draw[orange!85!black,very thick] (1,0)--(.25,-1);
\draw[gray,dashed] (4,0)--(4,4) node[midway,right=7pt] {$u$};
\draw[gray,dashed] (.25,0)--(.25,-1) node[midway,left=7pt] {$v$};
\draw[blue!60!black,thick] (1,0)--(4,0) node[midway,below=7pt] {$h$};
\draw[orange!85!black,thick] (.25,0)--(1,0) node[midway,above=6pt] {$k$};
\draw[gray] (3.8,0)--(3.8,.2)--(4,.2);
\draw[gray] (.43,0)--(.43,-.18)--(.25,-.18);
\draw[violet] (1.36,0) arc[start angle=0,end angle=53.13010235,radius=.36];
\draw[violet] (.64,0) arc[start angle=180,end angle=233.13010235,radius=.36];
\fill (4,4) circle(2pt) node[above=8pt] {$A$};
\fill (.25,-1) circle(2pt) node[below=8pt] {$B$};
\fill (4,0) circle(1.5pt) node[below right=6pt] {$H$};
\fill (.25,0) circle(1.5pt) node[above=16pt] {$K$};
'''
write('pure_similarity',r'\node at (7.1,11.45) {先认熟悉的结构：两个直角三角形，相同的倾斜程度};'+
 r'\begin{scope}[shift={(1.7,4.2)},scale=1.25]'+geometry+r'''
\fill (1,0) circle(2pt) node[below right=6pt] {$P$};
\end{scope}
\node[anchor=west,align=left] at (8.6,7.1)
 {$A,P,B$ 共线\\[12pt]$H,P,K$ 共线\\[12pt]
 $AH\parallel BK$\\[16pt]两处直角相等\\[12pt]$P$ 处两角是对顶角\\[12pt]所以两个三角形相似};
\node at (7.1,1.7) {四条标出的边长 $h,k,u,v$ 都是正数。};
\node at (7.1,.65) {$\displaystyle \triangle PHA\sim\triangle PKB\qquad\Longrightarrow\qquad\frac hu=\frac kv$};''')

write('coordinate_mapping',r'\node at (7.1,11.45) {再加抛物线：普通点对应焦点，边长对应坐标差};'+
 r'\begin{scope}[shift={(1.7,4.2)},scale=1.25]'+r'''
\draw[->,gray] (-.45,0)--(4.75,0) node[above] {$x$};
\draw[->,gray] (0,-1.8)--(0,4.75) node[left] {$y$};
\draw[teal!75!black,thick,samples=120,domain=-1.7:4.5,variable=\t] plot ({\t*\t/4},{\t});
'''+geometry+r'''
\fill (1,0) circle(2pt) node[below right=6pt] {$F$};
\node[below left=7pt] at (0,0) {$O$};
\end{scope}
\node[anchor=west,align=left] at (8.5,7.2)
 {此图取 $p=2$\\[12pt]$P\ \longrightarrow\ F(1,0)$\\[14pt]
 $A(4,4),\quad B(1/4,-1)$\\[14pt]
 $u=y_A=4$\\[10pt]$v=-y_B=1$\\[10pt]
 $h=x_A-1=3$\\[10pt]$k=1-x_B=3/4$};
\node at (7.1,1.55) {注意：$v$ 是正的边长，下端点的纵坐标却是 $-v$。};
\node at (7.1,.6) {$\displaystyle \frac hu=\frac kv\quad\text{保留；再用}\quad x=\frac{y^2}{2p}\quad\text{替换横坐标。}$};''')

def curve():return r'\draw[teal!75!black,thick,samples=120,domain=-4.5:4.5,variable=\t] plot ({\t*\t/4},{\t});'
panels=''
for cx,a,b,label in [(1.6,2,-2,'通径：上下对称'),(6.0,4,-1,'斜弦：上长下短'),(10.4,1,-4,'斜弦：上短下长')]:
    x1,x2=a*a/4,b*b/4
    panels+=rf'\node at ({cx+.65},11.0) {{{label}}};'+'\n'
    panels+=rf'\begin{{scope}}[shift={{({cx},6.7)}},scale=.65]'+'\n'+curve()+r'''
\draw[->,gray] (-.7,0)--(5.25,0) node[above] {$x$};
\draw[->,gray] (0,-4.8)--(0,4.9);
\fill (1,0) circle(1.7pt) node[below right=5pt] {$F$};
'''+rf'\draw[blue!75!black,very thick] ({x1},{a})--(1,0);\draw[orange!85!black,very thick] (1,0)--({x2},{b});'+'\n'
    panels+=rf'\fill ({x1},{a}) circle(1.7pt) node[above=7pt] {{$A$}};\fill ({x2},{b}) circle(1.7pt) node[below=7pt] {{$B$}};'+'\n'+r'\end{scope}'+'\n'
    fx=lambda n:str(int(n)) if n==int(n) else r'\frac14'
    panels+=rf'\node at ({cx+.65},2.6) {{$y_Ay_B={a}\times({b})=-4$}};'+'\n'
    panels+=rf'\node at ({cx+.65},1.65) {{$x_Ax_B={fx(x1)}\times {fx(x2)}=1$}};'+'\n'
write('product_comparison',r'\node at (7.1,12.15) {同一抛物线、同一尺度：端点在变，两个坐标积不变};'+panels+
 r'\node at (7.1,.65) {$y^2=4x,\ p=2$：负积说明纵坐标异号，不要求绝对值相等。};',12.7)

write('tangent_right_angle',r'''
\node at (7.1,11.95) {切线推广：两切线成直角，交点恰好落在准线上};
\begin{scope}[shift={(3.1,4.2)},scale=1.05]
\draw[->,gray] (-1.65,0)--(4.9,0) node[above] {$x$};
\draw[->,gray] (0,-2.2)--(0,5.15) node[left] {$y$};
\draw[violet,dashed] (-1,-2.2)--(-1,5.05);
\node[violet,rotate=90] at (-1.5,3.8) {准线 $x=-1$};
\draw[teal!75!black,thick,samples=120,domain=-2.2:4.5,variable=\t] plot ({\t*\t/4},{\t});
\draw[gray!75,thick] (4,4)--(.25,-1);
\draw[blue!75!black,very thick] (-1,1.5)--(4,4);
\draw[orange!85!black,very thick] (-1,1.5)--(.25,-1);
\draw[black] (-.68695,1.65652)--(-.53043,1.34348)--(-.84348,1.18695);
\fill (-1,1.5) circle(2pt) node[left=8pt] {$T$};
\fill (4,4) circle(2pt) node[above left=7pt] {$A$};
\fill (.25,-1) circle(2pt) node[below left=7pt] {$B$};
\fill (1,0) circle(2pt) node[below right=6pt] {$F$};
\end{scope}
\node[anchor=west,align=left] at (9.1,7.15)
 {$A(4,4)$\\[12pt]$B(1/4,-1)$\\[12pt]$T(-1,3/2)$\\[16pt]
 蓝色切线：$k_A=1/2$\\[12pt]橙色切线：$k_B=-2$\\[14pt]$k_Ak_B=-1$};
\node at (7.1,1.4) {灰线是焦点弦 $AB$；蓝、橙两线是端点处的切线。};
\node at (7.1,.55) {$y^2=4x,\quad p=2,\quad y_Ay_B=-4\quad\Longrightarrow\quad k_Ak_B=-1$};''',12.5)

panels=''
for cx,typ,title in [(1.6,0,'焦点弦：可用定值'),(6,1,'普通弦：不满足定值'),(10.4,2,'轴线：仅一个交点')]:
    panels+=rf'\node at ({cx+.65},10.8) {{{title}}};\begin{{scope}}[shift={{({cx},6)}},scale=.65]'+'\n'+curve()+r'''
\draw[->,gray] (-.7,0)--(5.25,0) node[above] {$x$};
\fill (1,0) circle(2pt) node[below right=5pt] {$F$};
'''
    if typ<2:
        x=1 if typ==0 else 2;y=2 if typ==0 else 2*2**.5
        panels+=rf'\draw[blue!75!black,very thick] ({x},{-y})--({x},{y});\fill ({x},{y}) circle(2pt);\fill ({x},{-y}) circle(2pt);'
    else:panels+=r'\draw[red!80!black,very thick] (-.5,0)--(5,0);\fill (0,0) circle(2pt) node[below left=5pt] {$O$};'
    panels+='\n'+r'\end{scope}'+'\n'
    lines=[r'$x_Ax_B=1$\\[10pt]$y_Ay_B=-4$',r'$x_Ax_B=4$\\[10pt]$y_Ay_B=-8$',r'只有顶点 $O$\\[10pt]没有两个端点'][typ]
    panels+=rf'\node[align=center] at ({cx+.65},2.1) {{{lines}}};'+'\n'
write('validity_comparison',r'\node at (7.1,11.95) {先检查结构：经过焦点，并且有两个不同的有限交点};'+panels+
 r'\node at (7.1,.65) {三图均为 $y^2=4x,\ p=2$，坐标尺度相同。};',12.5)

panels=''
for cx,cy,typ,title in [(3.2,10.8,0,r'$y^2=4x$'),(10.7,10.8,1,r'$y^2=-4x$'),(3.2,4.5,2,r'$x^2=4y$'),(10.7,4.5,3,r'$x^2=-4y$')]:
    transform=[lambda x,y:(x,y),lambda x,y:(-x,y),lambda x,y:(y,x),lambda x,y:(y,-x)][typ]
    panels+=rf'\node at ({cx},{cy+2.3}) {{{title}}};\begin{{scope}}[shift={{({cx},{cy})}},scale=.53]'+'\n'
    # Curves centred on the displayed focus; exact isometry preserves scale.
    pts=[transform(((-4.4+i*8.8/120)**2)/4-1,-4.4+i*8.8/120) for i in range(121)]
    panels+=r'\draw[teal!75!black,thick] '+'--'.join(f'({x:.8f},{y:.8f})' for x,y in pts)+';\n'
    a=transform(3,4);b=transform(-.75,-1)
    panels+=rf'\draw[blue!75!black,very thick] ({a[0]},{a[1]})--(0,0);\draw[orange!85!black,very thick] (0,0)--({b[0]},{b[1]});'
    anchors=[('above left=7pt','below left=7pt','below right=7pt'),('above right=7pt','below right=7pt','below left=7pt'),('above left=7pt','above left=7pt','above=12pt'),('below right=7pt','above left=7pt','below=12pt')][typ]
    for (x,y),n,anc in [(a,'A',anchors[0]),(b,'B',anchors[1]),((0,0),'F',anchors[2])]:panels+=rf'\fill ({x},{y}) circle(2pt) node[{anc}] {{${n}$}};'
    panels+='\n'+r'\end{scope}'+'\n'
    product=r'$x_Ax_B=1,\quad y_Ay_B=-4$' if typ<2 else r'$x_Ax_B=-4,\quad y_Ay_B=1$'
    panels+=rf'\node at ({cx},{cy-2.85}) {{{product}}};'+'\n'
write('four_openings',r'\node at (7.1,14.45) {左右翻折：积不变；改成上下开口：交换横纵角色};'+panels+
 r'\node at (7.1,.65) {四图均取 $p=2$、同一尺度，图形按标准坐标方向放置。};',15)

# Only after producing diagrams, edit their surrounding teaching text.
def box(kind,content):return '\\clearpage\n\\begin{'+kind+'box}\n'+content+'\n\\end{'+kind+'box}\n'
def fig(stem):return '\\begin{center}\\input{assets/tikz/C055_'+stem+'.tex}\\end{center}\n'
ex=box('explanation',r'''\textbf{第一步，先认初中几何。}暂时没有抛物线、焦点和坐标；只看普通斜线上的两个直角三角形。
'''+fig('pure_similarity')+r'''对应的水平边与竖直边之比相等：$h/u=k/v$。先记住这一个熟悉的相似关系，四个字母都表示正的边长。''')
ex+=box('explanation',r'''\textbf{第二步，把同一结构放回抛物线。}图形、尺度和颜色保持不变；普通点 $P$ 对应焦点 $F$，两端点落在曲线上。
'''+fig('coordinate_mapping')+r'''对一般非竖直焦点弦，先按左右端点标号：$u=y_A>0$、$v=-y_B>0$（负斜率时将图上下翻折）。横向边长为
\[
 h=\frac{u^2-p^2}{2p},\qquad k=\frac{p^2-v^2}{2p}.
\]
相似给 $h/u=k/v$，整理成 $(u+v)(uv-p^2)=0$。因 $u+v>0$，得到 $uv=p^2$，所以\textbf{带符号的纵坐标积为 $y_Ay_B=-uv=-p^2$}。完整推导见方法二。''')
ex+=box('explanation',r'''\textbf{第三步，观察变化，再抽象成定值。}三图只改变过焦点直线的方向。端点可以不对称；不要把“乘积固定”误读成“两数互为相反数”。
'''+fig('product_comparison')+r'''读图时，上方纵坐标为正，下方为负；绝对值相乘均为 $4$，所以纵积均为 $-4$。横积则均为 $1$。
一般情形中，只需证明纵积，横积就随之得到：
\[
 x_1x_2=\frac{y_1^2y_2^2}{4p^2}=\frac{(y_1y_2)^2}{4p^2}=\frac{p^2}{4}.
\]
已知一端纵坐标 $y_A=t\ne0$，另一端由乘积配对确定：$y_B=-p^2/t$，$x_B=p^3/(2t^2)$。上面的三图用于观察，下面的证明覆盖任意有限焦点弦。''')
(base/'02_explanation.tex').write_text(ex,encoding='utf8')

proof=(base/'03_proof.tex').read_text(encoding='utf8')
chunks=proof.split(r'\medskip\hrule\medskip')
chunks[0]=chunks[0].replace(r'\begin{proofbox}','').strip()
chunks[-1]=chunks[-1].replace(r'\end{proofbox}','').strip()
chunks[1]=r'''\textbf{\textcolor{CProof}{方法二：最低门槛，相似三角形加因式分解}}

\textbf{先沿用前两幅图。}非竖直且正斜率时，把右上端记为 $A$、左下端记为 $B$。令 $u=y_A>0$、$v=-y_B>0$，焦点横坐标为 $p/2$。
\[
 x_A=\frac{u^2}{2p},\qquad x_B=\frac{v^2}{2p},\qquad
 h=x_A-\frac p2,\qquad k=\frac p2-x_B.
\]
由于焦点在两端点之间，$h,k>0$。\textbf{第1步，只用相似：}
\[
 \frac hu=\frac kv.
\]
\textbf{第2步，用抛物线方程替换水平边：}
\[
 \frac{u^2-p^2}{2pu}=\frac{p^2-v^2}{2pv}
 \quad\Longrightarrow\quad v(u^2-p^2)=u(p^2-v^2).
\]
\textbf{第3步，移项并提取共同因子：}
\[
 u^2v+uv^2=p^2(u+v)
 \quad\Longrightarrow\quad (u+v)(uv-p^2)=0.
\]
$u+v>0$，故 $uv=p^2$。注意 $B$ 的纵坐标是 $-v$，所以
\[
 \boxed{y_Ay_B=-uv=-p^2},\qquad
 \boxed{x_Ax_B=\frac{u^2v^2}{4p^2}=\frac{p^2}{4}}.
\]
\textbf{补齐情况。}负斜率时先上下翻折，边长与横积不变；两个纵坐标同时变号，纵积也不变。竖直通径单独代入 $x=p/2$，得 $y=\pm p$，两个积同样成立。

\medskip
\textbf{也可直接用带符号的坐标，不作图形分类。}设 $A(a^2/(2p),a)$、$B(b^2/(2p),b)$，其中 $a,b\ne0$ 且 $a\ne b$。三点共线给
\[
 \frac{a^2-p^2}{2pa}=\frac{b^2-p^2}{2pb}
 \quad\Longrightarrow\quad (a-b)(ab+p^2)=0.
\]
约去 $a-b\ne0$，仍得 $ab=-p^2$。这就是前面相似比的带符号写法；不需要韦达定理。
'''
(base/'03_proof.tex').write_text(''.join(box('proof',s.strip()) for s in chunks),encoding='utf8')

examples=(base/'04_examples.tex').read_text(encoding='utf8').replace(r'\begin{examplebox}','').replace(r'\end{examplebox}','').split(r'\medskip\hrule\medskip')
examples[0]+=r'\par\smallskip\textbf{回验：}$A(1,-2)$、$B(1,2)$ 的连线 $x=1$ 正是通径，横积 $1$、纵积 $-4$。'
examples[3]=fig('tangent_right_angle')+examples[3]+r'\par\smallskip\textbf{回验切线：}$4y=2(x+4)$ 与 $-y=2(x+1/4)$ 都通过 $T(-1,3/2)$，斜率分别为 $1/2,-2$。'
(base/'04_examples.tex').write_text(box('example',examples[0]+r'\medskip\hrule\medskip'+examples[1])+box('example',examples[2])+box('example',examples[3])+box('example',examples[4]),encoding='utf8')

traps=(base/'05_traps.tex').read_text(encoding='utf8')
new=box('trap',r'\textbf{先看结构差异，再判断能否使用定值。}'+fig('validity_comparison')+r'中图虽有两个交点，却没有经过焦点；右图虽过焦点，却没有两个交点。这两个条件缺一不可。')
new+=box('trap',r'\textbf{再看开口方向：哪个变量被平方，哪个坐标积就是负的。}'+fig('four_openings')+r'左右开口的两个横坐标同时变号，乘积仍为正；上下开口则交换横纵角色。这里使用以顶点为原点的标准坐标。')
(base/'05_traps.tex').write_text(new+'\n\\clearpage\n'+traps,encoding='utf8')
summary=(base/'06_summary.tex').read_text(encoding='utf8');(base/'06_summary.tex').write_text('\\clearpage\n'+summary,encoding='utf8')
meta=json.loads((base/'meta.json').read_text(encoding='utf8'))
meta['content']['intuition']='先抽出初中相似三角形h/u=k/v，再映射到抛物线，用x=y²/(2p)替换水平边，因式分解得uv=p²。注意两端纵坐标为u与-v，所以纵积为-p²；横积由平方关系得到。比较一般斜弦与通径，不能把乘积固定误认为对称。'
meta['content']['derivation'][1]='最低门槛：纯几何相似h/u=k/v，替换水平边后得(u+v)(uv-p²)=0，从而uv=p²、y_Ay_B=-p²；竖直弦另验。保留带符号设点共线推导(a-b)(ab+p²)=0。'
meta['remarks']+=' 新增六幅TikZ：assets/tikz/C055_pure_similarity.tex（纯初中相似）、C055_coordinate_mapping.tex（同形同尺度逐步加入坐标）、C055_product_comparison.tex（三条弦坐标积比较）、C055_tangent_right_angle.tex（切线直角与准线交点）、C055_validity_comparison.tex（适用条件反例）、C055_four_openings.tex（开口与坐标互换）。替换图文不对应的小通径图输入，原图源保留；压缩重复空间描述，保留三种证明及切线推广、四道例题和上开口变式。'
meta['meta']['updated_at']='2026-10-26'
(base/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('C055: six diagrams authored; existing proofs and examples retained.')
