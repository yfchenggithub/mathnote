# Task 17B-M — Content Audit

日期：2026-10-15（Asia/Shanghai）。数据全部从实际包统计；完整机器证据：`build/task17b-evidence/delivery-audit.json`（含完整节点 section/knowledge ID、Manifest 和外部关系），非人工预填计数。

正式来源 `sha256:4ca08754bc494571ee02e576aa75c1bf122a4d29db699ef51c57366bbd80fdc7`：schema 2；1,031 节点、572 knowledge/搜索、14 一级 chapter、888 canonical related、18 唯一跨分类边；117 图片、572 PDF、1 MP4，共 690 媒体文件，包内总文件 696，总字节 131,012,637。**与用户提供的已审计基线一致，无数量或版本差异**。旧 17A-F 的 579 口径未提供原始清单；本任务以真实 Full v2 精确 ID 为准，不推测其差额、不增删知识以凑数。

| 指标 | 集合 | 解析几何 |
| --- | --- | --- |
| packageId | `zhishu.math.set` | `zhishu.math.analytic-geometry` |
| Module Content Version | `sha256:863078df25f8e210751df5b8f7256f711233b1fc920bc2911c5677a7b66b0204` | `sha256:4ab3f6304d42752a46d1384766ad56f580f3b93de42266a515c4e0b6a9c34d3c` |
| Envelope packageHash | `4854299dc6ba963ec4ec4979342acf9d32508138c1774228bb0d67cc01acc113` | `6ccef9bd4af704938240d660d0335688c993af56f3bc424cad7b7bb10f4779b8` |
| Module Root | `struct:集合` | `struct:解析几何` |
| 节点数（含数学根） | 25 | 180 |
| 正式结论数 | 12 | 105 |
| SearchDocument 数 | 12 | 105 |
| 图片数（含 GIF） | 3 | 100 |
| PDF 数 | 12 | 105 |
| MP4 数 | 0 | 1 |
| 内部关系数 | 13 | 192 |
| 跨模块关系数 | 3 | 3 |
| ZIP 大小（bytes） | 2409052 | 37408410 |
| ZIP SHA-256 | a01be102c036d6807c02e873a0cd840f17ad8a9d97c03668dc1a6289e3b43d4c | d192575d307164b6f2ed19a366315d63be21874c196e7d82945ec79cd97e085e |
| 总媒体资源数 | 15 | 206 |
| 后代 section 数 | 11 | 73 |

两个 ZIP 绝对路径：

- `D:\mathnote\build\zhishu-module-packages\sets.zip`
- `D:\mathnote\build\zhishu-module-packages\analytic-geometry.zip`

共同 subject root 为 `root-high-school-math`。集合=原根+1 chapter+11 section+12 knowledge；解析几何=原根+1 chapter+73 section+105 knowledge。保留共同根能完整保留原 parentId，不产生悬空树，也不重新定义数学根。

边界通过独立的“逐节点向上查父链”核对，与切片器向下收集结果做精确集合比较。所有原节点完整记录和数组顺序、搜索完整记录、资产/视频记录逐项相同；资源逐文件直接比较原字节，而非抽样或仅比较总数。全部选中原实体 hash 与 Full v2 登记相同。正式 knowledge ID 交集为空；两包资源 URI 交集为空，跨包资源内容 hash 交集也为空；没有实际共享媒体要依赖另一 ZIP。

真实一级 chapter 下直属分支：集合为“集合的概念与运算”；解析几何为“圆”“圆锥曲线”“椭圆”“直线”，原 sortOrder=10/20/30/40。双曲线和抛物线等属于真实后代树，未凭人工概念重排层级。解析几何知识 ID 含 C 和 P 两组，C025/C026 不在此子树；未按 03_conic 或 UID 前缀过滤。

集合全部 knowledge ID：`S001, S003, S005, S006, S011, S012, S013, S014, S015, S016, S017, S025`。

解析几何全部 knowledge ID：`C001, C002, C003, C004, C005, C006, C007, C008, C009, C010, C011, C012, C013, C014, C015, C016, C017, C018, C019, C020, C021, C022, C023, C024, C027, C028, C029, C030, C031, C032, C033, C034, C035, C036, C037, C038, C039, C040, C041, C042, C043, C044, C045, C046, C047, C048, C049, C050, C051, C052, C053, C054, C055, C056, C057, C058, C059, C060, C061, C062, C063, C064, C065, C066, C067, C068, C069, C070, C071, C072, C073, C074, C075, C076, C077, C078, C079, C080, C081, C082, C083, P001, P002, P003, P004, P005, P006, P011, P012, P013, P014, P015, P016, P017, P018, P019, P020, P021, P022, P023, P024, P025, P026, P027, P053`。

| 模块 | relationId | 包外端点 | 真实外部 chapter |
| --- | --- | --- | --- |
| sets | `S006:related:S023` | `S023` | `struct:逻辑用语` |
| sets | `S011:related:S023` | `S023` | `struct:逻辑用语` |
| sets | `S012:related:S023` | `S023` | `struct:逻辑用语` |
| analytic-geometry | `C023:related:C025` | `C025` | `struct:立体几何` |
| analytic-geometry | `C023:related:C026` | `C026` | `struct:立体几何` |
| analytic-geometry | `P025:related:P052` | `P052` | `struct:平面几何` |

这 6 个边界核心分别逐条回查 Full v2，原 id/sourceId/targetId/type 不变，targetPackageId 均 null。两个试点间没有真实跨边；互装不会补齐上述目标。全量 18 条跨分类边仅做来源只读统计，本任务未生产其他 12 模块，不将“双包 6 条”冒称全集所有边的切片端到端覆盖。
