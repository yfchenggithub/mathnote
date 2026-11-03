# C073 开口向上 GIF 验收

日期：2026-11-03。场景：`scene_upward.py / C073UpwardTangentMidpoint`。

## 数学与分镜

事实源为本 UID 六段 TeX 与 meta.json 中的 x²=2py 结论。
选取 x²=4y（p=2），固定 A(-2,1)，移动 B=(b,b²/4)，b∈[0,3]。
M=((b-2)/2,-b/2)，N=((b-2)/2,(b²+4)/8)，因此 x_M=x_N，且 y_N-y_M=(b+2)²/8>0。
两切点全程不同，MN 始终是一条确定的竖直线。

关键状态：

- b=3：M=(1/2,-3/2)，N=(1/2,13/8)，与 y 轴平行。
- b=2：M=(0,-1)，N=(0,1)，MN 与 y 轴重合。
- b=0：B 为顶点，B 处切线 y=0，M=(-1,0)，N=(-1,1/2)。
- 返回 b=3，起止几何、公式、数值、状态文字一致。

坐标采用横纵相同的 1.05 场景单位比例，动画直接渲染真实抛物线，未旋转或修改既有 GIF。
模型在同 UID 内复用纯坐标交换及切线裁切；未引入其他 UID 私有实现。

## 验收

| Gate | 状态 | 证据 |
|---|---|---|
| M 数学 | PASS | 7 项联合测试通过，其中新加 3 项：一般参数、961 个动画采样及切线裁切、对称弦和顶点状态 |
| V 本地视觉 | PASS | 检查 GIF 解码后的 0、2、5、8、10.5、13.5、17 秒帧；点标签避让坐标轴与竖直辅助线；两行固定品牌文案完整 |
| T 教学表达 | PASS | 连续移动 B，实时横坐标来自模型；在与 y 轴重合和顶点水平切线处停顿 |
| G 技术 | PASS | 冻结 verify_gif.py 全帧解码通过；576×1024，212 帧，168 个不同帧，17.66 秒，无限循环，0 黑帧，单帧 80–90 ms |
| USER VISUAL | PENDING | 等待用户视觉确认 |
| D ANDROID DEVICE | PENDING | 等待用户 Android 真机确认 |
| FINAL FREEZE | PENDING | 用户视觉及真机 Gate 未确认 |

## 交付边界

构建与关键帧：`build/manim/C073-production/C073/upward_tangent_midpoint_motion/`。
按用户要求，冻结 exporter 使用 `-Publish` 首次写入 `images/c073_upward_tangent_midpoint_motion.gif`，不使用 `-Overwrite`。
原向右开口 GIF 的 SHA256 保持 `fed9aae13d31b52a09bc4a293926977671f5632fc2a54c962c4eb803b09e9354`。
未修改正式六段 TeX、meta.json、PDF、共享生产工具；未运行 Publisher、Content Package、Sync 或 APK 构建。
