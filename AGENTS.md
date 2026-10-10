# AGENTS.md — MathNote 全局规则与按需加载入口

本文件只规定所有任务共用的边界和规范路由。链接的 Markdown 不会自动加载；开始编辑或构建前，必须按任务目的和实际修改范围主动读取对应文档。涉及多个任务类型时，合并读取其全部适用规范；不能为节省上下文跳过相关强制规则。

## 全局规则

- 数学正确性优先于渲染成功、排版或美化；报告实际验证结果，不得把未执行的检查称为通过。
- 修改前检查相关文件和工作树，保留已有改动，只改任务范围内的内容。
- 默认一次只处理用户指定的一个 UID；跨 UID 操作或全仓库扫描必须得到明确授权。
- 不启动子 Agent，不并行委派，不建议或自动切换模型；模型由用户决定。
- 不擅自批量修改、发布、部署、Git 提交或覆盖正式资源；遵守用户明确指定的范围与授权。
- 不擅自突破[数学渲染架构契约](docs/architecture/math-rendering-boundaries.md)；例外须先向用户说明影响并获得批准。
- 正式六段 TeX、`meta.json` 与已发布资源各有职责。读取正式知识源不等于获准修改它。
- Task 14C.MP4.2A 批准 Publisher 自动发现正式 UID 的 `videos/share_assets.json`，无参数 `build-content` 在 `build/zhishu-content-package` 发布唯一正式 v2 包，视频为空时也保持 v2。历史 v1 仅可在隔离目录用于迁移测试；MathNote 发布不得执行 Zhishu Sync。正式 GIF、数学源、PDF 与冻结 Scene 仍按原规则保护。

## 任务路由：在编辑或构建前读取

| 实际任务 | 必须读取 | 加载边界 |
| --- | --- | --- |
| 六段 TeX、数学结论教学表达、PDF 教学图、PDF 编译或逐页验收 | [PDF 结论完善规范](docs/guidelines/pdf-conclusion-guidelines.md) | 包含单 UID 工作边界、先图后文、R030 特例和交付门槛。 |
| 静态数学卡片 PNG、静态绘图代码及其构建/测试/预览 | [数学渲染架构契约](docs/architecture/math-rendering-boundaries.md)，以及以后该静态模块适用的内部规范 | 仅把六段 TeX 当知识源读取时，不触发 PDF 专属规范。 |
| Manim Scene、数学 GIF、动画分镜与视觉修改，以及其构建/测试/验收/发布 | [数学渲染架构契约](docs/architecture/math-rendering-boundaries.md)、[数学 GIF 视觉规范](scripts/manim/VISUAL_GUIDELINES.md)、[Manim 生产说明](scripts/manim/README.md)、[Task 13F 冻结报告](scripts/manim/TASK_13F_FREEZE.md) | 仅把六段 TeX 当知识源读取时，不触发 PDF 专属规范。 |
| Publisher、图像命名/扫描/消费边界或资源发布调整 | [数学渲染架构契约](docs/architecture/math-rendering-boundaries.md)，并核对实际 Publisher 资产契约 | 不能以文档代替现行代码审计。 |
| 普通 `meta.json` 字段维护或其他局部任务 | 只读任务实际涉及的现有规范和文件 | 不涉及 PDF 完善或数学图像生产时，不强制读取上述两份专属文档。 |

路由依据是任务目的和实际修改范围，不是访问过的文件名。例如 C051 静态卡片读取 TeX，不会自动变成 PDF 完善任务。若同一任务也修改 TeX/PDF 内容或 PDF 教学图，须同时读取 PDF 规范；若同时涉及静态或动态生产，也须读取架构契约。任务范围扩大时，在新增编辑或构建前补读相应规范。

## 数学 GIF 制作规则

- 每条 UID 以自己的正式六段 TeX 和 `meta.json` 为事实源，先做数学审计，再独立建立数学模型与教学分镜。C001、C002、F031、T021 等已有动画只可作工程或视觉参考，不得机械复制其模型、布局或运动；统一视觉语言，不建立固定数学分镜模板。
- 数学坐标、几何关系、函数、参数、轨迹和适用条件由模型决定；视觉调整不得改变数学含义。动画源码与测试归当前 UID 的 `manim/`，正式 GIF 归当前 UID 的 `images/`。
- 复用 Task 13F 冻结的发现、渲染、导出与验证工具；不得为单条 UID 随意修改共享工具。正式资源写入、覆盖与发布遵守架构契约及 Manim 生产说明。
- GIF 验收分别记录数学自动测试与关键状态、真实关键帧、全帧技术检查、教学表达、视觉质量和 Android 真机效果；核对图形、公式、参数与运动轨迹一致。各 Gate 使用 PASS / FAIL / BLOCKED / PENDING，并报告实际证据。
- Android 真机验收由用户确认；未经确认不得标记 Android PASS 或动画 FINAL FREEZE。区分 LOCAL PRODUCTION PASS、USER VISUAL PASS、ANDROID DEVICE PASS、FINAL FREEZE 与 PUBLISHED / SYNCED。
- 未经明确授权，不得覆盖已有正式 GIF、修改其他 UID 的冻结数学资产，或执行正式 Publisher、Content Package、Sync 与 APK 构建/发布。
