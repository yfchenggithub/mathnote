from pathlib import Path
for stem in ['pure_similarity','coordinate_mapping']:
 p=Path(f'assets/tikz/C055_{stem}.tex');s=p.read_text(encoding='utf8')
 s=s.replace('node[midway,right=7pt] {$u$}','node[midway,right=7pt,text=blue!75!black] {$u$}')
 s=s.replace('node[midway,left=7pt] {$v$}',r';\node[orange!85!black] at (-.75,-.6) {$v$}')
 if stem=='coordinate_mapping':
  s=s.replace(r'node[above=16pt] {$K$}',r';\node at (.7,1.0) {$K$};\draw[gray,thin] (.58,.78)--(.25,.06)')
  s=s.replace('node[below left=7pt] at (0,0)', 'node[above left=8pt] at (0,0)')
 p.write_text(s,encoding='utf8')
p=Path('assets/tikz/C055_product_comparison.tex');s=p.read_text(encoding='utf8');pos=s.index('shift={(10.4,6.7)}');s=s[:pos]+s[pos:].replace('node[below right=5pt] {$F$}','node[above right=7pt] {$F$}',1);p.write_text(s,encoding='utf8')
p=Path('assets/tikz/C055_validity_comparison.tex');s=p.read_text(encoding='utf8');pos=s.index('shift={(6,6)}');s=s[:pos]+s[pos:].replace('node[below right=5pt] {$F$}','node[above=10pt] {$F$}',1);p.write_text(s,encoding='utf8')
p=Path('assets/tikz/C055_four_openings.tex');s=p.read_text(encoding='utf8').replace('rectangle (14.2,15)','rectangle (14.2,16)').replace('(7.1,14.45)','(7.1,15.45)').replace('13.100000000000001','14.1')
s=s.replace(r'(-1,-0.75) circle(2pt) node[above left=7pt] {$B$}',r'(-1,-0.75) circle(2pt) node[below=10pt] {$B$}')
p.write_text(s,encoding='utf8')
p=Path('03_conic/C055_parabola_focal_chord_product/02_explanation.tex');s=p.read_text(encoding='utf8').replace('对一般非竖直焦点弦，先按左右端点标号：','对一般非竖直焦点弦，负斜率时先上下翻折，再按图中的左右端点标号：').replace('（负斜率时将图上下翻折）','');p.write_text(s,encoding='utf8')
p=Path('03_conic/C055_parabola_focal_chord_product/06_summary.tex');s=p.read_text(encoding='utf8').replace(r'\item \textbf{最低门槛：}设点',r'\item \textbf{最低门槛：}先用相似 $h/u=k/v$，代入坐标得 $(u+v)(uv-p^2)=0$。也可设点');p.write_text(s,encoding='utf8')
