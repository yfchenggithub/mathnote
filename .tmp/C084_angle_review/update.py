from pathlib import Path
import shutil,json,hashlib
r=Path('D:/mathnote');u=r/'03_conic/C084_hyperbola_focal_triangle_internal_angle_bisector';w=r/'.tmp/C084_angle_review'
(w/'before').mkdir(parents=True,exist_ok=True)
for p in u.iterdir():
 if p.is_file():shutil.copy2(p,w/'before'/p.name)
pdf=u/'pdfs/C084_hyperbola_focal_triangle_internal_angle_bisector.pdf'
(w/'formal_pdf.sha256').write_text(hashlib.sha256(pdf.read_bytes()).hexdigest())
p=u/'03_proof.tex';s=p.read_text(encoding='utf8');anchor='\\textbf{第1步：设三条直线的斜率。}'
assert s.count(anchor)==1
s=s.replace(anchor,r'''\input{assets/tikz/C084_tangent_angle_two_roots}
\textbf{看图读式：}上图先固定两个相等半角；下图把另一根命名为 $N$，
用底边内部／外部区分内、外角平分线。下文仍以 $m$ 表示待求的候选轴截距。
\end{proofbox}
\clearpage
\begin{proofbox}
\textbf{方法六（续）：由等角列式，再用位置选根。}

'''+anchor)
old='另一个根对应\\textbf{外角平分线与 $x$ 轴的交点}；它不满足题设的内角条件。'
assert old in s
s=s.replace(old,'另一个根对应图中的 $N$，位于底边延长线上，应舍去。')
p.write_text(s,encoding='utf8')
p=u/'meta.json';m=json.loads(p.read_text(encoding='utf8'))
m['remarks']+=' 本轮为新增方法六补图 assets/tikz/C084_tangent_angle_two_roots.tex：同尺度上下两层，先看两个相等半角，再用M在底边内部、N在底边外部解释两个代数根的筛选，替代纯文字的外根位置说明。'
m['meta']['updated_at']='2026-10-27'
m['content']['derivation'].append('倒角公式法：相邻夹角正切相等，得到(mx₀-a²)(c²x₀-a²m)=0；用-c<m<c选择内根，外根为N的横坐标c²x₀/a²。')
m['shareConfig']['shareDesc']=m['shareConfig']['shareDesc'].replace('五种证明','六种证明').replace('内切圆及半角向量','内切圆、半角向量及倒角公式')
for keyword in ['倒角公式','两直线夹角正切公式','内外角平分线两根筛选']:
 if keyword not in m['search']['keywords']:m['search']['keywords'].append(keyword)
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Added one two-panel TikZ in method six; preserved the new proof.')
