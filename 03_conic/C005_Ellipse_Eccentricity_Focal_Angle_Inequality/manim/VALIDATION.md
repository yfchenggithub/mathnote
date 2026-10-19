# C005 GIF 本地验收 · 2026-10-19

交付文件：`../images/ellipse_eccentricity_focal_angle_inequality.gif`。
用户明确要求生成并放入该 UID 的 images/；通过共享 exporter 的
`-Publish -AssetName ellipse_eccentricity_focal_angle_inequality.gif` 首次写入，
未使用覆盖参数。

| Gate | 状态 | 已执行证据 |
| --- | --- | --- |
| 数学审计 | PASS | 当前六段正式 TeX 与 meta.json 的核心不等式一致；模型独立建立，不使用其他 UID 私有数学实现 |
| 数学自动测试 | PASS | 6 项 unittest 实际通过；7 种离心率各 721 个采样点，验证椭圆方程、焦半径和、向量角、半角不等式、半角恒等式及精确差值恒等式；另测等号位置、零角端点、存在性、逆向求点及参数域 |
| 关键状态 | PASS | e=0.6 时最大角约 73.7398°；e=√2/2 时 90°；e=√3/2 时 120°；e=0.9 时最大角约 128.3161° |
| 目标角实际求解 | PASS | a=5、e=0.9，P≈(2.72165527,1.82827585) 的实际向量夹角为 120°，半角正弦约 0.8660254<0.9 |
| 真实关键帧 | PASS | 已查看最终 GIF 的 0、3、5、9.7、14.5、18、21.1、27 秒合成图，以及临界直角、非端点 120°的全尺寸帧；焦点、角弧、数值、比较条、参数与公式一致 |
| 全帧技术检查 | PASS | 576×1024；329 帧；266 个不同帧；27.41 秒；每帧 80–90 ms；无限循环；完整解码；0 黑帧；329 帧方差检查无纯色空帧 |
| 教学表达 | PASS（本地审查） | 普通点严格不等→短轴端点取等→固定 a 改变 e→直角和 120°门槛→非短轴点实现 120°；区分任意性与存在性 |
| 视觉质量 | PASS（本地审查） | 横纵等比例；条带共用 [0,1] 固定刻度；蓝椭圆/e、橙射线/角度/半角正弦、绿最大值和结论；无关键文字裁切；首尾回到相同数学状态 |
| LOCAL PRODUCTION | PASS | 共享工具真实渲染、导出成功；4,652,169 bytes，约 4.44 MiB |
| USER VISUAL | PENDING | 待用户查看 |
| ANDROID DEVICE | PENDING | 未执行 Android 真机验收，待用户确认 |
| FINAL FREEZE | PENDING | 用户视觉与真机验收尚未完成 |
| UID images/ 写入 | PASS | 按用户要求首次写入新文件，未覆盖原有 PNG/GIF |
| Publisher 内容包 / Sync | PENDING（未执行） | 未运行内容包、Sync、APK 或 Git 提交 |

首末帧 RGB 通道平均绝对差为 0.427 / 0.359 / 0.355（0–255），
包含 GIF 编码及抗锯齿差异，不宣称逐像素一致。
数值条带保留三位小数，角度读数保留一位小数；等号判定依据数学点位，
不是以四舍五入后的相同显示值判断。

构建证据在 `build/manim/C005/focal_angle_bound/`：
`render.log`、`contact.png`、`key_00.png` 至 `key_07.png`、
`frame_review.json`、MP4、隔离 GIF、`protected_hashes.json`。

已核对 Publisher 实际消费契约：`publish.py` 调用 `asset_preparation.py`，
worker `prepare_knowledge_images.mjs` 接受 images/ 下直接 PNG/GIF；
验证 GIF 多帧、时序、无限循环后按原文件名逐字节复制。
这里只审计契约，不执行 Publisher。

任务开始记录的 12 个既有文件（六段 TeX、main.tex、meta.json、PDF、
三张 PNG）在写入前重算 SHA-256，0 个变化。
工作树中原有 TeX 与 PDF 修改全部保留。
