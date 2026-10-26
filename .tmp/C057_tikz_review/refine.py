from pathlib import Path
root=Path('assets/tikz')
# Keep finite-intersection markers visible at the actual small panel scales.
for stem in ['statement_comparison','same_branch_sum','cross_branch_difference']:
 p=root/f'C057_{stem}.tex';s=p.read_text(encoding='utf8').replace('circle(2pt)','circle(6pt)');p.write_text(s,encoding='utf8')
p=root/'C057_intersection_boundary.tex';s=p.read_text(encoding='utf8').replace('circle(2.5pt)','circle(10pt)').replace('circle(2pt)','circle(8pt)');p.write_text(s,encoding='utf8')

# The long same-ray distance BF contains AF: show it once more as a straightened ruler.
p=root/'C057_cross_branch_difference.tex';s=p.read_text(encoding='utf8')
s=s.replace('rectangle (14.2,13.1)','rectangle (14.2,15)').replace('(7.1,12.45)','(7.1,14.35)')
s=s.replace('shift={(4.5,7.1)}','shift={(4.5,9.0)}').replace('(-10,-9) rectangle (10,9)','(-10,-4) rectangle (10,9)').replace('(9.5,8.15)','(9.5,10.0)')
pos=s.index(r'\node at (7.1,3.6)')
strip=r'''
\node at (7.1,7.15) {把这条斜线展开看长度：$BF=AF+AB=3+9=12$};
\draw[orange!85!black,very thick] (2.2,6.0)--(8.2,6.0);
\draw[blue!75!black,very thick] (6.7,6.0)--(8.2,6.0);
\fill (2.2,6.0) circle(2pt) node[above=8pt] {$B$};
\fill (6.7,6.0) circle(2pt) node[above=8pt] {$A$};
\fill (8.2,6.0) circle(2pt) node[above=8pt] {$F$};
\draw[<->,orange!85!black] (2.2,5.45)--(8.2,5.45);
\node[orange!85!black] at (5.2,4.9) {整段 $BF=12$};
\node[anchor=west] at (9.3,6.0) {$AF=3,\ AB=9$};
'''
s=s[:pos]+strip+s[pos:]
p.write_text(s,encoding='utf8')

# Introduce coordinate notation explicitly and mark the right angles.
p=root/'C057_pure_projection.tex';s=p.read_text(encoding='utf8')
s=s.replace(r'\fill (0,0) circle(2pt) node[below right=8pt] {$P$};\end{scope}',r'\fill (0,0) circle(2pt) node[below right=8pt] {$P$};\end{scope}')
s=s.replace(r'\node at (7.1,.6) {所有 $PA,PB$ 都是正长度；分子才是有正负号的水平位移。};',r'\node at (7.1,1.3) {$x_P,x_A,x_B$ 分别是三点的横坐标。};\node at (7.1,.6) {所有 $PA,PB$ 都是正长度；分子才是有正负号的水平位移。};')
s=s.replace(r'\draw[gray] (-3,0)--(2,0);',r'\draw[gray] (-3,0)--(2,0);',1)
# Place square markers at the feet, using the upper and lower triangle orientations.
mark1=r'\draw[gray] (1.05,0)--(1.05,.15)--(1.2,.15);\draw[gray] (-.45,0)--(-.45,-.15)--(-.6,-.15);'
mark2=r'\draw[gray] (-.45,0)--(-.45,.15)--(-.6,.15);\draw[gray] (-1.65,0)--(-1.65,.15)--(-1.8,.15);'
needle=r'\fill (0,0) circle(2pt)'
idx=s.index(needle);s=s[:idx]+mark1+'\n'+s[idx:]
idx=s.index(needle,idx+len(mark1)+len(needle));s=s[:idx]+mark2+'\n'+s[idx:]
p.write_text(s,encoding='utf8')
