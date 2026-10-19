# C009 GIF 本地验收 · 2026-10-19

交付：`../images/ellipse_tangent_slope_range.gif`。
用户明确要求生成并放入本 UID 的 images/，通过共享 exporter 的
`-Publish -AssetName ellipse_tangent_slope_range.gif` 首次写入，未使用覆盖参数。

| Gate | 状态 | 已执行证据 |
| --- | --- | --- |
| 数学审计 | PASS | 读取当前六段 TeX 与 meta.json，核对有限斜率全集、过点方程、韦达前提、点位置分类及竖直切线分支 |
| 数学自动测试 | PASS | 6 项 unittest 实际通过；验证正/负/零及大有限斜率均有两条平行切线；斜率根满足相切条件、判别式与韦达关系；独立几何模型核验切线及点位 |
| 运动模型 | PASS | 对三段定点运动共 503 个采样状态核验真实切点、一般式相切、经过 M、线段裁切；分别统计实切线总数与有限斜率数 |
| 数学关键状态 | PASS | M=(0,2)：两切线、斜率 ±√3/2；M=(2,2)：两切线但只有有限斜率 3/8，另有 x=2；M=(2,0)：唯一竖直切线；M=(1,0)：无实切线 |
| 真实关键帧 | PASS | 已查看最终 GIF 的 0、3.4、6.7、9、14、19.8、22.8、24.95 秒合成图，以及竖直分支和长轴端点全尺寸帧；直线、切点、参数、坐标与说明一致 |
| 全帧技术检查 | PASS | 576×1024；303 帧；252 个不同帧；25.25 秒；80–90 ms/帧；无限循环；完整解码；0 黑帧；303 帧方差检查无纯色空帧 |
| 教学表达 | PASS（本地审查） | 自由方向的斜率全集→固定点后的有限根→二次项消失的竖直分支→椭圆上与内点的条数；明确“不存在斜率”和“不存在切线”不同 |
| 视觉质量 | PASS（本地审查） | 等比例坐标；蓝椭圆、橙/绿两切线与切点、深色定点；文字与公式未裁切；端点退化式 1=0 旁注明斜率方程无解；首尾恢复相同状态 |
| LOCAL PRODUCTION | PASS | 共享工具真实渲染并导出成功；3,975,310 bytes，约 3.79 MiB |
| USER VISUAL | PENDING | 待用户查看 |
| ANDROID DEVICE | PENDING | 未执行 Android 真机验收，待用户确认 |
| FINAL FREEZE | PENDING | 用户视觉与真机验收未完成 |
| UID images/ 写入 | PASS | 按用户要求首次写入新 GIF，未覆盖原有 PNG/GIF |
| Publisher 内容包 / Sync | PENDING（未执行） | 未执行内容包、Sync、APK 或 Git 提交 |

首末帧 RGB 通道平均绝对差为 0.426 / 0.388 / 0.384（0–255），
包含 GIF 编码与抗锯齿差异，不宣称逐像素完全相同。
未把竖直方向显示成“无穷大斜率”；它始终按一般式绘制。
斜率方程只数有限根，切线总数由实际几何接触模型独立求得。

证据位于 `build/manim/C009/tangent_slope_range/`：
`render.log`、`contact.png`、`key_00.png` 至 `key_07.png`、
`frame_review.json`、MP4、隔离 GIF、`protected_hashes.json`。

已核对 Publisher 实际消费契约：`prepare_knowledge_images.mjs` 接受
images/ 下的直接 PNG/GIF，验证多帧、时序及无限循环后按原名逐字节复制。
本任务只核对消费代码，不运行 Publisher。

任务开始记录 12 个既有文件 SHA-256（六段 TeX、main.tex、meta.json、PDF、
原有三张 PNG）；本地验收时复核均未变化。任务不写入正式知识源或 PDF，
已有用户改动全部保留。
