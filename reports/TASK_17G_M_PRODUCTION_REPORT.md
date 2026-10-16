# Task 17G-M — PRODUCTION REPORT

日期：2026-10-16（Asia/Shanghai）。

MathNote 生产与完整性门 PASS；TASK 17G-M **CONDITIONAL PASS**；**17G-Z READY NO（当前消费端身份白名单阻碍）**。生产输入完整；条件不来自 Android 真机未参与。

MODULE PRODUCTION PASS。正式输出 `D:/mathnote/build/zhishu-module-packages`，14 个 ZIP 与展开目录实际存在。发布索引按 packageId 升序，无随机时间戳或绝对本机路径；没有增加 ZIP Manifest 字段。全部 packageVersion=1。两个试点原身份及原字节完全保留。

| 模块 | moduleId | packageId | 节点 | 结论 | 搜索 | 媒体 | 内部 | 外部 | ZIP / bytes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 解析几何 | math.analytic-geometry | zhishu.math.analytic-geometry | 180 | 105 | 105 | 206 | 192 | 3 | analytic-geometry.zip / 37408410 |
| 函数 | math.functions | zhishu.math.functions | 130 | 78 | 78 | 82 | 111 | 6 | functions.zip / 17502263 |
| 不等式 | math.inequalities | zhishu.math.inequalities | 98 | 64 | 64 | 64 | 95 | 0 | inequalities.zip / 11390557 |
| 逻辑用语 | math.logic | zhishu.math.logic | 27 | 10 | 10 | 10 | 12 | 5 | logic.zip / 1590781 |
| 平面几何 | math.plane-geometry | zhishu.math.plane-geometry | 53 | 31 | 31 | 31 | 41 | 1 | plane-geometry.zip / 5226847 |
| 前置知识 | math.prerequisites | zhishu.math.prerequisites | 114 | 55 | 55 | 55 | 74 | 0 | prerequisites.zip / 9357489 |
| 概率 | math.probability | zhishu.math.probability | 61 | 31 | 31 | 35 | 54 | 6 | probability.zip / 8747931 |
| 数列 | math.sequences | zhishu.math.sequences | 87 | 42 | 42 | 42 | 59 | 4 | sequences.zip / 7410755 |
| 集合 | math.set | zhishu.math.set | 25 | 12 | 12 | 15 | 13 | 3 | sets.zip / 2409052 |
| 立体几何 | math.solid-geometry | zhishu.math.solid-geometry | 100 | 58 | 58 | 63 | 86 | 2 | solid-geometry.zip / 12100878 |
| 统计 | math.statistics | zhishu.math.statistics | 28 | 11 | 11 | 11 | 11 | 6 | statistics.zip / 2221637 |
| 解三角形 | math.triangle-solving | zhishu.math.triangle-solving | 21 | 13 | 13 | 13 | 22 | 0 | triangle-solving.zip / 2247177 |
| 三角函数 | math.trigonometry | zhishu.math.trigonometry | 44 | 24 | 24 | 25 | 38 | 0 | trigonometry.zip / 7523926 |
| 向量 | math.vectors | zhishu.math.vectors | 76 | 38 | 38 | 38 | 62 | 0 | vectors.zip / 6251559 |

| 模块 | PDF bytes | 第1轮打包及逐包验证秒 | 第2轮打包及逐包验证秒 |
| --- | --- | --- | --- |
| 解析几何 | 17964836 | 18.365 | 14.997 |
| 函数 | 13326181 | 5.989 | 6.643 |
| 不等式 | 11126924 | 5.045 | 5.713 |
| 逻辑用语 | 1544003 | 1.132 | 1.144 |
| 平面几何 | 5106303 | 2.607 | 2.73 |
| 前置知识 | 9130536 | 4.837 | 4.516 |
| 概率 | 5536785 | 3.045 | 3.011 |
| 数列 | 7240073 | 3.74 | 3.381 |
| 集合 | 2040276 | 1.5 | 1.344 |
| 立体几何 | 9899167 | 4.773 | 4.969 |
| 统计 | 2171569 | 1.105 | 1.165 |
| 解三角形 | 2195348 | 1.361 | 1.291 |
| 三角函数 | 4222766 | 2.165 | 2.209 |
| 向量 | 6083803 | 2.929 | 2.993 |

总 ZIP 131,389,262 bytes（125.303 MiB）；最小 logic.zip 1,590,781 bytes，最大 analytic-geometry.zip 37,408,410 bytes。全局唯一媒体 128,954,029 bytes，PDF 总 97,588,570 bytes。

两轮完整切片（含逐包验证）分别 77.233 / 77.066 秒；额外 staging 全量 ZIP 审计分别 48.191 / 44.555 秒。正式目录全部 ZIP 的独立完整审计耗时 17.394 秒。提交复制与提交后验证合计 55.423 秒。逐包校验已计入模块打包时段，未另外拆分成纯校验耗时；不把混合时段冒充纯验证耗时。计时仅为本机生产数据，不参与发布内容哈希。

流程：原切片器→两轮隔离 staging（第二轮反向模块顺序）→逐包独立与来源校验→独立父链全局审计→全部媒体哈希→产物目录及 ZIP 字节比较→已有正式文件保护→统一目录提交。提交后正式索引再次验证，且正式文件集合及哈希精确等于 staging。

不同的已有正式文件一律拒绝替换并保留 staging；无关文件受保护。不可读目录必须失败，不视为空目录。Windows WinError 5/32/33 只做有上限重试，不更改 ACL。提交失败沿用备份恢复；原故障注入回滚测试通过。不承诺未经测试的进程断电恢复。

| Gate | 内容 | 状态 |
| --- | --- | --- |
| G1 | 正式数学源冻结 | PASS |
| G2 | 全部一级分类发现 | PASS |
| G3 | 14正式ZIP齐全 | PASS |
| G4 | 全部正式结论覆盖 | PASS |
| G5 | 无重复knowledgeId | PASS |
| G6 | 搜索完整 | PASS |
| G7 | 全局节点完整 | PASS |
| G8 | 父链、共享根与分类合法 | PASS |
| G9 | 全部正式媒体完整 | PASS |
| G10 | 媒体二进制哈希正确 | PASS |
| G11 | 内部关系完整 | PASS |
| G12 | 跨模块关系完整 | PASS |
| G13 | 无非法目标 | PASS |
| G14 | 逐包独立Python Schema v4校验 | PASS |
| G15 | contentVersion/packageHash正确 | PASS |
| G16 | 两轮ZIP字节一致 | PASS |
| G17 | 两个正式试点兼容 | PASS |
| G18 | 发布索引精确一致 | PASS |
| G19 | 联合结构/所有权/关系可验证 | PASS（结构层；当前App全量启用BLOCKED） |
| G20 | 正式数学源未改 | PASS |
| G21 | Zhishu工程未改 | PASS |
| G22 | Publisher与相关测试通过 | PASS |
| G23 | 交接资料完整并披露消费端阻碍 | PASS |

知树当前 `MODULE_V4_REGISTRY` 仅登记集合、解析几何。只读执行真实 TypeScript Manifest 解析，2 包接受、另外 12 包以 `identity: unregistered/mismatched module identity` 拒绝；`normalizeCandidatePackageIds` 同样拒绝全量选择。未修改或绕过白名单。当前未修改的 App 不能直接安装/启用全部 14 包。

状态：SOURCE AUDIT PASS；MODULE DISCOVERY PASS；MODULE PRODUCTION PASS；KNOWLEDGE COVERAGE PASS；MEDIA COMPLETENESS PASS；RELATION COMPLETENESS PASS；SCHEMA V4 VALIDATION PASS（Python）；HASH DETERMINISM PASS；EXISTING PILOT COMPATIBILITY PASS；FULL MODULE AGGREGATION AUDIT PASS（元数据结构）；AUTOMATED TEST PASS；TASK 17G-M CONDITIONAL PASS；17G-Z READY NO（当前消费者）。

