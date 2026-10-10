# Task 14C.MP4.2A — MathNote Single Canonical Publisher

日期：2026-10-10。状态：**MATHNOTE DEFAULT PUBLISH PASS · SINGLE SCHEMA V2 · C002 MP4 INCLUDED**。本任务只在 MathNote 完成；未运行 Zhishu Sync、Android 构建或 Git 提交。

## 1. Pre-flight Audit

先读取根 `AGENTS.md`、数学渲染架构契约、Publisher 实现和测试、Task 14C.MP4.1 正式 v2 契约及 C002 `videos/share_assets.json`。工作树开始时只有 `scripts/zhishu/__pycache__/content_package.cpython-314.pyc` 已修改；该既有改动未重置。正式默认目录 `D:\mathnote\build\zhishu-content-package` 当时存在 v1 包，版本 `sha256:b289b18501c57d656580170b363d2cea38e790dcd9ac7a1ae5189ba0bce4ce1b`。

C002 正式 MP4 源文件为 545,671 字节，SHA-256 `1a09bc46118dff27770035efa4327588a4dc252730430862918cd98753f28c74`，与源登记一致。本任务授权全体正式知识源的视频登记扫描及一次正式默认发布；没有修改正式 GIF、TeX、PDF、Manim Scene 或其他 UID 资源。

## 2. Default Publisher Root Cause

旧 `publish.py` 只在使用 `--share-video-uid C002` 时向 `build_package` 传入视频选择，且拒绝默认输出路径。旧 `content_package.py` 据该参数选择 v2；无参数时固定构建 v1，因而默认包没有 C002 MP4 和 GIF→MP4 关系。这是 Zhishu 从默认包读取时视频降级的直接原因。

## 3. Single Schema v2 Implementation

`build-content` 与 `build-package` 现在默认都生成 `schemaVersion: 2`。无参数 `build-content` 使用默认准备目录，并发布到唯一正式目录 `D:\mathnote\build\zhishu-content-package`。v2 始终包含 `animation-shares.json` 及既定 Manifest 字段；无登记视频时，关系文件为 `[]`，`counts.animationShares` 和 `counts.videoAssets` 均为 `0`，`shareAssetHashes` 为 `{}`，不新增契约结构。`schemaVersion` 校验及未知版本拒绝仍保留。

历史 v1 构建仅保留为 Python API 的显式迁移测试能力，且被禁止写入正式默认目录；CLI 日常构建不提供 v1 选择。代码继续先在临时目录完成资源复制、Manifest 生成和整包验证，再原子替换目标包。默认构建不会因视频发现失败退回 v1。

若已有有效 v2 包包含的视频在新扫描结果中消失，Publisher 报出被移除的 MP4 Asset ID，保留旧包。只有经明确审查后传入 `--allow-video-removal` 才允许该删除。损坏、缺失、未登记视频或无效关联均使构建失败，不能通过该删除开关跳过源验证。

## 4. Automatic MP4 Discovery

Publisher 遍历既有白名单 Source Discovery 找到的正式知识源，检查各 UID 的 `videos/share_assets.json`。不硬编码 C002，不根据 GIF 文件名猜测 MP4；逐项核对 `displayAssetId`、GIF URI/源哈希、`shareAssetId`、MP4 URI、MIME、大小、SHA-256 及真实 MP4 格式。重复或交叉关联、孤儿 MP4、未登记文件和符号链接目录被拒绝。未来新增正式登记视频无需修改命令或 Publisher UID 列表。

测试使用 C002 两个 GIF 的配对 fixture 和另一个 UID 的配对 fixture，验证多动画及跨 UID 的自动收录；未批量生产真实新视频。

## 5. Default Content Package Verification

先在 `build/validation/14C_MP4_2A/` 隔离目录完成完整 `build-content`，零错误、零警告。随后**不加任何额外参数**，两次执行：

```powershell
cd D:\mathnote
python.exe .\scripts\zhishu\publish.py build-content
```

两次正式执行均零错误、零警告，并得到相同 `contentVersion`、`packageHash`、总大小和计数。默认正式包的实际 `schemaVersion` 为 `2`；`contentVersion` 是 `sha256:a888e7e7b2e4f1ad8b4b5320922e45e4c08b5789c4406dc67ea9a897f1570c44`，总大小 127,099,285 字节。其计数为 1,030 KnowledgeNodes、32 Relations、667 原有 KnowledgeAssets（96 图片、571 PDF）、571 SearchDocuments、1 AnimationShare、1 VideoAsset。独立调用 `validate_package` 返回 0 项问题。

正式包的四个原有运行时 JSON、`animation-shares.json`、Manifest 和 C002 MP4 与隔离验证包逐文件 SHA-256 相同。C002 图片顺序仍是 `001.webp`、`002.webp`、`003.webp`、`004.webp`、原 GIF，sortOrder 分别为 10、20、30、40、50；GIF SHA-256 仍为 `1ad4d074699a3d193627bb0cbeadd7fdbedc53e833e8772fd9f0584494f9a5ad`。

## 6. C002 GIF→MP4 Verification

| 字段 | 正式包实际值 |
| --- | --- |
| GIF Asset ID | `C002:image:ellipse_line_distance.gif` |
| GIF 逻辑 URI | `resources/images/C002/ellipse_line_distance.gif` |
| MP4 Asset ID | `C002:share-video:ellipse_line_distance.mp4` |
| MP4 逻辑 URI / 包内路径 | `resources/videos/C002/ellipse_line_distance.mp4` |
| MIME | `video/mp4` |
| MP4 大小 | 545,671 字节 |
| MP4 SHA-256 | `1a09bc46118dff27770035efa4327588a4dc252730430862918cd98753f28c74` |

正式包 `animation-shares.json` 以精确 GIF Asset ID 显式指向上述 MP4 Asset ID；Manifest `files.animationShares`、两个视频计数及 `shareAssetHashes` 与文件实物吻合。MP4 未进入 `knowledge-assets.json` 图片列表。

## 7. Automated Test Results

- Publisher、Content Package、资产准备、Runtime Mapping 和架构边界套件：**65 项 PASS**。覆盖默认 v2、空视频 v2、历史 v1、跨 UID 自动发现、多 GIF、缺失/损坏/未登记视频、错误关联、重复输出、发布失败保留旧包，以及显式删除保护。
- 隔离完整 `build-content`：**PASS**，0 错误、0 警告；结果与 Task 14C.MP4.1 已验证的 v2 版本一致。
- 正式无参数 `build-content` 两次：**PASS**，版本和计数一致，C002 MP4 均保留。
- 正式目录整包 `validate_package`：**PASS**，0 项问题；实物 MP4 与 Manifest SHA-256、源 SHA-256 一致。
- `git diff --check`：**PASS**（仅有 Git 行尾转换提示）。

## 8. Changed Files

- `scripts/zhishu/share_videos.py`：扫描所有正式 UID 的视频源登记。
- `scripts/zhishu/content_package.py`：默认 v2、空视频 v2、历史 v1 隔离及视频移除保护。
- `scripts/zhishu/publish.py`：无参数正式 v2 发布及可选移除确认开关。
- `tests/test_zhishu_share_videos.py`、`tests/test_zhishu_publish.py`：新场景与 CLI 回归。
- `AGENTS.md`、`docs/architecture/math-rendering-boundaries.md`、`scripts/zhishu/README.md`：更新已批准的正式发布边界和操作说明。
- 本报告。

## 9. Git Status

上述 MathNote 代码、测试、文档为本任务修改；本报告为新增。`scripts/zhishu/__pycache__/content_package.cpython-314.pyc` 在任务开始时已是修改状态；未对其执行还原，运行指定的 `python.exe` 命令可能再次更新缓存字节，该文件不属于本任务源码修改。未执行全局 reset/clean。`build/` 中的隔离及正式包是构建产物。没有 Git 提交。

## 10. Zhishu Handoff

Zhishu 的正式输入现在是 `D:\mathnote\build\zhishu-content-package`，默认始终为 schema v2。Sync 应按 Task 14C.MP4.1 契约读取 `animation-shares.json`、复制并验证 `resources/videos/`，用 GIF Asset ID 查找 MP4 Asset ID/URI；原图片/PDF Registry 含义保持不变。现有旧版 Sync 只接受 v1，不能直接读取新的正式默认包。此消费端升级属于下一阶段；本任务没有运行或修改 Zhishu Sync。
