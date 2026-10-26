from pathlib import Path
import math,json
root=Path('03_conic/C052_ellipse_focal_chord_length'); assets=Path('assets/tikz')
def put(p,s): p.write_text(s.strip()+'\n',encoding='utf-8')
def frame(h,title): return [r'\begin{tikzpicture}[font=\small,>=stealth]',rf'\draw[rounded corners=3pt,gray!45] (0,0) rectangle (14.2,{h});',rf'\node at (7.1,{h-.55}) {{{title}}};']
def end(parts,name): put(assets/('C052_'+name+'.tex'),'\n'.join(parts+[r'\end{tikzpicture}']))
def xy(p): return f'({p[0]:.7f},{p[1]:.7f})'
def geometry(cx,cy,sc,theta=60,focus=1,angle=True):
    # x²/4+y²/3=1, right/left focus ±1. Unit line direction yields true distances.
    q=math.radians(theta); u,v=math.cos(q),math.sin(q)
    r=3/(2+focus*u);s=3/(2-focus*u)
    A=(focus+r*u,r*v);B=(focus-s*u,-s*v)
    parts=[rf'\begin{{scope}}[shift={{({cx},{cy})}},scale={sc}]',
           r'\draw[->,gray] (-2.4,0)--(2.55,0) node[above] {$x$};',
           r'\draw[teal!75!black,thick] (0,0) ellipse (2 and 1.7320508);',
           rf'\draw[blue!75!black,very thick] ({focus},0)--{xy(A)};',
           rf'\draw[orange!85!black,very thick] ({focus},0)--{xy(B)};',
           rf'\fill {xy(A)} circle(2pt) node[above right=4pt] {{$A$}};',
           rf'\fill {xy(B)} circle(2pt) node[below left=4pt] {{$B$}};',
           rf'\fill ({focus},0) circle(2pt) node[below {"left" if theta>90 else "right"}=4pt] {{$F$}};']
    if angle:
        parts += [rf'\draw[violet,->] ({focus+.47},0) arc[start angle=0,end angle={theta},radius=.47];',
                  rf'\node[violet] at ({focus+.82*math.cos(q/2):.7f},{.82*math.sin(q/2):.7f}) {{$\theta={theta}^\circ$}};']
    parts += [r'\end{scope}']
    return parts,A,B,r,s

p=frame(9.8,r'焦点把弦分成两段：整条弦长 $L=AF+FB=r+s$')
g,A,B,r,s=geometry(4.7,4.9,1.5)
p+=g
p += [r'\node[anchor=west,align=left] at (9.2,6.1) {$x^2/4+y^2/3=1$\\[8pt]$F=(1,0)$\\[10pt]$\textcolor{blue!75!black}{r=AF=6/5}$\\[8pt]$\textcolor{orange!85!black}{s=BF=2}$\\[10pt]$L=6/5+2=16/5$};',
      r'\node at (7.1,1.25) {$\displaystyle \textcolor{blue!75!black}{r=\frac{b^2}{a+c\cos\theta}},\qquad \textcolor{orange!85!black}{s=\frac{b^2}{a-c\cos\theta}}$};',
      r'\node at (7.1,.5) {焦点在弦内部；两段通常不等，必须相加才是整条弦。};']
end(p,'focal_chord_split')

p=frame(9.7,r'固定同一椭圆、同一焦点：弦从长轴转向通径，长度变短')
for cx,theta,title,L in [(2.25,0,'长轴弦（最长）','4'),(6.95,60,'一般焦点弦','16/5'),(11.65,90,'通径（最短）','3')]:
    p += [rf'\node at ({cx},8.35) {{{title}}};',rf'\node at ({cx},7.6) {{$\theta={theta}^\circ$}};']
    g,*_=geometry(cx,4.6,.81,theta,angle=False);p+=g
    p += [rf'\node at ({cx},1.85) {{$L={L}$}};']
p += [r'\node at (7.1,.65) {$a=2,\ b^2=3,\ c=1$；三图同尺度，$\displaystyle 3=\frac{2b^2}{a}\le L\le2a=4$。};']
end(p,'three_directions')

p=frame(10.5,r'证明二的构造：椭圆定义给斜边，勾股定理给平方')
p += [r'\begin{scope}[shift={(4.4,5.4)},scale=1.5]',
      r'\draw[->,gray] (-2.35,0)--(2.15,0) node[below] {$x$};',
      r'\draw[teal!75!black,thick] (0,0) ellipse (2 and 1.7320508);',
      r'\fill[violet!10] (-1,0)--(1.6,0)--(1.6,1.0392305)--cycle;',
      r'\draw[violet,thick] (-1,0)--(1.6,1.0392305);',
      r'\draw[blue!75!black,very thick] (1,0)--(1.6,1.0392305);',
      r'\draw[orange!85!black,thick,dashed] (-1,0)--(1.6,0)--(1.6,1.0392305);',
      r'\draw[orange!85!black] (1.4,0)--(1.4,.2)--(1.6,.2);',
      r'\fill (-1,0) circle(2pt) node[below=4pt] {$F_1$};',
      r'\fill (1,0) circle(2pt) node[below=4pt] {$F$};',
      r'\fill (1.6,0) circle(2pt) node[below right=4pt] {$H$};',
      r'\fill (1.6,1.0392305) circle(2pt) node[above right=4pt] {$A$};',
      r'\draw[gray,dotted] (-1,-.3)--(-1,-2.25);',
      r'\draw[gray,dotted] (1.6,-.3)--(1.6,-2.25);',
      r'\draw[<->,orange!85!black] (-1,-2.2)--(1.6,-2.2) node[midway,below] {$F_1H=2c+r\cos\theta$};',
      r'\end{scope}',
      r'\node[anchor=west,align=left] at (9.15,6.5) {$AF=r$\\[8pt]$AF_1=2a-r$\\[8pt]$AH=r\sin\theta$\\[10pt]$AF_1^2=F_1H^2+AH^2$};',
      r'\node at (7.1,.65) {$\displaystyle (2a-r)^2=(2c+r\cos\theta)^2+(r\sin\theta)^2$};']
end(p,'definition_pythagoras')

p=frame(9.4,r'左右焦点为何同式？关于 $y$ 轴镜像，弦长保持不变')
for cx,focus,theta,title in [(3.65,1,60,'过右焦点'),(10.55,-1,120,'过左焦点')]:
    p += [rf'\node at ({cx},8.1) {{{title}}};']
    g,*_=geometry(cx,4.7,1.08,theta,focus,angle=False);p+=g
    p += [rf'\node at ({cx},1.9) {{$\theta={theta}^\circ,\quad L=16/5$}};']
p += [r'\node at (7.1,.65) {$\cos^2(180^\circ-\theta)=\cos^2\theta$；同一倾斜角过另一焦点也得到相同总长。};']
end(p,'left_right_focus')

p=frame(9.4,r'反求倾斜角要有两个答案：同一右焦点，$60^\circ$ 与 $120^\circ$')
for cx,theta in [(3.65,60),(10.55,120)]:
    p += [rf'\node at ({cx},8.1) {{$\theta={theta}^\circ$}};']
    g,*_=geometry(cx,4.7,1.08,theta,angle=False);p+=g
    p += [rf'\node at ({cx},1.9) {{$L=16/5$}};']
p += [r'\node at (7.1,.65) {两条弦关于 $x$ 轴对称；$\cos\theta=\pm1/2$，但 $\cos^2\theta$ 都是 $1/4$。};']
end(p,'supplementary_angles')

p=frame(9.6,r'同样竖直：经过焦点的才是通径，经过中心的是短轴弦')
for cx,xval,title,length in [(3.65,0,'普通竖直弦：$x=0$',r'2\sqrt3'),(10.55,1,'竖直焦点弦：$x=1$','3')]:
    y=math.sqrt(3*(1-xval*xval/4))
    p += [rf'\node at ({cx},8.25) {{{title}}};',rf'\begin{{scope}}[shift={{({cx},4.8)}},scale=1.1]',
          r'\draw[->,gray] (-2.35,0)--(2.5,0) node[above] {$x$};',
          r'\draw[teal!75!black,thick] (0,0) ellipse (2 and 1.7320508);',
          rf'\draw[blue!75!black,very thick] ({xval},{-y:.7f})--({xval},{y:.7f});',
          rf'\fill ({xval},{y:.7f}) circle(2pt) node[above=4pt] {{$A$}};',
          rf'\fill ({xval},{-y:.7f}) circle(2pt) node[below=4pt] {{$B$}};',
          r'\fill (1,0) circle(2pt) node[below right=4pt] {$F(1,0)$};',
          r'\end{scope}',rf'\node at ({cx},1.75) {{$L={length}$}};']
p += [r'\node at (7.1,.6) {椭圆均为 $x^2/4+y^2/3=1$；焦点弦公式不能用于左图的普通弦。};']
end(p,'ordinary_chord_vs_latus')

# Rotated ellipse, a=5,b=3,c=4, line 30° from x-axis, 60° from the major y-axis.
p=frame(11.5,r'长轴在 $y$ 轴：用弦与长轴的角 $\varphi$，不是与 $x$ 轴的角 $\theta$')
q=math.radians(30);u,v=math.cos(q),math.sin(q)
r=9/(5+4*v);s=9/(5-4*v)
A=(r*u,4+r*v);B=(-s*u,4-s*v)
p += [r'\begin{scope}[shift={(4.5,5.6)},scale=.8]',
      r'\draw[->,gray] (-3.7,0)--(3.7,0) node[right] {$x$};',
      r'\draw[->,gray] (0,-5.3)--(0,5.7) node[above] {$y$};',
      r'\draw[teal!75!black,thick] (0,0) ellipse (3 and 5);',
      r'\draw[gray,dashed] (-.5,4)--(3.4,4);',
      rf'\draw[blue!75!black,very thick] {xy(B)}--{xy(A)};',
      rf'\fill {xy(A)} circle(2pt) node[right=4pt] {{$A$}};',
      rf'\fill {xy(B)} circle(2pt) node[below left=4pt] {{$B$}};',
      r'\fill (0,4) circle(2pt) node[below right=4pt] {$F$};',
      r'\node[below left=4pt] at (0,0) {$O$};',
      r'\draw[violet,->] (.8,4) arc[start angle=0,end angle=30,radius=.8];',
      r'\draw[orange!85!black,->] (.952628,4.55) arc[start angle=30,end angle=90,radius=1.1];',
      r'\end{scope}',
      r'\node[anchor=west,align=left] at (9.0,7.0) {$x^2/9+y^2/25=1$\\[8pt]$F=(0,4)$\\[10pt]$\textcolor{violet}{\theta=30^\circ}$（相对横轴）\\[8pt]$\textcolor{orange!85!black}{\varphi=60^\circ}$（相对长轴）\\[10pt]$\cos^2\varphi=\sin^2\theta=1/4$\\[10pt]$L=30/7$};',
      r'\node at (7.1,.55) {先找长轴，再量夹角；虚线与 $x$ 轴平行，橙色弧才对应公式中的角。};']
end(p,'vertical_major_axis_angle')

# Figure-led explanation replaces repeated verbal descriptions.
put(root/'02_explanation.tex',r'''
\clearpage
\begin{explanationbox}
\textbf{先把“弦长”和“焦半径”分清：}在 $x^2/4+y^2/3=1$ 中，取右焦点 $F(1,0)$，让直线以 $60^\circ$ 穿过它。
\begin{center}\input{assets/tikz/C052_focal_chord_split.tex}\end{center}
蓝段是 $AF=r$，橙段是 $BF=s$；由于焦点在椭圆内部，\textbf{整条弦是两段相加}。
一般地，两段分别为 $b^2/(a+c\cos\theta)$ 与 $b^2/(a-c\cos\theta)$。
通分时分母相乘，出现平方差 $(a+cu)(a-cu)=a^2-c^2u^2$（$u=\cos\theta$），因此
\[
 \boxed{L=r+s=\frac{2ab^2}{a^2-c^2\cos^2\theta}}.
\]
\end{explanationbox}
\clearpage
\begin{explanationbox}
\textbf{转动弦，长度怎样变？}只改变方向，保持椭圆、焦点和绘图尺度相同。
\begin{center}\input{assets/tikz/C052_three_directions.tex}\end{center}
沿长轴得到 $2a$；垂直长轴得到通径 $2b^2/a$；其他方向介于两者之间。
因为 $b^2\le a^2-c^2\cos^2\theta\le a^2$，所以
\[
 \boxed{\frac{2b^2}{a}\le L\le2a}.
\]
\textbf{图后的检查：}这里最短的是“过焦点的通径”，不是“所有椭圆弦中最短”。
\end{explanationbox}
\clearpage
\begin{explanationbox}
\textbf{选左焦点还是右焦点？}镜像使焦点换边，椭圆和弦长不变。
\begin{center}\input{assets/tikz/C052_left_right_focus.tex}\end{center}
图中镜像将方向角从 $\theta$ 换为 $\pi-\theta$，余弦变号而平方不变。
因此总弦长与焦点选哪一个无关；两侧焦半径的次序可能互换，\textbf{总长始终是两段之和}。
\end{explanationbox}
''')

p=root/'03_proof.tex';s=p.read_text(encoding='utf-8')
s=s.replace('% 不依赖额外 tikz 源文件；不改写原有图形资源。','% 图形构造见 C052_definition_pythagoras.tex。')
s='\\clearpage\n'+s
for marker in ['证明二：','证明三：','证明四：']:
    token='\\textbf{\\textcolor{CProof}{'+marker
    pos=s.index(token)
    s=s[:pos]+'\\end{proofbox}\n\\clearpage\n\\begin{proofbox}\n'+s[pos:]
pos=s.index('\\textbf{做法：}'); stop=s.index('\\textbf{第1步',pos)
s=s[:pos]+r'''
\begin{center}\input{assets/tikz/C052_definition_pythagoras.tex}\end{center}
图取 $a=2,b^2=3,c=1,\theta=60^\circ$。一般推导只用图中的水平、竖直分量；即使投影方向改变，平方后的距离表达式仍成立。

'''+s[stop:]
# Shorten method2 algebra while retaining cancellation and the opposite-ray proof.
a=s.index('\\textbf{第1步 从椭圆定义');b=s.index('\\textbf{第3步',a)
s=s[:a]+r'''
\textbf{第1步 定义与勾股给出同一个平方：}
$AF_1=2a-r$，故
\[
 (2a-r)^2=(2c+ru)^2+r^2\sin^2\theta=4c^2+4cru+r^2.
\]
\textbf{第2步 两边消去 $r^2$：}
\[
 4a^2-4ar=4c^2+4cru
 \ \Longrightarrow\ \boxed{r(a+cu)=b^2}.
\]
'''+s[b:]
put(p,s)

p=root/'04_examples.tex';s=p.read_text(encoding='utf-8');s='\\clearpage\n'+s
# Preserve all eight examples, dedicate pages to inverse angle and rotated-axis geometry.
for num,figure in [(2,'supplementary_angles'),(8,'vertical_major_axis_angle')]:
    marker='\\textbf{\\textcolor{CExample}{例'+str(num)
    pos=s.index(marker);s=s[:pos]+'\\end{examplebox}\n\\clearpage\n\\begin{examplebox}\n'+s[pos:]
    insert=s.index('\\textbf{解：}',s.index(marker))
    s=s[:insert]+'\\begin{center}\\input{assets/tikz/C052_'+figure+'.tex}\\end{center}\n'+s[insert:]
# Keep later examples together and avoid splitting figure-led page after example2.
pos=s.index('\\textbf{\\textcolor{CExample}{例3')
s=s[:pos]+'\\end{examplebox}\n\\clearpage\n\\begin{examplebox}\n'+s[pos:]
pos=s.index('\\textbf{\\textcolor{CExample}{例6')
s=s[:pos]+'\\end{examplebox}\n\\clearpage\n\\begin{examplebox}\n'+s[pos:]
put(p,s)

p=root/'05_traps.tex';s=p.read_text(encoding='utf-8')
# A compact visual trap page, retaining all original traps on following pages.
intro=r'''
\clearpage
\begin{trapbox}
\textbf{先辨弦：}“垂直长轴”还不够，通径必须经过焦点。
\begin{center}\input{assets/tikz/C052_ordinary_chord_vs_latus.tex}\end{center}
左图给 $2\sqrt3$，右图才是通径 $2b^2/a=3$。\textbf{错误做法：}把任意竖直弦代入通径公式。
\textbf{正确替代：}先检查是否过焦点；普通弦应将直线与椭圆联立。
\end{trapbox}
\clearpage
'''
put(p,intro+s)
p=root/'06_summary.tex';put(p,'\\clearpage\n'+p.read_text(encoding='utf-8'))
p=root/'01_statement.tex';s=p.read_text(encoding='utf-8').replace('若沿 $FA$ 的方向角','若沿 $F_2A$ 的方向角');put(p,s)
p=root/'meta.json';m=json.loads(p.read_text(encoding='utf-8'))
m['remarks']+=' 2026-10-25补充七幅精确TikZ：assets/tikz/C052_focal_chord_split.tex（两段相加）、C052_three_directions.tex（转动与最值）、C052_definition_pythagoras.tex（定义勾股构造）、C052_left_right_focus.tex（焦点镜像）、C052_supplementary_angles.tex（反求双角）、C052_ordinary_chord_vs_latus.tex（普通竖弦与通径）、C052_vertical_major_axis_angle.tex（长轴转向后的角度）；以图缩短重复空间描述，四种证明与八例保留。'
m['interactive']['has_diagram']=True;m['meta']['updated_at']='2026-10-25';put(p,json.dumps(m,ensure_ascii=False,indent=2))
print('C052: 7 precise TikZ diagrams added; four methods and eight examples preserved.')
