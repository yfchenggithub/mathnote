# Task 13G.4V.3D — C043 Rose Premium 最终 QA 与发布准备评估

日期：2026-10-12（Asia/Shanghai）。范围：仅 C043 的 Rose Premium 001/002/003 候选卡。**最终结论：CONDITIONAL；CONTENT REVIEW BLOCKED；DEVICE VALIDATION PENDING。**本报告完成审计，不授权图片修订、正式覆盖或发布。

## 1. Pre-flight

已读取根 `AGENTS.md`、数学渲染架构契约、静态卡片 README、C051/C043 冻结报告、13G 阶段评估、3B.1 遮挡修复报告、3C 三卡报告、C043 六段 TeX 与 `meta.json`、C043 模型/测试、Rose 源码与构建报告，以及现行 Publisher 代码和资产契约。开始时 `git status --short` 为空。架构契约仍为 **ARCHITECTURE REVIEW PENDING**。

测试/转换前在 `.build/static_cards_rose_release_qa/C043/preflight_hashes.json` 保存 212 个相关文件的 SHA-256，包括 3C 的 172 个受保护文件、Rose 候选图和源码、C043 正式 PDF、Publisher 关键文件。3C 的保护范围包括 V2、Style A、Style A 精修、Style Lab、原 A/B、修复 A/B、Task 13F 源及冻结 GIF。C043 正式 PDF 实际位于 `pdfs/`，本次已纳入额外快照。

## 2. Rose Premium 基准核验

| 卡 | 1080×1440 PNG SHA-256 | SVG SHA-256 |
| --- | --- | --- |
| 001 | `664a198eeadc61123d40fa37949494b3d26f95972a0b47bd2ed2c12168da4baa` | `3c405c2941b44f9f7af37b94c6447489b609b5e2094b8bd7cca21efb4528c6ce` |
| 002 | `85096655f6ff7036c5a0e72a8cbbdb2b805839c2f887714f70cadf00d4552be8` | `891c6c22f39ed4607f482518e6baf18c52527298ad57bf50a64895e6425508fa` |
| 003 | `724dfdf423d098d6911d44590759e9fb9ef09613b76c36677bea1c159d07a99f` | `57279236d82a05001dddc9636667f7f7499cb2eeaed176c045fdcb5f7b329087` |

三张 PNG 可解码、尺寸正确；三张 SVG 可解析。六张手机图与 `build_report.json` 记录哈希一致，360px 为 360×480，390px 为 390×520。两张三卡联系表可解码。最终 `002.png`、SVG 和两张手机图均与 `.build/static_cards_ab_experiment_fix/C043/B_rose/` 中已选版本逐字节一致；002 PNG 符合用户给定固定哈希。所有候选文件在本任务内保持原字节。

## 3. 数学逐卡终审

| 卡 | 结果 | 逐项核对 |
| --- | --- | --- |
| 001 快记 | **MATH PASS** | 横轴型 `x²/a²−y²/b²=1`，`a,b>0`，`c²=a²+b²`；`a` 实半轴长、`b` 虚半轴长、`c` 半焦距且 `c>0`。图中 O=(0,0)、A=(3,0)、B=(3,4)，OA⊥AB，OA=3、AB=4、OB=5=c；B 代入方程左边为 0，不在双曲线上，且 B≠F₂=(5,0)。蓝/青绿/琥珀三边与 a/b/c 标签对应。|
| 002 快懂 | **MATH PASS** | 方程与正参数条件正确；两分支分别在 x≤−a、x≥a，A=(a,0)、F₂=(c,0)、B=(a,b)，OB 与 OF₂ 的长度均为 c，但位置不同。B 是辅助矩形角点，既不在曲线上也不是焦点。图中未绘制渐近线，故“渐近线图面验收”不适用；其模型关系由 C043 测试覆盖。|
| 003 快用 | **MATH PASS** | `9x²−16y²=144` 除以 144 得 `x²/16−y²/9=1`；`a²=16,b²=9,a=4,b=3,c=√(16+9)=5`。焦点 `F₁=(-5,0),F₂=(5,0)`，渐近线 `y=±3x/4`；正项指向 x 轴。c 是半焦距，完整焦距为 10。无几何图区，**GEOMETRY ASSOCIATION — NOT APPLICABLE**。|

上述结论结合正式六段 TeX、`meta.json`、实际卡面、当前模型计算和可见图核对；并非仅依据旧测试结果。三卡都明确针对横轴型标准式，未把公式错误推广到非标准形式。002 中 `OA=a, AB=b, OB=OF₂=c` 使用了几何中以线段符号表示长度的常见约定；其底部说明对“不同线段”的表达仍需修订，见下节。

## 4. 文案与数学措辞终审

两处属于准确性与术语问题，数值公式和图形本身正确。正式六段 TeX 的直觉段也有“c 是斜边”式比喻，但正式条件、结论和 `meta.json` 明确 c 为**半焦距长度**。卡面应避免把长度参数直接说成线段。

| 卡 | 现有可见文字 | 最简建议 | 影响与处理 |
| --- | --- | --- | --- |
| 001 | `c 是辅助直角三角形的斜边。` | `c 是辅助直角三角形的斜边长。` | 补一个“长”，明确 c 是长度；数学模型不变，底部文案需要重渲染并复测版面。|
| 002 | `斜边与半焦距等长，` / `但它们不是同一线段。` | `OB 与 OF₂ 等长，` / `但不是同一条线段。` | “斜边”指代不够明确，“半焦距”是长度量，而“同一线段”比较对象应是 OB 与 OF₂。建议显式点名两条线段；保留两行结构，但需要重渲染和人工复审。|

002 关系区已写明 B 不是焦点，图上 B 与 F₂ 分离，因此当前文案尚未构成错误的几何结果；但按本任务要求的出版级严谨性，以上两处均应在正式发布前修订。**CONTENT CHANGE APPROVAL REQUIRED；CONTENT REVIEW BLOCKED。**本任务未改文字、未重渲染，也不能沿用这次视觉 PASS 为未来修订版的视觉 PASS。若用户决定保留原文，应明确承担此术语歧义并记录书面审稿决定。

## 5. Typography 与图形终审

本轮 Rose 专项测试对现有源码在 Matplotlib 最终 renderer 下重新测量，已存构建报告的 artist 显示坐标与当前输出哈希一致。001/003 所有登记的胶囊/公式区域通过位置、边界和文本碰撞门：001 标准式胶囊到分式净距 **8.895px**；003 题目 **8.250px**、标准式 **9.113px**，其余注册公式间距更大。已选 002 的独立回归重新测得标准方程胶囊背景到 MathText **11.879px**，文字到公式 **16.879px**，公式到底边 **4.879px**，背景与标题重叠面积均为 0。3B.1 负例恢复旧坐标时会被拒绝；Rose 专项负例移动 001/003 胶囊也会被拒绝。

001 的 O/A/B/a/b/c 六个图内标签、002 的七个图内标签均登记并通过 coverage、collision、association；001 的 a→OA、b→AB、c→OB 明确核对。文字互撞计数三卡均为 0，边界检查 PASS。人工查看 PNG、六张缩放图和三张 WebP：分式分子/分母、根号、±、F₁/F₂ 下标、重点公式及底部记忆文案无可见裁切或缺字；001 点位和直角、002 曲线与点位归属可辨。局部装饰 patch 的每种潜在接触不由语义标签门穷尽，人工审图已覆盖当前成品。

## 6. 视觉与移动端

用户对现有三卡联系表的**图片视觉审核 PASS**。本轮三卡 PNG、SVG、手机图与已审核构建报告和选定 002 基准一致，因此该历史审图结论适用于**当前未修改的图**。逐张查看 360px 与 390px：三卡公式、点位、线段颜色、下标、底部文字均可辨；001/003 的既有 renderer 测量记录为 360px 等比缩放下必要文字最小包围盒高度 15.33px。WebP quality 85 隔离转换后，肉眼未见明显文字或曲线压缩伪影。**模拟手机图片 PASS；Android 真机 PENDING。**

用户真机验收清单：

1. 用相册/普通图片查看器按实际显示比例看 001：核心公式、O/A/B/a/b/c、参数定义、底部两行均无需频繁放大。
2. 看 002：标准分式完整，O/A/B/F₂ 可分辨，蓝色曲线、绿色直角边、橙色斜边可分辨，底部两行舒适阅读。
3. 看 003：原题、标准式、根号、焦点下标与正负号无歧义，黄色结果框及方法文字清楚。
4. 连看三卡：主题统一，玫红和浅粉长时间阅读舒适。记录设备、屏幕/缩放状态、结果与截图。

相册通过仍不等于知树 App 内显示/交互通过；后者须待未来正式集成后单独验收。本次无可用真机实测证据。

## 7. Publisher 隔离兼容性

已审计现行 `prepare_knowledge_images.mjs`、`asset_preparation.py`、`runtime_mapping.py`、`content_package.py`、`publish.py` 与 Publisher README。只将 Rose 三张 PNG **复制**到 `.build/static_cards_rose_release_qa/C043/source_png/`，用当前 Node worker 在同一隔离根目录生成 WebP；没有调用正式 `prepare-assets` 或 `build-content`。参数：Sharp **0.34.5**、WebP **quality 85**、最大宽 1440、不放大、保留纵横比。三张 WebP 均解码为 1080×1440，源/输出哈希与 worker manifest 一致，方向正确。

| 卡 | PNG 字节 | WebP 字节 | WebP SHA-256 |
| --- | ---: | ---: | --- |
| 001 | 160202 | 75774 | `52ba8ec27ac593c6b7b0034004b40e4988d495d571b44d9a9a52b54ae696e45a` |
| 002 | 171565 | 82450 | `ef51f7574c9907ef16a324ec4987c600f3d206ce0a35958d6b021172a91db52c` |
| 003 | 189691 | 89878 | `fce76c3b0c0ef2c422e592b7a1b504810d5dee8ff2d74b7687762975b2fa9165` |

用现行 `map_runtime` 构造**只含 C043** 的发现结果，读取隔离 WebP：**3 图片 Asset + 1 既有 PDF Asset**、错误 0、警告 0。图片 ID 为 `C043:image:001.webp` 至 `003.webp`，URI 为 `resources/images/C043/001.webp` 至 `003.webp`，sortOrder 为 10/20/30。详情见隔离 `publisher_dry_run_audit.json`。当前正式 Publisher 只发现 `<UID>/images/`；那里仍是 V1，故**未构建含 Rose 的 Content Package**，也未验证完整包、Sync 或 App。按现行契约，正式包固定 schema v2；旧 Zhishu Sync 接受 v1，不能把它列作已通链路。

## 8. V1 → Rose 迁移方案与回滚

| 方案 | 冻结/兼容性 | 成本与回滚 | 结论 |
| --- | --- | --- | --- |
| A 受控替换 | 正式 `C043/images/001.png`—`003.png` 与 V1 路径冲突；替换前必须有独立 V1 备份、六位哈希清单、用户批准及新冻结记录。同名 WebP 维持同一 Asset ID/URI，内容哈希和包版本会变；App/缓存更新行为尚待实际验证。 | 现行 Publisher 路径可复用，实施成本最低；用预先验证的 V1 字节副本和包备份回滚，若一张校验失败不得进行后续发布。 | **未来受控发布的首选**，当前未经授权不得执行。 |
| B 版本化并存 | 当前扫描会把同目录新增图片当作额外 Asset，缺少选默认版本的注册/选择语义；不能假定 App 只显示 Rose。 | 需另立 Publisher/Registry/App 方案和回归，维护成本较高；保留 V1 较直观。 | 当前架构**未具备安全并存入口**。 |
| C 仅保留 Preview | V1 正式 PNG、WebP 和包不变。 | 零迁移风险；用户暂时看不到新版。 | **本轮实际状态与当前推荐**，直到前置条件满足。 |

未来 Task 13G.4V.3E 若采用 A，先锁定最终修订版三图哈希与视觉/真机结果；保存原 V1 PNG 和正式 v2 包的字节、哈希、资产清单；在隔离目录以真实正式源布局重建并验证 WebP、完整 schema v2 包、diff 和 Asset ID/URI；记录旧→新内容哈希及缓存策略；在明确授权后做受控切换，任何失败恢复旧 PNG/包并复核旧哈希。全程不得把 MathNote Publisher 的 v2 包交给未升级的旧 Sync；Sync 升级与执行需独立任务及授权。之后才做 App 内渲染/交互验收和新版本 FINAL FREEZE。

## 9. 冻结与历史资源完整性

| 正式资产 | 001 | 002 | 003 |
| --- | --- | --- | --- |
| C043 V1 | `f4a09f974c984fccba2fa0a6eda55bbba411aee9b157c1e01b9d5e399574fafb` | `eac8a4d0b9ed784f1616da48e89a6acc88f90310582596d9e139c9113560abac` | `558b584aa4b3d7fac632b980c53f991a4858ed83047bfdaae2152eb8986ef9d2` |
| C051 V1 | `b835627c929140e5b36b34eb81714e66cbcabd75b74bc6a0abe67cdb11eedeb0` | `736e3a9497cf7f0a99bc49f387e4b0e57e59114f915b7f3ac7743b6694606af9` | `01eca6b6097468b36d9b44cda45e361acb44dd482654d70b21e23cc6150b0313` |

六张正式 PNG 均与冻结报告固定 SHA-256 一致。测试/隔离转换后的 212 文件快照：缺失 0、变更 0；包括历史试验、Rose 候选、正式 TeX/meta/PDF、Publisher 关键源码与 Task 13F。未修改正式资源、GIF、PDF、App、内容包，未 Sync、APK 或 Git 提交。

## 10. 自动化回归

| 检查 | 本轮实际结果 |
| --- | --- |
| C043 模型、正式源与卡面内容、辅助几何 | `test_model.py` **7/7 PASS**；Rose 专项中 `mathematical_checks()` **11/11 PASS**。 |
| Rose 三卡内容、标签、公式区域、002 字节基准 | `test_cards.py` **4/4 PASS**。 |
| 3B.1 胶囊/MathText 正向与负向回归 | `test_formula_spacing.py` **2/2 PASS**。 |
| 公共标签覆盖/碰撞/关联及静态动态架构边界 | `tests.test_static_label_layout tests.test_rendering_boundaries` **20/20 PASS**（隔离权限复跑）。 |
| PNG/SVG/手机预览/联系表、固定哈希 | 当前文件重新解码/解析并对比构建记录 **PASS**。 |
| Publisher 隔离转换/单 UID URI 映射 | 3/3 WebP 解码及哈希 **PASS**；3 图片 + 1 PDF Asset、0 错误/0 警告。 |

公共测试第一次在受限沙箱中有 3 项 `TemporaryDirectory` 写入抛 `PermissionError`，即使将 TEMP/TMP 指向工作区仍复现；其余 17 项通过。随后仅对相同命令在隔离权限下复跑，20/20 通过。此环境错误未计为数学失败，也未修改断言。现有自动测试锁定旧文案；其 PASS 不等于措辞出版审查 PASS。

## 11. Release Readiness Matrix

| Gate | 状态 | 依据/剩余项 |
| --- | --- | --- |
| 1 Mathematics | **PASS** | 三卡公式、几何、例题逐项正确。 |
| 2 Content | **BLOCKED** | 两处术语需用户批准修订；`CONTENT REVIEW BLOCKED`。 |
| 3 Visual | **PASS（当前字节）** | 用户已审图；当前哈希未变。修订后须重新审图。 |
| 4 Typography | **PASS（当前字节）** | 当前 renderer 检查与遮挡负例均通过。 |
| 5 Mobile | **PREVIEW PASS / DEVICE PENDING** | 六张缩放图已看，Android 无实测。 |
| 6 Regression | **PASS** | 212 文件无差异、正式六图固定哈希一致。 |
| 7 Publisher | **ISOLATED CONVERSION PASS / PACKAGE PENDING** | 单 UID 转换与映射通过；含 Rose 的完整正式包未建。 |
| 8 Release Safety | **PLAN PASS / EXECUTION PENDING** | A 的备份、原子切换与回滚原则已定，缓存/App/Sync 未实证。 |
| 9 Authorization | **PENDING** | 未批准卡面修订、正式覆盖、Publisher 发布或 Sync。 |

## 12. 用户待确认与下一阶段

1. 批准或明确驳回 001/002 的上述精确措辞。若批准，独立修订任务须重渲染并让用户重新确认新图；已选 002 的旧哈希仍作历史基准，不能静默更新。
2. 按第 6 节清单确认 Android 相册真机阅读；正式集成后再确认 App 内显示。记录设备和截图。
3. 待前两项满足后，明确选择未来发布策略，若选 A，单独授权 Task 13G.4V.3E 的 V1 保护、隔离完整包演练、受控替换及回滚演练。旧 Sync 的 v2 兼容升级另立边界，不随本任务执行。

下一阶段发布计划须写明正式目录 `03_conic/C043_hyperbola_abc_relation/images/`、旧三图/包备份位置与哈希、最终 Rose 三图哈希、WebP 转换参数、稳定 URI/Asset ID、全包 schema v2/diff 门、切换和回滚机制、新版冻结清单、隔离及正式回归、Sync 独立授权与 App 最终验收。正式替换前先确认同 URI 缓存更新方案。

## 13. 交付与最终状态

本任务仅新增本报告、`TASK_13G_4V_3D_RELEASE_READINESS.json`，以及隔离 QA 目录中的预检哈希、Publisher job/manifest/WebP、转换与完整性审计数据。Rose 三卡和正式资源均未更改。

- **Code / Asset QA：PASS**（自动化、格式、数学模型与当前图形技术质量）。
- **Human Image Review：PASS**（仅当前 SHA-256 对应版本）。
- **Android Device Gate：PENDING**。
- **Release Readiness：CONDITIONAL**，原因是正式内容文字修订尚未获授权且待重审、Android 真机待确认、含 Rose 的完整 v2 包与 App/缓存链路待下一任务验证。当前候选图不能直接发布。
- **任务状态：TASK 13G.4V.3D — RELEASE READINESS REVIEW COMPLETE。**
