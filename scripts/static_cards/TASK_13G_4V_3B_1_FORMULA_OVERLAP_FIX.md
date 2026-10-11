# Task 13G.4V.3B.1 — C043-002 公式遮挡修复

**状态：`TASK 13G.4V.3B.1 — A/B VISUAL REVIEW PENDING`**

## 1. Pre-flight

- 已读取根 `AGENTS.md`、静态渲染架构契约、静态卡片 README、13G.4V.3B 报告、C043/C051 正式冻结清单以及本次 A/B 源码。只处理 C043-002；架构契约仍为 `ARCHITECTURE REVIEW PENDING`。
- 起始工作树已有上轮未跟踪的 `static_cards_ab_experiment/cards.py`、`build.py` 和 13G.4V.3B 报告；本轮保留这些文件的既有内容，仅做指定位置的局部改动并新增专用检查、构建入口与报告。
- 原始 A/B 图片仍在 `.build/static_cards_ab_experiment/C043/`。其原始 `build_report.json` 将文字重叠标为 PASS，因为旧检查未纳入胶囊背景与 MathText 的碰撞。

## 2. 复现与根因

测量使用 Matplotlib **3.10.9 / Agg / 100 DPI** 的最终渲染器；MathText 字体集为 `dejavusans`，中文标题使用 `C:\Windows\Fonts\Noto Sans SC Bold (TrueType).otf`。下表为左上角原点的实际 artist 显示包围盒，单位 px；Blue/Rose 数值相同。

| 对象 | 修复前 `[左, 上, 右, 下]` | 修复后 `[左, 上, 右, 下]` |
| --- | --- | --- |
| 标准方程面板 | `[58,255,1022,400]` | `[58,234,1022,405]` |
| 胶囊背景 | `[80,266,504,318]` | `[80,238,504,290]` |
| 胶囊标题文字 | `[102,257.453,447.5,302]` | `[102,240.453,447.5,285]` |
| 40pt 公式 | `[85,301.879,657.073,400.121]` | **完全不变** |

旧版胶囊背景与公式包围盒垂直相交 **16.121px**，交叠面积 **6754.699px²**；标题文字与公式包围盒相交 **0.121px**，面积 **41.805px²**。公式还比原面板底边低 **0.121px**。固定位置的 52px 胶囊和约 98.242px 高的 MathText 公式无法在原 145px 面板内保留安全间隔。旧 Typography Gate 只比较文字与文字，未检测胶囊背景，所以出现错误的 PASS。这里的包围盒是渲染器测得的 artist 边界；并非逐像素字形掩码。

## 3. 最小修复与共享布局

- 共享代码中标准方程面板从 `y=255, h=145` 调整为 `y=234, h=171`；胶囊从 `y=266` 上移到 `y=238`，标题回到现有胶囊默认基线。公式仍在 `y=351`，**字号 40pt、内容和横向位置均不变**。
- 修复后胶囊背景到公式的垂直净距为 **11.879px**；标题文字到公式为 **16.879px**；公式到底部面板边界为 **4.879px**。检查阈值分别为 8px、8px、3px。
- Blue/Rose 仍调用同一个 `card_002()`；没有主题专属坐标或配色修改。两版文字布局、数学几何和标签签名一致；数学几何及标签签名还与原始 A/B 构建报告一致。

## 4. Typography 回归

- 新的 C043-002 专用检查登记面板、胶囊背景、标题和 MathText 四个对象，采用最终渲染器的显示包围盒，验证背景/文字到公式的安全间距及公式在面板内的余量。此检查在隔离构建中执行；不扩展成全项目碰撞引擎。
- **正向 PASS：** Blue 和 Rose 的胶囊/公式重叠面积均为 0；公式 40pt；两主题包围盒完全一致。
- **负向 PASS：** 在测试中恢复旧面板、胶囊和标题坐标，两个主题均重现 `−16.121px` 间距，并被新检查以“capsule background / MathText formula”明确拒绝。旧文字检查对同一负例仍返回 0 次文字重叠，证明其覆盖缺口。
- 专用回归测试：**2/2 PASS**。完整数值见 `layout_overlap_report.json`。

## 5. 数学、渲染与手机复验

- C043 模型测试 **7/7 PASS**；构建中既有 11 项模型结论及正式知识源检查通过。公式保持 `x²/a²−y²/b²=1`、`a,b>0`，关系 `c²=a²+b²`；B 仍是辅助矩形角点，不在曲线上、不是焦点；`OB=OF₂` 是等长而非同一线段。
- 两张 PNG 均可解码且为 **1080×1440**，两张 SVG 均可解析。360×480 与 390×520 预览均已生成并人工查看：x²、y² 分子，分式横线，a²、b² 分母以及 `(a,b>0)` 均能完整辨认；胶囊未压住公式。
- 修复前后逐像素差异在两主题中均仅位于 `[x=56..1024, y=232..407]`，即标准方程面板及其抗锯齿边缘。顶栏、几何图、关系说明和记忆区其余像素一致。
- 架构边界测试 **2/2 PASS**。初次在沙箱内执行时，测试自己的 `TemporaryDirectory` 无法写入；改在沙箱外运行后通过。该权限问题未涉及卡片构建。

## 6. 隔离预览与冻结回归

新输出：`.build/static_cards_ab_experiment_fix/C043/`。

| 类型 | 文件 |
| --- | --- |
| Blue | `A_blue/002.png`, `A_blue/002.svg`, `A_blue/002_mobile_360.png`, `A_blue/002_mobile_390.png` |
| Rose | `B_rose/002.png`, `B_rose/002.svg`, `B_rose/002_mobile_360.png`, `B_rose/002_mobile_390.png` |
| 对照 | `ab_comparison.png`, `ab_mobile_comparison.png`, `blue_before_after.png`, `rose_before_after.png` |
| 证据 | `layout_overlap_report.json`, `build_report.json` |

构建前后核对了 **86 个**原始 A/B、Style A、3A 精修和 Style Lab 预览文件的 SHA-256；全部未变。C043/C051 六张正式冻结 PNG 及选型 A-002、3A 精修 002 的既定哈希也保持一致。未发布、未执行 Publisher/Sync、未改数学源或其他 UID。

## 7. 修改文件与待审项目

- 修改：`03_conic/C043_hyperbola_abc_relation/static_cards_ab_experiment/cards.py` 的标准方程模块坐标与对象登记。
- 新增：同目录的 `formula_spacing.py`、`test_formula_spacing.py`、`build_fix.py`；本报告。原始 `build.py`、原始 A/B 图片及上轮报告均未改动。
- 待用户人工审图：确认蓝色与玫红修复版在实际手机上阅读是否舒适，并随后选择主题。**本次仅补上标准方程模块的胶囊背景/公式检查，不代表全项目 Typography Gate 已覆盖所有排版类型。**未进行 Android 真机验收，也未宣布视觉冻结。
