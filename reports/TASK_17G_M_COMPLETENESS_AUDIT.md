# Task 17G-M — COMPLETENESS AUDIT

日期：2026-10-16（Asia/Shanghai）。

KNOWLEDGE COVERAGE PASS / MEDIA COMPLETENESS PASS / RELATION COMPLETENESS PASS / FULL MODULE AGGREGATION AUDIT PASS（结构层）。

正式知识 ID 并集精确等于源 572 条，重复 0、遗漏 0、虚构 0；逐条完整记录及数组原顺序与 Full 一致。节点唯一集合 1031，与 Full 完整记录一致。各 ZIP 节点合计 1044，差额是数学根在 14 包各保留一份；聚合只留一次。唯一共享分类为 root-high-school-math，记录及 entity hash 相同，14 owner 合法。

独立于切片器向下收集，审计逐节点向上追溯 chapter，再核对每包边界。全部 parentId 保留，所有节点可到原根，无环、孤立、重复子节点或分类内容冲突。前置知识后代 section 真实类型保留。

SearchDocuments 572，ID 集合、标题、摘要、面包屑及中文数学符号所在完整原记录严格等于来源。每条知识恰好一份搜索文档，无跨模块误归属，无重新生成另一套搜索文本。

媒体唯一 ID 690，模块引用 690，ZIP实际媒体文件 690，跨包共享媒体 0，缺失 0，无引用额外媒体 0。图片117、PDF572、MP4 1 的 URI/assetId/knowledgeId 保留。全部实际媒体逐文件读取，核对大小、SHA256及原 Full 字节摘要；执行原图片格式、PDF头和MP4 ffprobe校验。切片未压缩图片、未重排PDF、未改变任何媒体字节。ZIP安全路径、链接、CRC、精确清单及固定条目元数据均通过检查。

| 关系口径 | 数量 |
| --- | ---: |
| 源meta原始 related 声明 | 1682 |
| 源meta canonical 重复声明 | 794 |
| Full源记录 / canonical唯一 | 888 / 888 |
| 模块内部原始记录 | 870 |
| 模块外部原始声明 | 36 |
| 模块全局canonical唯一 | 888 |
| 跨模块唯一连接 | 18 |
| 双端外部重复声明 | 18 |
| Full自身重复源记录 | 0 |
| 未解析关系 / 无效目标 | 0 / 0 |

外部边剥除 externalEndpointId/targetPackageId/resolutionPolicy 后逐条比较完整原关系核心；同ID异核心拒绝。内部边恰好声明一次，跨包边各端恰好声明一次，36条声明不等于36条有效连接。所有18条跨包连接的目标存在于正式572知识集合且owner唯一。targetPackageId继续保留null，符合原软引用契约并保持试点内容身份；通过实际知识owner解析，没有伪节点或改ID。

只读执行知树真实 calculateModuleV4Hashes：14包哈希一致；buildModuleOwnershipIndex：冲突0、知识572、搜索572、媒体690；resolveSnapshotRelations：870内部+36外部→888唯一关系，18跨包连接可解析，未解析0、无效目标0。输入是Python严格校验后的元数据模型，**不是实际安装记录、Runtime激活或Android验收**。

知树当前 `MODULE_V4_REGISTRY` 仅登记集合、解析几何。只读执行真实 TypeScript Manifest 解析，2 包接受、另外 12 包以 `identity: unregistered/mismatched module identity` 拒绝；`normalizeCandidatePackageIds` 同样拒绝全量选择。未修改或绕过白名单。当前未修改的 App 不能直接安装/启用全部 14 包。

证据：`build/task17g-evidence/release-candidate/round-1-audit.json`、`round-2-audit.json`（完整ID、owner、关系核心、源哈希），`final-audit.json`，`zhishu-compatibility.json`。不能将结构层 PASS 写成当前 App 全量安装 PASS。

