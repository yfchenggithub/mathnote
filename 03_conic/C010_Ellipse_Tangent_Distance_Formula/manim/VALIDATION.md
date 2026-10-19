# C010 GIF 本地验收 · 2026-10-19

交付：`../images/ellipse_tangent_distance.gif`。
用户明确要求生成并放入本 UID 的 images/；通过共享 exporter 的
`-Publish -AssetName ellipse_tangent_distance.gif` 首次写入，未使用覆盖参数。

| Gate | 状态 | 已执行证据 |
| --- | --- | --- |
| 数学审计 | PASS | 读取当前六段 TeX 与 meta.json；核对切线前提、两焦点垂距积/和、中心距范围及主圆完整轨迹的正向和逆向证明 |
| 数学自动测试 | PASS | 6 项 unittest 实际通过；四种轴比各 721 个法向角样本核验真实切点、切线方程、焦点到直线的距离、垂足在线上、垂线与切线正交、乘积/和、垂足半径及中心距范围 |
| 主圆完整可达 | PASS | 对 721 个主圆目标点独立构造 (p-c)x+qy=a²-cp，验证一般式相切并核对右焦点垂足确实为目标点；实现核验与正式逆向恒等式一致 |
| 数学关键状态 | PASS | a=5、b=4、c=3；水平 y=4 时 d1=d2=4、d0=4；竖直 x=5 时 d1=8、d2=2、d0=5；初始 3x+5y=25 对应 P=(3,16/5)、H2=(75/17,40/17) |
| 真实关键帧 | PASS | 已查看最终 GIF 的 0、4.3、8.6、10.7、15、20.4、24.2、26.1 秒合成图，以及竖直边界、中心垂足全尺寸帧；另查看开场全尺寸画面；距离、切点、垂足、直角标记、主圆和公式一致 |
| 全帧技术检查 | PASS | 576×1024；316 帧；265 个不同帧；26.33 秒；80–90 ms/帧；无限循环；完整解码；0 黑帧；316 帧方差检查无纯色空帧 |
| 教学表达 | PASS（本地审查） | 以实际垂线区分 P 与 H1/H2；先看距离变而积不变，再看主圆完整轨迹，最后加入中心垂足 Q；水平、竖直边界单独停顿 |
| 视觉质量 | PASS（本地审查） | 坐标统一等比例；蓝椭圆、橙/绿垂距及垂足、深色切线与切点；轨迹与当前 H2 保持同色；近重合点错开标签，真正竖直才标 P=H1=H2；核心内容未裁切 |
| LOCAL PRODUCTION | PASS | 共享工具真实渲染、导出成功；4,323,081 bytes，约 4.12 MiB |
| USER VISUAL | PENDING | 待用户查看 |
| ANDROID DEVICE | PENDING | 未执行 Android 真机验收，待用户确认 |
| FINAL FREEZE | PENDING | 用户视觉及真机验收未完成 |
| UID images/ 写入 | PASS | 按用户要求首次写入新 GIF，未覆盖原有 PNG/GIF |
| Publisher 内容包 / Sync | PENDING（未执行） | 未执行内容包、Sync、APK 或 Git 提交 |

两垂距显示为保留两位小数的近似值，乘积由实际未舍入的距离计算。
不以近似读数的直接乘法冒充精确不变量。
首末帧 RGB 通道平均绝对差为 0.512 / 0.421 / 0.390（0–255），
包含 GIF 编码与抗锯齿差异，不宣称逐像素相同。

证据位于 `build/manim/C010/tangent_distance/`：
`render.log`、`contact.png`、`key_00.png` 至 `key_07.png`、
`frame_review.json`、MP4、隔离 GIF、`protected_hashes.json`。

Publisher 实际消费契约已核对：`prepare_knowledge_images.mjs` 接受
images/ 下直接 PNG/GIF，验证动画时序、帧数及无限循环后按原名逐字节复制。
本任务只核对消费代码，不运行 Publisher。

本地验收时复核任务开始记录的 12 个既有文件 SHA-256：
六段 TeX、main.tex、meta.json、PDF、三张 PNG 均未变化。
已有用户改动保留；本任务不写入正式知识源或 PDF。
