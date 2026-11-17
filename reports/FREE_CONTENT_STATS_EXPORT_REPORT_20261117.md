# 免费版与全部内容统计

日期为 2026-11-17。本次沿用 2026-11-16 的 Full v2 快照，模块包版本设为 8，模块包结构为 Schema v4。

## 汇总

| 范围 | 二级结论条数 | 静态知识图片张数 | GIF 个数 | PDF 总页数 |
| --- | ---: | ---: | ---: | ---: |
| 免费版 | 180 | 97 | 44 | 1470 |
| 全部 | 591 | 314 | 143 | 4609 |

## 知树 App 接入字段

每个 ZIP 的 `manifest.json` 中，`contentStats` 保存全部统计，`freeContentStats` 保存免费版统计。两个对象使用相同字段。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `schemaVersion` | 整数 | 统计结构版本，当前固定为 1 |
| `knowledgeCount` | 非负整数 | 二级结论条数 |
| `imageCount` | 非负整数 | 静态知识图片张数 |
| `gifCount` | 非负整数 | GIF 个数 |
| `pdfPageCount` | 非负整数 | PDF 总页数 |

免费版条数读取 `manifest.freeContentStats.knowledgeCount`。全部 PDF 页数读取 `manifest.contentStats.pdfPageCount`。

免费版按结论的整数 `isPro=0` 筛选，资源根据其 `knowledgeId` 归属计入。结论和资源按正式 ID 去重，PDF 解析实际页树。目录节点、分享 MP4、封面和未登记资源不计入上述四项。

旧包可能缺少 `freeContentStats`。App 可将该组显示为“暂无统计”或隐藏该组，保留未知状态。Publisher 的显式历史兼容入口为 `allow_legacy_content_stats=True`。缺失的历史 `isPro` 不计为免费。

## 各模块免费版统计

| 模块 | ZIP | 二级结论 | 静态图片 | GIF | PDF 页数 |
| --- | --- | ---: | ---: | ---: | ---: |
| 解析几何 | analytic-geometry.zip | 36 | 82 | 36 | 526 |
| 函数 | functions.zip | 20 | 3 | 2 | 145 |
| 不等式 | inequalities.zip | 11 | 0 | 0 | 64 |
| 逻辑用语 | logic.zip | 7 | 0 | 0 | 32 |
| 平面几何 | plane-geometry.zip | 7 | 3 | 5 | 63 |
| 前置知识 | prerequisites.zip | 12 | 0 | 0 | 72 |
| 概率与统计 | probability-statistics.zip | 18 | 3 | 0 | 137 |
| 数列 | sequences.zip | 15 | 0 | 0 | 94 |
| 集合 | sets.zip | 9 | 3 | 0 | 49 |
| 立体几何 | solid-geometry.zip | 18 | 0 | 0 | 119 |
| 解三角形 | triangle-solving.zip | 4 | 0 | 0 | 25 |
| 三角函数 | trigonometry.zip | 7 | 0 | 0 | 51 |
| 向量 | vectors.zip | 16 | 3 | 1 | 93 |

## 交付与验证

- ZIP 目录为 `build/zhishu-free-content-stats-20261117/modules/`，包含 13 个新版 ZIP 及对应的解包目录。
- 来源为 `build/zhishu-content-stats-20261116/full/`，内容版本为 `sha256:cc709ec4c0621be12f803e81b324c5aafccfb597e42dea0a7443ad85a5191ea1`。
- 正常切包流程已校验 Full 来源、已复制资源、实际 ZIP、真实 PDF 页数及完整性哈希，并核对操作前后 Full 文件哈希一致。
- 相关回归为 79 项 PASS，覆盖模块包、完整模块发布、免费分类、分享字段，以及新增免费资源归属、多页 PDF、GIF、去重、空免费集合、缺失分类、非法类型、篡改重签与历史兼容场景。
- 首轮沙箱测试出现临时目录权限错误，普通文件权限下重跑 79 项得到 `OK`。原始重跑日志保存在 `FREE_CONTENT_STATS_TESTS_20261117.txt`。
- 每个 ZIP 的两组统计、字节数、SHA256 和内容版本保存在 `FREE_CONTENT_STATS_EXPORT_20261117.json`。
- 独立全 ZIP 审计为 PASS，结果文件为 `FREE_CONTENT_STATS_VALIDATION_20261117.json`。审计重新解析各包 PDF，复算两组统计，检查完整性、Full 来源、跨模块唯一归属和覆盖，并从 Full 重新计算总量与各模块之和对比；三个随机包另按真实图片格式与 PDF 页数抽查。
- 全部 591 条已打包结论均有显式整数分类，免费结论的 180 个 ID 与 `data/content/free-knowledge-selection.json` 完全一致。

本次交付覆盖数据包端。知树 App 的读取与界面展示由 App 端接入，实际显示效果待接入后验证。
