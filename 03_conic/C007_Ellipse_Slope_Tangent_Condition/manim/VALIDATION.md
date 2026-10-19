# C007 GIF 本地验收 · 2026-10-19

交付：`../images/ellipse_slope_tangent_condition.gif`。
用户明确要求生成并放入本 UID 的 images/，通过共享 exporter 的
`-Publish -AssetName ellipse_slope_tangent_condition.gif` 首次写入，未使用覆盖参数。

| Gate | 状态 | 已执行证据 |
| --- | --- | --- |
| 数学审计 | PASS | 读取当前六段 TeX 与 meta.json，确认相切充要条件、三种位置关系、正负截距、切点公式及有限斜率边界 |
| 数学自动测试 | PASS | 7 项 unittest 实际通过；三种轴比、五种正/零/负斜率、七种截距比例核验真实交点、椭圆方程、直线方程、判别式；另测切点法向量与切线方向正交、支撑极值、中心对称、一般式及竖直边界 |
| 绘图模型 | PASS | 601 条动画范围内的直线裁切样本均在原直线上且符合显示边界；坐标等比例，未为视觉效果移动切点 |
| 数学关键状态 | PASS | a=3、b=2、k=1/2；S=6.25；m=2、2.5、3 分别有 2、1、0 个交点；两切点为 (-1.8,1.6) 与 (1.8,-1.6) |
| 真实关键帧 | PASS | 已查看最终 GIF 的 0、2.7、5、8.8、12.5、16.8、19.5、24.4 秒合成图，以及正截距切点、双切线的全尺寸帧；直线、交点、切点、数值与不等号一致 |
| 全帧技术检查 | PASS | 576×1024；296 帧；235 个不同帧；24.66 秒；80–90 ms/帧；无限循环；完整解码；0 黑帧；296 帧方差检查无纯色空帧 |
| 教学表达 | PASS（本地审查） | 固定斜率平移；观察交点合并与消失；比较 m² 和 S；展示负截距切线、中心对称的两条平行切线；明确竖直切线不属斜率式 |
| 视觉质量 | PASS（本地审查） | 蓝椭圆、橙色当前直线、绿色交点/切点；蓝色参考切线用虚线区分；读数和文字未裁切；数学图形未变形；首尾回到相同状态 |
| LOCAL PRODUCTION | PASS | 共享渲染与导出成功；3,293,986 bytes，约 3.14 MiB |
| USER VISUAL | PENDING | 待用户查看 |
| ANDROID DEVICE | PENDING | 未执行 Android 真机验收，待用户确认 |
| FINAL FREEZE | PENDING | 用户视觉与真机验收尚未完成 |
| UID images/ 写入 | PASS | 按用户要求首次写入新 GIF，未覆盖原有 PNG/GIF |
| Publisher 内容包 / Sync | PENDING（未执行） | 未执行内容包、Sync、APK 或 Git 提交 |

首末帧 RGB 通道平均绝对差为 0.460 / 0.388 / 0.366（0–255），
含 GIF 编码及抗锯齿差异，不宣称逐像素相同。

证据目录：`build/manim/C007/slope_tangent_condition/`，包括
`render.log`、`contact.png`、`key_00.png` 至 `key_07.png`、
`frame_review.json`、MP4、隔离 GIF 和 `protected_hashes.json`。

实际 Publisher 消费契约已核对：`prepare_knowledge_images.mjs` 发现
images/ 下的直接 PNG/GIF，GIF 经多帧、时序、无限循环验证后按原名逐字节复制；
该名称符合现行契约。本任务只审计消费契约，不运行 Publisher。

任务开始记录本 UID 既有文件 SHA-256；六段 TeX、main.tex、meta.json、
PDF 及原有三张 PNG 均保持原样。用户已有的 TeX、元数据和 PDF 修改全部保留。
