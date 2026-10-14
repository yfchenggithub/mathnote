# Task 17A-M → Task 17A-Z：数据契约交接

状态：MathNote 端 **PROPOSED**，Zhishu 端全部 **PENDING**；2026-10-14。本次只审计 MathNote，没有读取、修改或运行 Zhishu Android/Sync 项目，因此不宣称安装、合并、卸载、授权或最低 App 版本已受支持。

## MathNote 可交付的稳定事实（VERIFIED）

| 项目 | 当前事实 / 建议交接语义 |
| --- | --- |
| 全集产物 | 无参数 [`build-content`](../scripts/zhishu/publish.py#L290) 发布 schema v2 目录；默认 `build/zhishu-content-package`。现行 Zhishu Sync 的 v2 支持**不得假定**，[`scripts/zhishu/README.md`](../scripts/zhishu/README.md#L116) 明示旧 Sync 只接受 v1。 |
| 节点 ID | `meta.id` 是结论 ID；`struct:<完整知识路径>` 是结构 ID；现有高中数学根为 `root-high-school-math`。模块包共享同一 ID 空间，禁止复制出新 ID。 |
| 分类路径 | `meta.knowledgeNode` 的完整路径及原父链、原 `sortOrder`；同一源目录可对应多种一级分类。 |
| 关联 | 当前仅 canonical、去重的 `related`，关系 ID `<较小UID>:related:<较大UID>`；18 条跨一级分类。现有 v2 要求端点同包，模块包建议提供原 ID 的外部关系记录。 |
| 资源 | 图片/PDF `KnowledgeAsset` 使用 `resources/images/<UID>/<name>.webp|.gif`、`resources/pdfs/<UID>/<name>.pdf`；MP4 通过 `animation-shares.json` 关联 GIF，URI 为 `resources/videos/<UID>/<name>.mp4`。全为包根相对逻辑路径。 |
| 版本及完整性 | 现行 `schemaVersion=2`、`contentVersion=sha256:<packageHash>`；`fileHashes`、`entityHashes`、`assetHashes`、`shareAssetHashes`。模块包额外需 `packageId`、`packageVersion`、`subjectId`、`moduleId` 和兼容 API 字段。 |

## 建议接口（PROPOSED）

MathNote 输出可单独传输的 `module package`，包含包标识、发行版本、schema 版本、学科/模块标识、根节点 ID、完整原始祖先路径、原结论/资产 ID、内部关系、外部关系引用、搜索文档、资源及逐文件/逐实体 SHA-256。Zhishu 应先验证哈希和包内封闭性，再维护全局实体索引。相同 ID+相同内容可被多个包引用；相同 ID+不同内容必须有可预测的版本/优先级策略。卸载一个包时不应删除仍被其他包引用的节点或资源。未安装目标的外部关系保留原目标 ID，安装后再解析；对缺失目标的 UI 表现由 Zhishu 决定。

MathNote 负责内容生成、包校验信息和确定性产物；Zhishu 负责选择/安装/更新/卸载、运行时合并、搜索与知识树展示、学习记录、收藏、购买和离线授权。数学包的 `packageKind=collection` 与单专题 `packageKind=module` 应能共享 ID，而非复制一份新结论。任何收费或数字签名方案均待产品和 Zhishu 独立确认。

## Task 17A-Z 待验证问题（PENDING）

1. 当前 APK/Sync 是否能读取 v2；若不能，迁移入口与兼容下限是什么？本任务不执行 Sync。
2. Android 使用何种全局主键、事务和包来源索引，能否在全集包与专题包同时安装时按 ID+哈希去重？版本冲突如何裁决？
3. 未安装目标包的外部关系需隐藏、显示占位还是提示安装？如何在后装/卸载时重新解析？
4. 同一个结构祖先节点被多个专题包包含时如何合并、排序、卸载？非数学学科的根与导航如何表示？
5. 搜索文档的全局去重与权重/排名如何合并？已有学习记录和收藏是否仍按原 knowledgeId 定位？
6. 包 schema、`minAppContentApi`、`packageVersion`、更新/回滚序列、依赖缺失策略与事务失败处理如何定义？
7. 资源 URI 是按包命名空间解析，还是合并到统一资源库？同 Asset ID 但哈希不同、同 URI 被不同包占用时如何处理？
8. 分享解锁 PDF、购买专题、数学全集授权与包安装状态的关系是什么？这些商业规则不应写进 MathNote 的原始结论 ID。
9. 是否需要签名/可信来源检查？当前建议只提供完整性哈希；它不能证明发布者身份。

这些问题未由 Zhishu 项目源码或真机验证，不能标为 PASS。建议 Task 17A-Z 先对上面的最小契约给出接受/修改结果，再冻结模块 schema。
