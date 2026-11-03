# C073 GIF 验收记录

日期：2026-11-03。状态：LOCAL PRODUCTION PASS；用户视觉与 Android 验收待确认。

## 事实源、模型与分镜

读取当前 UID 的正式六段 TeX 与 meta.json。模型、测试、场景均位于本目录；未修改数学知识源、PDF、共享工具或其他 UID。
图取 p=2，固定 y_A=-2，y_B 在 [0,4] 连续往返。M=(-b/2,(b-2)/2)，N=((b²+4)/8,(b-2)/2)；两切点全程不同，MN 长度为 (b+2)²/8>0。
对称状态 b=2 时 M=(-1,0)、N=(1,0)，MN 与 x 轴重合；顶点状态 b=0 时 B=(0,0)、其切线 x=0，M=(0,-1)、N=(1/2,-1)。

## 验收 Gate

| Gate | 状态 | 实际证据 |
|---|---|---|
| M 数学自动测试 | PASS | `test_model.py` 4 项测试通过；一般参数含 p<0、顶点及对称情形；动画范围 961 个采样点检查曲线、切线裁切、交点、中点及非零距离 |
| 数学关键状态 | PASS | b=4、2、0 与模型吻合；不把重合称为两条不同直线平行 |
| V 本地视觉 | PASS | 检查解码 GIF 的 0、2、5、8、10.5、13.5、17 秒真实帧；修正 A、B、M 标签避让；等比例坐标；两行入口文案完整 |
| T 教学表达 | PASS | 由 B 的连续运动凸显 M、N 同高；在轴重合和顶点竖直切线处停顿，实时数值与模型同步；动画为示例演示，一般证明保留在 PDF |
| G 全帧技术 | PASS | 576×1024，212 帧，168 个不同帧，17.66 秒；每帧 80–90 ms；无限循环；全帧解码成功，0 黑帧；2,593,458 bytes |
| USER VISUAL | PENDING | 尚未收到用户视觉确认 |
| D ANDROID DEVICE | PENDING | 尚未收到用户 Android 真机播放、字体、裁切与循环确认 |
| FINAL FREEZE | PENDING | 用户视觉及 Android Gate 尚待确认 |

全帧底部区域与首帧的最大平均像素差为 1.025/255，属于视频/调色板编码微小差异；首尾全帧平均像素差为 0.030/255，首尾对象、文字和数值一致。图形比例与正文公式独立核对，不以技术解码替代数学检查。

## 路径与边界

- 隔离构建和关键帧证据：`build/manim/C073-production/C073/tangent_midpoint_motion/`。
- 用户明确要求写入本 UID 的 images；通过冻结 exporter 的 `-Publish` 写入 `images/c073_tangent_midpoint_motion.gif`，不使用 `-Overwrite`。
- 保留旧 `parabola_tangent_intersection_midpoint_parallel.gif` 和 `REUSE_C072_BATCH.md` 的已有删除状态。
- 已核对现行 `scripts/zhishu/publish.py`、`asset_preparation.py` 的 images/GIF 发现和字节保留逻辑；文件名符合 exporter 的资产命名检查。
- LOCAL ASSET WRITTEN 不等于 Publisher / Content Package / Sync 发布；本次未运行上述发布链路或 APK 构建。
