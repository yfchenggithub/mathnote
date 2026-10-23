# C046 圆锥曲线通径验收（2026-10-23）

六段、source.tex、meta.json同步；main.tex加入C046并跟踪。保留正确通径公式，明确弦段、对应轴与半通径，补齐参数正性、双焦点与正负/纵向开口。将原先“长度只与形状有关、与焦点位置无关”的含混说法改为尺寸参数决定长度、平移旋转不改长度。优先直接代焦点坐标三步求端点；新增焦准比加对称性几何证明，绝对值同时覆盖椭圆和双曲线；抛物线以平行线间距与等距定义解释2p。

| 图（assets/tikz/） | 问题与替代文字 |
|---|---|
| C046_three_latus_recta.tex | 整长与半长怎样区分？同尺度三条焦点通径替代乘2提醒 |
| C046_focus_directrix_geometry.tex | 半通径为什么是b²/a？焦准距离与对称弦替代纯代数记忆 |
| C046_latus_vs_oblique_chord.tex | 任意焦点弦都能套公式吗？同尺度同焦点两弦反例 |
| C046_orientation_invariance.tex | 改变开口后怎么算？同p反射/坐标交换替代方向限制 |

数学核验：`python -B 03_conic/C046_conic_latus_rectum_length/checks/verify_c046.py` PASS。216个端点与独立焦准距状态、实际TikZ比较图四端点与主图六端点、三例回验、斜弦长90/17与通径18/5、关联ID通过。正文完整两种证明，数值检查仅辅助验证。

官方单UID构建成功、独立预览映射。最终6页A4，200 DPI完整逐页检查，四图275 DPI全外框逐图检查。移动几何图AH长度标签避免压准线，移动纵向图F标签避免压轴；重编重审第3、4页及两图，第1、2、5、6页与已审版本像素相同。最终两遍XeLaTeX诊断无Overfull/Underfull/Warning/Missing character，无重叠、裁切或压框。

数学 PASS；编译 PASS；逐页视觉 PASS；逐图视觉 PASS。无已知未解决问题。未打包、发布或同步。

PDF SHA256: d1f5e14d0df767671afdd0a7914561b9009314c0f23c6f099ca0e56f3b45821c
