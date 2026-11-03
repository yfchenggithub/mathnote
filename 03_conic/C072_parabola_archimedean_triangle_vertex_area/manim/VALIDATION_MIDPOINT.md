# C072 中线平分性质修订验收

日期：2026-11-03。状态：**LOCAL PRODUCTION PASS / 正式覆盖待授权**。

## 教学分镜与数学依据

以正式六段 TeX、meta.json 为只读事实源。当前演示 x²=2py、p=1，
切点横坐标为 t-d、t+d，d>0。
由两切线求 P=(t,(t²-d²)/(2p))，由弦中点求 M=(t,(t²+d²)/(2p))；
再从曲线方程独立求 N=(t,t²/(2p))，故 PN=NM=d²/(2p)=PM/2。

1. 保留面积随间距变化、固定间距平移时面积不变的演示。
2. 在当前状态引入曲线交点 N，将 PM 分成两段并画相同刻痕。
3. 改变间距与位置，同步显示 PN、NM 的近似长度和 PN=NM=PM/2。
4. 返回开场状态循环。底部固定两行入口文案不随内容淡出。

## 证据

预览：`build/manim/C072/midpoint_revision/midpoint_revision.gif`。
MP4 位于同一目录。未使用 `-Publish` 或 `-Overwrite`。

| Gate | 状态 | 实际检查 |
| --- | --- | --- |
| M 数学自动测试 | PASS | test_batch.py 5 项通过；全运动参数矩形 1681 状态，另检查小弦、大弦、重合排除与小数舍入 |
| M 渲染状态 | PASS | 334 条实际渲染状态满足曲线上点、竖直对齐、线段内部、等长及面积行列式关系 |
| M 实际图像交点 | PASS | 对已导出 GIF 的 107 帧（含可辨认的淡入阶段）定位金色点 N，与模型投影的最大差为 1.23 px |
| V 真实关键帧 | PASS | 检查开场、最大间距、N 淡入、最小间距、横向移动、等长结论、退场和首尾；未见标签覆盖或裁切 |
| V 标签边界 | PASS | 8405 个实际 MathTex 标签矩形与曲线/三角形/中线逐一核对，无交叠；全图等比例坐标 |
| T 教学表达 | PASS | N 明确在曲线上，等长刻痕与同步数值共同展示“线段 PM 被平分”，未声称弧长被平分 |
| G 技术检查 | PASS | Task 13F 共享验证器完整解码：576×1024，220 帧，187 个不同帧，18.33 s，80–90 ms/帧，无黑帧，无限循环 |
| G 底部与循环 | PASS | 220 帧均核对两行文字轮廓；首尾视觉一致；允许 MP4 压缩/GIF 量化造成的边缘像素差异 |
| USER VISUAL | PENDING | 用户尚未确认此候选版本 |
| ANDROID DEVICE | PENDING | 需用户真机确认 |
| FINAL FREEZE | PENDING | 不能用本地检查代替用户与真机验收 |
| PUBLISHED / SYNCED | PENDING | 未覆盖正式资源，未运行 Publisher、Content Package、Sync 或 APK 构建 |

证据目录：`build/manim/C072/midpoint_review/`。
含 math_tests.log、build.log、frame_review.json、真实关键帧、全部 220 帧联系表和保护哈希。

候选 GIF 大小 2,312,072 bytes；SHA-256：
`56937b6ea9a0f286c34e9e7aac1f57bd81cd7d8bed2ee306554c2c32b1e14599`。

已有正式 GIF 的本轮基线 SHA-256：
`6788fa4f8b4ff2d59b7fa2d8c4b7e2344be2df02196f8ee69b77cfbbc1afbbf3`。
六段 TeX、meta.json、PDF、三幅 PNG 与正式 GIF 共 12 个保护文件均与本轮开始时一致。
此前 VALIDATION_BATCH.md 属历史记录，不作为本次修订或当前正式文件哈希的验收证明。
