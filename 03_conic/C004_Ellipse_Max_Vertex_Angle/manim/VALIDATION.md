# C004 GIF 本地验收 · 2026-10-19

目标文件：`../images/ellipse_max_vertex_angle.gif`。
用户明确要求生成 GIF 并放入 images/，通过共享 exporter 首次写入，
使用 `-Publish -AssetName ellipse_max_vertex_angle.gif`，未使用覆盖参数。

| Gate | 状态 | 已执行的证据 |
| --- | --- | --- |
| 数学审计 | PASS | 读取当前六段 TeX 和 meta.json，确认长轴端点张角为钝角、最大值公式和开定义域；未混用焦点张角模型 |
| 数学自动测试 | PASS | 7 项 unittest 实际通过；四种轴比，逐点对照实际向量角与通式、余弦定理、面积及斜率积；测试最大值、负正切、对称、单调性、端点无定义与极限 |
| 运动定义域 | PASS | 上下两开弧各 401 个采样点合法；切换时隐去动点图形，未将长轴端点当成可定义角的点 |
| 数学关键状态 | PASS | a=2、b=1；上/下短轴端点均 126.8698976°，实时显示 126.9°；靠近端点停止处约 95.975°，未显示成可取到的 90° |
| 真实关键帧 | PASS | 已查看最终 GIF 的 0、3.5、6.5、11.5、13.5、17.8、21、24.9 秒合成图，并查看上下最大值全尺寸帧；公式、射线、钝角弧、点位与读数一致 |
| 全帧技术检查 | PASS | 576×1024；302 帧；250 个不同帧；25.16 秒；80–90 ms/帧；无限循环；完整解码；0 黑帧；302 帧方差检查无纯色空帧 |
| 教学表达 | PASS（本地审查） | 先辨钝角，再展示高度单调关系；上短轴端点展示作高、直角、a/b 比；下短轴端点验证对称最大值；持续注明两长轴端点排除 |
| 视觉质量 | PASS（本地审查） | 等比例坐标；蓝椭圆、橙射线/角弧、绿高度/最大值；半透明三角形未遮住辅助线；文字、数值未裁切；首尾恢复同一合法状态 |
| LOCAL PRODUCTION | PASS | 共享工具渲染及导出成功，GIF 3,248,678 bytes（约 3.10 MiB） |
| USER VISUAL | PENDING | 待用户查看 |
| ANDROID DEVICE | PENDING | 未进行 Android 真机验收，待用户确认 |
| FINAL FREEZE | PENDING | 用户视觉和真机验收未完成 |
| UID images/ 写入 | PASS | 按用户要求首次写入新 GIF；未覆盖原有资源 |
| Publisher 内容包 / Sync | PENDING（未执行） | 未构建发布内容包，未运行 Sync 或 APK 构建 |

技术与图像证据在 `build/manim/C004/max_vertex_angle/`：
`render.log`、`contact.png`、`key_00.png` 至 `key_07.png`、
`frame_review.json`、MP4、隔离 GIF、`protected_hashes.json`。
首末帧 RGB 通道平均绝对差为 0.461 / 0.393 / 0.367（范围 0–255），
含 GIF 编码和抗锯齿差异，不宣称像素完全一致。

Publisher 实际契约已核对：`publish.py` 调用 `asset_preparation.py`，
worker `prepare_knowledge_images.mjs` 接受 images/ 下直接 PNG/GIF；
GIF 通过动画与循环检查后按原名逐字节复制。此次只审计消费契约，不执行 Publisher。

任务开始已记录 12 个既有文件的 SHA-256（六段 TeX、main.tex、
meta.json、PDF 和三张 PNG）；与写入前比较均无变化。
工作树中原有 TeX、元数据和 PDF 改动全部保留。
