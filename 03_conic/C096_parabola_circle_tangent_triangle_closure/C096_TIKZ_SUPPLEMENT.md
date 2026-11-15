# C096 TikZ 补图与验收

日期：2026-11-14。仅处理 C096，保留工作树中原有修改与图源副本。

## 视觉计划及落点

| 图源（均位于 assets/tikz/） | 卡点与可见关系 | 缩短的文字 | 数学检查 |
| --- | --- | --- | --- |
| C096_center_parameter.tex | 轴上两段长度组成 h，圆的最左点为 L | 圆心条件的位置解释 | OL=r²/k，LM=r |
| C096_chord_distance.tex | 同一个三角形用两组底高求面积，MH 垂直于弦 | 两种面积算法的脑补 | Q、R 在弦上，MH 垂直 QR |
| C096_proof_sum_product.tex | 方法一：另外两点确定第三条弦，圆心距为半径 | 方法一末尾的策略复述 | 非对称例三条弦均相切 |
| C096_proof_quadratic_roots.tex | 方法二：同一二次函数的两个横轴交点对应 b、c | 两根视角的重复说明 | 零点、对称轴、和积 |
| C096_proof_substitution_area.tex | 方法三：正方形减去矩形，余下面积为 −bc | 回代消去平方项的解释 | 画图区间有标明；恒等式无符号限制 |
| C096_proof_discriminant.tex | 方法四：固定同一圆，平移直线得到 2、1、0 个交点 | 判别式为零与唯一交点的联系 | 三面板尺度相同，切例 y²=0 |

## 修改范围

- 正文：01_statement.tex、02_explanation.tex、03_proof.tex；四种证明各有直接配图，长证明分步分页。
- 元数据：meta.json 补齐全部配图路径与用途记录，更新时间为 2026-11-14。
- 新增上述六个 TikZ 图源；既有 C096_core_triangle.tex 统一 A₁、A₂、A₃ 记号，并移动第三弦标签。
- 既有 C096_compare_circle_positions.tex、C096_segment_extension.tex 仅调整标签位置及图注间距；坐标、模型不变。
- 重新生成 pdfs/C096_parabola_circle_tangent_triangle_closure.pdf。未修改公共模板、构建器、其他 UID、index.tex 或两个 copy 图源；未执行发布、提交或 Sync。

## 实际验证

- 数学审计 PASS：核对主分支与另一分支的相切展开、和积表达式及判别式推导；a²=r² 的排除理由保留。
- 数值辅助核验 PASS：使用 Python Fraction 对两种分支共 72 组参数精确检查 (kh+bc)²=r²[k²+(b+c)²]。这属于参数抽查，不代替一般代数证明。
- 图形核验 PASS：a=1/2、k=r=1 时 b,c=(2±√37)/3；三弦的点在线上、相切关系和垂足 H=(13/5,−4/5) 均核对。面积恒等式、二次函数零点及顶点另作算术核验。
- 构建 PASS：标准单 UID 构建器成功；独立映射 .tmp/C096_conclusion_pdf_map.preview.json，未覆盖正式映射。
- PDF PASS：pdfinfo 确认 20 页、A4、未加密。
- 逐页视觉检查 PASS：全 20 页以 180 DPI 渲染检查；10 幅数学图所在页以 300 DPI 生成含完整内容框的局部图并逐图查看。修正间距后重编译并复查受影响页，未见重叠、裁切或压线。
- 元数据 PASS：JSON 可解析，additional_tikz 中所有路径均存在。

构建命令：

```powershell
python -B scripts/build_conclusion_pdfs.py C096 --overwrite --output-to-conclusion-pdfs --map-json .tmp/C096_conclusion_pdf_map.preview.json
```

已知未解决问题：本轮补图范围内未发现。
