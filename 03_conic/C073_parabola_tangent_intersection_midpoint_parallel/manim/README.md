# C073 — 切线交点与弦中点同高

事实源：本 UID 六段 TeX、meta.json。独立模型，不导入其他 UID。

## 分镜与数学审计

- 取 y²=4x，即 p=2。固定 A(1,-2)，令 B=(b²/4,b)，b 在 [0,4] 内连续往返；A、B 全程不同。
- 每帧由模型计算 M=(-b/2,(b-2)/2)、N=((4+b²)/8,(b-2)/2)，切线采用隐式方程裁切，覆盖顶点竖直切线。
- b=4 建立两切线、弦和 MN；b=2 停顿，MN 与 x 轴重合；b=0 停顿，B 为顶点；返回 b=4，无跳变循环。
- 不声称动画代替一般证明；一般的 p≠0、不同两切点结论见 PDF。源模型测试同时覆盖 p<0。
- MN 的绿色水平段与虚线追踪高度；动态数字来自同一模型。等比例坐标，无独立拉伸。
- 两行品牌文案全程固定；不创建 Publisher 包，不执行 Sync。

## 构建

```powershell
./.venv-manim/Scripts/python.exe -B -m unittest discover -s 03_conic/C073_parabola_tangent_intersection_midpoint_parallel/manim -p test_model.py
./scripts/manim/render.ps1 -Uid C073 -Scene C073TangentMidpoint -Name tangent_midpoint_motion -BuildRoot build/manim/C073-production
./scripts/manim/export_gif.ps1 -Uid C073 -Scene C073TangentMidpoint -Name tangent_midpoint_motion -BuildRoot build/manim/C073-production -AssetName c073_tangent_midpoint_motion.gif
```

只在本地数学、技术及真实关键帧检查后，用同一导出命令的 `-Publish` 写入 images。使用新文件名，保留用户已删除的旧 GIF 状态。

用户视觉验收及 Android 真机验收独立记录，未经确认不标记 FINAL FREEZE。

## 开口向上版本

`scene_upward.py` / `C073UpwardTangentMidpoint` 使用 x²=4y，固定 A(-2,1)，令 B=(b,b²/4)，b 在 [0,3] 连续往返。
其模型 `UpwardConfiguration` 通过同 UID 坐标交换得到：M=((b-2)/2,-b/2)，N=((b-2)/2,(b²+4)/8)。MN 全程竖直。
在 b=2 时突出 MN 与 y 轴重合；b=0 时 B 到达顶点，切线为水平直线 y=0。
单独布置竖直追踪线、实时横坐标、切点和中点标签；不旋转既有 GIF，不改原版场景或资源。

```powershell
./.venv-manim/Scripts/python.exe -B -m unittest discover -s 03_conic/C073_parabola_tangent_intersection_midpoint_parallel/manim -p test_*.py
./scripts/manim/render.ps1 -Uid C073 -Scene C073UpwardTangentMidpoint -SceneFile scene_upward.py -Name upward_tangent_midpoint_motion -BuildRoot build/manim/C073-production
./scripts/manim/export_gif.ps1 -Uid C073 -Scene C073UpwardTangentMidpoint -SceneFile scene_upward.py -Name upward_tangent_midpoint_motion -BuildRoot build/manim/C073-production -AssetName c073_upward_tangent_midpoint_motion.gif
```

经本地检查后以 `-Publish` 首次写入 images，不使用 `-Overwrite`。真机验收仍需用户确认。
