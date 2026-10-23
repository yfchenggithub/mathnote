# C047 椭圆焦点三角形面积验收（2026-10-23）

六段、source.tex、meta.json同步；main.tex标题加入C047。保留面积公式 S=b²tan(θ/2)，补齐非退化条件、焦点定义、端点延拓，以及固定椭圆的实际范围 0<θ≤2arctan(c/b)、0<S≤bc。将“与a无关”改为公式中不显含a，但角度可达范围受椭圆参数约束。

优先用内切圆、切线长相等及直角三角形正切直接证明；另给余弦定理证明，并用底高公式 S=c|y| 解释最大值。三道例题均核验点的存在性，补充同b不同a时给定角度可能不可达的反例。

| 图（assets/tikz/） | 教学目的 |
|---|---|
| C047_base_height.tex | 同一钝角焦点三角形比较半角公式与底高公式 |
| C047_incircle_proof.tex | 真实内切圆、切点与垂足展示低门槛半角证明 |
| C047_area_angle_range.tex | 同尺度展示退化端点、中间位置与面积最大值 |
| C047_angle_feasibility.tex | 同b不同a比较给定角度是否可达 |
| C047_equilateral_example.tex | 等边焦点三角形核验例题存在性及面积 |

数学核验：`python -B 03_conic/C047_ellipse_focus_triangle_area/checks/verify_c047.py` PASS。2148个独立角度、面积与内切圆半径状态；实际TikZ切点和垂直关系、三例、端点、不可达角度、关联ID及标题标识通过。数值检查辅助核验，正文保留完整证明。

官方单UID构建成功，使用隔离预览映射。最终5页A4，全部页面200 DPI逐页视觉检查，全部5图275 DPI完整外框逐图检查。主图焦点坐标标签压到椭圆边线，改为清晰点名后重编，重新检查最终第1页与主图；其余4页与已审版本像素一致。最终两遍XeLaTeX诊断无Overfull、Underfull、Warning、Missing character，无已知重叠或裁切。

数学 PASS；编译 PASS；逐页视觉 PASS；逐图视觉 PASS。未打包、发布或同步。按用户最新要求，C047提交后停止，不处理C048。

PDF SHA256: ea5a708b132ef50872a957f97821190e54ce1fc82a02961c39ed3050b53fa209
