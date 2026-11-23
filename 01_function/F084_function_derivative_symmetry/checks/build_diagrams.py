"""Exact PDF-only TikZ models for F084; no animation or published assets."""
from pathlib import Path
import math,json
ROOT=Path(__file__).resolve().parents[3]
UID='F084_function_derivative_symmetry'
OUT=ROOT/'assets/tikz'
G='teal!75!black';B='blue!70!black';O='orange!85!black';R='red!70!black'
def frame(h,title):
 return [r'\begin{tikzpicture}[font=\small,>=stealth,line join=round]',rf'\draw[draw=teal!45!black,fill=green!3,rounded corners=3pt] (0,0) rectangle (13.6,{h});',rf'\node at (6.8,{h-.55}) {{{title}}};']
def save(suffix,lines):
 assert not any(r'\x^' in line for line in lines), 'Parenthesize powers of negative plot coordinates'
 (OUT/(UID+'_'+suffix+'.tex')).write_text('\n'.join(lines+[r'\end{tikzpicture}'])+'\n',encoding='utf-8')
def scope(x,y,xs=1,ys=1):return rf'\begin{{scope}}[shift={{({x},{y})}},x={xs}cm,y={ys}cm]'
def dot(x,y,c=G):return rf'\fill[{c}] ({x},{y}) circle(2.5pt);'
def plot(expr,lo,hi,c=G):
 expr=expr.replace(r'\x^',r'(\x)^')
 return rf'\draw[{c},very thick,domain={lo}:{hi},samples=100] plot(\x,{{{expr}}});'
def axes(xmin,xmax,ymin,ymax):
 return [rf'\draw[gray,->] ({xmin},0)--({xmax},0) node[right] {{$x$}};',rf'\draw[gray,->] (0,{ymin})--(0,{ymax});']
def xticks(values,y=0):
 return [rf'\draw[gray] ({x},{y}+.08)--({x},{y}-.08);\node[below] at ({x},{y}-.15) {{${x}$}};' for x in values]
def build():
 q=frame(6.5,'同一对横坐标：原函数同高，导函数的值互为相反数')
 q += [r'\node at (3.5,5.15) {$f(x)=(x-2)^2+1$};',r'\node at (10.3,5.15) {$f^{\prime}(x)=2(x-2)$};',scope(1.2,1.4,.95,.55)]+axes(-.2,4.4,-.3,5.5)
 q += [plot('(\\x-2)^2+1',.3,3.7),r'\draw[dashed,teal!65!black] (2,0)--(2,5);',r'\node[above] at (2,5.1) {$x=2$};',r'\draw[dotted,gray] (1,2)--(3,2);',dot(1,2),dot(3,2),r'\node[above] at (1,2.8) {$2$};\node[above] at (3,2.8) {$2$};']+xticks([1,2,3])+[r'\end{scope}',scope(8.2,2.8,.95,.46)]+axes(-.2,4.4,-3.8,3.8)
 q += [plot('2*(\\x-2)',.3,3.7,B),r'\draw[dotted,gray] (0,-2)--(1,-2) (0,2)--(3,2);',dot(1,-2,B),dot(3,2,B),dot(2,0,B),r'\node[left] at (0,-2) {$-2$};\node[left] at (0,2) {$2$};',r'\node[above left] at (1.9,.45) {$(2,0)$};']+xticks([1,3])+[r'\end{scope}',r'\node at (6.8,.45) {$1,3$ 的中点是 $2$：左图看轴，右图看中心 $(2,0)$。};']
 save('01_statement_01',q)

 q=frame(7.5,'高度的对称性，怎样变成切线斜率的关系？')
 q += [r'\node at (3.4,6.35) {$f(x)=(x-2)^2+1$};',r'\node at (10.2,6.35) {$g(x)=(x-1)^3+7$};',scope(1.2,1.25,.95,.44)]+axes(-.2,4.4,-.3,10.5)
 q += [plot('(\\x-2)^2+1',.3,3.7),r'\draw[orange!85!black,thick,domain=.55:1.45] plot(\x,{4-2*\x});',r'\draw[orange!85!black,thick,domain=2.55:3.45] plot(\x,{2*\x-4});',r'\draw[dashed,gray] (2,0)--(2,8.8);',dot(1,2),dot(3,2),r'\node at (.6,6.4) {斜率 $-2$};\node at (3.5,6.4) {斜率 $2$};',r'\node[below] at (2,-.1) {$2$};',r'\end{scope}',scope(8.5,1.25,1,.44)]+axes(-.3,3.9,-.3,10.5)
 q += [plot('(\\x-1)^3+7',-.2,2.3),r'\draw[orange!85!black,thick,domain=-.25:.35] plot(\x,{3*\x+6});',r'\draw[orange!85!black,thick,domain=1.65:2.25] plot(\x,{3*\x+2});',r'\draw[gray,dotted] (0,6)--(2,8);',dot(0,6),dot(2,8),dot(1,7,B),r'\node[left] at (-.1,6) {$(0,6)$};\node[right] at (2.15,8) {$(2,8)$};',r'\node[below right] at (1.1,6.2) {$(1,7)$};',r'\node at (0,10.2) {斜率 $3$};\node at (2.6,10.2) {斜率 $3$};']+xticks([0,1,2])+[r'\end{scope}',r'\node at (3.4,.45) {轴对称：左右切线斜率反号};',r'\node at (10.2,.45) {中心对称：左右切线斜率相同};']
 save('02_explanation_01',q)

 q=frame(6.1,'$a-t$ 中的负号：$t$ 增大时，这个输入向左移动')
 q += [scope(1.3,1.6,1.2,.65)]+axes(-.1,4.4,-.2,4.8)+[plot('(\\x-2)^2+1',.3,3.7),dot(1,2),dot(3,2),r'\draw[dashed,gray] (2,0)--(2,4.5);',r'\draw[->,orange!85!black,very thick] (1,-.8)--(.55,-.8);',r'\draw[->,blue!70!black,very thick] (3,-.8)--(3.45,-.8);',r'\node[below] at (1,0) {$a-t=1$};\node[below] at (3,0) {$a+t=3$};',r'\end{scope}',r'\node[anchor=west,align=left,text width=5.4cm] at (7.3,3) {取 $a=2,t=1$。\\[10pt]$t$ 增大时：\\左点向左，右点向右；\\两边都沿图像升高。\\[10pt]但 $f^{\prime}(1)=-2$、$f^{\prime}(3)=2$。\\负号来自左边输入的反向变化。};',r'\node at (6.8,.4) {橙箭头：$a-t$ 减小；蓝箭头：$a+t$ 增大。};']
 save('03_proof_01',q)

 q=frame(5.9,'反推的关键：$H$、$K$ 的导数为零，各自图像都是水平线')
 q += [scope(4.8,1.3,1.35,.18),r'\draw[gray,->] (-2.6,0)--(2.7,0) node[right] {$t$};',r'\draw[gray,->] (0,-1)--(0,17);',r'\draw[teal!75!black,very thick] (-2.3,0)--(2.3,0);',r'\draw[blue!70!black,very thick] (-2.3,14)--(2.3,14);',r'\draw[gray,dashed] (0,0)--(0,14);',dot(0,0),dot(0,14,B),r'\node[below] at (0,-.2) {$0$};',r'\end{scope}',r'\node[anchor=west,align=left,text width=3.8cm] at (9,3.8) {$K(t)\equiv14$\\取 $f(x)=(x-1)^3+7$\\$a=1,\ K(0)=2f(1)=14$。};',r'\node[anchor=west,align=left,text width=3.8cm] at (9,1.6) {$H(t)\equiv0$\\取 $f(x)=(x-2)^2+1$\\$a=2,\ H(0)=0$。};',r'\node at (6.8,.4) {图示用具体函数展示；正文证明对任意符合条件的 $f$ 成立。};']
 save('03_proof_02',q)

 q=frame(6.5,'导数的平均数是 $b$，原函数对应两点的高度差是 $2bt$')
 q += [r'\node at (3.5,5.2) {$f^{\prime}(x)=2x+2$};',r'\node at (10.2,5.2) {$f(x)=x^2+2x$};',scope(3.3,1.75,1.25,.6)]+axes(-1.8,1.8,-1.2,4.6)
 q += [plot('2*\\x+2',-1.45,1.2,B),dot(-1,0,B),dot(1,4,B),dot(0,2,B),r'\draw[dotted,gray] (-1,0)--(1,4);',r'\node[left] at (-.1,2) {$(0,2)$};',r'\node[above left] at (-1,.1) {$0$};\node[above right] at (1,4.1) {$4$};']+xticks([-1,1])+[r'\end{scope}',scope(9.4,2.2,1.25,.6)]+axes(-1.8,2,-1.7,4.1)
 q += [plot('\\x^2+2*\\x',-1.65,1.1),dot(-1,-1),dot(1,3),r'\draw[orange!85!black,<->,thick] (1.55,-1)--(1.55,3);',r'\node[right] at (1.6,1) {$4$};',r'\draw[gray,dotted] (-1,-1)--(1.55,-1) (1,3)--(1.55,3);',r'\node[below left] at (-1,-1.1) {$-1$};\node[above] at (1,3.25) {$3$};']+xticks([-1,1])+[r'\end{scope}',r'\node at (6.8,.4) {取 $a=0,b=2,t=1$：$f(1)-f(-1)=3-(-1)=4=2bt$。};']
 save('03_proof_03',q)

 # Example 1 uses exactly the same model as the statement, with one maintained source.
 (OUT/(UID+'_04_examples_01.tex')).write_text(r'\input{assets/tikz/'+UID+'_01_statement_01.tex}\n'.replace('\\n','\n'),encoding='utf-8')

 q=frame(6.8,'导函数关于 $x=1$ 对称，原函数的中心高度由 $f(1)=7$ 确定')
 q += [r'\node at (3.5,5.55) {$f^{\prime}(x)=3(x-1)^2+2$};',r'\node at (10.1,5.55) {$f(x)=(x-1)^3+2(x-1)+7$};',scope(1.6,1.4,1.15,.4)]+axes(-.2,3.6,-.3,9.5)
 q += [plot('3*(\\x-1)^2+2',-.2,2.2,B),r'\draw[blue!65!black,dashed] (1,0)--(1,8.7);',dot(0,5,B),dot(2,5,B),r'\draw[dotted,gray] (0,5)--(2,5);',r'\node[above] at (0,5.7) {$5$};\node[above] at (2,5.7) {$5$};']+xticks([0,1,2])+[r'\end{scope}',scope(8.9,1.4,1.15,.32)]+axes(-.35,3.4,-.3,11.7)
 q += [plot('(\\x-1)^3+2*(\\x-1)+7',-.2,2.2),dot(0,4),dot(1,7,B),dot(2,10),r'\draw[dotted,gray] (0,4)--(2,10);',r'\node[left] at (-.12,4) {$4$};\node[above right] at (2,10) {$10$};',r'\node[below right] at (1.1,6.1) {$(1,7)$};']+xticks([0,1,2])+[r'\end{scope}',r'\node at (6.8,.45) {$0,2$ 关于 $1$ 配对；$f(0)+f(2)=4+10=14$。};']
 save('04_examples_02',q)

 q=frame(5.9,'不是关于 $x=0$ 对称，仍然可能有另一条对称轴')
 q += [scope(4.6,2.1,1.1,.75)]+axes(-3.2,1.7,-1.5,3.1)+[plot('\\x^2+2*\\x',-2.8,.8),r'\draw[teal!65!black,dashed] (-1,-1.25)--(-1,2.8);',r'\draw[red!65!black,dotted] (0,-1.25)--(0,2.8);',dot(-1,-1),dot(-2,0),dot(0,0)]+xticks([-2,-1,0])+[r'\end{scope}',r'\node[anchor=west,align=left,text width=4.7cm] at (8,3.1) {$f(x)=(x+1)^2-1$。\\[10pt]绿虚线 $x=-1$：真正的轴。\\[10pt]红点线 $x=0$：不是轴。\\[10pt]$b\ne0$ 只排除指定的 $x=a$。};',r'\node at (6.8,.4) {$f^{\prime}(x)=2x+2$ 关于 $(0,2)$ 中心对称，但 $f$ 的轴在 $x=-1$。};']
 save('04_examples_03',q)
 # Same counterexample and color coding for the corresponding trap.
 (OUT/(UID+'_05_traps_01.tex')).write_text(r'\input{assets/tikz/'+UID+'_04_examples_03.tex}'+'\n',encoding='utf-8')

 q=frame(6.4,r'取满足例题条件的 $f(x)=\sin(\pi x)$：一格反高，两格还原')
 q += [scope(1.3,2.7,1.75,1.15)]+axes(-.1,4.15,-1.4,1.5)+[plot('sin(180*\\x)',0,4),r'\draw[teal!65!black,dashed] (1.5,-1.25)--(1.5,1.25);',dot(2,0,B),r'\node[above] at (1.5,1.5) {轴 $x=\frac32$};',r'\node[below] at (2,-1.5) {中心 $(2,0)$};']+xticks([0,1,2,3,4])
 for x in [.25,1.25,2.25]:q.append(dot(x,math.sin(math.pi*x),O))
 q += [r'\draw[orange!85!black,dotted] (.25,{sqrt(.5)})--(2.25,{sqrt(.5)});',r'\end{scope}',r'\node[anchor=west,align=left,text width=3.7cm] at (9.2,3.3) {$f(x+1)=-f(x)$\\（本例 $f(2)=0$）。\\[12pt]再走一格：\\$f(x+2)=f(x)$。\\[12pt]图像只是代表例子，\\一般证明见正文。};']
 save('04_examples_04',q)

 q=frame(5.9,'中心的纵坐标是 $f(a)$，不一定是 $0$')
 q += [scope(1.6,1.1,1.25,.35)]+axes(-.3,3.3,-.3,11.5)+[plot('(\\x-1)^3+7',-.2,2.2),dot(0,6),dot(2,8),dot(1,7,B),r'\draw[dotted,gray] (0,6)--(2,8);',r'\draw[red!70!black,thick] (.92,-.25)--(1.08,.25) (.92,.25)--(1.08,-.25);',r'\node[below] at (1,-.4) {$(1,0)$};',r'\node[below right] at (1.1,6.5) {$(1,7)$};\node[left] at (0,6) {$6$};\node[above right] at (2,8) {$8$};',r'\end{scope}',r'\node[anchor=west,align=left,text width=6cm] at (6.6,2.5) {$f(x)=(x-1)^3+7$。\\[10pt]两点的平均高度为 $(6+8)/2=7$。\\[10pt]蓝点 $(1,7)$ 才是中心；\\红叉 $(1,0)$ 不是。\\[10pt]由 $f^{\prime}$ 的轴只能读出中心横坐标，\\纵坐标还须看 $f(1)$。};']
 save('trap_center_height',q)
 (OUT/(UID+'_trap_chain_sign.tex')).write_text(r'\input{assets/tikz/'+UID+'_03_proof_01.tex}'+'\n',encoding='utf-8')

 q=frame(6.5,'定义域即使左右对称，中间断开时仍不能直接反推')
 q += [scope(4.7,1.7,1.2,.58)]+axes(-2.7,2.7,-.3,6.5)+[r'\fill[gray!12] (-1,-.25) rectangle (1,6);',plot('\\x^2+1',-2.2,-1),plot('\\x^2',1,2.2),r'\draw[teal!75!black,fill=green!3,thick] (-1,2) circle(2.5pt) (1,1) circle(2.5pt);',dot(-2,5),dot(2,4),r'\node[above] at (-2,5.2) {$5$};\node[above] at (2,4.2) {$4$};']+xticks([-2,-1,1,2])+[r'\node at (0,6.6) {缺少中间区间};',r'\end{scope}',r'\node[anchor=west,align=left,text width=4.2cm] at (8.7,3.2) {$D=(-\infty,-1)\cup(1,\infty)$。\\[8pt]左边 $f=x^2+1$，\\右边 $f=x^2$。\\[8pt]两边都满足 $f^{\prime}=2x$，\\但 $f(-2)=5\ne4=f(2)$。};',r'\node at (6.8,.4) {两段可以相差不同常数；反推时需要在同一个对称区间上可导。};']
 save('trap_disconnected_domain',q)

 q=frame(5.4,r'取 $f(x)=\sin(3\pi x)$：$2$ 是周期，最小正周期却是 $\frac23$')
 q += [scope(1.3,2.5,4.8,.8)]+axes(-.05,2.15,-1.2,1.3)+[plot('sin(540*\\x)',0,2),r'\draw[orange!85!black,<->,thick] (0,-1.3)--(2,-1.3) node[midway,below] {周期 $2$};',r'\draw[blue!70!black,<->,thick] ({1/6},1.65)--({5/6},1.65) node[midway,above] {相邻波峰相距 $\frac23$};',dot(1/6,1,B),dot(5/6,1,B)]+xticks([0,1,2])+[r'\end{scope}',r'\node at (6.8,.4) {这条示例也关于 $x=\frac32$ 轴对称、关于 $(2,0)$ 中心对称。};']
 save('trap_period_vs_least',q)

 q=frame(8.2,'在 $a=0$ 的具体模型中记住：原轴导中，原中导轴')
 cases=[(2.8,5.8,'\\x^2','x^2',0,2),(9.6,5.8,'2*\\x','2x',-2.1,2.1),(2.8,2.3,'\\x^3','x^3',-1.2,1.2),(9.6,2.3,'3*\\x^2','3x^2',-.3,3.4)]
 for i,(ox,oy,expr,label,lo,hi) in enumerate(cases):
  q += [scope(ox,oy,1.3,.42)]+axes(-1.7,1.8,lo,hi)+[plot(expr,-1.05,1.05,G if i%2==0 else B),dot(0,0,G if i%2==0 else B),r'\end{scope}',rf'\node at ({ox},{oy-1.3}) {{${label}$：'+(['原函数轴对称','导函数中心对称','原函数中心对称','导函数轴对称'][i])+r'};']
 q += [r'\draw[->,teal!65!black,thick] (5.5,6.1)--(6.9,6.1) node[midway,above] {求导};',r'\draw[->,teal!65!black,thick] (5.5,2.65)--(6.9,2.65) node[midway,above] {求导};',r'\node at (6.8,.35) {一般位置先找 $a$；中心纵坐标分别看 $0$ 或 $f(a)$。};']
 save('06_summary_01',q)

def audit():
 count=0
 for a in [-2,0,1,2]:
  for t in [-2,-1,-.25,0,.5,1,2]:
   even=lambda x:(x-a)**4+2*(x-a)**2+3
   de=lambda x:4*(x-a)**3+4*(x-a)
   odd=lambda x:(x-a)**3+2*(x-a)+7
   do=lambda x:3*(x-a)**2+2
   assert math.isclose(even(a+t),even(a-t));assert math.isclose(de(a+t),-de(a-t),abs_tol=1e-12)
   assert math.isclose(odd(a+t)+odd(a-t),14);assert math.isclose(do(a+t),do(a-t))
   for b in [-2,0,2]:
    f=lambda x:(x-a)**4+b*(x-a)+3
    df=lambda x:4*(x-a)**3+b
    assert math.isclose(df(a+t)+df(a-t),2*b,abs_tol=1e-12)
    assert math.isclose(f(a+t)-f(a-t),2*b*t,abs_tol=1e-12);count+=1
 for x in [0,.1,.25,.7,1,2,3]:
  for k in [1,3]:
   f=lambda z:math.sin(k*math.pi*z)
   assert math.isclose(f(1.5+x),f(1.5-x),abs_tol=1e-12)
   assert math.isclose(f(2+x),-f(2-x),abs_tol=1e-12)
   assert math.isclose(f(x+1),-f(x),abs_tol=1e-12)
   assert math.isclose(f(x+2),f(x),abs_tol=1e-12);count+=1
 assert (0-1)**3+2*(0-1)+7==4 and (2-1)**3+2*(2-1)+7==10
 # Exact tangents used in the explanation: value and slope at both contacts.
 assert 4-2*1==(1-2)**2+1 and 2*3-4==(3-2)**2+1
 assert 3*0+6==(0-1)**3+7 and 3*2+2==(2-1)**3+7
 return count+5
if __name__=='__main__':
 checked=audit();build();print(f'PASS: {checked} model, symmetry, tangent and example checks; 15 UID-prefixed TikZ sources generated.')
