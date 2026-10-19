# C008 GIF 本地验收 · 2026-10-19

交付：`../images/ellipse_tangent_point_formula.gif`。
用户明确要求生成并放入 images/；通过共享 exporter 的
`-Publish -AssetName ellipse_tangent_point_formula.gif` 首次写入，未使用覆盖参数。

| Gate | 状态 | 已执行证据 |
| --- | --- | --- |
| 动画数学审计 | PASS | 读取当前六段正式 TeX 与 meta.json；切点式、坐标轴端点、外点两切点及极线所用结论已核对；原文另有一处未用于动画的例 5 笔误，见下文 |
| 数学自动测试 | PASS | 7 项 unittest 实际通过；三种椭圆各 721 个采样点核验切点、一般式相切判定、方向与法向量正交、支撑不等式；另测完整一周裁切、轴端点、正式例题、外点两切线、内点/原点分类及非法切点拒绝 |
| 数学关键状态 | PASS | a=2、b=1；上/下短轴端点切线 y=±1；左/右长轴端点切线 x=±2；初始 P=(√2,√2/2) 的切线为 (√2/4)x+(√2/2)y=1 |
| 外点与极线 | PASS | M=(2,2)，S=5；T1=(2,0)、T2=(-6/5,4/5)；两切线均经过 M；极线 x+4y-2=0 经过两切点，不经过 M |
| 真实关键帧 | PASS | 已查看最终 GIF 的 0、4.3、8.2、12、15.9、19.9、22、25.1 秒合成图，以及外点极线全尺寸帧；开场另查看全尺寸画面；点位、直线、坐标和公式一致 |
| 全帧技术检查 | PASS | 576×1024；304 帧；257 个不同帧；25.33 秒；80–90 ms/帧；无限循环；完整解码；0 黑帧；304 帧方差检查无纯色空帧 |
| 教学表达 | PASS（本地审查） | 已知切点直接代入→动态切线→四个轴端点→外点两切线和切点弦；区分切点式与极线；竖直切线使用一般式绘制 |
| 视觉质量 | PASS（本地审查） | 等比例坐标；蓝椭圆、橙切线/切点、绿极线；核心文字与公式无裁切；公式短过渡后再运动；首尾恢复相同状态 |
| LOCAL PRODUCTION | PASS | 共享工具真实渲染、导出成功，4,172,614 bytes，约 3.98 MiB |
| USER VISUAL | PENDING | 待用户查看 |
| ANDROID DEVICE | PENDING | 未执行 Android 真机验收，待用户确认 |
| FINAL FREEZE | PENDING | 用户视觉与真机验收未完成 |
| UID images/ 写入 | PASS | 按用户要求首次写入新 GIF；原有 PNG/GIF 未覆盖 |
| Publisher 内容包 / Sync | PENDING（未执行） | 未运行内容包、Sync、APK 或 Git 提交 |

首末帧 RGB 通道平均绝对差为 0.407 / 0.358 / 0.344（0–255），
含 GIF 编码及抗锯齿差异，不宣称逐像素完全相同。

构建证据位于 `build/manim/C008/tangent_point_formula/`：
`render.log`、`contact.png`、`key_00.png` 至 `key_07.png`、
`frame_review.json`、MP4、隔离 GIF、`protected_hashes.json`。

## 原文发现与并发更新

`04_examples.tex` 例 5：M2=(1/2,0) 对椭圆 x²/4+y²=1 的正确极线为
x/8=1，即 x=8，原文写成 x/4=1、x=4。已向用户说明；
本片不使用该错误示例，模型测试按正确 x=8 处理。本任务未修改正式知识源。

初始记录了 12 个既有文件的 SHA-256。六段 TeX 与三张 PNG 的哈希未变；
main.tex、meta.json、PDF 在任务执行期间出现并发变化，非本任务写入。
已重读当前 main.tex 和元数据，标题已更新为“椭圆切线方程与切点弦”，
动画使用的数学公式及外点条件保持一致；保留当前并发更新，不回滚、不覆盖。
因此不把全部 12 个文件宣称为“0 个变化”。

Publisher 实际消费契约已核对：`prepare_knowledge_images.mjs` 接受
images/ 下直接 PNG/GIF，验证动画时序与无限循环后按原文件名逐字节复制。
本任务只核对消费代码，不执行 Publisher。
