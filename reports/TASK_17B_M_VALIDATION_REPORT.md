# Task 17B-M — Validation Report

日期：2026-10-15（Asia/Shanghai）。**MathNote MODULE PACKAGE PASS；ZHISHU IMPORT PENDING**。

实际命令及结果（工作目录 D:\mathnote）：

```powershell
python.exe -B scripts/zhishu/slice_modules.py --input build/zhishu-content-package --output build/zhishu-module-packages --modules sets,analytic-geometry
python.exe -B scripts/zhishu/slice_modules.py --input build/zhishu-content-package --output build/task17b-evidence/repeated-module-packages --modules sets,analytic-geometry
python.exe -B scripts/zhishu/validate_module.py build/zhishu-module-packages/sets.zip --source build/zhishu-content-package
python.exe -B scripts/zhishu/validate_module.py build/zhishu-module-packages/analytic-geometry.zip --source build/zhishu-content-package
python.exe -B -m unittest tests.test_zhishu_module_package -v
python.exe -B -m unittest tests.test_zhishu_publish tests.test_zhishu_content_package tests.test_zhishu_share_videos
python.exe -B scripts/zhishu/publish.py build-content --prepared-assets build/task17b-evidence/runtime-assets --output build/task17b-evidence/full-regression
python.exe -B -c "import runpy; runpy.run_path('build/task17b-evidence/verify_delivery.py')"
git diff --check
```

| 验证 | 实际结果 |
| --- | --- |
| 原 Full v2 validator | PASS，0 issues；原包与隔离回归包均通过 |
| 集合 ZIP/目录独立验证 | PASS，不需要另一 ZIP 或 Full v2 |
| 解析几何 ZIP/目录独立验证 | PASS，含 GIF→MP4 登记和原 ffprobe 验证 |
| 两 ZIP/目录 --source | PASS，精确 ID/记录/顺序/关系/资源 hash |
| 独立审计方向 | PASS，父链向上归属算法独立核对切片器向下子树算法 |
| 原资源字节 | PASS，两个模块全部 221 媒体文件直接 read_bytes 比较相等 |
| 内部/外部关系 | PASS，集合 13+3，解析几何 192+3；原核心无损 |
| 两次确定性构建 | PASS，Manifest、完整文件清单/内容和 ZIP 原字节一致 |
| 新模块测试 | PASS，38 tests，最后一轮 30.333s；合成源/媒体 fixture，不改正式资源 |
| 原 Publisher/Full/视频回归 | PASS，43 tests，27.605s |
| 完整发布流程隔离构建 | PASS，Errors 0 / Warnings 0，与原 packageHash/contentVersion 一致 |
| 完整发布流程逐文件回归 | PASS，696 文件（含全部 JSON 和 690 媒体）与原正式包同字节 hash |
| 正式包输入保护 | PASS，696 文件与切片前快照完全相同 |
| 数学源和既有代码保护 | PASS，14,245 个原 tracked 文件内容变化 0 |
| Git 空白检查 | PASS，git diff --check 退出 0（本次新增文件仍为 untracked，另经 Python 导入/测试及报告检查） |

实际两次 ZIP SHA-256：集合 `a01be102c036d6807c02e873a0cd840f17ad8a9d97c03668dc1a6289e3b43d4c`；解析几何 `d192575d307164b6f2ed19a366315d63be21874c196e7d82945ec79cd97e085e`。相同输入、相同 packageVersion 的输出在不同暂存/输出路径相同。单模块重复执行还验证另一已成功模块保留。

| 必需负例 | 测试 | 拒绝结果 |
| --- | --- | --- |
| 删除知识节点 | `test_delete_knowledge_node` | PASS（被拒绝且有错误） |
| 篡改 parentId | `test_changed_parent` | PASS（被拒绝且有错误） |
| 删除被引用 PDF | `test_missing_pdf` | PASS（被拒绝且有错误） |
| 篡改图片内容 | `test_tampered_image` | PASS（被拒绝且有错误） |
| 篡改 Manifest hash | `test_tampered_manifest_hash` | PASS（被拒绝且有错误） |
| ZIP 路径穿越 | `test_zip_path_traversal` | PASS（被拒绝且有错误） |
| 内部边缺端点 | `test_internal_unknown_endpoint` | PASS（被拒绝且有错误） |
| 重复知识 ID | `test_duplicate_knowledge_id` | PASS（被拒绝且有错误） |
| 搜索文档不完整 | `test_incomplete_search_documents` | PASS（被拒绝且有错误） |
| 包类型/schema 错误 | `test_wrong_package_type / test_wrong_schema` | PASS（被拒绝且有错误） |
| 外部边错误转内部 | `test_external_edge_wrongly_internal` | PASS（被拒绝且有错误） |
| 损坏 Full v2 输入 | `test_damaged_full_input_rejected_old_output_preserved` | PASS（被拒绝且有错误） |

附加负例覆盖：循环父链、重新计算所有 hash 后篡改节点/遗漏内部关系/遗漏整条 knowledge、外部 source 在包外的缺失端点提示、重复 JSON 键、未知 Manifest 字段、NaN、bool 伪整数、ZIP 重复项/大小写碰撞/链接/保留设备名/额外资源/文件目录冲突/JSON 大小限制、输入输出祖孙重叠、无关输出文件保护、同发行序号改变 envelope、降级拒绝。合成跨包边的两侧核心 hash 一致，提示端点不同也能按 relationId+核心 hash 去重。

失败隔离实测：第二模块写 ZIP 故障和提交第二次 rename 故障均被注入；验证完整旧输出 hash 集合不变，没有不完整 ZIP 替换成功包。损坏输入在暂存前失败。这里只验证同步异常恢复；未测试进程断电/跨文件系统 Android 安装事务，不扩大为终端恢复保证。

独立内容版本实测：仅改合成解析几何 C001 后重建有效 Full v2，并将发行序号提高到 2；集合 sourcePackage/packageHash 变化而 contentVersion 不变，解析几何 contentVersion 变化。相同发行号不同 envelope 在同输出更新中拒绝。正式数学内容从未为此测试改变。

首次旧测试运行确曾被 Python 3.14 tempfile 的 Windows ACL 阻断，不能计入 PASS；随后获准环境中的 43 项重跑为真实 PASS。隔离完整构建未原地执行无参数默认输出，以保护输入；原命令默认值和路径由原 CLI 测试覆盖，生产代码未改变。

Final Gates：

| Gate | 状态 | 证据 |
| --- | --- | --- |
| G1 | PASS | Full v2 原 validator 0 issues |
| G2 | PASS | 集合完整父链子树/ID 精确比较 |
| G3 | PASS | 解析几何完整父链子树/ID 精确比较 |
| G4 | PASS | 全部 117 正式 knowledge ID/内容原样保留，无跨包知识重叠 |
| G5 | PASS | 全部 221 模块媒体原字节相同 |
| G6 | PASS | 全部 205 内部边逐记录相同 |
| G7 | PASS | 6 外部边原核心保留，无伪节点 |
| G8 | PASS | 两 ZIP/目录独立与 source 校验 |
| G9 | PASS | 两次 ZIP 和目录字节一致 |
| G10 | PASS | 12 类必需负例及附加用例，38 tests OK |
| G11 | PASS | 43 既有测试及隔离完整构建 696 文件相同 |
| G12 | PASS | 两 ZIP 实际存在，绝对路径/size/hash 已记录 |
| G13 | PASS | 五份报告实际生成 |
| G14 | PASS（交接明确） | schema v4 内容身份差异及消费接口完整说明；消费者认领/导入验收仍 PENDING |

Task 17B-M 整体 **CONDITIONAL PASS** 的条件只涉及新 v4/hash profile 双端认领，非本地包损坏。17A-F 的跨语言数字 golden/双端 fixture、Zhishu 实际导入、聚合、安装事务与 Android 媒体/数据保持未在 MathNote 侧执行，全部保持 PENDING，未宣布 CONTRACT FINAL FREEZE 或 Android PASS。
