# Task 14F.1 Result — G020 Independent 3D Mathematical Animation

日期：2026-10-10。目标 UID：`G020`。**G020 3D ANIMATION LOCAL PRODUCTION PASS；USER VISUAL ACCEPTANCE PENDING；ANDROID DEVICE ACCEPTANCE PENDING。** 本报告记录本地数学、三维投影、实际 GIF 和资源预览证据；不宣布动画 Final Freeze，也不代表正式 Publisher / Content Package / Sync。

## 1. Pre-flight 与真实数学身份

- 分支 `main`，开始时 `git status --short` 为空。实际目录为 [`05_geometry-solid/G020_three_perpendiculars/`](../)；`meta.json` 标题为**三垂线定理及其逆定理**。开工前无 `manim/` 或正式 GIF，`images/` 为空；现有正式 PDF 为 6 页 A4、155,687 字节，原文件保持不变。
- 已读根 `AGENTS.md`、渲染架构契约、Task 13F README/冻结报告、视觉规范、Task 14A G020 Backlog、Task 14F.0 及其 18 项清单。六段正式 TeX 与 `meta.json` 均全文核对。Task 14A 将 G020 排第 4、分类 A，理由是空间斜线与面内射影的垂直关系难由固定透视图读准。
- `check_env.ps1` 实际返回 Environment PASS：Python 3.14.3、Manim 0.21.0、Pillow 12.3.0、FFmpeg、TeX 与 Microsoft YaHei 可用。Manim 提供 `ThreeDScene`、`ThreeDCamera.project_point`、固定朝向文字与摄像机能力；本次实际使用 Cairo 渲染三维世界点/线和平面、固定摄像机及混合数学文字。
- 编辑前记录 34 个保护文件 SHA-256 于 `build/manim/G020/14F_1/protected_baseline.json`：G020 原有 10 文件、C001/C002/F031/T021/R028 既有 GIF、共享 Manim 文件、根规则/架构及图像资源工具。其他 UID 与 App/Publisher/Sync 以 Git 改动范围追加核查。

## 2. G020 SOURCE MATH GATE — PASS

正式条件：`PO⊥α` 于 `O`，`P` 在平面外，`A∈α` 且 `A≠O`，`l⊂α`，`OA` 为 `PA` 的正射影。正式结论：`l⊥OA ⇔ l⊥PA`。`01_statement.tex`、`03_proof.tex` 与 `meta.json` 对此一致；三个正式例题分别在正方体、三棱锥、正三棱柱中使用该射影垂直转化，并未给本动画增加新条件。`02_explanation.tex` 和 `06_summary.tex` 的点积与条件说明也相容。

`05_traps.tex` 对“射影”的一处口语化解释不够严整；本 Scene 只采用正式陈述和“整段 `PA` 的正射影是 `OA`”的明确定义，不引用该短句作为字幕。没有发现阻止本次坐标建模的实质矛盾。本任务未修订 TeX、`meta.json` 或 PDF。开工前的条件性准入已通过本次实际依赖的 Source Gate，但不把它记为独立的数学源 Final Freeze。

## 3. 动画价值与独立三维模型

**教学目标：** 学生看见斜线 `PA` 的高度分量对任一面内方向无点积贡献，因此 `l` 对斜线是否垂直，由斜线在平面的影子 `OA` 决定。动画先把 `l` 转到垂直于 `OA`，再抬高 `P`；斜线明显改变，射影和两条垂直关系保持。它展示了一张静态透视图难同时呈现的变化与不变量，不以环绕镜头代替教学动作。

[`math_model.py`](math_model.py) 用 `α:z=0`、`O=(0,0,0)`、`A=(a,0,0)`、`P=(0,0,h)`（`a>0,h>0`），演示取 `a=2.8`、`h:1.6→3.0`。面内 `l` 为过 `A`、方向 `d=(cos θ,sin θ,0)` 的直线，`θ:48°→90°`。令 `AP=A-P=(a,0,-h)`、`OA=(a,0,0)`，则

`d·AP = a cos θ = d·OA`。

因此正向与逆向均由同一个等式得到；`θ=90°` 时两者同为 0，与 `h` 无关。`P` 投到 `O`，`PA` 上任意分点 `P+t(A-P)` 投到 `tA`，故整段斜线的正射影确为 `OA`。这里特选 `l` 过 `A` 以让图中空间交点真实且直观；正式定理并不要求 `l` 过 `A`。`a=0` 会使 `OA` 退化、`h=0` 会使 `P` 不再位于面外，模型均拒绝；近边界正值和非垂直角度也已测试。

Scene 只从 `G020State` 获取世界点、线、分点投影和真实直角标记。平面矩形边界、字标偏移与颜色只用于表现，不另造数学点位。模型不导入 Manim，也不含摄像机、颜色或字体。

## 4. 分镜、18 项清单与三维附加 Gate

[`storyboard.md`](storyboard.md) 在渲染前确定五阶段：建立空间对象 → 显示整段正射影 → 面内 `l` 转至垂直 → 抬高 `P` 而射影不变 → 双向结论与回环。首次 `θ=90°` 和抬高后的不变量是两个关键停顿；摄像机全片固定，所以学生不会把镜头运动误认成对象运动。各阶段记录了数学问题、世界状态、运动、标签及可能误解。

[`pre_render_gate.md`](pre_render_gate.md) 在正式渲染前逐项记录 Task 14F.0 的 **18/18 PASS** 与 G020 三维附加 **6/6 PASS**，无 N/A；其中计划手机可读性和真实 GIF 遮挡仍由渲染后实际画面复核。使用原清单，没有建立第二套全局流程。

## 5. 数学测试与独立性

运行 `python -B -m unittest discover -s 05_geometry-solid/G020_three_perpendiculars/manim -p test_*.py -v`：**11/11 PASS**。原模型 9 项覆盖正式前提、初态、整段投影、`θ` 与 `h` 的中间状态、两方向真假、相关退化、刚体换基、模型生成的真实直角及最终标签状态；追加的两项使用 Manim 的实际 `ThreeDCamera.project_point` 检查三个观察角的可见点分离和正式取景边界。

关键预期值独立由坐标展开 `AP=(a,0,-h)` 与 `d=(cos θ,sin θ,0)` 得到 `a cos θ`，不是拿模型函数输出自身作期望。浮点检查采用约 `10⁻¹⁰` 的零值判定及明确的小数位断言，没有放宽到能吞掉非垂直情形。摄像机测试不拿二维屏幕角作为数学证明；换视角后世界点积保持不变。

## 6. 3D Scene、摄像机与二维投影

[`scene.py`](scene.py) 定义唯一直接 `ThreeDScene` 子类 `G020ThreePerpendiculars`。正式镜头固定 `φ=45°`、`θ=-35°`、`zoom=1.4`、中心 `(1.6,0,0.2)`：保持 `P/O` 高度分离，又让 `OA`、`l` 和 `PA` 有可辨形状。实际关键帧中 `P`、`O`、`A` 未重合，`l` 与 `PA` 的交点是真实的 `A`，没有把仅由透视产生的交叉标为数学交点。半透明平面提供深度线索，`PO` 与投影辅助线为虚线，`OA/l/PA` 保持各自颜色身份。

右角标记的三个世界角点来自模型中的实际单位方向，而非屏幕量角；非垂直初态不显示标记。Camera QA 将同一 `h=3,θ=90°` 世界状态投到正式斜视、近俯视和侧视三个诊断帧：`diagnostic_oblique.png`、`diagnostic_near_top.png`、`diagnostic_side.png`，及坐标/点积记录 [`qa_metrics.json`](../../../build/manim/G020/14F_1/qa/qa_metrics.json)。三个视角中世界点积均约 `1.7×10⁻¹⁶`；正式斜视的 `P/O`、`A/O` 投影间距分别约 3.25 与 3.15 场景单位，近俯视为 1.52 与 3.78，侧视为 3.94 与 1.54。诊断图只检查空间事实和相机误导，不代替正式 GIF 帧。

## 7. MP4 / GIF 实际生产

用未修改的 Task 13F `render.ps1` / `export_gif.ps1`，指定 `-Uid G020 -Scene G020ThreePerpendiculars -SceneFile scene.py -Name three_perpendiculars -BuildRoot build/manim/G020/14F_1`。隔离 MP4 在 `build/manim/G020/14F_1/G020/three_perpendiculars/three_perpendiculars.mp4`：**576×1024、24 FPS、370 帧、15.416 秒**（`ffprobe`）。最终候选 GIF 同目录：**576×1024、185 帧、164 个不同解码帧、15.41 秒、80–90 ms/帧、无限循环、1,503,382 字节**。

第一版真实接触表暴露阶段文字字形变换中的散乱字符与图形偏小；后续只调整 UID-local Scene 的阶段淡出/淡入、固定镜头取景和平面示意边界，再重渲染复核。中间候选保留在隔离构建目录，不是正式资产。最终候选及正式 GIF SHA-256 均为 `95a89823e80f8fb7c94b68f1507b9598c21cd932c6ec043b488f77443799eb3d`。

## 8. 真实关键帧、教学与视觉验收

[`qa.py`](qa.py) 从**最终实际 GIF** 解码全部 185 帧，保留帧 0、10、18、29、39、50、62、75、87、100、116、129、144、159、184 的全尺寸 PNG 和 [`contact_sheet.png`](../../../build/manim/G020/14F_1/qa/contact_sheet.png)。实际检查了开场、投影线、转动中间及首个真直角、抬高前/中/后、空间直角、公式和循环末帧。关键 P/O/A 点位、线段/影子对应、两个真实右角、字幕进入与退出、图形遮挡和回环均与模型及分镜一致。切换帧 62 的文字在淡出阶段较浅，没有旧版字符叠加；画面中核心几何始终可见。

实际帧 0、75、144 的 360×640 缩小图保存在 `qa/phone_360_frame_*.png`：标题、阶段语、结论公式和 P/O/A 可辨，本地没有观察到数学对象或公式裁切。平面是无限平面的有限示意片，边界在个别帧靠近画幅左缘；关键点、线段及数学标签均未越界。此为**本地手机宽度预览，不是 Android 真机验收**。

教学复核：学生能看到多个斜线内点竖直落到 `OA`；`l` 转到面内真垂直后，`P` 抬高而 `OA` 不动；结论在两真实关系同时显示时才出现。若只看首尾静态帧，会丢失这一“高度变化但垂直不变”的过程。视觉规范本地评分：数学图形 22/25、层级 18/20、字体/公式 17/20、颜色 14/15、运动与停顿 9/10、整体 8/10，**88/100**。扣分主要是 360 px 下点标签偏小、空间透视要求读者跟随投影虚线；没有以分数替代数学或用户验收。

## 9. GIF 全帧技术检查

冻结的 `verify_gif.py` 对候选和新增正式文件均返回 `valid=true`，尺寸/帧数/时长/循环/多帧运动与黑帧合格。独立 Pillow QA 扫描 **185/185**：空白帧 **0**，出现深色内容触及抽样 3 px 边框的帧 **0**；首尾帧平均绝对通道差 **0.304/255**，视觉构图一致。接触表及全尺寸关键帧未见异常透明、深度顺序突变、对象无因消失或明显调色板失真。上述自动指标不证明教学价值，故另做第 8 节人工检查。

## 10. Publisher 隔离预览与正式新增

候选拷贝与新增正式 `images/` 文件分别用现有 `scripts/zhishu/prepare_knowledge_images.mjs` 在 G020-only 隔离目录预览。两次均仅发现一条资源 `images/G020/g020_three_perpendiculars.gif`，保留 **185 帧、15,410 ms、无限循环**，源/输出 SHA-256 全等于上述候选哈希；没有转换成 WebP。正式来源的 manifest 在 `build/manim/G020/14F_1/publisher_preview_formal/output/manifest.json`。

本地阻塞 Gate 通过、目标名不存在且 34 个保护哈希未变后，调用 Task 13F 的 `export_gif.ps1 -Publish -AssetName g020_three_perpendiculars.gif`，**仅新增** [`images/g020_three_perpendiculars.gif`](../images/g020_three_perpendiculars.gif)，没有使用 `-Overwrite`。正式文件独立 `verify_gif.py --width 576 --height 1024` 再次通过，并与候选字节相同。本次没有执行正式 Publisher、Content Package、Sync、App 修改、APK 构建或 Git 提交。

## 11. 冻结资产、修改范围与限制

发布前后重新逐项比对 34 个基线文件：**0 改动、0 缺失**，包括 G020 原有正式源、元数据、PDF，五条既有 UID 的 GIF，Task 13F 工具、视觉规范和 Task 14F.0 文档。`git status --short` 仅出现 G020 的 `manim/` 与 `images/` 新增目录；其他 UID、共享工具、Publisher/Sync 与 App 文件没有工作树改动。

本轮新增 UID-local `math_model.py`、`test_math_model.py`、`test_camera.py`、`storyboard.md`、`pre_render_gate.md`、`scene.py`、`qa.py`、本报告和一条正式 GIF；MP4、候选 GIF、关键帧、接触表、三视角诊断图、测试/技术证据与隔离 Publisher 预览位于忽略的 `build/manim/G020/14F_1/`。

已知限制：用户尚未验收当前 GIF，Android 真机播放、页面裁切与实际阅读体验仍待用户确认；视觉规范自身也尚未全局 Final Freeze。动画示例选 `l` 过 `A` 以突出交点，不能误读为正式定理对 `l` 的附加限制。

额外运行仓库的 `tests.test_rendering_boundaries`：其中 `test_current_production_sources` **PASS**；另一项 `test_guard_detects_cross_import_and_build_call` 的临时目录夹具在当前 Windows 沙箱中两次因 `PermissionError` 终止，完整测试套件记为 **BLOCKED**，不称通过。该错误发生在夹具创建临时文件阶段，尚未执行其断言；G020 的数学与摄像机 11 项测试已独立通过。

## 12. Acceptance Gates 与最终状态

| Gate | 状态 | 实际证据 |
| --- | --- | --- |
| A Pre-flight | PASS | `main` 干净工作树、真实目录、PDF/资产、环境和保护基线 |
| B Source Math | PASS | 六段/元数据及动画所需条件、证明、例题核对 |
| C Animation Value | PASS | 转动 `l` 与抬高 `P` 显露不变的正射影和垂直 |
| D 3D Model | PASS | 独立 UID 模型、合法参数与投影定义 |
| E World Geometry | PASS | 点积恒等式、投影和真实直角；11 项测试 |
| F Camera / 2D Projection | PASS | 实际摄像机投影测试与正式关键帧 |
| G 18-item Checklist | PASS | 渲染前 18/18 加三维 6/6 |
| H Storyboard | PASS | 先于渲染的五阶段独立分镜 |
| I Mathematical Tests | PASS | 11/11，包括中间运动、边界和摄像机 |
| J 3D Scene | PASS | 单 UID、模型驱动、固定镜头 |
| K MP4 / GIF | PASS | 370 帧 MP4、185 帧正式 GIF |
| L Actual Keyframes | PASS | 15 个真实关键帧、全尺寸复核 |
| M Multi-view | PASS | 同一世界状态的斜视/近俯视/侧视诊断 |
| N Teaching Value | PASS | 投影对应、真垂直和抬高后的不变量可见 |
| O Visual Quality | PASS | 实际帧与 360 px 预览，本地 88/100 |
| P GIF Technology | PASS | 正式 185/185 解码、无黑/空帧、循环与首尾正常 |
| Q Isolated Publisher | PASS | 候选/正式来源各 1 资源，哈希/帧/循环一致 |
| R Frozen Assets | PASS | 34/34 保护文件不变，Git 改动限 G020 新文件 |
| S User Visual | PENDING | 用户尚未检查当前正式 GIF |
| T Android Device | PENDING | 尚无用户确认的真机播放 |

**Task 14F.1 — G020 3D ANIMATION LOCAL PRODUCTION PASS。**

**USER VISUAL ACCEPTANCE PENDING。ANDROID DEVICE ACCEPTANCE PENDING。G020 MATHEMATICAL ANIMATION FINAL FREEZE PENDING。** 正式资源已新增，但 Publisher/Content Package/Sync 仍是单独发布状态。
