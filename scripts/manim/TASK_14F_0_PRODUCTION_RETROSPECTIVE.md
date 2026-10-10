# Task 14F.0 Result — Mathematical GIF Production Retrospective

日期：2026-10-10。范围：已完成动画的证据复盘与 G020 轻量准入；本文是工作方法记录，不是任一 UID 的动画验收、源文冻结或发布许可。

## 1. Pre-flight

- 分支 `main`；开始时 `git status --short` 为空。根 `AGENTS.md`、渲染架构契约、Manim README、Task 13F 冻结报告、视觉规范、Task 14A Backlog 与清单均已检查。
- 核对 C001、C002、F031、T021、R028 的现有源码说明及相关生产报告；读取 G020 的六段正式 TeX 和 `meta.json`。Task 14A 清单是当时的机会审计快照：其 F031、T021、R028 `existing_gif` 空值不能代表今天仍无 GIF。
- 任务说明提及 Task 14D.V；本次在相关仓库文档中未找到独立的 14D.V 验收报告，因此不把它作为可引用的 PASS 证据。
- 本轮只读证据，不运行数学测试、Manim、PDF 编译、GIF 验证、Publisher、Sync 或 APK 构建；以下历史 PASS 均引用原报告，不冒充本轮复测。

## 2. Completed Animation Inventory

| UID | 已有数学模型与有效动效 | 现有正式 GIF |
| --- | --- | --- |
| C001 | 椭圆与圆周距离；半径跨越最近/最远距离阈值时，间隙、切触与交点连续变化；另有最大距离独立动画。 | 2 条，见 [C001 说明](../../03_conic/C001_ellipse_circle_min_max_distance/manim/README.md) |
| C002 | 椭圆到移动直线距离；相离、相切、相交时最小距离变为零，最大距离继续变化。 | 1 条，见 [C002 说明](../../03_conic/C002_ellipse_point_line_distance_extrema/manim/README.md) |
| F031 | 固定区间上移动二次函数对称轴；最近点在端点处换规则，最远端点在中点处换位并列。 | 1 条，见 [14B](../../01_function/F031_quadratic_moving_axis_extrema/manim/TASK_14B_RESULT.md) |
| T021 | 两种正弦曲线平移/横向伸缩路径；中间曲线不同、经调整位移后终点重合，负 `A` 另作翻折。 | 1 条，见 [14C.2B](../../08_trigonometry/T021_sine_transform_shift_order/manim/TASK_14C_2B_VISUAL_POLISH.md) |
| R028 | 贝叶斯诊断例题；从两类原总体筛出 99 与 999 人，合成 1,098 人阳性总体，再形成 `99/1098`。 | 1 条，见 [14E.2A](../../06_probability-stat/R028_bayes_formula/manim/TASK_14E_2A_RESULT.md) |

这些表达方式共享验证和视觉语言，但模型、关键状态、运动及分镜均由各 UID 的关系决定。[Task 14A](ANIMATION_BACKLOG.md) 的 A 类只表示潜在动效增益，不表示数学源或生产已经通过。

## 3. Freeze & Acceptance Status

`PENDING` 表示在所审证据中没有该版本的通过记录；不能由正式 GIF 文件存在、隔离 Publisher 预览成功或较早版本的评价推得通过。

| UID / 当前版本 | 本地数学、渲染与技术证据 | 用户视觉 | Android 真机 | 动画 Final Freeze | 正式 Publisher / Sync |
| --- | --- | --- | --- | --- | --- |
| C001 两条 | PASS：13F 的 5+4 数学回归、隔离重渲与全帧技术检查；完整教学/设备验收不由 13F 宣告 | PENDING：未见明确记录 | PENDING：未见明确记录 | PENDING | PENDING：仅见隔离资源预览 |
| C002 | PASS：13F 的 3 项数学回归、隔离重渲与全帧技术检查 | PENDING：未见明确记录 | PENDING：13F 明示另行验收 | PENDING | PENDING：仅见隔离资源预览 |
| F031 | PASS：14B 数学、真实关键帧、GIF 技术与本地视觉 | PENDING | PENDING | PENDING | PENDING：仅见隔离资源预览 |
| T021 14C.2B | PASS：本地数学 5+6、真实关键帧、全帧技术与本地视觉 | PENDING | PENDING | PENDING | PENDING：仅见隔离资源预览 |
| R028 14E.2A | PASS：本地数学 12+8、19 关键帧、全帧技术与本地视觉 | PENDING：旧版评价不沿用 | PENDING | PENDING | PENDING：仅见隔离资源预览 |

Task 13F 的 **FINAL FREEZE 只属于共享生产基础设施**。[T021 14C.1](../../08_trigonometry/T021_sine_transform_shift_order/manim/TASK_14C_1_SOURCE_FREEZE.md) 和 [R028 14E.1](../../06_probability-stat/R028_bayes_formula/R028_TASK_14E_1_SOURCE_FREEZE.md) 的 **FINAL FREEZE 只属于数学源/PDF**。`images/` 内正式资源的存在也不等于 Publisher、Content Package 或 Sync 已执行。[14D](TASK_14D_DESIGN_SYSTEM_INTEGRATION.md) 的视觉规范处于已集成候选状态，尚未最终冻结。

## 4. Successful Production Practices — Mathematical GIF Production Lessons Learned

1. **模型先于 Scene。** F031 用同一状态驱动曲线、极值标记和端点距离，并用独立候选值计算交叉检查；T021 用点坐标映射同时驱动曲线与跟踪点；R028 用精确 `Fraction` 计数驱动数字和新总体条宽。这让公式、图形和关键状态可以逐项核对。证据：[14B §5、9](../../01_function/F031_quadratic_moving_axis_extrema/manim/TASK_14B_RESULT.md)、[14C.2 §3、4](../../08_trigonometry/T021_sine_transform_shift_order/manim/TASK_14C_2_RESULT.md)、[14E.2 §3、5](../../06_probability-stat/R028_bayes_formula/manim/TASK_14E_2_RESULT.md)。
2. **按认知难点单独分镜。** C001/C002 以阈值和距离连续变化解释几何；F031 以极值点换位解释分段；T021 以双路径的中间差异解释调整后的等价复合；R028 以总体重组解释条件概率分母。复制场景数量、运动或容器布局会丢掉各自最难的一步。证据：上述 UID 说明与生产报告。
3. **检查真实 GIF 关键状态。** F031 的中点并列、T021 的 `(0,1)` 标签、R028 的转场及实际栅格比例都需要看到画面才能判断。模型测试能验证数值，真实关键帧才能核对文字、遮挡、坐标、颜色和“图形是否暗示了另一种关系”。证据：[14B §11–13](../../01_function/F031_quadratic_moving_axis_extrema/manim/TASK_14B_RESULT.md)、[14C.2A §2、6](../../08_trigonometry/T021_sine_transform_shift_order/manim/TASK_14C_2A_RESULT.md)、[14E.2A §2、4–5](../../06_probability-stat/R028_bayes_formula/manim/TASK_14E_2A_RESULT.md)。
4. **视觉层级随阶段改变。** T021 14C.2B 删除持续显示的参数、图例、双路径说明及厚边框，扩大固定坐标区，只在两路会合时展示双路径；数学轨迹保持原模型。下一次分镜时即可安排文字进入与退出，不必先做满屏版。证据：[14C.2B §2–8、12](../../08_trigonometry/T021_sine_transform_shift_order/manim/TASK_14C_2B_VISUAL_POLISH.md)。
5. **复用已冻结的生产工具。** Task 13F 以精确 UID/Scene 发现、`build/manim/` 隔离产物、`source.json` 绑定、显式发布及覆盖保护、全帧技术检查，在 C001/C002 的三条真实 GIF 上验证可重现及资源不被误覆。它证明生产通道可靠，不代替单条 UID 数学、教学或真机验收。证据：[Task 13F §4–13](TASK_13F_FREEZE.md)。

## 5. Rework Cases

- **T021 源文阻塞。** 原文允许 `A<0` 却只乘 `|A|`，把经调整位移的复合误说成一般可交换，并无条件声称两移距不同；14C 用 `A=-2` 反例停止生产，14C.1 修正并冻结源文。见 [14C §2–4](../../08_trigonometry/T021_sine_transform_shift_order/manim/TASK_14C_RESULT.md)。
- **T021 画面标签。** 旧帧的 P 在 `(0,1)`，文字却称“在原点不动”；坐标与轨迹计算通过也没捕获自然语言错误，14C.2A 对实际帧 42 定位并改为“在 y 轴上不动”。见 [14C.2A §2–4](../../08_trigonometry/T021_sine_transform_shift_order/manim/TASK_14C_2A_RESULT.md)。
- **T021 信息密度。** 初版同屏标题、参数、阶段、图例、两条全路径及公式，当前操作不突出；14C.2B 的前后关键帧显示分阶段展示后图形更清楚。见 [14C.2B §2、4、12](../../08_trigonometry/T021_sine_transform_shift_order/manim/TASK_14C_2B_VISUAL_POLISH.md)。
- **R028 源文歧义。** 审计发现先验和、全概率分母、后验和混写，“分母为 1”误读、`P(B)=1` 合法边界与医学检测两类似然措辞问题；14E.1 四处最小修订后才进入动画。见 [源审计 §12–15](../../06_probability-stat/R028_bayes_formula/R028_SOURCE_CONSISTENCY_AUDIT.md)、[14E.1 §4–11](../../06_probability-stat/R028_bayes_formula/R028_TASK_14E_1_SOURCE_FREEZE.md)。
- **R028 过程与图形。** 旧版数值正确，但 99、999 淡出/淡入不足以解释 1,098 的形成；源组等宽条的各自分母也不够显眼。旧正例条的数据宽度正确，边框越过橙紫边界才使可见橙段从 `40/448` 变成 `44/450≈9.78%`。14E.2A 让两个计数徽标连续移动、停留 `99+999=1098`、明确各组分母，并用条外箭头代替越界边框；新稳定帧均为 `40/448`。见 [14E.2A §2–6](../../06_probability-stat/R028_bayes_formula/manim/TASK_14E_2A_RESULT.md)。结果正确并不保证学生看到了结果的形成。

## 6. Root Cause Matrix

| 案例 | 根因 | 最早可发现阶段 | 下一次最小检查 |
| --- | --- | --- | --- |
| T021 负 `A`、位移条件及复合措辞 | 正式条件覆盖的分支未逐项代入，运算组合与可交换性混同 | Source Gate | 用一个负 `A` 反例、`ω=1`/`φ=0` 边界和两条点映射核对源文。 |
| T021 P“在原点” | 字幕手写语义未同模型坐标校验 | 脚本/关键帧 QA | 列出每句点位描述对应坐标，查看首个实际出现该句的帧。 |
| T021 满屏信息 | 分镜未限定每阶段第一焦点及文字退出时机 | Storyboard | 每阶段写一句“当前要看到的变化”，列出同时可见的文字。 |
| R028 三种求和混写 | 概率对象未标明，合法 `P(B)=1` 边界未试 | Source Gate | 分别写 `ΣP(A_i)=1`、`ΣP(B∣A_i)P(A_i)=P(B)`、`ΣP(A_i∣B)=1` 并试 0/1 边界。 |
| R028 1,098 形成不清 | 分镜有终态，无“99 与 999 怎样到达并求和”的可见因果链 | Storyboard / Preview | 在关键状态表中加入“两个数仍可追踪→求和停留→新总体成立”。 |
| R028 可见比例偏差 | 强调边框压到数据条，使栅格覆盖变宽；模型与 Scene 数据宽度本身正确 | Scene 几何 / GIF QA | 检查高亮前后同一扫描线可见分段，并核对条宽来自精确模型。 |
| R028 组间同宽暗示同一分母 | 各源组用象征性等宽容器，但条件率属于不同总体 | Model-to-Visual Review | 在每条百分比旁写明 `99/100`、`999/99,900`；声明源组容器仅为示意。 |

最省返工的前移检查是：**开工前对正式源做参数/边界反例；分镜前画出关键数量如何产生；渲染前逐句核对字幕与模型、逐项核对几何比例。** 它们分别针对源、教学因果链和画面语义，不能合并成笼统的“多测试”。

## 7. Standard Production Workflow

1. **Source Gate：** 审当前 UID 六段 TeX 与 `meta.json` 的结论、条件、示例和动画取值；已有有效 Source Freeze 可引用，只核当前动画依赖。发现阻塞性矛盾就停止动画，另行处理源文。
2. **Value Gate：** 写出静态图不能同样清楚展示的具体变化、对应或因果链；无独立增益则暂缓 GIF。
3. **Model：** 定义对象、参数、状态、不变量、合法边界和关键坐标/数量；Scene 只消费模型。
4. **Storyboard Gate：** 写清每阶段的教学问题、可见动作、当前焦点、关键停留和可能误导的比例/透视/文字。
5. **Mathematical Tests：** 在渲染前核公式、阈值、边界、对应点、守恒或条件分母；适当用独立方法交叉核对。
6. **Production：** 用 Task 13F 冻结工具在隔离 `build/manim/` 中渲染与导出；模型、Scene、测试留在单 UID。
7. **Actual GIF QA：** 核真实关键帧、全转场、标签、比例栅格、循环和全帧技术指标；局部手机宽度预览只算本地证据。
8. **User Acceptance：** 用户看当前版本真实 GIF，按明确问题定向修复；数学、教学、视觉均过关后停止无收益迭代。
9. **Android & Freeze：** 用户确认真机播放、循环、字体、图形、裁切和阅读体验后，才记录该版本动画 Final Freeze。
10. **Separate Publication：** Publisher、Content Package、Sync 独立授权与记录；资源已在 `images/` 不等于已同步。

## 8. Mathematical GIF Pre-render Checklist

以下 18 项在正式渲染前逐项回答“是/否”，否项先处理并记录原因；不增加新的审批系统。

1. 当前 UID、正式标题、六段 TeX 与 `meta.json` 已对应。
2. 动画所依赖的结论、前提与数据已核实，已有冻结证据仍适用。
3. 允许的正负、零值、退化和等号边界已核，未留数学阻塞。
4. 已用一句话写明 GIF 比静态图多揭示的关系。
5. 模型列出对象、参数、状态、不变量及合法区间。
6. 所有关键公式和示例数值由模型导出，Scene 无第二套计算。
7. 临界状态、切换点或条件分母已单独测试。
8. 重要几何坐标、长度、面积、角度或数量守恒已核。
9. 分镜每阶段只有一个主要教学目标。
10. 最难理解的变化在画面中有可追踪的起点、过程和终点。
11. 关键结果的来源可见，尤其合并、投影或变换顺序。
12. 画面不会以等宽、透视或示意形状暗示错误比例。
13. 所有点名、方位、方向、条件和结论文字已同模型逐句核对。
14. 当前操作比辅助说明突出，非当前文字有退出时机。
15. 颜色身份与图形对象跨阶段稳定。
16. 数字、公式和中文在计划的手机显示宽度仍可读。
17. 已列出需要从真实 GIF 核查的关键帧与转场。
18. 已确认隔离构建名、目标资源现状和覆盖授权边界。

## 9. Animation Suitability Criteria

判断单位是**当前 UID 的具体关系**，不能按模块或标题给等级。先问“随时间发生什么数学变化，学生因此多明白哪一步”，再比较准确静态图能否同样表达。

| 价值 | 准入判断 | 已有证据/候选 |
| --- | --- | --- |
| 高 | 连续轨迹、参数跨阈值、极值点换位、投影构造、变换顺序、条件总体重组等过程本身就是结论；可定义并验证关键状态。 | C001/C002 阈值，F031 换位，T021 双路径，R028 总体重组；G020 投影为候选。 |
| 有条件 | 多步推导、公式形变、递推或组合计数；只有动效能清楚呈现依赖或不变量时才做。 | Task 14A 将部分推导归 B 类；须逐条证明比静态分步图多出的信息。 |
| 低 | 单纯公式陈述、简短定义、一次性示意或短文即可讲清；时间轴未增加可验证的数学关系。 | Task 14A 的 C 类建议暂缓。 |

若正式源有阻塞、模型无法验证或运动会制造错误暗示，先处理风险；高价值分类也不自动放行。Task 14A 的 226/199/146 分类与排序是机会筛选，不是生产验收。

## 10. Production Efficiency Recommendations

- 复用有效 Source Freeze 的具体审计结论，逐项核当前动画依赖；不要机械重做已验证的全部审计，也不要借冻结跳过新示例或新边界。
- 在 Scene 前先交付一页关键状态/数值/字幕表。T021 的负 `A` 与 R028 的 99+999 说明源反例和过程草图比完整渲染更早、更便宜。
- 对人数、概率条、几何距离与坐标映射，提前写清“模型值→Scene 长度/位置→预期栅格关系”；渲染后只复核确需栅格才能看出的偏差。
- 自动化负责模型数值、边界、守恒、实际全帧解码、计时/循环及可采样比例；人工负责教学因果、文字语义、透视/比例暗示、视觉层级和 Android 阅读。R028 的边框误差说明两类检查要连接。
- 修订以已定位的问题为目标。达到数学、教学、本地视觉标准后，没有明确收益便停止审美微调；用户和 Android 验收仍独立进行。

## 11. Non-standardization Principles

统一源审计、模型测试、关键帧核对、技术验证、视觉语义与状态记录；**不统一**数学模型、Scene 数量/时长、参数轨迹、画面容器、概率或几何示例、数学高潮及图像布局。C001/C002、F031、T021、R028 的运动对象与教学难点均不同；把任一条的 Scene 作为跨 UID 模板会掩盖新 UID 的条件和误区。详见 [AGENTS.md](../../AGENTS.md) 与 [视觉规范 §14–16](VISUAL_GUIDELINES.md)。

## 12. G020 ANIMATION CANDIDATE ASSESSMENT

1. **正式主题与目录：** [G020 三垂线定理及其逆定理](../../05_geometry-solid/G020_three_perpendiculars/)；标题来自 `meta.json`，不是 UID 猜测。Task 14A 排第 **4**，分类 A，理由是空间斜线在平面中的正射影和垂直关系在固定透视图中容易误读。[Backlog §6–7](ANIMATION_BACKLOG.md)
2. **核心关系：** `PO⊥α` 于 `O`，`P` 在面外，`A∈α` 且 `A≠O`，`l⊂α`；`OA` 是 `PA` 的面内射影，`l⊥OA ⇔ l⊥PA`。本次核对了 [正式陈述](../../05_geometry-solid/G020_three_perpendiculars/01_statement.tex)、[证明](../../05_geometry-solid/G020_three_perpendiculars/03_proof.tex)、[例题](../../05_geometry-solid/G020_three_perpendiculars/04_examples.tex)及其余三段、元数据。
3. **最值得动画化：** 让 `P` 沿过 `O` 的法线移动，`PA` 随之变化而射影 `OA` 保持，必要时显示点积 `v_l·v_{PA}=v_l·v_{OA}`，使正逆命题所依赖的“竖直分量对面内直线点积为零”可见。可采用独立 3D 投影分镜；这是**候选方向**，不是已批准的 Scene 设计。
4. **已知风险：** `l` 必须在 `α` 内、`A≠O`、投影必须落在 `OA` 而非任意线段；透视下的视觉直角不能替代三维向量点积。例题字母可重新映射，但不能混淆面外点、垂足与斜足。当前未见明确源文阻塞，**不等于完整源审计 PASS**。
5. **资源与下一步：** 目录有正式六段、`meta.json` 和 PDF，当前未见 `manim/`、正式 GIF；Task 14A 的无 GIF 快照与现状一致。建议下一任务为**单 UID G020 独立动画生产**，开工首步执行常规 Source Gate 和 3D 点积/投影边界核验；若发现新源文矛盾即停产并另开 Source Audit/修订。现有证据不要求先安排独立修源任务，也不宣告数学源已完整审计、GIF 可发布。

## 13. Evidence & Source References

- 规则与流程：[根规则](../../AGENTS.md)、[架构契约](../../docs/architecture/math-rendering-boundaries.md)、[Manim README](README.md)、[Task 13F 冻结](TASK_13F_FREEZE.md)、[视觉规范](VISUAL_GUIDELINES.md)、[14D 集成](TASK_14D_DESIGN_SYSTEM_INTEGRATION.md)。
- 机会审计：[Task 14A Backlog](ANIMATION_BACKLOG.md)、[逐 UID 清单](ANIMATION_INVENTORY.csv)。清单生成于新动画之前，状态须以较新的生产报告为准。
- 生产与返工：[F031 14B](../../01_function/F031_quadratic_moving_axis_extrema/manim/TASK_14B_RESULT.md)；[T021 14C](../../08_trigonometry/T021_sine_transform_shift_order/manim/TASK_14C_RESULT.md)、[14C.1](../../08_trigonometry/T021_sine_transform_shift_order/manim/TASK_14C_1_SOURCE_FREEZE.md)、[14C.2](../../08_trigonometry/T021_sine_transform_shift_order/manim/TASK_14C_2_RESULT.md)、[14C.2A](../../08_trigonometry/T021_sine_transform_shift_order/manim/TASK_14C_2A_RESULT.md)、[14C.2B](../../08_trigonometry/T021_sine_transform_shift_order/manim/TASK_14C_2B_VISUAL_POLISH.md)；[R028 源审计](../../06_probability-stat/R028_bayes_formula/R028_SOURCE_CONSISTENCY_AUDIT.md)、[14E.1](../../06_probability-stat/R028_bayes_formula/R028_TASK_14E_1_SOURCE_FREEZE.md)、[14E.2](../../06_probability-stat/R028_bayes_formula/manim/TASK_14E_2_RESULT.md)、[14E.2A](../../06_probability-stat/R028_bayes_formula/manim/TASK_14E_2A_RESULT.md)。
- C001/C002 的模型及分镜以各自 UID 的 Manim README 为据；13F 提供其隔离重渲、数学回归、GIF 技术和资源兼容证据。未找到足以替它们宣告用户/Android/动画冻结的记录。

## 14. Scope & Integrity

本任务仅新增本报告。未修改 `AGENTS.md`、视觉规范、Backlog、六段 TeX、`meta.json`、模型、Scene、数学测试、GIF、PDF、共享工具或 Publisher/Sync；未做渲染、发布或 Git 提交。若以后需要全局规范修订，最小建议是在既有视觉规范的验收段补一句“逐帧核对数学字幕语义与实际点位/统计分母”，本任务不直接修改该规范。结束时 `git status --short` 仅显示本报告为未跟踪新文件；48 个相对链接目标均存在，未发现行尾空白。

## 15. Final Status

| Gate | 状态 | 本轮依据 |
| --- | --- | --- |
| A Evidence | PASS | Task 13F、14A、14B、14C、14D、14E 与 UID 记录已核对 |
| B Retrospective | PASS | 五类动画方法与 T021/R028 返工均有实例 |
| C Root Cause | PASS | 七项返工均定位最早发现阶段与最小预防检查 |
| D Workflow | PASS | 十步流程，源、模型、分镜、真实 GIF、用户、设备与发布分开 |
| E Checklist | PASS | 18 项渲染前自查 |
| F Suitability | PASS | 高/有条件/低价值按具体关系判断 |
| G Efficiency | PASS | 复用冻结、前移反例/分镜/比例核验，保留人工验收 |
| H G020 | PASS | 目录、主题、关系、资源现状与条件性下一任务已核 |
| I Scope | PASS | 仅本文档；无构建与正式资源修改 |
| J Evidence integrity | PASS | 本地、用户、Android、动画冻结及发布状态分别记录 |

**Task 14F.0 — MATHEMATICAL GIF PRODUCTION RETROSPECTIVE PASS.**

**PRODUCTION WORKFLOW READY FOR NEXT UID；G020 — NEXT ANIMATION READINESS: CONDITIONAL GO（先完成 G020 常规 Source Gate 与独立数学模型核验）。** 这不表示 G020 数学源已完整审计、动画已制作，或任何待验收 GIF 已 Final Freeze。
