# Task 17B-M → Task 17C-Z — Zhishu Handoff

日期：2026-10-15（Asia/Shanghai）。**MODULE PACKAGE PASS / ZHISHU IMPORT PENDING**。已完成 MathNote 生产侧；未修改 Zhishu、未运行 Sync、未安装包、未构建 APK、未进入 17C-Z。

| 模块 | ZIP 绝对路径 | bytes | SHA-256 |
| --- | --- | ---: | --- |
| 集合 | `D:\mathnote\build\zhishu-module-packages\sets.zip` | 2409052 | `a01be102c036d6807c02e873a0cd840f17ad8a9d97c03668dc1a6289e3b43d4c` |
| 解析几何 | `D:\mathnote\build\zhishu-module-packages\analytic-geometry.zip` | 37408410 | `d192575d307164b6f2ed19a366315d63be21874c196e7d82945ec79cd97e085e` |

来源 Full v2 为 `sha256:4ca08754bc494571ee02e576aa75c1bf122a4d29db699ef51c57366bbd80fdc7`。包 schemaVersion=4；packageId 分别为 zhishu.math.set / zhishu.math.analytic-geometry，moduleId 分别 math.set / math.analytic-geometry，subjectId=math.high-school；packageVersion=1。Manifest/资源/关系/哈希详细契约见 [Module Contract](TASK_17B_M_MODULE_CONTRACT.md)，实际清单见 [Content Audit](TASK_17B_M_CONTENT_AUDIT.md)。module 名称读取原 chapter.title；所有原 knowledgeId/assetId/parentId/sortOrder 保留，数学根仍 root-high-school-math。

**必须先认领版本修订**：17A-F 候选 v3 的 contentVersion 包含 sourcePackage，与本次独立内容版本要求冲突，因此使用显式 v4，不冒充原候选 v3。v4 packageHash 覆盖全部 Manifest（除自身及 contentVersion），contentVersion 对该载荷再排除 sourcePackage/packageVersion。同内容新来源可保留 contentVersion，但 envelope/packageHash/发行号变化。安装版本重复/冲突判断不能只比较 contentVersion。requiredCapabilities 使用 package-schema-v4；当前 v2/v3 消费器必须明确拒绝未知 v4，不能直接改 schema 数值绕过校验。

现阶段可独立在 Python 主机验证（不安装）：

```powershell
python.exe -B D:\mathnote\scripts\zhishu\validate_module.py D:\mathnote\build\zhishu-module-packages\sets.zip
python.exe -B D:\mathnote\scripts\zhishu\validate_module.py D:\mathnote\build\zhishu-module-packages\analytic-geometry.zip
```

需要追溯原始 Full 快照时加 `--source D:\mathnote\build\zhishu-content-package`，检查精确 ID 集合、逐记录/关系和全部资源 hash。独立结构校验不需要另一 ZIP；外部关联是软引用，不是安装硬依赖。独立 hash 只证明内部一致性，可信来源/签名和 Android 容量策略仍由后续消费端决定。

## 后续独立安装流程（待实现，不是当前 App 命令）

1. 先用共同 fixture 对齐 Python canonical，包括 1/1.0/-0.0/指数/中文/None/null/反斜线；认领 schema v4 两种 hash 的精确投影。不要用 JSON.stringify 直接替代 Python 序列化。保留旧 Full v2 支持和内置回退。
2. PackageManager 选择单个 ZIP，校验 schema/API/全部 requiredCapabilities，按本地策略安全解压至隔离暂存，验证精确文件/实体/资源清单、父链、搜索、关系和所有 hash。任一包可单独验证；不要求另一包已安装。
3. 建立 packageId+packageVersion+packageHash 注册和实体所有权；同学科同 ID 同 hash 共享（包括共同数学根），同 ID 不同节点/搜索/媒体 hash 拒绝。相同 URI 解析在各自包版本命名空间内，不按安装顺序覆盖。一次可恢复事务提交完整 registry+generation，失败继续旧内容。
4. 包文件放入 App 私有持久版本目录，不能仅留 cache；聚合 Repository 保持原对外接口。generation 同时更新树、Browse、搜索、资产和可见关系。保留现有匹配排名算法，搜索按原 knowledgeNodeId 去重。
5. URI 适配器把相对资源路径解析为当前持久版本实际 file URI；对 WebP/GIF 实际解码，生成并持久化 assetId+内容 hash 对应宽高缓存（本次 Manifest 不发 width/height）。验证失败不假设方形；PDF 直接使用持久文件 URI，分享 MP4 由原 animationShares 查表并适配 Android content URI/权限。原包 JSON 不写 file:// 或 content://。
6. 打开的 PDF/分享持有旧版本文件租约，更新/卸载延迟清理。包 registry 与收藏/学习记录/PDF 进度/永久分享解锁/license 分开；知识和资产原 ID 不变，重装按原 ID 重新关联，安装不等于授权。

## 外部关系与合并

按 relationId + 原核心 canonical hash 去重，剥除 externalEndpointId/targetPackageId/resolutionPolicy；提示元数据不同不造成伪冲突。同 ID 核心不同拒绝。未安装目标保存 UNRESOLVED，当前导航图隐藏；目标装入→RESOLVED，卸载→UNRESOLVED，重装恢复。无目标假节点，不借内置 fallback 的隐藏端点伪装已安装。

真实集合边是 S006/S011/S012→S023（逻辑用语）；解析几何边是 C023→C025/C026（立体几何）、P025→P052（平面几何）。**集合+解析几何互装不会使这六条边 resolved**。可用受控合成目标 fixture 或同源全集 owner 测恢复与去重，不能擅自生产其他正式模块。canonical source 在包外也已由 MathNote 合成测试覆盖。

## 后续真实门禁

schema v4/hash profile 的 Zhishu 认领及跨语言共同 fixture 尚 PENDING；当前 App 支持模块 ZIP 的事实未建立。文件选择、安全解压/空间上限、持久化事务/崩溃恢复、双包树/搜索聚合、关系装卸恢复、WebP/GIF 尺寸与动画、PDF 页数/旋转/访问 Gate/进度、MP4 chooser 成功取消/URI 权限、离线重启、用户数据与授权保持，均未在本任务进行 Android 验证。

17A-F 旧环境/579 来源问题保留为历史审计项，不推测其现在已修复；本任务已验证当前 MathNote 572 原正式 Full 输入可读且完整，不因此宣称 Zhishu generated 环境健康。Task 17C-Z 应按其最新实际环境与既有任务门禁继续。

交付止于这两包、工具、测试和五份报告。当前没有可诚实提供的 Zhishu 模块“安装命令”；上文是下一阶段接口实施流程，不声称现有 App 已能消费。等待用户开启下一任务，不自动执行。
