# C044 离心率几何定义与代数公式验收（2026-10-22）

六段、source.tex、meta.json同步；main.tex加入C044并跟踪。优先在已知焦准比恒定的前提下选顶点算常数，两段共线距离直接给出c/a，并明确该简法不独立证明恒定性。独立配方证明同时覆盖椭圆及双曲线两支，统一用绝对值并验证准距非零，补全原稿仅称“类似”的双曲线证明。明确圆不适用有限准线模型、抛物线不用c/a、e不定尺寸，以及固定a的椭圆e趋1时是线段极限而非直接变成抛物线。

| 图（assets/tikz/） | 问题与替代文字 |
|---|---|
| C044_same_focus_directrix.tex | 同焦准距离比怎样区分三类？同尺度三曲线及PF、PH替代抽象定义 |
| C044_vertex_ratio.tex | 怎样最快读出c/a？两组共线点替代一般点计算 |
| C044_ellipse_shape_boundary.tex | e与形状及圆边界怎样联系？固定a三态替代形变长文 |
| C044_paired_directrix_example.tex | 准线配错会怎样？实际例题点与两条准距替代对应提醒 |
| C044_same_e_different_size.tex | 同e能定尺寸吗？同坐标的两相似椭圆替代尺度说明 |

数学核验：`python -B 03_conic/C044_eccentricity_geometric_algebraic/checks/verify_c044.py` PASS。2166个焦准比与顶点状态、603个固定焦点准线状态、实际TikZ例题点和形状参数、尺寸缩放、圆边界及关联ID通过。例3补出两个实际点并验PF=4、右准距5、错误左准距20。正文完整证明，数值仅辅助复核。

官方单UID构建成功、独立预览映射。最终6页A4，200 DPI全页检查、五图275 DPI全外框逐图检查。调整分页消除一行文字孤页；移动压曲线或准线的P、F和长度标签，扩大同焦准模型的显示比例，补入顶点图坐标；上移相似椭圆以给图注留空。最终重审第2、3、5、6页及受影响三图，第1、4页与此前已审版本像素相同。两遍XeLaTeX最终诊断无Overfull/Underfull/Warning/Missing character；无重叠、裁切或压框。

数学 PASS；编译 PASS；逐页视觉 PASS；逐图视觉 PASS。无已知未解决问题。未打包、发布或同步。

PDF SHA256: 7c5a6a6037830a7555ec5e5fabb59b0f7ffe313a7eabe06e93f9b592d932153c
