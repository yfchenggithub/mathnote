from pathlib import Path
import re
root=Path('assets/tikz')
for stem in ['statement_overview','directrix_projection']:
 p=root/f'C056_{stem}.tex';s=p.read_text(encoding='utf8')
 s=re.sub(r'\\fill \(4,0\) circle\(2pt\) node\[[^\]]+\] \{\$F\$\};',lambda m:r'\fill (4,0) circle(2pt);\node at (2.7,-.9) {$F$};\draw[gray,thin] (3.3,-.65)--(3.95,-.03);',s)
 if stem=='statement_overview':
  s=s.replace(r'\draw[->,violet,thick] (4,0)--(5.2,{1.2*sqrt(3)});',r'\draw[->,violet,thick] (5.6,1.7)--(6.3,2.9124355653) node[above=6pt] {正向};')
  s=s.replace(r'\draw[violet] (4.8,0)',r'\node[gray,below=5pt] at (5.7,0) {$x$};\draw[violet] (4.8,0)')
 p.write_text(s,encoding='utf8')
p=root/'C056_pure_projection.tex';s=p.read_text(encoding='utf8').replace('node[below=8pt] {$B$}','node[left=10pt] {$B$}');p.write_text(s,encoding='utf8')
p=root/'C056_two_focal_triangles.tex';s=p.read_text(encoding='utf8').replace('node[below right=7pt] {$F$}','node[right=22pt] {$F$}')
s=s.replace(r'\node[violet] at (3.25,1.05) {$\pi-\theta$};',r'\node[violet] at (2.5,-1.3) {$\pi-\theta$};\draw[gray,thin] (2.9,-.95)--(3.5,.35);')
s=s.replace(r'\node[above=8pt] at (0,0) {$2c$};',r'\node[below=10pt] at (0,0) {$2c$};',1)
p.write_text(s,encoding='utf8')
p=root/'C056_angle_comparison.tex';s=p.read_text(encoding='utf8')
s=re.sub(r'\\fill \(4,0\) circle\(2pt\) node\[[^\]]+\] \{\$F\$\};',lambda m:r'\fill (4,0) circle(2pt);\node at (2.3,-.4) {$F$};\draw[gray,thin] (2.8,-.3)--(3.95,-.02);',s)
p.write_text(s,encoding='utf8')
p=root/'C056_chord_extremes.tex';s=p.read_text(encoding='utf8');s=re.sub(r'node\[[^\]]+\] \{\$F\$\}',lambda m:r'node[above left=10pt] {$F$}',s);p.write_text(s,encoding='utf8')
p=root/'C056_left_right_focus.tex';s=p.read_text(encoding='utf8').replace('node[below right=7pt] {$F$}','node[above left=10pt] {$F$}');p.write_text(s,encoding='utf8')
