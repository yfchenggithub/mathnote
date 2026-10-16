# Task 17G-M — TEST REPORT

日期：2026-10-16（Asia/Shanghai）。

AUTOMATED TEST PASS。最终 Python **100 tests / 100 PASS / 0 FAIL**：新增17，既有83（原模块38、Publisher/Full/分享视频43、架构边界2）。只读执行知树既有 Schema v4 测试 **60 PASS / 0 FAIL**；合计160测试通过。14真实ZIP独立及来源校验、两轮全局审计均通过。消费端12身份拒绝为已确认兼容阻碍，未记作安装成功。

实际执行命令（部分通过Python subprocess包装保存日志及真实exitCode）：

```powershell
python.exe -B scripts/zhishu/publish.py build-content --prepared-assets build/task17g-evidence/runtime-assets --output build/task17g-evidence/full-regression
python.exe -B scripts/zhishu/module_release.py --input build/zhishu-content-package --staging build/task17g-evidence/release-candidate
python.exe -B -m unittest tests.test_zhishu_module_package tests.test_zhishu_module_release tests.test_zhishu_publish tests.test_zhishu_content_package tests.test_zhishu_share_videos tests.test_rendering_boundaries -v
node --no-warnings --experimental-transform-types --import file:///D:/work/zhishu/src/data/knowledge/testing/registerProjectHooks.mjs --test --test-isolation=none D:/work/zhishu/src/data/knowledge/moduleV4.test.mjs
node --no-warnings --experimental-transform-types --import file:///D:/work/zhishu/src/data/knowledge/testing/registerProjectHooks.mjs build/task17g-evidence/check-zhishu.mjs build/task17g-evidence/release-candidate/round-1
git diff --check
```

正式提交实际调用 `promote_release(source, staged, output, frozen)`：source=`build/zhishu-content-package`，staged=`build/task17g-evidence/release-candidate/round-1`，output=`build/zhishu-module-packages`，frozen=本轮审计的696源文件哈希。提交前后验证、原文件保护及真实耗时见 `promotion.json`；正式索引再次校验见 `final-audit.json`。

| 要求 | 实际证据 |
| --- | --- |
| T01–T07 | 新增模块发现、唯一身份、归属、前置section测试及真实父链审计 |
| T08–T15 | 572/1031精确记录并集；原缺知识、重复、parent、cycle、搜索缺失负例 |
| T16–T23 | 690媒体真实字节；原缺PDF/篡改图/路径穿越/额外资源负例；既有视频测试 |
| T24–T30 | 真实870/36→888审计与知树关系函数；原错误外部端点/内外范围/双侧核心合并负例 |
| T31–T38 | 逐ZIP独立及source校验、Manifest重算、反序两轮字节一致、来源版本隔离及原试点快照 |
| T39–T45 | 14ZIP/index大小SHA身份篡改负例、真实联合owner/共享根/媒体归属检查 |
| T46–T47 | 源、Full、试点和Zhishu任务前后全部tracked文件哈希保护 |

新增负例包括未知/更名/空chapter、重复身份、数量不符、后续模块写入失败、变更已验收试点、无关文件保护、少ZIP、index大小/哈希/身份篡改、冻结源改变、路径重叠、Windows暂时重命名失败及不可读目录拒绝。原提交rename故障回滚测试继续通过。

环境异常如实记录：首次Publisher及旧测试被Python3.14 Windows tempfile ACL阻断，未计PASS，后获准普通用户环境重跑成功。初始合成全量测试1项因扩充Full后旧试点envelope变化而被保护门正确拒绝，fixture改为同一冻结Full下建立试点后通过。真实staging两次目录重命名WinError5失败，正式输出未变；增加有限重试后成功。ACL目录的rglob静默遗漏曾使对照检查失败，改为枚举异常必须上抛并新增负例；最终696文件完整哈希一致。报告中文编码验收中发现shell管道损失中文，已改用UTF8文件生成并复核。未编辑ACL、正式数学源或Zhishu。

正式保护：5440个tracked数学源目录文件无变化；Full696文件不变；两试点237文件不变；Zhishu1273个tracked文件全部哈希相同，Git HEAD及tracked状态保持。原其他tracked文件均保持，仅3个批准修改的既有代码/测试文件变化。证据 `protection.json`。

代码修改：module_package.py（稳定映射、全量发现、计时、Windows重试、不可读枚举失败）；slice_modules.py（--modules all）；新增module_release.py（复用切片器的双轮、全局审计、索引和保护提交）；原test_zhishu_module_package.py仅调整fixture资产计数及双包用例显式范围；新增test_zhishu_module_release.py的17项测试。publish.py、content_package.py、v4哈希算法及Publisher数学语义均未修改。

