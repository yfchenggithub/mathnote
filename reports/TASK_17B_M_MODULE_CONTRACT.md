# Task 17B-M — Module Contract

日期：2026-10-15（Asia/Shanghai）。状态：**MathNote IMPLEMENTED / MODULE PACKAGE PASS；双端契约认领 PENDING**。依赖 Task 17A-F 候选结构，未修改其历史文档或宣称 FINAL FREEZE。

## 版本冲突与最小修订

17A-F Schema Spec §7 的候选规则是 `v3.contentVersion = sha256:H(Manifest 除 packageHash/contentVersion)`；该摘要包含 `sourcePackage`，所以仅其他模块变化也会改变集合的内容版本。这与本任务 §7.1 的“来源版本变化但模块内容未变，contentVersion 不变”直接冲突。优先执行当前用户要求。

为避免将不同语义伪装为候选 v3，本实现用 **schemaVersion=4** 和能力 `package-schema-v4`。仅变更内容身份与 envelope 身份的分离；五个原 DTO、外部关系格式、Manifest 字段名及资源路径沿用候选。不加入另一套知识模型，不修改 Full v2。`packageHash` 仍验全 envelope：

```python
payload = manifest 删除 packageHash 和 contentVersion
packageHash = H(payload)
contentVersion = "sha256:" + H(payload 删除 sourcePackage 和 packageVersion)
```

`H` 完全沿用现有 Python canonical 算法：UTF-8；Unicode code point 键排序；紧凑 separators；对象 None 字段省略、数组 null 保留；数组次序保留；拒绝 NaN/Infinity。完整包 v2 算法原样不变。模块六个 JSON 文件使用 UTF-8、无 BOM、sort_keys、indent=2、LF 结尾；显式 `targetPackageId:null` 保存在文件字节中，entity canonical 仍遵守继承的 clean(None)。fileHashes 始终以实际原始字节计算。

`contentVersion` 是本模块数据、身份、能力、文件/实体/媒体完整性内容的摘要，来源与发行序号不参与；不是全量版本、ZIP hash 或数字签名。改变本地节点/搜索/关系/资源时版本变化。`packageHash` 覆盖来源与发行序号，改 sourcePackage 时仍能验真；安装端应以 packageId+packageVersion+packageHash 执行幂等/同号拒绝规则，以 contentVersion 判断内容是否改变。相同内容重新登记来源亦须提高发行序号（既有同号异 envelope 被拒绝），内容版本可以保持。

## 身份与固定 profile

| slug | packageId | moduleId | moduleRootNodeId |
| --- | --- | --- | --- |
| sets | zhishu.math.set | math.set | struct:集合 |
| analytic-geometry | zhishu.math.analytic-geometry | math.analytic-geometry | struct:解析几何 |

subjectId=`math.high-school`；packageKind=`module`；初次 packageVersion=1（正 JS 安全整数，CLI 可显式提供更高序号）；rootNodeId=`root-high-school-math`；minAppContentApi=1。模块名称来自原 moduleRoot 节点 title，Manifest 不擅加候选外 `moduleName` 字段。节点数包括共同根；结论数等于 searchDocuments 数。

必需 Manifest 字段精确为：schemaVersion/packageId/subjectId/moduleId/packageKind/packageVersion/rootNodeId/moduleRootNodeId/minAppContentApi/requiredCapabilities/dependencies/sourcePackage/files/counts/fileHashes/entityHashes/assetHashes/shareAssetHashes/resources/packageHash/contentVersion。未知顶层字段拒绝。此最小生产 profile 不发 minAppVersion、图片宽高或硬依赖；dependencies 必为 []，不声称当前 App 已实现 Content API 1。

requiredCapabilities 排序且精确匹配：`package-schema-v4`、`persistent-content-uri-v1`、`shared-entity-ownership-v1`；有外部边加 `external-related-v1`，有分享视频加 `animation-share-mp4-v1`。消费者须实现并明确支持全部要求，不能把 API 数值当作已实现能力。

## 文件、实体与资源

包根直接包含 manifest.json 和以下六个数组文件，不嵌套 slug 顶层目录：

| files key | 文件 | entityHashes 主键 |
| --- | --- | --- |
| knowledgeNodes | knowledge-nodes.json | id |
| knowledgeRelations | knowledge-relations.json | id |
| knowledgeAssets | knowledge-assets.json | id |
| searchDocuments | search-documents.json | knowledgeNodeId |
| animationShares | animation-shares.json | displayAssetId |
| externalRelations | external-relations.json | id |

空数组也存在；manifest 不自计 fileHash。counts 精确覆盖六组及 imageAssets/pdfAssets/videoAssets，均为非负 JS 安全整数，bool 不算整数。image 含 GIF；MP4 只在 animationShares。原记录数组保留源顺序，外部边按 sourceId/type/targetId 排序；原 sortOrder 不重算。

节点精确为选定一级 chapter 的完整子树加原 subject root，父 ID 全在本包，根 parentId 按原记录省略。ID 不重编号；每个本地 knowledge 恰好一条原搜索文档。校验单根、合法类型、父链、循环、ID 重复及 search 覆盖。两个模块仅共享数学根，正式 knowledge 无重叠。

资源取自本地 KnowledgeAsset 与本地 animation-share 的 URI，直接复制 Full v2 原字节。原图/PDF/share-video ID、URI、类型和关联不变。resources 为 URI→`{assetId,kind,mimeType,bytes,sha256}`，kind=image/pdf/share-video；fileHashes、entityHashes、assetHashes、shareAssetHashes 全部精确重算。MP4 必须关联同包真实 GIF，保留原 bytes/hash，并使用原 ffprobe H.264/yuv420p 验证。图片用 Pillow 校验实际格式；PDF 检查 MIME 头及原字节/哈希，不重新排版或压缩。

资源 URI 精确为 `resources/images|pdfs|videos/<knowledgeId>/<filename>`。拒绝绝对路径、盘符、UNC、反斜线、空段、`.`/`..`、控制字符、冒号、百分号、URL 特殊字符、Windows 非法字符、设备名、尾空格/点、符号链接/junction/文件硬链接、NFC+casefold 碰撞。禁止包外资源、额外未登记文件或孤儿文件。

## 关系核心与外部引用

内部边两端都在本地 knowledge；保留原 id/sourceId/targetId/type 及原 sortOrder（若有）。只接受 canonical ASCII `sourceId < targetId`、id=`sourceId:related:targetId`、type=related，拒绝自环、反向边、重复边和两文件重复登记。

恰好一端本地时，external-relations 复制完整核心并加：

```json
{
  "id": "S006:related:S023",
  "sourceId": "S006",
  "targetId": "S023",
  "type": "related",
  "externalEndpointId": "S023",
  "targetPackageId": null,
  "resolutionPolicy": "resolve-when-installed"
}
```

externalEndpointId 必为缺失的那端，canonical source 也可在包外；提示未知为 null，不猜测包 ID，不作为硬依赖。每条外部边必须且只能有一端缺失；不能以外部关系放宽父节点/资产存在性，不能创建伪节点/搜索文档。

运行时缺目标保留 UNRESOLVED 记录并隐藏导航；同学科真实目标装入且通过冲突校验后派生 RESOLVED，卸载再退回 UNRESOLVED，重装恢复。状态不写回不可变包。全局按 relationId + `H(剥除 externalEndpointId/targetPackageId/resolutionPolicy 的原核心)` 合并；同 ID 同核心只出现一次，异核心拒绝。externalRelations 实体 hash 验完整记录，不能直接用于两侧全局核心去重。

## 独立校验和确定性 ZIP

`validate_module.py <ZIP或目录>` 无需另一模块或 Full 包即可校验结构/资源/哈希；`--source <Full v2>` 额外用原完整验证器校验来源，逐组比对精确 ID 集合、完整记录与顺序、内部及外部核心关系、媒体 hash。自洽地删整条知识或关系并重算所有摘要，仅凭独立包无法知道原件存在；来源一致性模式会拒绝，测试覆盖这一边界。哈希不是来源签名。

ZIP 按路径 UTF-8 字节排序；固定 1980-01-01 00:00:00；UNIX 普通文件 0644；STORE；无目录项、额外字段或注释，包内无构建时间/随机 ID。校验器接受 STORE/DEFLATE，拒绝加密、链接、重复/冲突路径、CRC/大小错误及未支持方法，先检查再流式提取。

主机校验上限：20,000 文件、单文件 512 MiB、总解包 2 GiB、单 JSON 32 MiB、路径 16 层；这些是 Python 主机策略，**不是 Android 容量验证**。Android 本地上限、磁盘/时间预算、安全解压与恢复机制需 Task 17C-Z 自行验证。目录和 ZIP 均会检查相同资源完整性。

与 Full v2 的差异仅为模块筛选、包身份/来源/能力/资源清单、external-relations、重算计数/摘要和独立 ZIP。Full v2 schema、hash、命令和默认输出均不变。v4 不能送入当前 v2 导入器，也不能声称 v3 候选已支持。
