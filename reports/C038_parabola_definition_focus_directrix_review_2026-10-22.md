# C038 抛物线焦准定义验收（2026-10-22）

数学审计：修正原理解说明“开口朝向准线”的错误，统一为从顶点朝焦点、远离准线；p为焦准距，OF=p/2，标准方程系数2p。明确PH为垂距及PH>0，区分退化点处0/0与e=1。六段正文、source.tex、meta.json同步，main.tex加入C038。

证明采用非负距离等式的一次等价平方（最低计算门槛）；补充垂直平分线构造，说明构造的充分性、必要性与唯一交点。例3保留最小值4，补足取等点P=(1,2)及坐标不等式回验，强调其他定点不能直接照搬取等条件。

| 图（assets/tikz/） | 问题 / 缩短文字 |
|---|---|
| C038_equal_distance.tex | 点到直线怎样量距离？用垂足与两等长线段替代抽象描述 |
| C038_perpendicular_bisector.tex | 等距轨迹怎样构造？用实际交点替代构造脑补 |
| C038_horizontal_openings.tex | 正负号怎样改变水平开口？同尺度替代四形式的横向记忆 |
| C038_vertical_openings.tex | 换平方项后焦准位置怎样变化？同尺度替代纵向记忆 |
| C038_minimum_broken_path.tex | 距离和为何有下界且能达到？以折线拉直替代最值文字 |
| C038_degenerate_focus.tex | 焦点落准线上会怎样？同尺度抛物线/直线替代退化描述 |

数学核验：`python -B 03_conic/C038_parabola_definition_focus_directrix/checks/verify_c038.py` PASS。3216个四方向采样状态、几何构造正交与等距、801个最值采样与精确取等点、退化情形、例题和关联ID均通过。采样为辅助核验，正文给出完整推理。

官方单UID构建成功，预览映射隔离。最终PDF7页、A4。200 DPI全页逐页检查；6幅图均作275 DPI完整外框裁切逐图检查。修正准线标签与y轴标签、线段长度标记、构造线名称与淡色曲线、Q标签与曲线的接近问题后重新构建并检查第1、3、4页及三幅局部图；第2、5、6、7页像素与已审页面相同。两遍XeLaTeX诊断无Overfull/Underfull/Warning/Missing character；无重叠、裁切或压框。

数学 PASS；编译 PASS；逐页视觉 PASS；逐图视觉 PASS。无已知未解决问题。未打包、发布或同步。

PDF SHA256: 50122ee551a44b8fc2f119456cd30dd65aa4ae20cf35ef6ed4d8038a59126403
