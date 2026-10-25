from pathlib import Path
import math
base=Path('assets/tikz')
p=base/'C051_math_audit_geometry.tex'
s=p.read_text(encoding='utf-8').replace('4.4,5.2','4.4,4.9')
s=s.replace('(3.7,0) node[right]','(2.1,0) node[right]')
s=s.replace(r'\draw[<->,blue!75!black] (0,-.8)--(1,-.8) node[midway,below] {$p/2$};',r'''\draw[gray,dotted] (1,2.2)--(1,3.15);
 \draw[<->,blue!75!black] (0,3.15)--(1,3.15) node[midway,above] {$p/2$};''')
# The axis arrow does not run behind the latus-rectum label.
s=s.replace(r'\draw[->,gray] (-1.8,0)--(2.1,0) node[right] {$x$};',r'\draw[->,gray] (-1.8,0)--(2.1,0) node[above] {$x$};')
p.write_text(s,encoding='utf-8')
p=base/'C051_area_height.tex'
s=p.read_text(encoding='utf-8').replace('domain=-.9:4.25','domain=0:4.25')
p.write_text(s,encoding='utf-8')
p=base/'C051_four_openings.tex'
s=p.read_text(encoding='utf-8')
for x,label in [('1,2','P'),('-1,2','Q'),('1,0','F'),('0,0','O')]:
    import re
    s=re.sub(r'\\fill \('+re.escape(x)+r'\) circle\((?:2|1\.7)pt\) node\[[^\]]+\] \{\$'+label+r'\$\};',r'\\fill ('+x+r') circle(2pt);',s)
anchors=[['above right','above left','below right','below left'],['below left','below right','above left','below right'],['above left','below left','above right','below right'],['below right','above right','below left','above left']]
chunks=s.split(r'\end{scope}\end{scope}')
for i,a in enumerate([0,180,90,270]):
    text=''
    for (x,y),label,anchor in zip([(1,2),(-1,2),(1,0),(0,0)],'PQFO',anchors[i]):
        ar=math.radians(a); xx=round(x*math.cos(ar)-y*math.sin(ar),6); yy=round(x*math.sin(ar)+y*math.cos(ar),6)
        text+=rf'\node[{anchor}=3pt] at ({xx},{yy}) {{${label}$}};'+'\n'
    chunks[i]+=r'\end{scope}'+'\n'+text+r'\end{scope}'
s=''.join(chunks).replace('(-2.7,0)--(2.7,0)','(-2.5,0)--(2.5,0)').replace('(0,-2.7)--(0,2.7)','(0,-2.5)--(0,2.5)')
p.write_text(s,encoding='utf-8')
p=Path('03_conic/C051_parabola_focal_radius_coordinate/03_proof.tex')
s=p.read_text(encoding='utf-8')
start=s.index('  \\medskip\n  \\textbf{\\textcolor{CProof}{推荐顺序}}')
s=s[:start]+'\\end{proofbox}\n'
s=s.replace('  \\textbf{速度优势：}一眼认准线，直接得结果；不用两点距离公式，也不用展开平方。','')
start=s.index('  \\textbf{适用价值：}')
end=s.index('  \\medskip',start)
s=s[:start]+s[end:]
p.write_text(s,encoding='utf-8')
print('Corrected dimension-label crossings, panel label anchors and orphan proof paragraph.')
