# Task 17A-M：后续实施路线与 Gate

状态：**规划建议；本次未进入实施**。2026-10-14。

## 下一步唯一建议

先开展 **Task 17A-Z 数据契约核验**：由 Zhishu 侧确认模块 schema、相同 knowledgeId 的去重/冲突、外部关系、资源 URI、版本/安装事务及 v2 迁移入口。其结果是 MathNote 模块打包实现的接口输入；本报告交付后等待用户确认，不自动开始开发。

**唯一建议的下一项 MathNote 实施任务**是契约确认后的 **17A-M.2 独立切片器及模块校验最小原型**：从经验证的完整 v2 包只读生成集合与解析几何的隔离测试包，保留原 ID、原实体与跨分类引用，且不改 `publish.py build-content`。在 17A-Z 契约未确认前先完成 17A-M.1 规格冻结，不开始该原型。

## MathNote 后续任务拆分（PROPOSED）

1. **17A-M.1 契约冻结**：综合 17A-Z 反馈，冻结 packageId、subjectId、moduleId、schema、跨包关系、版本和哈希规则；验收是示例 Manifest 与解析规则双方一致。不能修改正式 TeX、`meta.json` 或 UID ID。
2. **17A-M.2 独立切片器**：只读输入经验证的完整 v2 包，按正式一级结构 ID 选择节点/搜索/资源，保留原记录和外部关系，输出到隔离目录；验收包括集合与解析几何的 UID/节点/资产/关系清单与审计库存一致。正式 `build-content` 保持原样。
3. **17A-M.3 模块校验器与确定性 ZIP**：验证所有本地/外部关系、资源精确覆盖、哈希、版本、ZIP 重复性及拒绝恶意相对路径；验收为重复生成字节一致，篡改测试失败。
4. **17A-M.4 双模块隔离试点**：集合 `struct:集合` 与解析几何 `struct:解析几何`，分别生成并验证测试包；再生成解析几何 V1.1，验证仅预期内容和版本变化。与现有 v2 全集逐实体比对原 ID、搜索和图片/PDF/GIF/MP4；此时仍须遵守正式资源发布授权。
5. **17A-M.5 全集回归与发布流程**：保留无参数 `build-content` 的 v2 默认行为和输出。对照基线的节点顺序、Manifest、所有资源和原测试；是否纳入正式发布需另行授权。

依赖次序：17A-Z → M.1 → M.2 → M.3 → M.4 → M.5。若 17A-Z 证明独立切片不能满足运行时树/关系语义，再重新评估 Publisher 原生模块构建；不能把重构作为默认前提。

## 审计 Gate 结果

| Gate | 状态 | 本次证据 / 剩余边界 |
| --- | --- | --- |
| G1 调用链 | **PASS · VERIFIED** | [`publish.py`](../scripts/zhishu/publish.py#L260) 及各被调模块已追踪。 |
| G2 输出结构 | **PASS · VERIFIED（源码及既有包）** | [`content_package.py`](../scripts/zhishu/content_package.py#L679) 与既有 schema v2 Manifest 一致；`validate_package` 0 项问题。 |
| G3 ID 稳定性 | **PASS · VERIFIED（规则）** | [`runtime_mapping.py`](../scripts/zhishu/runtime_mapping.py#L127) 使用 `meta.id` 与 `struct:<路径>`；跨版本实际稳定性待回归。 |
| G4 模块清单 | **PASS · VERIFIED** | 14 类、572 条、1,031 节点，见库存报告。 |
| G5 资源与跨分类 | **PASS · VERIFIED（当前源与发布包）** | 690 个源资源文件、18 条唯一跨分类关系；更新包 690 个资源、131,012,637 字节，117 个图片 URI 与当前源一致。 |
| G6 方案比较 | **PASS · PROPOSED** | A/B/C 已比较；A 未实际实现。 |
| G7 全集兼容 | **PENDING** | 保持原 v2 入口的方案已给出，未实现模块包、未执行包字节回归。 |
| G8 跨项目契约 | **PENDING** | MathNote 建议已给出，Zhishu 未审计/确认。 |
| G9 跨学科问题 | **PASS · VERIFIED/PROPOSED** | 固定 11 数学源目录、数学根、C/G/R 等 UID 惯例与中文结构路径已识别；抽象方案待冻结。 |
| G10 最小路线 | **PASS · PROPOSED** | 先契约，再只读切片、校验、双模块试点。 |

本次实际运行：只读源扫描与统计；`python -m unittest tests.test_zhishu_publish tests.test_zhishu_content_package`，**30 tests OK**；用户运行 `build-content` 更新正式包后，以只读进程对新包运行 `validate_package`，**0 项问题**，`verify_prepared_runtime_images` **PASS**，四组 DTO、117 个图片 URI、PDF 和视频登记均与当前源一致。用户要求普通进程可读后，对当前包目录仅添加当前账户 `(OI)(CI)(RX)` ACL；普通沙箱进程读取 Manifest 与运行包校验均成功。本审计未运行 `build-content`、模块包生成、Sync 或 Android 真机验收。后续重建替换包目录时需复核 ACL。

## 最重要的剩余风险

- 模块包需要新校验语义；当前 v2 强制单根、父节点/关系端点同包。18 条跨分类关系不能无损塞进原格式。
- 一级分类与 11 个源目录错位；特别是解析几何跨 `03_conic` 和 `09_geometry-plane`。过滤必须基于知识树路径。
- 固定高中数学根、目录白名单和数学 UID 习惯不适合作为跨学科包格式的永恒约束。保留现行数学生产行为，同时在新包头引入学科/模块 ID。
- 当前源文件 270,760,344 字节包含 PNG 和 MP4；已验证的更新包目录为 131,012,637 字节。模块 ZIP 大小仍为 UNKNOWN，时间/空间预算要在隔离试点测量。
- Zhishu 端 v2 读取、安装/卸载/更新/授权语义未验证；MathNote 不应自行规定 Android 内部实现。
