# P036 外角平分线比例 PDF 精修验收

日期：2026-10-22。范围仅P036；开始时工作树干净。

## 数学审计与最终内容

- 原稿主比例BD/DC=AB/AC正确；原正弦证明把D处两角说成互补，属于关键错误。D在BC外部时DB、DC同向，两个角应相等，现已修正。
- 明确非退化、AB≠AC、普通正长度等条件；补充唯一有限交点、左右外分顺序、外分差关系、显式长度与坐标。
- 证明一优先：直角三角形全等得D到AB、AC的距离相等；同一对三角形面积按共同高、相等高计算两次，直接得到比例，覆盖左右外分。
- 证明二：先处理B,C,D顺序，过C作CF平行AD，角关系得AF=AC，再用BCF与BDA相似；另一侧交换B、C，明确覆盖两分支。
- 证明三：正弦定理短证，分别说明A处互补、D处相等，约分前检查正弦分母非零。
- 补证AB=AC当且仅当外角平分线平行BC，等腰无有限交点；非等腰时存在且交点不在BC内部。
- 三题均回验：例1还反求BC=4并验证三角形存在；例2由差关系求BD=10并用通式回验；例3以两种线段分解得到DE=4，核对内外分点顺序。
- 有向线段单独约定B=0,C=a，BD的代数值为xD、DC为a−xD，因此有向比为−AB/AC；不与普通长度混用。

## 先图后文与文件范围

编辑前已给出六行视觉计划，随后先生成几何图形，再围绕图形重写六段正文。修改P036的01—06、source.tex、meta.json、pdfs中的PDF；新增10幅assets/tikz/P036_*.tex和UID内checks/verify_p036.py。本报告为本UID的验收记录。
保持main.tex、共享排版/工具、正式images资源、其他UID、发布映射不变。未提交、未发布。

## 主图逐幅验收

| 图形 | 页 | 回答的问题及替代文字 | 数学/视觉 |
|---|---:|---|---|
| P036_left_external.tex | 2 | AB<AC时，D在B外侧；实数图替代延长方向与长度差的文字猜测。 | PASS / PASS |
| P036_right_external.tex | 2 | AB>AC时，D在C外侧；同一长度单位下替代右侧外分结构描述。 | PASS / PASS |
| P036_near_isosceles.tex | 3 | 外分坐标t=r/(r−1)随邻边比变化；替代接近等腰时交点远移的想象。 | PASS / PASS |
| P036_area_from_a.tex | 4 | ABD与ACD共用高AH；替代面积比第一步的空间脑补。 | PASS / PASS |
| P036_area_from_d.tex | 5 | 等距垂线DM、DN及全等直角三角形；替代第二种面积算法的辅助线描述。 | PASS / PASS |
| P036_parallel_proof.tex | 6 | CF平行AD，等腰AFC与相似BCF/BDA；替代构造和对应关系的长段文字。 | PASS / PASS |
| P036_sine_angles.tex | 7 | A处两角互补，D处两射线同向、两角相等；替代并纠正原有错误论证。 | PASS / PASS |
| P036_isosceles.tex | 8 | 内角平分线垂直BC，外角平分线平行BC；替代没有有限交点的边界想象。 | PASS / PASS |
| P036_inner_outer.tex | 9 | 例3同轴显示B,E,C,D、BE+EC与EC+CD；替代内外分点和差结构的脑补。 | PASS / PASS |
| P036_reversed_ratio.tex | 10 | 固定同一三角形，比较正确D与倒置比例产生的D*；替代倒数错误的位置描述。 | PASS / PASS |

所有图以实际坐标绘制，几何坐标只用等比例缩放和平移。主标签为small，无缩字救场。几何图均完整外框275 DPI裁切并按原分辨率逐幅查看；先检查标题与边框净距，再核对点、角弧、垂线、直角标记、延长线、比例尺和标签。每图可从标题及图形直接读出核心关系，图后以短观察取代原有重复文字。
首轮发现并修正AC=3标签压线、θ压住AC、C靠近垂足直角标记、错误模型边长标签穿线、理解说明孤立标题与例1跨页孤行。最终复查未发现重叠、裁切、压线或错误分页。

## 实际执行的检查

- PASS：python -B 09_geometry-plane/P036_external_angle_bisector_ratio/checks/verify_p036.py。读取9幅实际图中的坐标与角弧值，核对边长、外分位置、比例、长度差、垂足、等距、面积比、辅助线平行、AF=AC、内外角平分线垂直及等腰足点。
- PASS：2705组满足三角形不等式的整数边长样例（包含等腰），检查通式、方向、等距与面积关系；三道例题及有向比另用精确分数验证。样例检查是回归核验，不替代正文普遍证明。
- PASS：10幅图全部被六段正文引用并在meta remarks记录用途；JSON可解析，has_diagram和updated_at同步；关联P035、P042目录存在。
- PASS：沿用scripts/build_conclusion_pdfs.py，仅构建P036，使用--overwrite --output-to-conclusion-pdfs --map-json .tmp/P036_review/map.preview.json。
- PASS：同源诊断包装连续两遍XeLaTeX及最后分页修订后的再次编译，最终日志无Overfull、Underfull、Missing character或Warning。
- PASS：pdfinfo确认11页A4（595.28×841.89 pt），无加密。
- PASS：全部11页以200 DPI渲染逐页检查；全部10图以275 DPI完整外框裁切逐幅检查。最终分页修订后重渲染第8、9页，并更新第9页图的275 DPI裁切；其他图位置经bbox比较保持不变。
- PASS：git diff --check。临时渲染、预览映射、诊断包装与日志验收后清理。

## 最终交付

PDF：09_geometry-plane/P036_external_angle_bisector_ratio/pdfs/P036_external_angle_bisector_ratio.pdf
SHA256：b96c15c8b29a2c3ed4fb150371add9bcb8d23bbf867862599072cfe070de40c9
未解决问题：无。本轮止于P036。
