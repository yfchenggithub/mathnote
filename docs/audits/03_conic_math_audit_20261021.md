# 03_conic 数学审计与修复（2026-10-21）

范围：审阅 C001–C083 的核心公式、适用条件和例题，对发现问题的证明及六段正文、元数据进行交叉核对。按用户要求跨 UID 修复；没有执行 Publisher、Sync、APK 构建或 Git 提交。审计不是对所有可能命题、所有实数参数的机器形式化证明。

本轮修改 40 条 UID。下面区分实质错误与条件、术语和表述修正；没有把原本正确的主公式都称为错误。

## 实质计算、公式或证明错误

| UID | 原问题 | 修正与核验 |
| --- | --- | --- |
| C003 | TeX 已正确，但元数据仍写 `tan(θ/2)=c/yP`。 | 同步为 `tan(θ/2)=c∣yP∣/b²`；正文、检索公式及摘要一致。最大焦角为 `2arcsin(e)`。 |
| C008 | 椭圆 `x²/4+y²=1` 的点 `(1/2,0)` 被算成极线 `x=4`。 | 系数为 `(1/2)/4=1/8`，正确极线为 `x=8`，无实切点。 |
| C021 | 证明把 `r1²r2²=a⁴b⁴S²` 中的 `S²` 写成分母；例题切点 `(1,√3/2)` 不在所给椭圆上；元数据的原点距离公式也写错。 | 重写可逐步核算的恒等式 `r1r2=a²b²S`，`d=1/√S`。改用合法切点 `(1,3/2)`，直接算出 `√(r1r2)d=2√3=ab`。 |
| C024 | 周长近似计算与末位舍入错误；把小误差近似说成可作精确式；极扁极限数值不准。 | `(a,b)=(5,3),(10,6),(9,7)` 的近似值保留三位小数分别为 `25.527、51.054、50.462`；`14π/11≈3.99839065`。说明 `b→0+` 的周长极限，保持近似号，不声称有限次检验就是误差界证明。 |
| C032 | 元数据推导中一次项符号为正，与正确圆心矛盾。 | 展开式为 `x²+y²−2a(λ²+1)x/(λ²−1)+a²=0`。 |
| C036 | 证明声称仅由 `a>c` 可保证任意平面点的 `2a−PF2>0`。 | 正性来自原定义 `PF1+PF2=2a`；补充从标准方程返回距离和的逆向验证，排除平方增根。 |
| C038 | 建系说正向从焦点指向准线，却把焦点放在正半轴；例题混用 `4p` 与 `2p`。 | 正向改为准线垂足指向焦点；`x²=4y` 按本章 `x²=2py` 约定应取 `p=2`。元数据区分平移形式与顶点在原点的标准式。 |
| C045 | 检索技巧把椭圆焦点轴判为平方项系数较大者；正文还把两类曲线混用同一正负判断。 | 归一化椭圆：分母较大、即平方项系数较小者对应焦点轴；双曲线看正项变量。 |
| C055 | 元数据称焦点是抛物线的对称中心；又说左开口必改变两个坐标积；证明把设线范围说成所有过焦点直线。 | 抛物线无对称中心；左右开口的 `x1x2=p²/4、y1y2=−p²` 相同，上下开口交换坐标；`x=my+p/2` 覆盖实际两点焦点弦，水平轴线只有一个交点，不在两点弦范围内。 |
| C056 | 在右焦点、正向极轴与 A 沿 θ 方向的条件下，把两焦半径和比例全部倒写；证明中途改极轴强行对应根；三个例题随之出错。 | `AF=b²/(a+c cosθ)`，`BF=b²/(a−c cosθ)`，`AF/BF=(1−e cosθ)/(1+e cosθ)`。例 1 为 `3/7`，例 2 为 `(33−20√2)/17`；例 3 在规定端点方向下斜率 `−√5/2`。未规定端点命名时须讨论两条对称直线。 |
| C059 | 抛物线中斜率为 2 的弦中点轨迹只写 `y=1` 或“一段”；又一概称 `y0=0` 则斜率不存在。 | 实际轨迹 `y=1,x>1/4`，是开射线；有心曲线的中心弦须单独讨论，不能一概判竖直。 |
| C060 | 元数据将 `y0≠0` 解释为弦不水平；部分正文把所有 `y0=0` 情况都判成竖直弦；平行弦中点轨迹说成整条直线。 | 水平弦可以有非零中点纵坐标；非中心且 `y0=0` 才对应竖直弦，中心可对应任意中心弦；实际非退化中点轨迹为开线段。 |
| C061 | 用 `S=x0²/a²−y0²/b²<1` 保证弦存在，并排除了本可存在的同支弦；三个例题的结果均受影响；遗漏竖直弦。 | `y0≠0` 时存在当且仅当 `S<0` 或 `S>1`。由 `S−a²b²S t²=1` 严格推出。原例 1 的 `S=8/9`，无解；例 2 轨迹为 `y=9x/8, ∣x∣>8/√7`；原例 3 亦无解。`y0=0,∣x0∣>a` 可有竖直弦，原点中心弦须 `∣k∣<b/a`。 |
| C062 | 轨迹的排除点被解释为弦不存在，并误称“抛物线段”。 | `(1,0)` 对应实际存在的竖直弦 `x=1`；排除原因是题目限定有限斜率。轨迹 `y²=x−1,y≠0` 向两端无界。 |
| C065 | 斜率和为 3 的另一解写成 `(3,−5/2)`。 | 正确为 `(-3,−5/2)`，与 `(3,5/2)` 中心对称；两解均代回曲线且斜率和为 3。原解关于 x 轴的对称点给斜率和 −3。 |
| C067 | 把“只有一个公共点”当作抛物线切线定义；原重根证明没有排除水平线降次。 | 改用参数导向量 `(t/p,1)`，覆盖顶点切线；展示水平线也可只有一个交点却不相切。 |
| C069 | 例 1 的 `(3,1)` 和例 2 的 `(2,6)` 实际作不出两条实切线，却给出“切点弦”；元数据还把外点的极线称作经过该点的切线。 | 两例分别有 `q=5/4、3>1`，实切点弦不存在，原式只为极线。标准双曲线有两不同有限实切点当且仅当 `q<1 且 q≠0`，渐近线点仅一有限切点，中心无实切线。补充实际存在的两切点例。 |
| C070 | `x²=6y` 的点 `(-1,1)` 在凸侧内部，原题仍称其极线为切点弦；解释还误说切点弦连着外点。 | `x0²−6y0=−5<0`，无实切点弦；极线 `x+3y+3=0` 与曲线无实交点。切点弦连接两个切点，不是连接外点与切点。 |
| C074 | 在 PH 明确指向抛物线开口时，却说切线平分 ∠FPH 内角；还说顶点没有切线。 | 此约定下**法线平分内角、切线平分外角**；反向轴射线才交换角色。用单位方向向量之和证明，并核对椭圆、双曲线、抛物线三幅实际几何图。顶点仍有唯一切线。 |
| C075 | 把所有点都认为具有有限极线，把“曲线外”一概等同两实切点；把极化称作曲线退化。 | 有心曲线排除中心；一般式一次项系数不同时为零。只有两不同有限实切点存在时才称实切点弦；曲线本身未退化。 |
| C076 | 把有二次项、无实奇点或实数不可约等模糊条件当作非退化判据；说退化时交换对称恒等式不成立。 | 用三阶齐次对称矩阵可逆说明非退化；退化可破坏一一配极对应，但双线性交换恒等式仍成立。中心限制明确为有限平面的限制。 |
| C077 | 与 C075 同类的定义域和切点存在性遗漏；例 2 的 `(2,1)` 作不出双曲线实切点弦；外点极线被说成一阶泰勒近似，一次项还允许直接换为 x0。 | 原例 2 `q=11/3>1`，只有极线 `6x−y=3`，无实切点弦。极化应为 `S(P)+(1/2)∇S(P)·(X−P)`，不能混同通常泰勒一次项；一次项须取平均值。 |
| C079 | 一般证明展开交叉项漏掉 b，导致唯一交点坐标式错误；元数据纵轴渐近线互换错误。 | 交叉项为 `2εd x/(ab)`，正确 `x=−a(b²+d²)/(2εbd)`；纵轴渐近线为 `y=±(a/b)x`。用例题 `(-10/3,-4)` 及多组参数回代。 |
| C080 | 证明先设正半轴 A、B，却又令 B² 等于负分母，逻辑矛盾。 | 引入有符号分母 Dx、Dy。双曲线虚半轴平方为 `−Dy>0`，半焦距平方为 `Dx−Dy`；补足同焦点曲线的逆向表示。 |

## 术语、范围和辅助推导同步修正

| UID | 问题与修正 |
| --- | --- |
| C027、C030 | 元数据将 c 称为焦距；改为半焦距，焦距是 2c。 |
| C028 | 元数据写含未定义参数的焦点极坐标式，且角度说明自相矛盾；改为右焦点、正向极轴下 `r=(b²/a)/(1+e cosθ)`，说明弦长只依赖 `cos²θ`。 |
| C034 | 元数据消元步骤在没有 B≠0 的前提下除以 B；补齐消元方向与非零系数要求，区分韦达代数意义和两实交点。 |
| C035 | 元数据把 A≠0 和 Δx>0 当作所有开口、所有两点弦的统一条件；按左右、上下开口区分，明确竖直弦横坐标可能重合。 |
| C044 | 核心公式和摘要未把 e=c/a 限定于椭圆、双曲线；补明抛物线 e=1 由定义得到。 |
| C046 | 通径条件说成垂直于任意坐标轴，双曲线也称长轴；明确椭圆长轴、双曲线实轴、抛物线对称轴。 |
| C048 | “与 a 无关”易被理解为可忽略实际三角形条件，虚半轴与分母也有混称；改为表达式不显含 a，b 为分母平方根，角须来自实际三角形。 |
| C050 | 已知点在曲线上时，横坐标正负确能判断分支，原陷阱表述反而否认；修正为先确认点在曲线上。 |
| C051 | 把 p/2 误称半通径；正确为焦点到顶点距离，半通径为 p。元数据中“距离正就可判断点在内部”的说法也删除。 |
| C053 | 元数据声称倾斜角正弦公式不分开口方向；明确只对左右开口同式，上下开口按 x 轴倾斜角应改为余弦平方。 |
| C054 | 错说左开口的倒数和形式会变化；p 为正焦准距时，四种开口的倒数和均为 2/p，因旋转、反射保持长度。 |
| C058 | 元数据斜率设线证明遗漏通径；改用 x=my+p/2，覆盖所有实际两点焦点弦。 |
| C066 | 元数据说 y0=0 可以把斜率分母“约掉”；改为斜率式不能代零，统一切点式可以。 |
| C073 | 声明缺少两点不同与 M、N 定义；补齐，并以 `(y1−y2)²/(4p)≠0` 保证 MN 确实是非零连线。 |
| C082 | 多处把 c 称作焦距；统一为半焦距，焦距为 2c。 |

## 验证记录

- 独立数学回归：`tests/test_conic_math_audit_20261021.py`，12 组测试通过。重建交点、距离、单位射线与导向量，没有导入现有动画模型。
- 全部 83 个 meta.json 可解析；修复的检索公式与正文重复项同步检查。
- PDF：40 份均已重编译并同步至各 UID 自己的 `pdfs/`，共 295 页；全部以 200 DPI 渲染，未发现非水印文字超出页面边界。
- 既有 GIF、PNG 与冻结 Scene 保留；本轮新增的 TikZ 教学图用于 PDF 数学说明。

复现数学检查：

```powershell
.venv-manim\Scripts\python.exe -B -m unittest discover -s tests -p test_conic_math_audit_20261021.py
```

## 最终本地交付记录

- 数学回归：PASS，12 组独立检查；日志见 `build/math-audit-20261021/math_tests_final.log`。参数抽样检验用于发现反例，与正文中的代数证明互相补充，不把抽样等同于一般性证明。
- PDF 编译与全页技术检查：PASS，40 份、295 页；完整 200 DPI 渲染及逐页文字边界记录见 `build/math-audit-20261021/pdf_technical_qa.json`。原有旋转水印的变换包围盒单独记录，不计作正文溢出。C045、C076 的长公式在视觉检查中发现越界，已改写为中间量或分行并重编译。
- 教学图：本轮新增 31 幅精确 TikZ 图（29 条 UID），分别说明合法切点、焦点弦方向、弦存在域、切点存在条件、轴向约定、内外角平分线、极线和共焦曲线等；用实际曲线、点和射线替代相应位置关系的纯文字说明。300 DPI 外框裁切证据见 `build/math-audit-20261021/figure_qa_300dpi/`。
- 正式本地 PDF：已备份原文件后，将核验版本同步至各 UID 的 `pdfs/<原目录名>.pdf`；逐文件哈希及路径见 `build/math-audit-20261021/final_audit.json`。没有执行发布或同步工具。
- 资源保护：PASS，原有 193 个 GIF/PNG、197 个 Manim Python 文件与任务开始前 SHA-256 完全一致。C056、C074 的旧动画审计记录追加了源文问题已修复的日期说明，保留历史记录。
- 本轮为数学源与本地 PDF 修复；没有重新验收动画。USER VISUAL / ANDROID DEVICE / FINAL FREEZE 仍为 PENDING，未标记 PUBLISHED / SYNCED。

修改范围为上述 UID 的必要六段 TeX、`meta.json`、本地 PDF，以及新增的 `assets/tikz/Cxxx_*` 配图；C030 使用短页眉标题避免与左侧页眉相叠，C074 主标题同步。共享编译器、共享样式、Publisher 与旧 `source.tex` 均未修改。各页经联系表检查，新增主图另以 300 DPI 外框裁切检查；图形与正文条件、标签、坐标及射线方向交叉核对。

- 本地 PDF 视觉检查：PASS（页面联系表与新增主图 300 DPI 外框裁切）；发现的长公式、页眉及图中标签压线问题均已处理，并检查受影响页。40 份目标 PDF 与验收版本逐文件 SHA-256 一致。详细变更文件列表及视觉记录已加入 `build/math-audit-20261021/final_audit.json`。

## 修复后的本地 PDF 索引

| UID | PDF |
| --- | --- |
| C003 | [打开 PDF](D:/mathnote/03_conic/C003_Ellipse_Max_Focal_Angle/pdfs/C003_Ellipse_Max_Focal_Angle.pdf) |
| C008 | [打开 PDF](D:/mathnote/03_conic/C008_Ellipse_Tangent_Point_Formula/pdfs/C008_Ellipse_Tangent_Point_Formula.pdf) |
| C021 | [打开 PDF](D:/mathnote/03_conic/C021_ellipse_tangent_distance_focal_radius_product/pdfs/C021_ellipse_tangent_distance_focal_radius_product.pdf) |
| C024 | [打开 PDF](D:/mathnote/03_conic/C024_ellipse_perimeter_ramanujan/pdfs/C024_ellipse_perimeter_ramanujan.pdf) |
| C027 | [打开 PDF](D:/mathnote/03_conic/C027_ellipse_focal_chord_length/pdfs/C027_ellipse_focal_chord_length.pdf) |
| C028 | [打开 PDF](D:/mathnote/03_conic/C028_ellipse_focal_chord_length/pdfs/C028_ellipse_focal_chord_length.pdf) |
| C030 | [打开 PDF](D:/mathnote/03_conic/C030_ellipse_focal_triangle_perimeter_constant/pdfs/C030_ellipse_focal_triangle_perimeter_constant.pdf) |
| C032 | [打开 PDF](D:/mathnote/03_conic/C032_apollonius_circle_ratio/pdfs/C032_apollonius_circle_ratio.pdf) |
| C034 | [打开 PDF](D:/mathnote/03_conic/C034_line_hyperbola_direct_vieta/pdfs/C034_line_hyperbola_direct_vieta.pdf) |
| C035 | [打开 PDF](D:/mathnote/03_conic/C035_parabola_vieta_fixed_form/pdfs/C035_parabola_vieta_fixed_form.pdf) |
| C036 | [打开 PDF](D:/mathnote/03_conic/C036_ellipse_first_definition/pdfs/C036_ellipse_first_definition.pdf) |
| C038 | [打开 PDF](D:/mathnote/03_conic/C038_parabola_definition_focus_directrix/pdfs/C038_parabola_definition_focus_directrix.pdf) |
| C044 | [打开 PDF](D:/mathnote/03_conic/C044_eccentricity_geometric_algebraic/pdfs/C044_eccentricity_geometric_algebraic.pdf) |
| C045 | [打开 PDF](D:/mathnote/03_conic/C045_conic_standard_forms_focus_x/pdfs/C045_conic_standard_forms_focus_x.pdf) |
| C046 | [打开 PDF](D:/mathnote/03_conic/C046_conic_latus_rectum_length/pdfs/C046_conic_latus_rectum_length.pdf) |
| C048 | [打开 PDF](D:/mathnote/03_conic/C048_hyperbola_focus_triangle_area/pdfs/C048_hyperbola_focus_triangle_area.pdf) |
| C050 | [打开 PDF](D:/mathnote/03_conic/C050_hyperbola_focal_radius/pdfs/C050_hyperbola_focal_radius.pdf) |
| C051 | [打开 PDF](D:/mathnote/03_conic/C051_parabola_focal_radius_coordinate/pdfs/C051_parabola_focal_radius_coordinate.pdf) |
| C053 | [打开 PDF](D:/mathnote/03_conic/C053_parabola_focal_chord_length_inclination/pdfs/C053_parabola_focal_chord_length_inclination.pdf) |
| C054 | [打开 PDF](D:/mathnote/03_conic/C054_parabola_focal_chord_reciprocal_sum/pdfs/C054_parabola_focal_chord_reciprocal_sum.pdf) |
| C055 | [打开 PDF](D:/mathnote/03_conic/C055_parabola_focal_chord_product/pdfs/C055_parabola_focal_chord_product.pdf) |
| C056 | [打开 PDF](D:/mathnote/03_conic/C056_ellipse_focal_chord_ratio/pdfs/C056_ellipse_focal_chord_ratio.pdf) |
| C058 | [打开 PDF](D:/mathnote/03_conic/C058_parabola_focal_chord_reciprocal_sum/pdfs/C058_parabola_focal_chord_reciprocal_sum.pdf) |
| C059 | [打开 PDF](D:/mathnote/03_conic/C059_midpoint_chord_slope/pdfs/C059_midpoint_chord_slope.pdf) |
| C060 | [打开 PDF](D:/mathnote/03_conic/C060_ellipse_midpoint_chord_slope/pdfs/C060_ellipse_midpoint_chord_slope.pdf) |
| C061 | [打开 PDF](D:/mathnote/03_conic/C061_hyperbola_midpoint_chord_slope/pdfs/C061_hyperbola_midpoint_chord_slope.pdf) |
| C062 | [打开 PDF](D:/mathnote/03_conic/C062_parabola_midpoint_chord_slope/pdfs/C062_parabola_midpoint_chord_slope.pdf) |
| C065 | [打开 PDF](D:/mathnote/03_conic/C065_hyperbola_slope_product_constant/pdfs/C065_hyperbola_slope_product_constant.pdf) |
| C066 | [打开 PDF](D:/mathnote/03_conic/C066_hyperbola_tangent_half_substitution/pdfs/C066_hyperbola_tangent_half_substitution.pdf) |
| C067 | [打开 PDF](D:/mathnote/03_conic/C067_parabola_tangent_point_form/pdfs/C067_parabola_tangent_point_form.pdf) |
| C069 | [打开 PDF](D:/mathnote/03_conic/C069_hyperbola_chord_of_contact/pdfs/C069_hyperbola_chord_of_contact.pdf) |
| C070 | [打开 PDF](D:/mathnote/03_conic/C070_parabola_contact_chord/pdfs/C070_parabola_contact_chord.pdf) |
| C073 | [打开 PDF](D:/mathnote/03_conic/C073_parabola_tangent_intersection_midpoint_parallel/pdfs/C073_parabola_tangent_intersection_midpoint_parallel.pdf) |
| C074 | [打开 PDF](D:/mathnote/03_conic/C074_conic_optical_angle_bisector/pdfs/C074_conic_optical_angle_bisector.pdf) |
| C075 | [打开 PDF](D:/mathnote/03_conic/C075_polar_line_equation/pdfs/C075_polar_line_equation.pdf) |
| C076 | [打开 PDF](D:/mathnote/03_conic/C076_pole_polar_conjugacy/pdfs/C076_pole_polar_conjugacy.pdf) |
| C077 | [打开 PDF](D:/mathnote/03_conic/C077_pole_polar_principle/pdfs/C077_pole_polar_principle.pdf) |
| C079 | [打开 PDF](D:/mathnote/03_conic/C079_hyperbola_asymptote_parallel_unique/pdfs/C079_hyperbola_asymptote_parallel_unique.pdf) |
| C080 | [打开 PDF](D:/mathnote/03_conic/C080_confocal_conic_family/pdfs/C080_confocal_conic_family.pdf) |
| C082 | [打开 PDF](D:/mathnote/03_conic/C082_confocal_conic_family/pdfs/C082_confocal_conic_family.pdf) |
