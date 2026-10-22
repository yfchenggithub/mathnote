# C043 双曲线参数关系验收（2026-10-22）

同步六段、source.tex、meta.json；main.tex加入C043并跟踪。优先以平方差配合和差求短焦半径，距离公式平方一次推出关系，替代原两次消根号长推导；另从标准方程构造候选焦点，完整覆盖左右支绝对值与正根验证。辅助矩形明确使用中心至角点的半对角线，角点和虚轴端点均非曲线点。补齐逆向例题中心原点与轴方向条件；开口含义限定为渐近线指向右方的两射线夹角，明确比值b/a与尺度。

| 图（assets/tikz/） | 问题与替代文字 |
|---|---|
| C043_rectangle_diagonal.tex | c对应哪条线？半对角线与辅助圆替代泛称直角三角形 |
| C043_distance_difference.tex | 两距离怎样算？具体焦半径、平方差与和差替代消根号步骤 |
| C043_opening_ratio.tex | 开口由什么决定？固定a三态同尺度替代笼统开阔描述 |
| C043_positive_term_axis.tex | a看正项还是大分母？横纵同尺度反例 |
| C043_confocal_comparison.tex | 同焦点是否同参数？共用坐标与焦点替代两模型脑补 |

数学核验：`python -B 03_conic/C043_hyperbola_abc_relation/checks/verify_c043.py` PASS。2814个双支距离、符号及方程状态，实际TikZ点P和三组焦点坐标、渐近线张角、三例回验、无效参数边界、关联ID通过。正文完整证明，数值采样仅作辅助复核。

官方单UID构建成功、独立预览映射。最终5页A4，200 DPI完整逐页审阅；五图275 DPI全外框逐图审阅。首次审图后将圆图上移以避开说明，调整焦点标签与点标记，曲线范围覆盖标出的P；修正图题“对角线”为“半对角线”。重编重审第1、2、3、5页及对应四图，第4页像素与已审页面相同。最终两遍XeLaTeX诊断无Overfull/Underfull/Warning/Missing character；无重叠、裁切或压框。

数学 PASS；编译 PASS；逐页视觉 PASS；逐图视觉 PASS。无已知未解决问题。未打包、发布或同步。

PDF SHA256: e26ceaf270c56500ebef99ea9aca6875b9bb5b4d7b9433b0dc73ad35268e3a84
