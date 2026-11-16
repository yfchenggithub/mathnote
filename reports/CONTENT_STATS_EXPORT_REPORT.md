# MathNote 内容包统计导出报告

日期：2026-11-16。

## 结果

全部 13 个当前模块 ZIP 已通过现有导出链路生成，包版本为 7，保留 Schema v4。每个 ZIP 的 manifest.json 均包含 contentStats（schemaVersion=1），统计与实际 ZIP 内容一致。

正式来源仍为 11 个生产目录；章节包按现有知识树划分为 13 个模块（集合/逻辑、三角函数/解三角形分别导出），概率与统计保持一个独立模块包。

交付目录：`build/zhishu-content-stats-20261116/modules/`。独立概率与统计包：`probability-statistics.zip`。旧包和默认 Full 输出未被覆盖。

## 每个模块的实际统计

| 模块 | ZIP | 二级结论 | 静态知识图片 | GIF | PDF 总页数 |
| --- | --- | ---: | ---: | ---: | ---: |
| 解析几何 | [analytic-geometry.zip](D:/mathnote/build/zhishu-content-stats-20261116/modules/analytic-geometry.zip) | 120 | 274 | 120 | 1556 |
| 函数 | [functions.zip](D:/mathnote/build/zhishu-content-stats-20261116/modules/functions.zip) | 80 | 6 | 3 | 542 |
| 不等式 | [inequalities.zip](D:/mathnote/build/zhishu-content-stats-20261116/modules/inequalities.zip) | 64 | 0 | 0 | 383 |
| 逻辑用语 | [logic.zip](D:/mathnote/build/zhishu-content-stats-20261116/modules/logic.zip) | 10 | 0 | 0 | 50 |
| 平面几何 | [plane-geometry.zip](D:/mathnote/build/zhishu-content-stats-20261116/modules/plane-geometry.zip) | 31 | 3 | 7 | 218 |
| 前置知识 | [prerequisites.zip](D:/mathnote/build/zhishu-content-stats-20261116/modules/prerequisites.zip) | 55 | 0 | 0 | 338 |
| 概率与统计 | [probability-statistics.zip](D:/mathnote/build/zhishu-content-stats-20261116/modules/probability-statistics.zip) | 42 | 3 | 1 | 297 |
| 数列 | [sequences.zip](D:/mathnote/build/zhishu-content-stats-20261116/modules/sequences.zip) | 42 | 0 | 0 | 277 |
| 集合 | [sets.zip](D:/mathnote/build/zhishu-content-stats-20261116/modules/sets.zip) | 12 | 3 | 0 | 65 |
| 立体几何 | [solid-geometry.zip](D:/mathnote/build/zhishu-content-stats-20261116/modules/solid-geometry.zip) | 58 | 10 | 3 | 422 |
| 解三角形 | [triangle-solving.zip](D:/mathnote/build/zhishu-content-stats-20261116/modules/triangle-solving.zip) | 13 | 3 | 3 | 92 |
| 三角函数 | [trigonometry.zip](D:/mathnote/build/zhishu-content-stats-20261116/modules/trigonometry.zip) | 24 | 0 | 1 | 156 |
| 向量 | [vectors.zip](D:/mathnote/build/zhishu-content-stats-20261116/modules/vectors.zip) | 40 | 12 | 5 | 213 |
| **去重汇总** | **13 个 ZIP** | **591** | **314** | **143** | **4609** |

## 统计和一致性验证

- 统计在资源筛选、复制完成后生成；仅使用最终 KnowledgeNode 和 KnowledgeAsset 清单，不扫描工程目录作为计数依据。
- knowledgeCount 按 type=knowledge 的唯一 ID 统计，不包含 root/chapter/section，免费和授权均包含。
- imageCount 只含正式静态知识图片；GIF 单独计数。分享 MP4、图标、封面、预览和未登记资源不参与统计。原 counts.imageAssets 保留原有包含 GIF 的语义。
- 全部 591 份实际打包 PDF 均由 Poppler pdfinfo 解析真实页树，pdfPageCount 是实际页数之和；解析失败、诊断错误或工具缺失均阻止事务提交。
- 所有 ZIP 重新解包，复算统计、文件/实体/媒体哈希，并按原校验规则核对 Full 来源、章节树、关系、媒体格式和视频。未放宽既有校验。
- 按现有资源唯一 ID/knowledgeId 归属核对跨模块覆盖，重复或冲突归属被拒绝。完整集合去重统计与模块统计之和相等；共享目录节点未计入。内容相同但 ID 不同的正式资源遵循现有身份规则，不按文件字节哈希合并。
- 跨模块共享媒体条目：0。没有遗漏或重复归属知识/媒体资源。

## 随机抽查

从 13 个 ZIP 随机抽取以下 3 个模块，再次按真实图片格式区分静态图/GIF、按知识 ID 去重，并逐份解析 PDF。每份 PDF 的实际页数证据保存在 CONTENT_STATS_VALIDATION.json 的 randomSamples.pdfPagesByAssetId。

| ZIP | 知识 | 静态图 | GIF | PDF 页数 | 结果 |
| --- | ---: | ---: | ---: | ---: | --- |
| analytic-geometry.zip | 120 | 274 | 120 | 1556 | PASS |
| triangle-solving.zip | 13 | 3 | 3 | 92 | PASS |
| functions.zip | 80 | 6 | 3 | 542 | PASS |

## 不变性与兼容性

- 当前 Full 内容哈希仍为 `cc709ec4c0621be12f803e81b324c5aafccfb597e42dea0a7443ad85a5191ea1`，与本次任务前相同；知识内容、ID、isPro、shareConfig 和媒体字节未改变。
- 源结论仍为 591 条，免费 180、授权 411。新增 contentStats 参与模块 packageHash 和 contentVersion；完整性覆盖新增字段。
- 保留 Schema v4、现有 counts、目录结构、媒体 URI 和 requiredCapabilities。新版本导出及默认验证均要求完整统计。历史无统计的 Schema v4 可使用显式 allow_legacy_content_stats=True 只读兼容验证；正式导出不提供跳过统计选项。
- 未修改 Android、权限、付费、搜索界面、知识树界面或分享配置；未执行 Sync、commit 或 push。

## 测试结果

- 模块包及发布回归：62/62 PASS。包含新增多页 PDF、GIF 去重、篡改重签、字段缺失/错误类型、PDF 损坏事务回滚、解析器缺失等测试。
- 其余完整项目测试：150/151 PASS，1 FAIL。合计 212/213 PASS。完整回归不能标记为全绿。
- 失败项：tests.test_conic_math_audit_20261021.ConicMathAudit.test_all_83_metadata_parse_and_corrected_source_search_formulas；第 205 行固定断言 83 个圆锥曲线目录，当前实际为 94。该测试文件与 HEAD 字节内容一致，生产目录本次未修改；保留原测试标准，未将断言改成新数字。
- 正式 Full 构建：0 errors / 0 warnings。全部模块导出与实际 ZIP 来源、统计、完整性审计 PASS。

## 修改文件和交付证据

| 文件 | 用途 |
| --- | --- |
| scripts/zhishu/content_stats.py | 基于实际资源计算统计，使用 Poppler 读取页数，严格字段校验 |
| scripts/zhishu/module_package.py | 写入和校验 manifest.contentStats、哈希覆盖、历史只读兼容开关 |
| scripts/zhishu/module_release.py | 完整模块审计、去重汇总、跨模块一致性核对 |
| scripts/check_content_stats.py | 全 ZIP 审计 CLI、随机三包抽查及每 PDF 页数证据 |
| tests/test_zhishu_module_package.py | 将原占位 PDF 测试夹具改为真实 PDF；新增统计和失败保护测试 |
| scripts/zhishu/README.md | 统计语义、依赖、兼容验证及审计命令 |
| reports/CONTENT_STATS_VALIDATION.json | 每包统计、SHA256、全量来源和跨模块审计、随机样本页数 |
| reports/CONTENT_STATS_MODULE_TESTS.txt | 模块包及发布测试完整日志 |
| reports/CONTENT_STATS_OTHER_REGRESSION_TESTS.txt | 其余完整项目测试日志（含原有失败） |
| reports/CONTENT_STATS_TEST_SUMMARY.json | 测试数量与原有失败原因 |
| reports/CONTENT_STATS_BUILD_LOG.txt | 既有 Publisher Full 构建结果 |
| reports/CONTENT_STATS_MODULE_EXPORT_LOG.json | 13 个实际模块导出结果 |
| reports/CONTENT_STATS_EXPORT_REPORT.md | 本报告 |

## ZIP 身份

| ZIP | 字节数 | SHA256 |
| --- | ---: | --- |
| analytic-geometry.zip | 679410425 | `f498fce255bc93ed19340277d70472afbfb11fac74c864a63d9d2900871b1392` |
| functions.zip | 23289793 | `d67a9607dec562f74a18cccd9296e7dc7dc8d9dac0beae8222d68cb8307642c9` |
| inequalities.zip | 11437125 | `81aec796650a094c03f0071a8382cc2d99f057e8a3aa3411f6f210d935a6d7d1` |
| logic.zip | 1606788 | `a32b4ff5cb11428dac0ff50c05823a9ade945c646be720bcc81ff3fb4c68a295` |
| plane-geometry.zip | 16851804 | `32d6421457f4baac502a6dbdd59f04357853651227975ba66912494421bbab61` |
| prerequisites.zip | 9443771 | `954161a03e5ed8b76b24102ad734ff351ef1caacb760a2d35603fe0f2d25c305` |
| probability-statistics.zip | 11043068 | `1cdc616d4d640a74c8eba1b8f22ef77d189b5206c795a75247336ec907ae69eb` |
| sequences.zip | 7451751 | `4ab844f3b8ab52ab41face918a4413587cd6b589e816ae2cfdfca06858a04865` |
| sets.zip | 2427213 | `fd5983b3c45a2bd7d87ab0255e572dcbc3f972aaaed70e8507ef99364995ef93` |
| solid-geometry.zip | 27336696 | `6af8a95b53b25f84df98da07e30b7c4d57e5a3295567846262b57ce5e0380e94` |
| triangle-solving.zip | 9351106 | `75d554a6701304ff789351d9828f4dd7cd5ca208eaf61ea7a4690c6d547d2412` |
| trigonometry.zip | 7557778 | `ada15ad4556f44ecd7027ae6596f9dfe0f06465584bbee11b79216c3a76260df` |
| vectors.zip | 25484293 | `5c90ec0d0a6c4c2ab6a69192242e443433ca8b7b456ca565babedbb2b9d35fc5` |
