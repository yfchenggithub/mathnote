from pathlib import Path
import json

for mode in [1, 2]:
    title = r'第一种分法：沿 $F_1I$ 分成蓝、绿两个三角形' if mode == 1 else r'第二种分法：沿 $PF_2$ 分成橙、红两个三角形'
    lines = [r'\begin{center}', r'\begin{tikzpicture}[x=1cm,y=1cm,line cap=round,line join=round,font=\small]',
             r'\draw[black!25,rounded corners=3pt] (0,0) rectangle (14.4,6.8);',
             rf'\node[font=\small\bfseries] at (7.2,6.3) {{{title}}};',
             r'\begin{scope}[shift={(4.5,1.35)},x=1.05cm,y=1.05cm]',
             r'\coordinate (A) at (-2,0);', r'\coordinate (P) at (2.5,{3*sqrt(7)/2});',
             r'\coordinate (B) at (2,0);', r'\coordinate (I) at (5,{sqrt(7)});']
    if mode == 1:
        lines += [r'\fill[blue!23] (P)--(A)--(I)--cycle;', r'\fill[green!23] (I)--(A)--(B)--cycle;',
                  r'\draw[blue!65!black,line width=1.2pt] (A)--(I);',
                  r'\node[blue!60!black] at (1.9,2.5) {$S_{PF_1I}$};',
                  r'\node[green!40!black] at (1.7,.73) {$S_{IF_1F_2}$};']
    else:
        lines += [r'\fill[orange!23] (P)--(A)--(B)--cycle;', r'\fill[red!23] (I)--(P)--(B)--cycle;',
                  r'\draw[red!70!black,line width=1.2pt] (P)--(B);',
                  r'\node[orange!60!black] at (.55,1.25) {$S_{PF_1F_2}$};',
                  r'\node[red!60!black] at (3.3,2.25) {$S_{IPF_2}$};']
    lines += [r'\draw[black!80,line width=1.1pt] (P)--(A)--(B)--(I)--cycle;',
              r'\foreach \q in {A,P,B,I} \fill (\q) circle (1.7pt);',
              r'\node[below left] at (A) {$F_1$};', r'\node[above left] at (P) {$P$};',
              r'\node[below] at (B) {$F_2$};', r'\node[right] at (I) {$I$};', r'\end{scope}']
    formula = (r'$S_{\text{四边形}}=\textcolor{blue!60!black}{S_{PF_1I}}+\textcolor{green!40!black}{S_{IF_1F_2}}$'
               if mode == 1 else r'$S_{\text{四边形}}=\textcolor{orange!60!black}{S_{PF_1F_2}}+\textcolor{red!60!black}{S_{IPF_2}}$')
    lines += [rf'\node at (7.2,.5) {{{formula}}};', r'\end{tikzpicture}', r'\end{center}']
    name = 'C048_quadrilateral_split_' + ('f1_i' if mode == 1 else 'p_f2') + '.tex'
    (Path('assets/tikz')/name).write_text('\n'.join(lines)+'\n', encoding='utf-8')

uid = Path('03_conic/C048_hyperbola_focus_triangle_area')
p = uid/'03_proof.tex'
s = p.read_bytes().decode('utf-8')
start = s.index(r'\textbf{第3步：三个底边所在直线到 $I$ 的距离都是 $r$。}')
end = s.index(r'\textbf{第4步：', start)
replacement = r'''\textbf{第3步：同一个四边形，两种分法。} 下面两图的四边形 $PF_1F_2I$ 完全相同、尺度相同，只更换分割线。
\input{assets/tikz/C048_quadrilateral_split_f1_i}
\input{assets/tikz/C048_quadrilateral_split_p_f2}
两种分法的总面积相等，故\textbf{把第二图的红色三角形减去}：
\[
S_{PF_1F_2}=S_{PF_1I}+S_{IF_1F_2}-S_{IPF_2}.
\]
\end{proofbox}
\clearpage
\begin{proofbox}
\textbf{\textcolor{CProof}{方法五（最后一步）：将面积分解换成底乘高}}

三个底边所在直线到 $I$ 的距离都为 $r$，因此
\[
S=\frac12 mr+\frac12(2c)r-\frac12 nr
 =\frac r2(m-n+2c)=\boxed{(a+c)r}.
\]
'''
if '\r\n' in s:
    replacement = replacement.replace('\n', '\r\n')
p.write_bytes((s[:start]+replacement+s[end:]).encode('utf-8'))
p = uid/'meta.json'
d = json.loads(p.read_text(encoding='utf-8'))
d['remarks'] += ' 2026-10-24 按用户反馈，方法五面积分解改为两个同尺度完整四边形：assets/tikz/C048_quadrilateral_split_f1_i.tex沿F1I分为蓝绿两块，C048_quadrilateral_split_p_f2.tex沿PF2分为橙红两块。以同一总面积建立等式，替代旧三面板的相加相减说明。'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Added two full-quadrilateral TikZ diagrams in method five.')
