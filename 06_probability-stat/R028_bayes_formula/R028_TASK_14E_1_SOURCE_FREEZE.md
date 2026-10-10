# Task 14E.1 Result — R028 Bayes Formula Minimal Source Correction & Freeze

日期：2026-10-10。目标 UID：`R028`。本报告只记录四处正式表述修订及由此引起的 R028 PDF 回归，不涉及 Manim、GIF、Publisher、Content Package、Sync 或 App。

## 1. Pre-flight

- Git 分支 `main`；开始时 `git status --short` 为空。实际目录为 `06_probability-stat/R028_bayes_formula/`，其路径上没有适用的嵌套 `AGENTS.md`。
- 已读取根 `AGENTS.md`、`docs/guidelines/pdf-conclusion-guidelines.md`、`docs/architecture/math-rendering-boundaries.md`、Task 14E.0 完整审计报告、六段正式 TeX、`meta.json`、`source.tex`、`main.tex`，并检查旧正式 PDF。
- Task 14E.0 的九个源文件 SHA-256 与本轮开始时相同；四个定位及原文仍准确。旧 PDF 为 7 页 A4，原 SHA-256 为 `79E46959ADAFB523A168116AF413ACFE4870BD5F79FAAF0EA0EE6F6856C1EC72`。
- 已检查换行：三份待改 TeX 使用 UTF-8、LF、无 BOM；`meta.json` 使用 UTF-8、CRLF、无 BOM。原有 `images/` 为空。

## 2. Task 14E.0 Audit Baseline

依据 `R028_SOURCE_CONSISTENCY_AUDIT.md` 的第 12、14 节：`06_summary.tex:17` 与 `meta.json:123` 的“和为 1”缺乏概率对象；`05_traps.tex:12` 对合法边界 `P(B)=1` 作了错误的无条件断言；`02_explanation.tex:38` 的单一“检测准确率”不能清楚表示诊断题需要的两类条件概率。审计同时确认核心贝叶斯公式、证明和三道例题正确，故本轮保留它们原样。

## 3. Authorized Change Scope

只改 `02_explanation.tex:38`、`05_traps.tex:12`、`06_summary.tex:17` 和 `meta.json:123` 的现有文字。正式 PDF 可在现有 R028 构建链下由这些修订重建；`01_statement.tex`、`03_proof.tex`、`04_examples.tex`、`source.tex`、`main.tex`、其他 UID、图像和共享工具均保持不变。没有新建教学图；本任务的冻结对象是**数学知识源**，不宣称现有 PDF 达到项目规范所称的整体教学图完善状态。

## 4. Fix A — Summary

- 位置：`06_probability-stat/R028_bayes_formula/06_summary.tex:17`。
- 原文：“计算分母时必须包含所有划分事件，且概率和为1。”
- 修订：“分母须包含全部划分事件，等于 $P(B)$，不一定为 1；另检验先验概率之和、后验概率之和各为 1。”
- 数学依据：`Σ_iP(A_i)=1`、`Σ_iP(B|A_i)P(A_i)=P(B)`、`Σ_iP(A_i|B)=1` 是三个不同的求和。修订保留全部类别的要求，并消除“分母恒为 1”的危险读法。
- 验证：源码旧句消失，新句只出现一次；正式 PDF 第 7 页显示正确、无裁切。

## 5. Fix B — Metadata

- 位置：`06_probability-stat/R028_bayes_formula/meta.json:123`，唯一变化路径为 `/content/common_tricks/1`。
- 原文：“分母必须包含所有划分事件的全概率，求和等于1可做检验。”
- 修订：“分母须包含全部划分事件，等于P(B)，不一定为1；先验概率之和、后验概率之和各为1。”
- 数学依据与 Fix A 一致。JSON 字段名、键集合、层级、类型、UID、关系及其他字段值均不变；原 CRLF 和无 BOM 格式保持。`meta.updated_at` 依本任务仅改审计指定字段的明确范围保留原值；如以后另行开展元数据版本维护，可依 PDF 规范同步。
- 验证：JSON 解析通过；对 `HEAD` 中旧 JSON 与当前 JSON 递归比较，仅上述一个字符串值改变。下游只读 `source_discovery._validate_meta` 返回无错误，`runtime_mapping._load_sources` 单 UID 映射出 `R028` 且错误数为 0。

## 6. Fix C — Traps

- 位置：`06_probability-stat/R028_bayes_formula/05_traps.tex:12`。
- 原文：“直接使用乘法公式计算联合概率，但条件概率需要归一化，否则会得到错误数值，且所有后验概率之和不会等于1。”
- 修订：“直接用乘法公式得到的是联合概率，求和为 $P(B)$；求后验概率须除以 $P(B)$，不可未经计算就把分母取 1；若 $P(B)=1$，分母确为 1。”
- 数学依据：`Σ_iP(A_i∩B)=P(B)`；当 `P(B)=1`，联合概率与后验概率相等。修订保留“不能擅取分母为 1”的教学目标，同时允许合法边界。
- 验证：边界测试见第 11 节；正式 PDF 第 6 页文字与公式清晰，未见越界。

## 7. Fix D — Explanation

- 位置：`06_probability-stat/R028_bayes_formula/02_explanation.tex:38`。
- 原文：“需已知患病率（先验）和检测准确率（似然）。”
- 修订：“需已知患病率（先验）、患病时阳性率（灵敏度）和未患病时阳性率（假阳性率；可由特异度求得）。”
- 数学依据：诊断阳性的两类似然为 `P(+|患病)` 和 `P(+|未患病)`；二元结果下后一项为 `1−特异度`。`04_examples.tex:5,11-12` 正好使用这些值。没有改动例题数据。
- 验证：正式 PDF 第 2 页自然换行，无文字遮挡或乱码。

## 8. Minimal Diff Verification

`git diff --numstat` 对四份源文件各为 `1` 行新增、`1` 行删除。逐行 diff 只含上列四处替换；无公式、例题、LaTeX 环境、字段结构或整文件格式化变化。`git diff --check` 无空白错误。Git 对三份 TeX 提示工作树 LF 将来可能按配置转为 CRLF，但实测本轮文件字节仍是 LF，未发生换行重写。

## 9. Mathematical Regression

- `01_statement.tex:4-5,14-23` 的划分、`P(A_i)>0`、`P(B)>0`、一般式与二分式不变且正确。
- `03_proof.tex:9-34` 仍按条件概率、乘法公式、全概率公式和代入四步推导，前提与下标一致。
- `02_explanation.tex:9-21` 明确先验、似然、后验以及分母为 `P(B)`；修订的诊断文字与例 1 一致。
- `05_traps.tex:10-12` 区分联合概率和条件概率，不排除 `P(B)=1`。
- `06_summary.tex:9-17` 区分两种归一化与全概率分母；`meta.json:97-123` 的公式、条件与提示语义一致。

## 10. Numerical Examples

从未改动的 `04_examples.tex` 实际题设提取先验与似然，使用一次性 `decimal.Decimal` 命令重新计算；没有把审计报告中的分母作为输入。三题先验和为 1，全部后验在 `[0,1]` 内且和为 1。

| 例题 | 先验 | 似然 | 分子 | 独立计算的 `P(B)` | 目标后验 | 原文结果 |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 1 阳性后患病 | `0.001, 0.999` | `0.99, 0.01` | `0.00099` | `0.01098` | `0.090163934...` | `≈0.0902` PASS |
| 2 次品来自甲 | `0.5, 0.3, 0.2` | `0.01, 0.02, 0.03` | `0.005` | `0.017` | `0.294117647...` | `≈0.2941` PASS |
| 3 两正面后公平币 | `0.5, 0.5` | `0.25, 1` | `0.125` | `0.625` | `0.2` | `0.2` PASS |

例 1 的 `0.1% = 0.001`、灵敏度 `99%` 与假阳性率 `1%` 一致；例 3 的两次公平硬币抛掷按题设独立。四位小数舍入与百分数表述正确。

## 11. Boundary Conditions

对完整二元划分独立检查：

| 情形 | 先验 | 似然 | `P(B)` | 结论 |
| --- | --- | --- | ---: | --- |
| 普通 | 例 3 的 `0.5, 0.5` | `0.25, 1` | `0.625` | 分母不为 1，后验 `0.2, 0.8` |
| 合法边界 | `0.4, 0.6` | `1, 1`（`B=Ω`） | `1` | 分母可为 1，后验 `0.4, 0.6` |
| 不可条件化 | `0.4, 0.6` | `0, 0` | `0` | 通常定义下 `P(A_i|B)` 不存在 |

因此先验归一化、全概率分母、后验归一化、分母可小于或等于 1、零概率条件不可用六项数学回归均通过。

## 12. Cross-file Consistency

六段 TeX 与 `meta.json` 重新核对后：`P(A_i)` 是先验，`P(B|A_i)` 是似然，`P(A_i|B)` 是后验；全概率分母为 `P(B)`。正式陈述和总结均保留 `P(B)>0`，没有声称分母恒为 1；易错提醒允许 `P(B)=1`；诊断解释与例 1 的灵敏度、特异度及假阳性率相容。原有三题与证明未改变。未发现四处修订引入的新冲突。

## 13. Metadata Validation

当前 `meta.json` 可解析为 JSON；对前后解析树递归比较，仅 `/content/common_tricks/1` 的字符串值变化，无 key、数组长度、类型或非目标字段变化。ID 仍为 `R028`，`core.title` 仍为“贝叶斯公式”。现行 Zhishu 只读发现与映射代码对单 UID 验证通过（第 5 节）。

仓库另有旧 `scripts/check_meta_json.py`，其旧式 `META_SCHEMA` 在修订前后**均报告相同的 55 项**缺失或额外字段，不适用于这份现有元数据格式；本任务没有改它，也不把这项既有不兼容误报为本次 schema 通过或新增回归。实际 JSON 结构与下游解析兼容性按上述差分和现行读取代码验证。

## 14. Formal TeX / PDF Build

`main.tex` 直接 `\input` 六段正式 TeX；目录中的 `source.tex` 是独立输入材料，不在该 PDF 的实际编译链中，故无需再生成且哈希不变。正式脚本 `scripts/build_conclusion_pdfs.py` 为选中 UID 生成临时 wrapper，经 `latexmk -xelatex` 构建。采用 `--modules 06_probability-stat --ids R028 --conclusions R028_bayes_formula` 限定为单 UID，映射文件另置临时路径，没有覆盖正式映射。

先以 `--output-dir build/conclusion_pdfs/R028_14E1_preview` 成功构建候选 PDF；审核后备份旧正式 PDF 到 `build/conclusion_pdfs/R028_14E1_backup/R028_bayes_formula.before.pdf`，备份 SHA-256 与旧正式 PDF 相同，再通过脚本的 `--output-to-conclusion-pdfs --overwrite` 更新 `pdfs/R028_bayes_formula.pdf`，返回 `success: 1, failed: 0`。正式映射为 `R028 → R028_bayes_formula.pdf`。没有执行 Publisher 或内容包流程。

## 15. Actual PDF Visual Validation

候选和最终正式 PDF 均为 **7 页 A4**，非加密，可由 `pdfinfo` 读取。两份 PDF 均以 `pdftoppm -r 200 -png` 渲染完整七页；实际逐页查看候选版，第 2 页诊断解释、第 6 页易错点、第 7 页总结均显示修订后的内容，中文、公式、分数、下标、条件和边框正常。第 1、3–5 页的陈述、证明与三道例题也已逐页抽查，未见新重叠、裁切、乱码或分页断裂。

最终正式 PDF 的七张页面 PNG 与已查看的候选版 **7/7 SHA-256 完全相同**；两份 PDF 经 `pdftotext -layout -enc UTF-8` 抽取的文本 SHA-256 也相同。PDF 文件本身因构建时间元数据而字节不同，但可见页面与文本一致。源文件修订后的旧短语已消失，新短语已核对；正式 PDF 没有停留在旧版本。

## 16. Frozen Asset Integrity

- 受保护的 `01_statement.tex`、`03_proof.tex`、`04_examples.tex`、`source.tex`、`main.tex` 前后 SHA-256 完全相同；`images/` 仍为空。
- Task 13F 的 `render.ps1`、`export_gif.ps1`、`production.py`、`verify_gif.py`、`check_env.ps1`、`requirements.txt`、`README.md`、`TASK_13F_FREEZE.md`，以及 PDF 构建脚本和 `scripts/zhishu/publish.py`，逐项与开始时的干净 Git `HEAD` 字节对比，均为 `UNCHANGED`。
- `git diff --name-only` 仅有四份修订源文件与 R028 正式 PDF；没有其他 UID、GIF、共享工具或 Publisher 代码变化。旧 PDF 备份已验证可恢复；无异常删除。

## 17. Changed Files & SHA-256

| 文件 | 开始 SHA-256 | 完成 SHA-256 | 类型 |
| --- | --- | --- | --- |
| `02_explanation.tex` | `745AE20B2B492F840F196DCCB63A045A4D44002AE5A27D062CC6AE0E37EF69AA` | `59DF64F95448BB2EDDD75D18A43B881F6ED89C8F67862EF0B66DE8F1C2E4F9BC` | 授权单句修订 |
| `05_traps.tex` | `D3A673E73FB1DAB3D471B7D8D98C8423915DFF402B49B2BCAB10210A2DCAEDE7` | `8F50A4A7BF2181CD21B9E4257E9ADB0618A509D6E536CF084B2381548CE11451` | 授权单句修订 |
| `06_summary.tex` | `1C80448D3A7A5A42327F403FB1203D8886F8969D474B41D1218DE86C9F088A75` | `12FAA7C27CC755A2505DA6410F1DEF68C494E115991BDB33316BC8CC4ED00938` | 授权单句修订 |
| `meta.json` | `EFC89DB21131405A7BDF18C80187BED6009D04471F032DA4F753A48908C15ECA` | `005A54CFC5459695C942E2C35A8A04E5D50718D99EBDCA100747CA8E4D784334` | 授权单字段值修订 |
| `pdfs/R028_bayes_formula.pdf` | `79E46959ADAFB523A168116AF413ACFE4870BD5F79FAAF0EA0EE6F6856C1EC72` | `D24E933A6FB5C9BA95FDFDDEF1F28CE7B5C99F9BA63B8B58A50F913AE1A73658` | 授权正式构建产物 |

未变文件：`01_statement.tex` `A0804FA1EC503A718C61CCD3F8893C3487AB786A046E523399D6EBEB8E4370D5`；`03_proof.tex` `AE3054B9AAEF68DFB348D1A1E0AC6D60D0B085563C3940EDD85FD2EAF6877B28`；`04_examples.tex` `7A1C3127F943E9E84CB6A61D7C8CEA68CF88652F0B44019F3B5A41FB7BFDA11E`；`source.tex` `52D0FEADFD5BE6979C61C08DD79DC82AF036422DD95B5A92F0068AA53B9587B0`；`main.tex` `10F0610F7B2DEBD2CD77919CB8EB0163C10B2E220A343BE10789F7F18AA19BEF`。

## 18. Known Issues & Scope Notes

- 旧 `check_meta_json.py` 与 R028 的既有格式不匹配（前后均 55 项）；现行下游解析及结构差分已通过。该旧校验器未被本次修订引入或修改。
- 现有 PDF 没有新增主教学图；依任务“只改四处”范围，本轮只验收修订文字与 PDF 回归，不宣称整份 PDF 完成项目规范意义上的教学图完善。
- `meta.updated_at` 保持不变是本轮仅修改审计指定字段的明确范围与 PDF 规范更新时间建议之间的范围取舍；本报告记录实际修订日期，不虚报元数据时间。

## 19. Acceptance Gates

| Gate | 状态 | 证据 |
| --- | --- | --- |
| A Pre-flight | PASS | 规则、审计报告、分支、干净工作树、目录及原始哈希 |
| B Fix A | PASS | Summary 第 17 行明确三种求和 |
| C Fix B | PASS | Metadata 单字段值变化，JSON 与下游读取成功 |
| D Fix C | PASS | Traps 允许 `P(B)=1`，边界反例通过 |
| E Fix D | PASS | Explanation 区分灵敏度、假阳性率与特异度 |
| F Minimal Diff | PASS | 四个 `1+/1-`，原换行保持，`git diff --check` 无错误 |
| G Formula Regression | PASS | Statement、Proof 哈希不变且公式、条件复核正确 |
| H Numerical Regression | PASS | 三题 Decimal 复算、舍入与范围正确 |
| I Cross-file Consistency | PASS | 六段 TeX 与 Metadata 修订后语义一致 |
| J Source Generation | PASS | `main.tex` 直接引用六段；`source.tex` 非本 PDF 构建产物且未变 |
| K PDF Build | PASS | 候选及正式单 UID 构建各 `success: 1`，7 页 A4 |
| L PDF Visual Validation | PASS | 全部 7 页实看候选；正式版 7/7 PNG 与候选相同 |
| M Metadata Compatibility | PASS | JSON 树仅单值变、现行发现/映射解析零错误；旧校验器限制见第 13 节 |
| N Frozen Asset Integrity | PASS | 五个源/中间文件不变，共享工具与其他 UID 未变，旧 PDF 可恢复 |
| O Final Freeze Evidence | PASS | 本报告列出原句、新句、测试、PDF 验收、哈希与门禁 |

## 20. Final Status

**SOURCE CORRECTION PASS — PDF REGRESSION PASS — R028 MATHEMATICAL SOURCE FINAL FREEZE — R028 ANIMATION MATH SOURCE READY.** 这表示后续可独立启动 R028 GIF 教学设计任务；本任务没有制作 GIF，也未进行 GIF 验收、Android 真机验收或知树 App 发布/同步。数学源冻结不代表动画冻结。
