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

## 任务路由：在编辑或构建前读取

| 实际任务 | 必须读取 | 加载边界 |
| --- | --- | --- |
| 六段 TeX、数学结论教学表达、PDF 教学图、PDF 编译或逐页验收 | [PDF 结论完善规范](docs/guidelines/pdf-conclusion-guidelines.md) | 包含单 UID 工作边界、先图后文、R030 特例和交付门槛。 |
| 静态数学卡片 PNG、静态绘图代码及其构建/测试/预览 | [数学渲染架构契约](docs/architecture/math-rendering-boundaries.md)，以及以后该静态模块适用的内部规范 | 仅把六段 TeX 当知识源读取时，不触发 PDF 专属规范。 |
| Manim Scene、动态 GIF 及其构建/测试/发布 | [数学渲染架构契约](docs/architecture/math-rendering-boundaries.md)，并按需读 `scripts/manim/README.md`、`scripts/manim/TASK_13F_FREEZE.md` | 仅把六段 TeX 当知识源读取时，不触发 PDF 专属规范。 |
| Publisher、图像命名/扫描/消费边界或资源发布调整 | [数学渲染架构契约](docs/architecture/math-rendering-boundaries.md)，并核对实际 Publisher 资产契约 | 不能以文档代替现行代码审计。 |
| 普通 `meta.json` 字段维护或其他局部任务 | 只读任务实际涉及的现有规范和文件 | 不涉及 PDF 完善或数学图像生产时，不强制读取上述两份专属文档。 |

路由依据是任务目的和实际修改范围，不是访问过的文件名。例如 C051 静态卡片读取 TeX，不会自动变成 PDF 完善任务。若同一任务也修改 TeX/PDF 内容或 PDF 教学图，须同时读取 PDF 规范；若同时涉及静态或动态生产，也须读取架构契约。任务范围扩大时，在新增编辑或构建前补读相应规范。
