# 概率与统计独立 ZIP 导出

完成校验日期：2026-11-16（Asia/Shanghai）。构建于上一轮开始，沿用目录中的 20261115 标记。

- ZIP：`build/zhishu-probability-stat-20261115/modules/probability-statistics.zip`
- 大小：11,042,929 字节，约 10.53 MiB。
- SHA-256：`8505d6cffe7439367ce7c4047264eb329389f02c787b033bb5543ff1ee405a3f`
- Schema：模块 v4；packageVersion：6。
- packageId：`zhishu.math.probability-statistics`。
- 唯一一级章节：`概率与统计`，moduleRootNodeId 为 `struct:概率与统计`。
- 二级结论：42 条，UID 集合与 `06_probability-stat` 正式源完全一致。
- isPro：18 条整数 0、24 条整数 1；逐 UID 与正式源一致。
- 资源：42 个 PDF、4 个图片资源；无视频。
- 共 87 个树节点，其中 42 个是二级结论；其余根与分类节点未计入结论数量。

## 代码与兼容性

新增合并模块注册，保留历史 probability/statistics 包身份以供历史校验使用；禁止合并章节与拆分章节同时出现在同一完整包。完整发行辅助工具分别支持当前 13 章节和历史 14 章节布局。未修改知识 UID、媒体引用格式或模块 Schema。

使用现有 Publisher 从正式源构建隔离 Full v2，再用现有 slicer 仅导出 probability-statistics；没有生成其他模块 ZIP，没有替换既有正式完整包或旧模块包，没有执行 Sync、App 修改、commit 或 push。

## 实际验证

- Publisher：PASS，0 错误、0 警告。
- 模块包及发行回归：57 项通过，包含新合并布局、历史拆分布局及混合布局拒绝测试。
- 最终 ZIP：现有独立包及来源一致性验证器 PASS；42 个 UID、标题、整数 isPro 与章节均逐项核对。
- 来源保护：439 个 `06_probability-stat` 文件的 SHA-256 与本次导出前一致。

机器证据：`reports/PROBABILITY_STATISTICS_ZIP_VALIDATION.json`。
测试日志：`reports/PROBABILITY_STATISTICS_EXPORT_TESTS.txt`。
