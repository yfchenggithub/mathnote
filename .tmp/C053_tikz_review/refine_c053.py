from pathlib import Path
import re
d=Path('assets/tikz')
def edit(n,f):
 p=d/('C053_'+n+'.tex');p.write_text(f(p.read_text(encoding='utf-8')),encoding='utf-8')
for n in ['focal_chord_notation','angle_comparison','forward_projection']:
 edit(n,lambda s:s.replace(r'node[above right=4pt] {$A$}',r'node[above=8pt] {$A$}').replace(r'node[below right=4pt] {$B$}',r'node[below left=6pt] {$B$}'))
for n in ['angle_comparison','validity_comparison']:
 edit(n,lambda s:s.replace('shift={(6.6,','shift={(6.4,').replace('shift={(11.2,','shift={(10.8,').replace('(7.199999999999999,','(7.0,').replace('(11.799999999999999,','(11.4,'))
 # Titles and length labels retain evenly spaced text centers.
def fixangles(s):
 i=s.index(r'\begin{scope}[shift={(10.8,')
 return s[:i]+s[i:].replace(r'node[below right=5pt] {$F$}',r'node[below left=5pt] {$F$}',1)
edit('angle_comparison',fixangles)
for n in ['forward_projection','backward_projection']:
 def reorder(s):
  lines=s.splitlines();ci=next(i for i,l in enumerate(lines) if r'plot ({\t*\t/4}' in l)
  line=lines.pop(ci);fi=next(i for i,l in enumerate(lines) if l.startswith(r'\fill['))
  lines.insert(fi+1,line)
  return '\n'.join(lines)+'\n'
 edit(n,reorder)
edit('forward_projection',lambda s:s.replace(r'node[above left=4pt] {$H$}',r'node[below left=5pt] {$H$}'))
def mirror(s):
 s=s.replace(r'node[above right=4pt] {$A$}',r'node[above=8pt] {$A$}').replace(r'node[above left=4pt] {$A$}',r'node[above=8pt] {$A$}')
 s=s.replace(r'node[below right=4pt] {$B$}',r'node[below left=6pt] {$B$}').replace(r'node[below left=4pt] {$B$}',r'node[below right=6pt] {$B$}')
 old=r'\draw[->,gray] (-1.1,0)--(1.1,0);'
 s=s.replace(old,r'\draw[->,gray] (-1.1,0)--(4.5,0);',1)
 s=s.replace(old,r'\draw[->,gray] (-4.5,0)--(1.1,0);',1)
 return s
edit('opening_reflection',mirror)
edit('vertical_axis_angle',lambda s:s.replace(r'node[above left=5pt] {$B$}',r'node[above=10pt] {$B$}'))
base=Path('03_conic/C053_parabola_focal_chord_length_inclination')
for n,color in [('01_statement.tex','CStatement'),('03_proof.tex','CProof'),('06_summary.tex','CSummary')]:
 p=base/n;s=p.read_text(encoding='utf-8')
 s=s.replace('\\medskip\n\\textbf{\\textcolor{'+color,'\\par\\medskip\n\\textbf{\\textcolor{'+color)
 p.write_text(s,encoding='utf-8')
print('C053 labels, drawing order, margins and heading paragraphs refined.')
