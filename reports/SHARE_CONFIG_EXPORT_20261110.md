# shareConfig 正式导出链路修复与本地包验收

日期：2026-11-10（Asia/Shanghai）。状态：**SOURCE FIXED / LOCAL EXPORT PASS / 6 项发行测试环境受阻**。没有 Git 提交、上传、Sync、App 源码修改或 APK 操作。

## 实际检查与范围

任务开始时工作树干净。读取根 AGENTS.md、数学渲染架构契约、Publisher README、Schema v4 模块契约及实际构建/切片/校验代码。现有 `build/zhishu-module-packages` 确为14个ZIP，但本轮实际数为572条 `type=knowledge` 节点、含shareConfig为0；不是背景中另一时点的672。当前正式源为11个目录模块、588条结论，全部已有完整title/shareDesc。

当前源与旧归档有16条收录差异，重导出增加来自当前源的现存节点，不能将这一变化归因于本次新增知识或改ID。新增收录ID：`C084, C085, C086, C087, C088, C089, C090, C091, C092, C093, C094, F079, F080, G057, G058, P054, V039, V040`。旧归档有但当前源没有的ID：`C025, C026`。

本轮只修复分享元数据导出，没有润色或改写meta.json中的任何文案，没有添加公众号推广语。生成数据全部放在已忽略的build/.build/.tmp目录；旧正式ZIP与源素材均保留。

## 修改文件与函数

| 文件 | 主要变化 |
| --- | --- |
| [runtime_mapping.py](../scripts/zhishu/runtime_mapping.py) | KnowledgeNode新增可选shareConfig；parse_share_config集中校验并选择两字段；_load_sources将当前节点配置读入_MappedSource；_build_nodes按同一节点ID携带配置，仅知识节点有值 |
| [content_package.py](../scripts/zhishu/content_package.py) | _validate_entity_shapes复用同一解析器，Full包和模块包均明确拒绝非法类型；原序列化、哈希算法、版本和资源逻辑不变 |
| [Publisher README](../scripts/zhishu/README.md) | 记录可选字段、缺失/null/空白兼容与正式重导出约定 |
| [test_zhishu_share_config_export.py](../tests/test_zhishu_share_config_export.py) | 8项测试方法及兼容/非法类型子用例，使用实际映射、Full写包、模块切片、ZIP读取与校验器 |
| 本报告 | 完整交付证据与受阻情况 |

没有修改module_package.py、module_release.py、share-site或知树App源码。复用了已有dict/字符串、dataclass、_json_value/_write_json与哈希机制，没有额外分享DTO、替代字段或第三方依赖。

## 传递路径

```text
正式UID/meta.json.shareConfig
  → runtime_mapping._load_sources / parse_share_config
  → 对应_MappedSource.share_config
  → _build_nodes / KnowledgeNode.shareConfig
  → content_package._runtime_entities / dataclass asdict / _json_value
  → 正式Full v2的knowledge-nodes.json
  → module_package.select（按知识树模块筛选并保留原记录）
  → make_manifest / 现有哈希与版本计算 / write_zip
  → Schema v4 ZIP根目录knowledge-nodes.json.shareConfig
```

结构节点不补分享配置；title、id、parentId、sortOrder、shortTitle不从分享字段替换。现有全量实体哈希、文件哈希、包哈希与contentVersion自然覆盖新增可选字段，不需要手改产物或ZIP。

## 兼容与报错规则

| 源输入 | 导出行为 |
| --- | --- |
| 完整title/shareDesc | 两字段逐字保留 |
| 只有title或只有shareDesc | 只导出已有字符串字段 |
| 不存在shareConfig或对象为null | 不导出shareConfig |
| 对象为空或两字段均缺失/null | 不导出shareConfig |
| 某字段null，另一字段为字符串 | 省略null字段，保留另一字段 |
| 空串、仅空白、前后空白、换行 | 字符串原样保留；不trim，不补默认，不改标点或数学符号 |
| 配置对象为数字/布尔/字符串/数组等 | MappingIssue携带源meta.json路径，构建失败 |
| title/shareDesc为非字符串且非null | 明确报shareConfig.title或shareConfig.shareDesc类型错误，构建失败；不使用str()转换 |
| imageUrl等其他源键 | 不带入两字段文字契约，原meta与资源逻辑不变 |

Full和Schema v4模块校验均复用该类型规则，未放宽现有校验。默认标题、描述、空白处理与公众号模板仍由App负责。

## 测试与环境限制

| 检查 | 实际结果 |
| --- | --- |
| 新增端到端测试 | 8/8 PASS；覆盖完整与两种部分配置、缺失/null/空白、非法类型、双节点防串用、中文数学符号原样、原id/title/summary/shortTitle、ZIP透传、哈希变化及确定性 |
| 完整相关回归 | 149项已运行：143 PASS、6 ERROR；错误全部为模块发行目录os.replace的WinError 5，没有分享字段断言失败 |
| 单独发行回归及换临时目录重跑 | 17项中11 PASS、同6项ERROR；换用既有.build、.tmp及顶层build后，目录重命名仍受阻 |
| 未修改Git HEAD基线，同一build临时目录 | 17项中11 PASS、同6项相同WinError 5，证明此问题可在未修改源码重现 |
| 正式build-content / Full v2校验 | PASS：Errors=0、Warnings=0 |
| 正式build-package重复Full导出 | PASS：所有实际文件与首轮逐字节一致 |
| 正式切片器两轮全部14模块 | PASS：每轮均完成目录与ZIP校验；两轮逐文件及ZIP字节完全一致 |
| 现有release.audit_modules | PASS：实际解包、父链独立遍历、全量节点/搜索/关系覆盖及资源哈希检查 |
| ZIP内实际JSON与源一一对应 | PASS：588/588；缺失配置ID均为空 |
| 知树当前verifyModuleV4Content读取校验 | PASS：14/14、588条均校验通过，逐模块实际资源哈希及shareConfig对应；未安装真机 |
| 原源文件与归档保留 | PASS：6493份受保护源文件哈希未变，旧14个ZIP哈希未变 |

6项受阻测试为：

```text
test_all_coverage_media_relations_index_and_determinism
test_changed_accepted_pilot_blocks_promotion_and_keeps_staging
test_index_tampered_size_hash_or_identity_rejected
test_missing_zip_fails_global_audit
test_source_change_before_promotion_is_rejected
test_unrelated_official_file_is_preserved
```

错误位置均为`module_package.rename_directory → os.replace(.../staging/.round-1.tmp-..., .../staging/round-1)`。保留错误日志，没有关闭、mock掉、跳过或削弱这些检查，也没有为绕过环境错误修改发布工具。**不能宣称149项全部通过**；发行测试完整绿灯为环境受阻。真实本地切片产物和全局审计均已成功。

测试命令：

```powershell
# 临时目录设置为项目忽略目录，PYTHONDONTWRITEBYTECODE=1
python -B -m unittest -v tests.test_zhishu_share_config_export
python -B -m unittest tests.test_zhishu_source_discovery tests.test_zhishu_source_initialization tests.test_zhishu_runtime_mapping tests.test_zhishu_content_package tests.test_zhishu_asset_preparation tests.test_zhishu_share_videos tests.test_zhishu_publish tests.test_zhishu_module_package tests.test_zhishu_module_release tests.test_rendering_boundaries tests.test_zhishu_share_config_export
```

日志：[新增测试](../build/share-config-export-20261110/share-tests.log)、[149项首轮](../build/share-config-export-20261110/regression-tests.log)、[.build重跑](../build/share-config-export-20261110/regression-existing-build-temp.log)、[未修改基线同目录](../build/share-config-export-20261110/baseline-same-temp-release-tests.log)、[App读取](../build/share-config-export-20261110/app-reader-audit.log)。

## 正式流程重导出与版本

以下全部是本地正式格式导出，没有上传、执行Sync或提升覆盖旧归档。新目录便于核对和保留已发布历史；没有采用上轮临时字段注入方式，没有对实际生产JSON或ZIP补字段后手工重算哈希。

```powershell
python -B scripts/zhishu/publish.py build-content --prepared-assets build/share-config-export-20261110/runtime-assets --output build/zhishu-content-package-share-config-20261110
python -B scripts/zhishu/publish.py build-package --prepared-assets build/share-config-export-20261110/runtime-assets --output build/share-config-export-20261110/full-repeat
python -B scripts/zhishu/slice_modules.py --input build/zhishu-content-package-share-config-20261110 --output build/zhishu-module-packages-share-config-20261110-v4 --modules all --package-version 4
python -B scripts/zhishu/slice_modules.py --input build/zhishu-content-package-share-config-20261110 --output build/share-config-export-20261110/module-repeat-v4 --modules all --package-version 4
```

Schema仍为v4，没有增加能力名称或修改能力计算逻辑。发行序号设为4，避免与旧正式版1以及此前已交付的解析几何试包2/3产生同号异内容冲突；以后更新时继续提高发行序号。当前源比旧归档已有新结论及MP4，故某些旧包和新包的既有视频能力标志会不同；这来自当前资源数据，不是shareConfig扩展增加能力。单一分享字段变化的测试已验证能力集合不变。

Full两轮contentVersion均为`sha256:8cdb220945468ee43df9af0de313d34ad4ec6630a9f965201f32af1f07803211`。实际Full有1070个节点（含结构节点）、588条知识/搜索记录、432张运行时图片、588份PDF、120个GIF分享MP4。Schema v4的两轮14个ZIP均逐字节相同。

## 各模块实际ZIP统计

| 模块/新ZIP路径 | 旧knowledge数 | 新knowledge数 | 含shareConfig数 | 缺失配置ID |
| --- | ---: | ---: | ---: | --- |
| [analytic-geometry](../build/zhishu-module-packages-share-config-20261110-v4/analytic-geometry.zip) | 105 | 117 | 117 | `[]` |
| [functions](../build/zhishu-module-packages-share-config-20261110-v4/functions.zip) | 78 | 80 | 80 | `[]` |
| [inequalities](../build/zhishu-module-packages-share-config-20261110-v4/inequalities.zip) | 64 | 64 | 64 | `[]` |
| [logic](../build/zhishu-module-packages-share-config-20261110-v4/logic.zip) | 10 | 10 | 10 | `[]` |
| [plane-geometry](../build/zhishu-module-packages-share-config-20261110-v4/plane-geometry.zip) | 31 | 31 | 31 | `[]` |
| [prerequisites](../build/zhishu-module-packages-share-config-20261110-v4/prerequisites.zip) | 55 | 55 | 55 | `[]` |
| [probability](../build/zhishu-module-packages-share-config-20261110-v4/probability.zip) | 31 | 31 | 31 | `[]` |
| [sequences](../build/zhishu-module-packages-share-config-20261110-v4/sequences.zip) | 42 | 42 | 42 | `[]` |
| [sets](../build/zhishu-module-packages-share-config-20261110-v4/sets.zip) | 12 | 12 | 12 | `[]` |
| [solid-geometry](../build/zhishu-module-packages-share-config-20261110-v4/solid-geometry.zip) | 58 | 58 | 58 | `[]` |
| [statistics](../build/zhishu-module-packages-share-config-20261110-v4/statistics.zip) | 11 | 11 | 11 | `[]` |
| [triangle-solving](../build/zhishu-module-packages-share-config-20261110-v4/triangle-solving.zip) | 13 | 13 | 13 | `[]` |
| [trigonometry](../build/zhishu-module-packages-share-config-20261110-v4/trigonometry.zip) | 24 | 24 | 24 | `[]` |
| [vectors](../build/zhishu-module-packages-share-config-20261110-v4/vectors.zip) | 38 | 40 | 40 | `[]` |
| 合计 | 572 | 588 | 588 | `[]` |

## 各模块contentVersion前后对比

前值来自本轮任务开始时旧正式ZIP的manifest，后值来自本轮新ZIP的manifest。完整packageHash、ZIP SHA-256、文件大小及能力集合也保存在[zip-audit.json](../build/share-config-export-20261110/zip-audit.json)。

| 模块 | 导出前contentVersion | 导出后contentVersion |
| --- | --- | --- |
| analytic-geometry | `sha256:4ab3f6304d42752a46d1384766ad56f580f3b93de42266a515c4e0b6a9c34d3c` | `sha256:4c5bf305eb16b0a1fbe53b87b31fd3e303a3f31fbc48c9d787113baf86b99384` |
| functions | `sha256:07e7258db967ca08cc1177a4a58d2f9201ee0a052bf385d5262a37d54d0ae029` | `sha256:9335bea95eb53f49d8169c2df90e98aac4fc99c063bb196a81453038153b5b2e` |
| inequalities | `sha256:2545b554f9d6773b6157902af5ea58268521f8e5a33e47a26d3006327b3afd6b` | `sha256:f397ad3495c39f2a23ea7b11bcf7e73bec6de16720b6ecaefb4a19867a2f72c0` |
| logic | `sha256:a4de18c1590812c7563c0870375c2269d0d80d39de644dcea59783f2a9dbf02d` | `sha256:ac64e67ae5489d45f831bf87e0033577bf01114c0cd67ef2a2d5b559d5f4c8b5` |
| plane-geometry | `sha256:57c8ba7194914ffbd992c799c9a55a79e78fb910dc3977dc6ec70d7fb43ddfea` | `sha256:ee74832e10b0257d9dcc5d40cd35fc680e8440393d232a393fd80f7f77f8cfbd` |
| prerequisites | `sha256:ea43e3a661d35cbb26eee5b143477ecd7bc5b5af5e9fbde6d119d464e88fea80` | `sha256:33b03e606f8e84cb11deb826195ac6b8b003f2ac88b276807634cf891afe1538` |
| probability | `sha256:42365650ed846d6bfa943e62552c376380e31641ec117ebfa5f6503dde4d0344` | `sha256:5bb489e1c6af941ac21e54ebd9b4fa1b764bca10d2faa3daf4f25dd84fe9945b` |
| sequences | `sha256:657e9aa5f37a46d7e510b0aaa6698f03379b7a413888bf2de7f4241f2ebd4ad7` | `sha256:62a24c7edb9d253dd11e2b040e8fd3cc5d2573d2f4f5d4ff94b5ecf766cceb43` |
| sets | `sha256:863078df25f8e210751df5b8f7256f711233b1fc920bc2911c5677a7b66b0204` | `sha256:6bff8e670fb8c401d0c7557e81bec0be90c86be41551c10e750adc237b85c78b` |
| solid-geometry | `sha256:d7152ef845089e3d36b9e70e38ec4fb35b43f68bbc5edc5a014d4bccc49b2be3` | `sha256:a87145478aa2d69189123cc55959eb036e27f0b85812b78933b110113bc5dd2a` |
| statistics | `sha256:82ebe0e7ad810d183dded4b4f4d37f78ee2a7af87a6c26f939de7a0a6a438b5f` | `sha256:3f5bbb8593537f093416a04caaed0c8858f9dc7f45f3c78457af2d7c21c4617f` |
| triangle-solving | `sha256:dd156ad36d9cdefcb502a816c1214b543da91b426d0e00a5332c2f29f51c9ae5` | `sha256:aaeccd1ec33cf4173a8b06638058b7da53874c094267e3f11283d55d00546aca` |
| trigonometry | `sha256:f8297a253b1ee0e624aaccd1ae97cf20e822c8d80fb7327206815b24e52694a8` | `sha256:e0bfd72e609920d8e5fe55d497c33abe2cc7a0246bbb25c9c3f108cfc4acd9d4` |
| vectors | `sha256:7a3d71fceada802273f1978dc2f5d2304762ee65b7678716d2922c918ca7f0b5` | `sha256:f945208dcd7d02c276ce47c7080b1fd7699526b22a038f1295f6b8e5d6be1187` |

只变C001.shareConfig的合成测试验证：C001实体哈希、knowledge-nodes文件哈希、Full包哈希、所属解析几何模块contentVersion随之改变；C002实体、原title/ID/排序/父链/搜索summary不变，另一函数模块contentVersion也不变。相同输入两次导出的JSON及ZIP字节一致。

## 两个真实节点的ZIP内记录

以下内容直接来自本轮ZIP内knowledge-nodes.json，原标题未替换成分享标题：

```json
{
  "id": "C067",
  "title": "抛物线切线方程（切点式）",
  "shareConfig": {
    "shareDesc": "切点已经给出，还要设直线、联立再令判别式为零？确认点在对应抛物线上后，用切点式直接写切线，顶点处也适用。若只是切线经过的点，仍须另求切点，不能直接代入。",
    "title": "已知切点，抛物线切线直接写出"
  }
}
```

```json
{
  "id": "F080",
  "title": "倒数对称式与整体换元法",
  "shareConfig": {
    "shareDesc": "高次幂与倒数幂成对出现，逐项展开容易越算越长。把t与1/t的和看成整体，可将首尾对称的特定四次方程化为二次方程；先筛新变量范围，再回代，避免引入无实根的结果。",
    "title": "倒数对称式：四次方程可以先降次"
  }
}
```

## 最终工作树

```text
 M scripts/zhishu/README.md
 M scripts/zhishu/content_package.py
 M scripts/zhishu/runtime_mapping.py
?? reports/SHARE_CONFIG_EXPORT_20261110.md
?? tests/test_zhishu_share_config_export.py
```

待提交文件数：5。工作树仅含上述源码、说明、测试和本报告；没有meta.json、TeX、媒体或App代码改动。未自动提交Git。

证据：[完整ZIP审计](../build/share-config-export-20261110/zip-audit.json)、[全局模块审计](../build/share-config-export-20261110/global-module-audit.json)、[App读取审计](../build/share-config-export-20261110/app-reader-audit.json)、[模块索引](../build/share-config-export-20261110/release-index.json)、[构建日志](../build/share-config-export-20261110/build-content.log)。

以后修改正式UID的meta.json.shareConfig，再经上述正式生产与切片流程重导出，字段即自动进入v4知识节点；不需要再次修改App。当前App纯读取代码已验证可接受本轮数据，真机安装及重启生效未在本任务执行。
