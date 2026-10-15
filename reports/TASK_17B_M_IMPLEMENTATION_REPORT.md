# Task 17B-M — Implementation Report

日期：2026-10-15（Asia/Shanghai）。结论：**CONDITIONAL PASS**；MathNote **MODULE PACKAGE PASS**，**ZHISHU IMPORT PENDING**。本任务生产侧验证全部通过；schema v4 相对 17A-F 候选的内容版本修订仍需 Zhishu 认领，不能宣布双端 FINAL FREEZE。

新增代码（既有 Publisher 文件未修改）：

- `scripts/zhishu/module_package.py`：注册边界、原 DTO 切片、schema v4 Manifest、资源清单、独立校验、安全 ZIP、暂存与整体替换。
- `scripts/zhishu/slice_modules.py`：独立 CLI，指定输入/输出/试点模块/发行序号。
- `scripts/zhishu/validate_module.py`：单目录/单 ZIP 校验，`--source` 执行完整来源一致性校验。
- `tests/test_zhishu_module_package.py`：38 项合成 fixture、负例、确定性、独立版本和失败隔离测试。

新增五份 `reports/TASK_17B_M_*.md`；两个真实 ZIP 及其展开目录在 `D:\mathnote\build\zhishu-module-packages`。`build/` 被既有 `.gitignore` 忽略，ZIP 已实际生成，未擅自 Git add/commit。任务临时证据和独立核对脚本在 `build/task17b-evidence/`，不属于包内内容。

输入是原正式 `D:\mathnote\build\zhishu-content-package`，schema v2，`sha256:4ca08754bc494571ee02e576aa75c1bf122a4d29db699ef51c57366bbd80fdc7`。先读取并运行原 `content_package.validate_package`，再切片；切片器不调用源发现、TeX、图片预处理、Publisher、Sync 或 Android。仅两个受控 slug：`sets`、`analytic-geometry`；映射来自 17A-F 明示登记，并核对实际 chapter ID、title、type 和 parentId，不能按源目录或 UID 前缀选择。

所有原数学 ID、父链、sortOrder、节点/搜索/资产/视频记录和资源字节保留。模块含原 subject root 作为祖先上下文；所有其他模块子树排除。未知安装提示包使用 null，不凭名称猜包。

完整 Publisher 保护：原 `publish.py`、`content_package.py` 及所有原 tracked 文件内容均未修改。输入/输出必须互不包含；禁止正式 Full 输出作为模块目标；既有输出含无关文件则拒绝。全部所选目录和 ZIP 验证完成后才整体替换输出，第二模块失败时两包旧输出都保持；重命名提交失败恢复备份。单模块更新保留另一试点输出。已有同发行序号异 envelope 拒绝，显式提高 `--package-version` 才允许更新。不会自动发布到外部服务。

实际命令：

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

验证结果：新增 **38 tests OK**；既有 Publisher/Full/视频 **43 tests OK**；隔离完整构建 **Errors 0 / Warnings 0**，与正式包 **696 个文件逐文件哈希相同**；两次模块目录、Manifest、文件列表和 ZIP 原字节相同。最终对修改前 **14,245 个 tracked 文件**逐文件复核，内容变化 0；正式 Full 包 696 文件与修改前快照相同。

正式无参数 `build-content` 默认路径由原有 CLI 测试确认；为了保护切片输入，本次**未原地重建默认正式输出**，实际运行相同完整流程的显式隔离输出。生成的 117 个 WebP/GIF 运行时镜像仅在隔离目录；未重新绘制数学图片，未编译 PDF，未修改数学源。

环境记录：普通沙箱首次执行旧测试与 Python `tempfile.mkdtemp(0700)` 遇 Windows Python 3.14 保护 ACL，不能记为通过。旧测试和隔离 Publisher 已在获准的普通用户执行环境中重跑成功。新模块工具的暂存目录以正常 mkdir 继承父 ACL，不编辑 ACL；新工具及 38 项测试在普通沙箱通过。首次两个失败暂存目录已按明确绝对路径清理。没有更改正式目录权限。

全部所需 17A-M、17A-Z、17A-F 文档均存在并已读取。17A-F 的“正式产物不可读”已由本次读取和校验事实解除；其“实施等待冻结”是旧评审门禁，本次用户任务明确授权在 CONDITIONAL/冲突时做最小显式扩展。未借此声称其他 Zhishu 门禁关闭。唯一字段语义冲突及选择见 [Module Contract](TASK_17B_M_MODULE_CONTRACT.md)。
