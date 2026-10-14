# Task 17A-M：MathNote Publisher 架构审计

状态：**审计完成；实现待确认**。范围仅限 MathNote；2026-10-14。`git status --short` 在审计前为空。未执行 `build-content`、Sync 或正式包写入。结论中的 VERIFIED 是源码或正式源数据所证实，不等于模块包已构建成功。

## 总体结论

**CONDITIONAL YES**：可以在完整 v2 发布结果上增加独立的模块切片与打包步骤，保留原 `build-content`。但不能把完整包的 JSON 简单过滤后仍声称它是合格的 v2 包：现有验证要求单根树、关系端点和资源均在包内，而正式数据有 18 条跨一级分类关系。需要明确模块包 schema、跨包引用和安装端解析契约；这些均为 PROPOSED，尚未由 Zhishu 验证。

## 真实调用链（VERIFIED）

1. [`publish.py`](../scripts/zhishu/publish.py#L42) `build_parser` 声明 `build-content`，只支持 `--prepared-assets`、`--output`、`--allow-video-removal`，没有 `--module`；默认输出为 `build/zhishu-content-package`（第 39、87–104 行）。
2. [`publish.py`](../scripts/zhishu/publish.py#L260) `main` 调用 `scan_repository` → `prepare_runtime_images` → `verify_prepared_runtime_images` → `map_runtime` → `build_package`（第 290–309 行）；任一步失败返回非零或异常，正式输出不应被替换。
3. [`source_discovery.py`](../scripts/zhishu/source_discovery.py#L10) `MODULE_NAMES` 固定 11 个源目录；`scan_repository` 只枚举这些目录的直接子目录，读取 `meta.json` 并验证 JSON（第 65–105 行）。分类边界实际来自 `knowledgeNode`，不是源目录名。
4. [`asset_preparation.py`](../scripts/zhishu/asset_preparation.py#L83) `prepare_runtime_images` 为所有 UID 建立图片镜像，经 Node/Sharp 将 PNG 转 WebP、GIF 原样保留；使用临时目录、旧目录备份和替换（第 83–145 行）。`verify_prepared_runtime_images` 校验源和输出哈希、工具版本、文件覆盖（第 147 行起）。Node 实现见 [`prepare_knowledge_images.mjs`](../scripts/zhishu/prepare_knowledge_images.mjs#L21)，会拒绝不支持的图片与输出名冲突。
5. [`runtime_mapping.py`](../scripts/zhishu/runtime_mapping.py#L206) `_load_sources` 读 `meta.id`、`core.title`、`knowledgeNode`；`_build_nodes` 从知识路径生成一个固定高中数学根、一级 `chapter`、后续 `section` 与结论 `knowledge`（第 256–306 行）。结论 ID 就是 `meta.id`；结构 ID 是 `struct:<完整路径>`；同级 `sortOrder` 按标题和 ID 重算。`_build_relations` 只消费 `relations.related_ids`，按端点字典序去重为 canonical 无向 related；目标必须存在于全集（第 308–347 行）。
6. [`runtime_mapping.py`](../scripts/zhishu/runtime_mapping.py#L350) `_build_assets` 从预处理图片目录和 UID 的 `pdfs/` 映射 `KnowledgeAsset`，ID 为 `<UID>:<image|pdf>:<文件名>`，URI 为 `resources/<images|pdfs>/<UID>/<文件名>`；`_build_search_documents` 对每个结论从 `core/search/searchmeta/ranking` 生成一条搜索文档（第 390–438 行）；`_validate_runtime` 验证 ID 唯一、父节点、关系端点、资源所属节点和搜索覆盖（第 444–505 行）。
7. [`content_package.py`](../scripts/zhishu/content_package.py#L646) `build_package` 默认 schema v2；`load_share_videos` 扫描正式 `videos/share_assets.json`，验证 GIF/MP4 对应、大小、哈希与编码（[`share_videos.py`](../scripts/zhishu/share_videos.py#L91)，第 194 行起）。构建器写四个实体 JSON、`animation-shares.json` 和 `resources/`，复制 PDF 与视频，计算实体/文件/资源哈希，生成 Manifest；先对临时包调用 `validate_package`，检查视频移除，再 `_safe_replace_directory` 替换输出（第 679–768 行）。
8. [`content_package.py`](../scripts/zhishu/content_package.py#L374) `validate_package` 检查形状、ID 唯一、**恰好一个 root**、父节点及关系端点存在、资源精确覆盖、视频关联、各级哈希、计数及 `contentVersion == sha256:<packageHash>`（第 451–606 行）。包格式是**目录**，现行代码不生成 ZIP。

真实数据流：正式六段 TeX/PDF 与 `meta.json`、UID `images/`、`videos/share_assets.json` → 扫描与图片预处理 → Runtime DTO → v2 包目录 `build/zhishu-content-package` → 未来由 Zhishu 消费。六段 TeX 在此链路中并不被解析为结论正文；当前 DTO 内容主要来自 `meta.json`，PDF 则作为已有文件复制。这是源码可证实的边界，不能假定模块包自动包含六段 TeX。

## 五个主要耦合点

| 耦合 | 源码依据 | 模块影响 |
| --- | --- | --- |
| 固定数学源目录与根节点 | `source_discovery.MODULE_NAMES`；`runtime_mapping.ROOT_NODE_ID`、`_build_nodes` | 跨学科需可配置发现和 subject/root 契约；按源目录切片会错分多种一级分类。 |
| 全集存在性 | `_build_relations`、`_validate_runtime`；`validate_package` 第 489–515 行 | 单模块中外部关联端点缺失；当前 v2 校验拒绝，不能静默丢弃而宣称关联无损。 |
| 结构和顺序由全集重算 | `_build_nodes` 第 256–306 行 | 重建子集可能改变同级 `sortOrder`；必须从全集复制原节点记录与祖先路径。 |
| 图片镜像全量重建 | `prepare_runtime_images`；`_build_assets` | 原生模块发布仍会付出全量预处理成本；后处理切片可避免新建第二套数学映射。 |
| Manifest/资源封闭世界 | `build_package`、`validate_package` | 需重算每个模块的计数和哈希，并定义外部引用、包 ID/版本，不能复用全集 Manifest。 |

## 失败与验证边界

预处理镜像先生成到临时目录，再替换镜像；若此后映射或包构建失败，**图片镜像可能已更新，而旧正式包仍在**。包构建在临时目录验证成功才替换输出；`_safe_replace_directory` 对替换失败有备份恢复（第 609–625 行）。`build_package` 对映射错误返回 `PackageBuildResult.errors`，对包构建中的 `OSError/ValueError/JSONDecodeError` 返回错误；CLI 以非零退出。该审计未在正式输出上实测故障恢复。

只读源扫描实得 572 个 UID、零扫描错误；针对 Publisher 与包的现有 30 项单元测试运行通过。**更新后补充核验（2026-10-14）**：`build/zhishu-content-package` 确为无参数 `build-content` 的默认输出目录，目录实际存在，Manifest 为 schema v2，`validate_package` 返回 **0 项问题**；包内有 1,031 节点、888 关系、572 搜索文档、689 条资源登记（117 图片、572 PDF）和 1 个 MP4 分享关联，共 690 个资源文件，整个目录 131,012,637 字节。`contentVersion` 为 `sha256:4ca08754bc494571ee02e576aa75c1bf122a4d29db699ef51c57366bbd80fdc7`。用户要求普通进程可读后，仅对当前正式包目录增加当前账户的 `(OI)(CI)(RX)` ACL；普通沙箱进程已成功读取 Manifest 并运行 `validate_package`，返回 **0 项问题**。该目录原 ACL 关闭继承；后续完整重建会替换目录，需复核新目录权限。

**当前源覆盖通过**：`verify_prepared_runtime_images` 通过，117 个源图片 URI 与包内 117 个图片 URI 完全一致，包含 C079/C080 各 3 张新图；四组 DTO 记录与当前元数据映射相等，视频登记相等，572 份 PDF 与当前源字节一致。该包可作为当前 MathNote 完整 v2 内容的已验证只读输入；模块切片和 Android/Sync 消费能力仍为 **PENDING**。详见库存与交接报告。

## 跨学科适配边界

[`source_discovery.MODULE_NAMES`](../scripts/zhishu/source_discovery.py#L10) 和 [`runtime_mapping.ROOT_NODE_ID`](../scripts/zhishu/runtime_mapping.py#L21) 明确绑定当前高中数学；`_build_nodes` 将顶层路径解析为数学根下的 chapter。结论 ID 来自 `meta.id`，映射器**没有**强制 C/G/R 等 UID 前缀；新包格式不应加入此前缀假设。`SearchDocument.category`、关键词和公式字段从 `meta` 原样映射，字段结构可复用，但当前内容多为数学术语；新增学科时要验证搜索语义。`KnowledgeAsset.type` 当前只有 image/pdf，MP4 是独立分享关系；物理等学科若需音频、交互仿真或不同视频用途，需另行扩展，而不能滥用现有 MP4 分享字段。未来新学科还需改源发现白名单/根节点策略，但本次不增加学科内容或改动现有 Publisher。
