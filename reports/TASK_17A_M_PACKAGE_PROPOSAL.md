# Task 17A-M：独立知识包格式建议

状态：**PROPOSED**；2026-10-14。现行正式格式是 schema v2 的**目录**，含 `manifest.json`、`knowledge-nodes.json`、`knowledge-relations.json`、`knowledge-assets.json`、`search-documents.json`、`animation-shares.json` 与 `resources/`；源代码见 [`content_package.py`](../scripts/zhishu/content_package.py#L30) 的文件常量、[`build_package`](../scripts/zhishu/content_package.py#L646) 和 [`validate_package`](../scripts/zhishu/content_package.py#L374)。现行 CLI 不生成 ZIP、无 packageId/moduleId、无最低 App 版本和包依赖字段。以下结构不能当作已实现能力。

## 建议的模块包契约

建议复用 v2 的四个 DTO JSON、资源 URI、`animation-shares.json`、canonical JSON/文件/资源 SHA-256 规则，新增 **module package schema v3**（或独立封套版本；编号待 Task 17A-Z 确认）。ZIP 仅作分发容器，内部仍用相同相对路径：

```text
zhishu.math.set.v1.zip
  manifest.json
  knowledge-nodes.json
  knowledge-relations.json
  knowledge-assets.json
  search-documents.json
  animation-shares.json
  external-relations.json        # 待安装目标的跨包关联
  resources/images/<UID>/...
  resources/pdfs/<UID>/...
  resources/videos/<UID>/...
```

`manifest.json` 的建议新增字段：`packageId`（稳定，如 `zhishu.math.set`）、`subjectId`（如 `math.high-school`）、`moduleId`（稳定、与显示名称分离，如 `set`）、`packageKind`（`module` 或 `collection`）、`rootNodeId`、`packageVersion`、`minAppContentApi`、`dependencies`、`files.externalRelations`、`counts.externalRelations`。现有 `schemaVersion` 表示文件/语义契约版本，`contentVersion` 继续由内容哈希得出。`packageVersion` 是发行序号或语义版本，允许相同内容重打包时保留版本，也要求更新顺序明确；不能单靠 `contentVersion` 表示 V1.1 的业务版本。`subjectId`、`moduleId` 不从中文标题或 UID 前缀推断，应由受控登记表映射到一级结构 ID。上述字段均须在 Zhishu 端验证后冻结。

**ID 不变原则**：结论 `knowledgeId` 保持 `meta.id`；结构节点使用当前 `struct:<完整路径>`；图片/PDF 资产 ID 保持 `<UID>:<type>:<文件名>`，MP4 使用当前 `<UID>:share-video:<文件名>`。同一结论出现在数学全集和专题包时，ID 与实体内容哈希必须相同。安装端对相同 ID+哈希去重或按包引用计数，对相同 ID 不同哈希按确定优先级拒绝/升级，绝不生成第二套 ID。若源内容变化但 ID 不变，版本和内容哈希随之变化。

## 树、关系、搜索与资源规则

- 从完整正式包选择一级 chapter 的后代及共同根；**复制原节点记录**，保留 `parentId`、`sortOrder`、原结构路径。旧 `validate_package` 要求恰好一个 root；模块包可保留 `root-high-school-math` 作为路径上下文，但同一节点跨包安装的合并策略需 Zhishu 确认。未来其他学科需要学科根，而非永久复用高中数学根。
- 内部两端均在本包的关系留在 `knowledge-relations.json`；有一端在本包之外的 canonical `related` 保留到 `external-relations.json`，含原 relation ID、`sourceId`、`targetId`、`type`、`targetPackageId`（若可知）与 `resolutionPolicy`。目标包未安装时呈“不可跳转/可提示安装”，安装后按全局 knowledgeId 解析。**不能**静默删除这 18 条关系，也不能往知识树塞无完整内容的假结论。旧 v2 验证器不接受缺失端点，故模块 schema 校验必须新增这一语义。
- 搜索只包含本包结论的原 `SearchDocument`；不按全集位置重排、不重算排名字段。多个包安装后的全局去重、排序与词典组合由 Zhishu 处理；跨包搜索效果未验证。
- 资源集精确等于所选 `KnowledgeAsset.uri`、关联 GIF 的 MP4 URI，目录不得有孤儿文件。图片已转 WebP、GIF 和 PDF 字节沿用完整包，MP4 单独通过 `animation-shares.json` 关联。每个相对 URI 做路径安全检查，校验大小与 SHA-256；允许不同包持有相同字节，冲突按稳定 Asset ID+哈希裁决。当前 690 个正式源资源中未发现跨一级分类字节完全相同文件，但设计不能依赖这一偶然现状。
- `manifest.fileHashes`、`entityHashes`、`assetHashes`、`shareAssetHashes` 与 `packageHash` 在切片后**重新计算**；定义并测试 ZIP 条目排序、时间戳归一、路径大小写和压缩参数，以便包文件本身可重复生成。最低兼容 App 内容 API 与模块 schema 由 Task 17A-Z 协商。现阶段只需哈希/完整性；包级数字签名、加密、付款授权均不实现。分发信任来源及签名需求留待产品/安装设计验证。

## 全集与专题的关系

无参数 `build-content` 仍产出原 v2 完整数学目录，不改字段、排序或资源。未来“数学全集包”可以是现有 v2 完整包的分发封装，或一份带 `packageKind=collection` 的 v3 包清单；二者的 Android 安装/升级语义须先确认。模块包须能从同一完整包确定性切出。对已有 v2 包绝不可原地加入 v3 字段后仍称其为兼容 v2。

## 必须新增的模块验证（PROPOSED）

校验 packageId/moduleId/subjectId 唯一与稳定；节点集合等于选定子树加祖先；所有本地父节点与本地关系端点存在；外部关系的原始 ID/端点可在完整包回查；搜索和资源覆盖恰好等于本地结论；视频登记仍精确匹配 GIF；内容/文件/资源哈希完整；与完整包共享的节点、搜索、资产记录逐实体字节一致。全集 v2 的 [`validate_package`](../scripts/zhishu/content_package.py#L374) 应继续独立运行，不放宽其校验条件。
