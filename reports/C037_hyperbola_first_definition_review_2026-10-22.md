# C037 双曲线第一定义验收（2026-10-22）

六段正文、source.tex、meta.json 同步，main.tex 加入 C037 标识。

数学改进：明确 0<a<c，实半轴与虚半轴不要求大小顺序；补齐距离差为零的垂直平分线、差等于焦距的含焦点向外射线及超过焦距的空集；修正焦点位置不能单独确定离心率的表述。优先平方差法，保留直接平方法，加入两支分别取正平方根的充分性验证。修正顶点处非退化三角形的误用。三题各有回验，例3以实际坐标证明候选13可以实现。

| 图（assets/tikz/） | 问题与替代文字 |
|---|---|
| C037_signed_branches.tex | 为何必须绝对值？用真实两支距离差替代抽象分支说明 |
| C037_difference_boundary.tex | 差为零或等于焦距是什么？以同尺度轨迹替代边界描述 |
| C037_focus_direction.tex | 正项为何决定实轴？替代分母大小的错误记忆 |
| C037_example_feasibility.tex | 正距离候选都存在吗？两圆相交/分离替代例3脑补 |

数学检查：`python -B 03_conic/C037_hyperbola_first_definition/checks/verify_c037.py` PASS，独立距离模型覆盖3208个双支状态，含顶点、近退化参数；实际图示点的距离、双曲线方程、例题点、边界与关联ID通过。

官方单UID构建成功，独立预览映射；PDF最终6页、A4。200 DPI全部6页逐页检查；四幅图均有275 DPI完整外框裁切并逐图检查。改进例题分页，调整分支标签及横纵对照公式间距后重编、重渲染、重审。两遍XeLaTeX诊断无Overfull/Underfull/Warning/Missing character；最终图文无重叠、裁切或压框。检查期间PDF哈希稳定。

数学 PASS；编译 PASS；逐页视觉 PASS；逐图视觉 PASS。无已知未解决问题。未打包、发布或同步。

PDF SHA256: 92d177467efdd5e868dc31a6c3f9b871d758933b9679a2c37b97f6477556357b
