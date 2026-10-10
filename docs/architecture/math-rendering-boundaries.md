# MathNote 数学图像渲染架构契约（Task 13G.0A）

状态：**ARCHITECTURE REVIEW PENDING**。本契约适用于现在及未来所有二级结论 UID；Task 13G.1、13G.2 均须遵守。用户审核后才能宣布 **ARCHITECTURE FINAL FREEZE**。

## 目标与目录职责

一套正式数学知识源，两条独立图像生产线，一个受控的正式资源发布层。两个模块共享知识源和发布目录，不共享彼此的实现或构建过程。

| 位置 | 职责 |
| --- | --- |
| `<UID>/01_statement.tex` 至 `06_summary.tex`、`meta.json` | 正式数学知识源；两个渲染模块只能独立读取，不得擅改。`<UID>` 是任一实际二级结论目录。 |
| `scripts/manim/` | 动态 GIF 的 UID 中立构建、导出、技术验证工具。 |
| `<UID>/manim/` | 该 UID 的动画数学模型、场景与测试。 |
| `scripts/static_cards/` | 未来静态数学卡片的 UID 中立构建、导出、验证工具。当前不创建实现。 |
| `<UID>/static_cards/` | 未来该 UID 的静态卡片模型、布局与测试；可选。 |
| `<UID>/images/` | 审核后显式发布的正式 PNG/GIF 资源；不是临时构建目录。 |
| `<UID>/videos/` | 经单 UID 审核的可选 MP4 分享资源与显式 GIF 关联源登记；不参与静态卡片或 GIF 渲染。当前仅 C002 有正式配套视频。 |

`manim/` 和 `static_cards/` 是平级可选目录。一个 UID 可有其中一个、两个或都没有；任何一方的存在、成功或产物均不是另一方的前置条件。规则不限于 `03_conic`。

## 依赖与技术边界

动态模块可以读取正式知识源，调用自身的 UID 数学模型及 `scripts/manim/` 工具，使用 Manim 等第三方库。静态模块可以读取同一知识源，调用自身模型及 `scripts/static_cards/` 工具，使用 SymPy、Matplotlib、SVG、LaTeX 等第三方库；也可直接使用第三方 Manim 作为独立的静态渲染引擎。模块隔离指代码和构建依赖隔离，不强制第三方技术栈不同。

禁止静态模块导入 `scripts/manim/` 或 `<UID>/manim/` 的内部代码，禁止动态模块导入 `scripts/static_cards/` 或 `<UID>/static_cards/` 的内部代码。禁止通过 subprocess、PowerShell、路径别名等方式跨模块调用构建入口；禁止用既有 GIF、动态 Scene 或既有 PNG 作为另一生产线的构建前提。一个 UID 的私有数学实现不得直接成为另一 UID 的公共库。`scripts/static_cards/` 不得反向依赖任何 UID 私有源码。两条生产线各自的构建、验证、日志、缓存、清理、失败处理和测试入口应独立，不能触碰对方的临时产物。

若确有重复的纯数学模型需要共享，必须先提出架构变更并获用户批准。提案应证明模型与渲染器无关，不含 Manim Scene、卡片布局或生成命令，不依赖任一生产线，并有独立数学测试。本任务不创建公共模型；少量重复代码可以暂留。

## 构建与发布

动态预览以 Task 13F 已冻结的 `build/manim/` 配置为准，不能为本契约修改其行为。静态预览建议独立放在 `.build/static_cards/<UID>/` 或仓库既有受控构建根目录；正式路径由后续任务决定。两条生产线须独立执行、失败、记录、缓存、验证及清理；一方失败不得损坏另一方已生成资源。

流程为：生产源码 → 隔离预览资源 → 数学和图像验证 → 人工审核 → 显式发布到 `<UID>/images/`。默认构建不得直接写 `images/`；文件名冲突须阻止发布或要求明确处理，不得静默覆盖 PNG/GIF。发布前须检查 Publisher 的实际命名和资源契约，不得绕过 `scripts/zhishu/publish.py` 所代表的正式发布链路。现有链路从 UID 的 `images/` 发现 PNG/GIF，预处理时 PNG 转 WebP、GIF 原样保留，再映射为 `resources/images/<UID>/...`；不得因静态模块改变既有 GIF 逻辑 URI。

两个模块须分别验证真实数学模型、图形内容及技术格式。曲线点、切点、焦点、准线、标注距离与角度、坐标变换、参数范围和退化情形应按相应结论核验。渲染成功不能替代数学正确性；数学验证失败不得发布。

Task 14C.MP4.2A 批准单一正式 Publisher：无参数 `build-content` 自动扫描正式知识源中的 `videos/share_assets.json`，始终生成 schema v2 包，默认输出 `build/zhishu-content-package`。有正式视频时在 `resources/videos/<UID>/` 登记 MP4，以独立 `animation-shares.json` 将精确 GIF Asset ID 关联到分享视频 Asset ID；无视频时该文件是空数组，Manifest 中视频计数和哈希集合为空。未登记视频、损坏视频和失效关联使构建失败；已发布视频的移除须显式使用 `--allow-video-removal`。MP4 不进入 `images/`、`knowledge-assets.json` 的图片列表、PDF 或 SearchDocuments。历史 v1 构建只可用于隔离迁移测试。旧版 Sync 只接受 v1，须升级后才能读取新的正式 v2 包；MathNote 任务不执行 Sync。

## 目录示例

```text
03_conic/C001_ellipse_circle_min_max_distance/
  01_statement.tex ... 06_summary.tex  meta.json
  manim/                  # 已有动画源码与测试
  images/                 # 已发布 001.png、002.png、003.png 和两个 GIF，均须保留

03_conic/C051_parabola_focal_radius_coordinate/
  01_statement.tex ... 06_summary.tex  meta.json
  images/                 # 已有正式资源目录；未来静态卡片预设 001.png—003.png，尚未生成
  static_cards/           # 仅在未来静态任务实施时创建
```

## 验证、局限与变更审批

`python -m unittest tests.test_rendering_boundaries` 对当前 Python 导入及 PowerShell/Python 的可静态识别跨模块构建调用执行最小检查；未来新增文件也在检查范围。动态计算的命令、运行时导入、路径别名及外部入口不能仅靠静态检查证明安全，须在代码评审和实际构建中复核。数学正确性另由各 UID 的模型测试和视觉审核负责。

若需突破任一边界，须先指出冲突规则、解释现有架构不能满足的需求、提出至少一种不破坏边界的方案，评估已发布 GIF/PNG 与 Publisher 的影响，列明回归验证，等待用户批准。批准后同步更新本文件、根 `AGENTS.md` 与自动检查。未经批准不得改变目录或依赖规则。
