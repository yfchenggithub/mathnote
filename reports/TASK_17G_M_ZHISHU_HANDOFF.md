# Task 17G-M — ZHISHU HANDOFF

日期：2026-10-16（Asia/Shanghai）。

MathNote 生产与完整性门 PASS；TASK 17G-M **CONDITIONAL PASS**；**17G-Z READY NO（当前消费端身份白名单阻碍）**。生产输入完整；条件不来自 Android 真机未参与。

正式目录：`D:/mathnote/build/zhishu-module-packages`；发布索引：`D:/mathnote/build/zhishu-module-packages/release-index.json`，14项按packageId排序，仅用于发布审计。Full v2继续只作MathNote内部中间产物，不作为App Runtime交付。

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

| 模块 / ZIP | contentVersion | packageHash | ZIP SHA256 |
| --- | --- | --- | --- |
| 解析几何 / analytic-geometry.zip | sha256:4ab3f6304d42752a46d1384766ad56f580f3b93de42266a515c4e0b6a9c34d3c | 6ccef9bd4af704938240d660d0335688c993af56f3bc424cad7b7bb10f4779b8 | d192575d307164b6f2ed19a366315d63be21874c196e7d82945ec79cd97e085e |
| 函数 / functions.zip | sha256:07e7258db967ca08cc1177a4a58d2f9201ee0a052bf385d5262a37d54d0ae029 | 627d7938516afbff0974a01d67789d3b8e892282aba203a1e42a2b5793242f2c | d262a3b34f83a18c8fff1727ecfb80724e0a486ed337ad60dd9aca68f28be9db |
| 不等式 / inequalities.zip | sha256:2545b554f9d6773b6157902af5ea58268521f8e5a33e47a26d3006327b3afd6b | 8be53e4a7e90b82ef31fed660751578b6a566ba3b1f7cbca7c00a9de5de36cc7 | f1cb714410ee4306206f253accac9095c8700d8ce3bc554f2c01a9e231c54b1b |
| 逻辑用语 / logic.zip | sha256:a4de18c1590812c7563c0870375c2269d0d80d39de644dcea59783f2a9dbf02d | f328b46d6f4698b10108f6ecdad6ee71d2051e933e47d39e2f022f753fd6ac24 | dad9b96c627638adf3e01fe5ffacaa06187d003db6074aa48348133586ee6e90 |
| 平面几何 / plane-geometry.zip | sha256:57c8ba7194914ffbd992c799c9a55a79e78fb910dc3977dc6ec70d7fb43ddfea | ef092ca6a2df3eb9150ee1700b3ad6e8bed100f5a843aaf5a47e292897a8203a | 7f761928e27a6250808204cb257e5af6770b82b2cfec6388fb9706429e74721d |
| 前置知识 / prerequisites.zip | sha256:ea43e3a661d35cbb26eee5b143477ecd7bc5b5af5e9fbde6d119d464e88fea80 | b7169af6c67dc882a4ed8c3b691ff713417e60e2d9f5607b6837d2008474f729 | 0018de004322b2f3b6d0a980884dcb933c01b5f33d19fdf1f3014dff5c3f071c |
| 概率 / probability.zip | sha256:42365650ed846d6bfa943e62552c376380e31641ec117ebfa5f6503dde4d0344 | ae5d6db2026fd054b763b953bedd6a63ba8c65b1c7c7587a16c0cd366aa99b60 | 1e93de8795903b7d527e268fc0a6a071f09a975fabfff6f0509d0d038757b12e |
| 数列 / sequences.zip | sha256:657e9aa5f37a46d7e510b0aaa6698f03379b7a413888bf2de7f4241f2ebd4ad7 | d7f603e901e247c8768ba1f76db485ae738a4a9c855cd9a3520de56800d047a9 | f4e5da0bc2ce0bb1d9cc823c03c406fd30075efc205d54f6291438d3146dcbc6 |
| 集合 / sets.zip | sha256:863078df25f8e210751df5b8f7256f711233b1fc920bc2911c5677a7b66b0204 | 4854299dc6ba963ec4ec4979342acf9d32508138c1774228bb0d67cc01acc113 | a01be102c036d6807c02e873a0cd840f17ad8a9d97c03668dc1a6289e3b43d4c |
| 立体几何 / solid-geometry.zip | sha256:d7152ef845089e3d36b9e70e38ec4fb35b43f68bbc5edc5a014d4bccc49b2be3 | fa3d5527b985f5c2d7ce5da63904168f6094b1bb993107c966ee5e0b398a8e20 | 7e3d7b7fd675268f3ba05aa3f73e5dc8e6b6c28bb706d63b66b67a638735e3fa |
| 统计 / statistics.zip | sha256:82ebe0e7ad810d183dded4b4f4d37f78ee2a7af87a6c26f939de7a0a6a438b5f | 3383901aa37049eb66567de0c7f142e5ce7e08b27998ae9d414ddaae97cde150 | d889e86eadb13ac51b8cc224771c28bc2ec4c84a4bff55ca053dfd6f57fdd444 |
| 解三角形 / triangle-solving.zip | sha256:dd156ad36d9cdefcb502a816c1214b543da91b426d0e00a5332c2f29f51c9ae5 | f24779930e17512cf3a601f9d3a0fd9acc550387bc069589abd6b70e807b5e2e | 20c4256790c853be0515ff99c362ac0ae38536791dfc02631969fad590867645 |
| 三角函数 / trigonometry.zip | sha256:f8297a253b1ee0e624aaccd1ae97cf20e822c8d80fb7327206815b24e52694a8 | 9b7a698ef1513f0d7d760f02cc31fc4b506f29064e598c4e84f3a198493e9902 | d94c89bc5763fa3fd90fa6d05578c39a6a5430799e638e881f3ab9f4a14bc1e9 |
| 向量 / vectors.zip | sha256:7a3d71fceada802273f1978dc2f5d2304762ee65b7678716d2922c918ca7f0b5 | 3ec394179ffb576279455cffd76cf5429276928b2e93e55ff44bbee41363fdea | 3f1ee9fa2b8da47606ec7eba8941e48c6d1baac0c4e9c6a4b8ac8f325bd254ac |

全部ZIP实际绝对路径：

- `D:/mathnote/build/zhishu-module-packages/analytic-geometry.zip`
- `D:/mathnote/build/zhishu-module-packages/functions.zip`
- `D:/mathnote/build/zhishu-module-packages/inequalities.zip`
- `D:/mathnote/build/zhishu-module-packages/logic.zip`
- `D:/mathnote/build/zhishu-module-packages/plane-geometry.zip`
- `D:/mathnote/build/zhishu-module-packages/prerequisites.zip`
- `D:/mathnote/build/zhishu-module-packages/probability.zip`
- `D:/mathnote/build/zhishu-module-packages/sequences.zip`
- `D:/mathnote/build/zhishu-module-packages/sets.zip`
- `D:/mathnote/build/zhishu-module-packages/solid-geometry.zip`
- `D:/mathnote/build/zhishu-module-packages/statistics.zip`
- `D:/mathnote/build/zhishu-module-packages/triangle-solving.zip`
- `D:/mathnote/build/zhishu-module-packages/trigonometry.zip`
- `D:/mathnote/build/zhishu-module-packages/vectors.zip`

总规模：572正式知识、1031唯一节点、572搜索文档、690媒体（117图/572PDF/1MP4）；ZIP总131389262 bytes，唯一媒体128954029 bytes；888唯一关系，其中18跨模块。14包共享原数学根，记录完全一致；每条正式知识owner唯一。36外部声明按canonical合并成18条跨包连接，目标均在全集。targetPackageId null符合原契约，通过实际knowledge owner解析。

已验证：源/Full一致、逐包Python Schema v4与source、全部媒体哈希、全集覆盖与父链、搜索原记录、关系canonical、两轮ZIP字节一致、原试点字节、正式索引与ZIP，以及知树真实哈希/所有权/关系元数据函数。未执行实际安装、Runtime激活或Android测试。

## 当前阻碍与下一阶段

知树当前 `MODULE_V4_REGISTRY` 仅登记集合、解析几何。只读执行真实 TypeScript Manifest 解析，2 包接受、另外 12 包以 `identity: unregistered/mismatched module identity` 拒绝；`normalizeCandidatePackageIds` 同样拒绝全量选择。未修改或绕过白名单。当前未修改的 App 不能直接安装/启用全部 14 包。

以下12个新增稳定身份需要后续获授权的Zhishu任务认领，不改变既有两个身份：

| 模块 | packageId | moduleId |
| --- | --- | --- |
| 函数 | zhishu.math.functions | math.functions |
| 不等式 | zhishu.math.inequalities | math.inequalities |
| 逻辑用语 | zhishu.math.logic | math.logic |
| 平面几何 | zhishu.math.plane-geometry | math.plane-geometry |
| 前置知识 | zhishu.math.prerequisites | math.prerequisites |
| 概率 | zhishu.math.probability | math.probability |
| 数列 | zhishu.math.sequences | math.sequences |
| 立体几何 | zhishu.math.solid-geometry | math.solid-geometry |
| 统计 | zhishu.math.statistics | math.statistics |
| 解三角形 | zhishu.math.triangle-solving | math.triangle-solving |
| 三角函数 | zhishu.math.trigonometry | math.trigonometry |
| 向量 | zhishu.math.vectors | math.vectors |

仅补登记还不能宣布Android通过；必须随后真实安装及激活14包。本任务未修改消费端或自动启动17G-Z。

1. 在支持14身份的消费端逐包导入ZIP，核对索引SHA256、Manifest能力、安装收据及媒体；任一包可独立安装。原集合/解析几何为相同发行包，按幂等导入处理，不强造更新版本。
2. 安装后一次启用全部14包，核对原根1个、唯一节点1031、正式知识572、owner无冲突，前置知识55条保持可浏览。
3. 全量搜索572知识ID并抽查中文公式、标题、摘要；检查装卸时搜索、Browse同步，无重复或遗漏。
4. 知识地图核对888唯一连接、18跨包连接全部resolved；仅安装单包或卸载目标时保留unresolved声明，重装恢复，不伪造节点，不因双端声明重复连接。
5. 实机核对690媒体的模块、assetId、持久目录URI；检查WebP/GIF/PDF/MP4分享、PDF进度和访问Gate。MP4只走animationShares，不进图片索引。
6. 验证收藏、学习状态、PDF进度、分享解锁与授权在更新/卸载/重装后按原ID关联。两试点没有新内容版本，不能用同包冒充异生产版本更新验收；17F真实不同版本更新遗留项仍待验。
7. 全规模冷启动、离线重启、内存、索引耗时、搜索/地图/页面性能与APK覆盖升级统一交17G-Z实测。当前包体积只是规模证据，不推测启动毫秒或内存。继续遵守安装时严格验证一次、兼容重启复用收据的既有规则。

未执行Sync、APK构建、Runtime重构、SQLite优化、三卡/GIF生产或源结论修订；交付到此停止。

