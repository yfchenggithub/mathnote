# F089｜勾股整数数组的构造规律

本包依据用户上传的九文件 F083 框架制作，但所有数学内容均已替换为 F089 的内容。

## 九文件
- source.tex（LaTeX 结论提要）
- 01_statement.tex（核心结论）
- 02_explanation.tex（直观理解）
- 03_proof.tex（3 种证明思路）
- 04_examples.tex（3 道典型例题）
- 05_traps.tex（3 个常见误区）
- 06_summary.tex（快记／快懂／快用）
- main.tex（保留 \Conclusion、subsection、六个 input）
- meta.json（保留原模板的全部顶层元数据字段）

图源：assets/tikz/ 下 4 张可编辑的 TikZ 图；各讲解区块均引用对应图源。

原始资料：《高中数学常用数值与估算方法大全：从记忆到推导》，第13—16页。
原文件存在个别计算误写或近似精度问题，本包已在相关处订正，避免将近似式写成恒等式。

## 集成注意
1. main.tex 中的 `01_function/` 路径前缀来自上传的 F083 模板，为保持框架原样而保留；尤其 F089、F090 在 metadata 中属于 `geometry`，应按你的项目实际模块目录调整路径前缀。未经实际项目校对，不应直接覆盖已有源码。
2. isPro 暂依上传模板设为数值 `0`，不代表正式免费/PRO 分层决定；正式发布前请核对。
3. JSONL 文件与 ZIP 内容一致：每个 JSONL 含一行 JSON 对象，带 id、metadata、files、assets，方便脚本读取；它不是现有 App 的已验证原生导入协议。
4. 所有示意图独立放置；保留你自己的主题色盒子和 LaTeX 样式定义，避免与原始项目宏冲突。
