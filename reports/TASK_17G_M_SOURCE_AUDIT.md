# Task 17G-M — SOURCE AUDIT

日期：2026-10-16（Asia/Shanghai）。

SOURCE AUDIT PASS / MODULE DISCOVERY PASS。

冻结源 Git HEAD：`79d55747168c6b2a337cd3dadf0b2af4d2ba50f5`；开始时工作树无已有改动。Full v2 内容身份：`sha256:4ca08754bc494571ee02e576aa75c1bf122a4d29db699ef51c57366bbd80fdc7`。完整 Manifest、696 个输入文件 SHA256、最终工具哈希在 `build/task17g-evidence/input-freeze.json`；每条 knowledgeId、源 meta 路径、knowledgeNode 与 chapter 在 `source-records.json`。

现有正式 Full 通过原 validator。使用原 `publish.py build-content` 流程隔离重建（`--prepared-assets build/task17g-evidence/runtime-assets --output build/task17g-evidence/full-regression`），Errors 0 / Warnings 0；全部 696 文件与正式包及任务前快照逐文件哈希一致，无需原地重建正式 Full。未手工修改 Runtime JSON。

| 指标 | 实际 | 历史基线 | 差异 |
| --- | --- | --- | --- |
| 节点 | 1031 | 1031 | 0 |
| 正式结论 | 572 | 572 | 0 |
| 搜索文档 | 572 | 572 | 0 |
| 媒体唯一ID | 690 | 690 | 0 |
| 知识树一级分类 | 14 | 14 | 0 |

图片 117（包含 GIF），PDF 572，分享 MP4 1，共 690 个媒体。源 meta 中 related_ids 原始声明 1682 条，canonical 后 888 条，重复声明 794 条；Full 源关系 888 条，全部为 canonical related，Full 记录自身重复 0。这是现有 Publisher 去重行为，本任务未改变其数学语义。

与 572 / 1031 / 690 历史基线的差异均为 0。新增、删除或改变的正式知识 ID 均为空；没有以其他历史数字推算或补造内容。

## 11 个物理目录与 14 个知识树一级分类

| 源目录 | 条数 | 知识树一级分类及条数 |
| --- | --- | --- |
| 00_set | 22 | 集合 12；逻辑用语 10 |
| 01_function | 78 | 函数 78 |
| 02_sequence | 42 | 数列 42 |
| 03_conic | 83 | 解析几何 81；立体几何 2 |
| 04_vector | 38 | 向量 38 |
| 05_geometry-solid | 56 | 立体几何 56 |
| 06_probability-stat | 42 | 概率 31；统计 11 |
| 07_inequality | 64 | 不等式 64 |
| 08_trigonometry | 39 | 三角函数 24；解三角形 13；平面几何 2 |
| 09_geometry-plane | 53 | 解析几何 24；平面几何 29 |
| 10_junior_basics | 55 | 前置知识 55 |

现有 `runtime_mapping._load_sources` 读取 `meta.json.knowledgeNode`；`_build_nodes` 用该路径第一段建立 chapter。源目录白名单只用于发现文件，不决定树归属。集合/逻辑用语、概率/统计、三角函数/解三角形三组合并目录各拆成两类，故多出 3 类。跨目录归属按原知识路径保留，例如 03_conic 中 2 条属于立体几何，09_geometry-plane 中 24 条属于解析几何。用户本轮已明确选择按知识树 14 类生产。

| 正式一级分类 | 原 chapter ID | 正式结论 |
| --- | --- | --- |
| 解析几何 | struct:解析几何 | 105 |
| 函数 | struct:函数 | 78 |
| 不等式 | struct:不等式 | 64 |
| 逻辑用语 | struct:逻辑用语 | 10 |
| 平面几何 | struct:平面几何 | 31 |
| 前置知识 | struct:前置知识 | 55 |
| 概率 | struct:概率 | 31 |
| 数列 | struct:数列 | 42 |
| 集合 | struct:集合 | 12 |
| 立体几何 | struct:立体几何 | 58 |
| 统计 | struct:统计 | 11 |
| 解三角形 | struct:解三角形 | 13 |
| 三角函数 | struct:三角函数 | 24 |
| 向量 | struct:向量 | 38 |

前置知识是原 chapter，包含 55 条正式知识；其后代 section 与 knowledge 真实类型保留，没有改成 prerequisite 关系。未修改正式分类、六段 TeX、meta、PDF 或图片。本次审计验证发布一致性，不宣称重新证明所有数学结论。

