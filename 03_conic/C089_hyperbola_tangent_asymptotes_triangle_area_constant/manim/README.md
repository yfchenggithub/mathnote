# C089 切线三角形面积不变量

数学源：本 UID 的正式六段 TeX 和 meta.json（仅阅读，本任务不修改）。
独立模型：`model.py`；独立 Scene：`scene_area.py:C089TangentArea`。

模型以 t 为参数，右支 P=(a cosh t,b sinh t)，
A=(a exp t,b exp t)，B=(a exp(-t),-b exp(-t))；
左支同时乘 -1。所有点满足标准切线方程，P=(A+B)/2，
面积为 ab，OA·OB=a²+b²。动画取 a=1.5、b=1、-0.75≤t≤0.75，
显示右支，严格保持等比例坐标；测试额外覆盖左右支及顶点。

分镜：顶点底高计算 → 上移切点 → 返回顶点并显示乘积不变量 →
下移切点 → 返回顶点并总结面积公式 → 同一顶点无跳变循环。
底部两行品牌文案全程固定。三角形面积读数来自模型行列式。

```powershell
.\.venv-manim\Scripts\python.exe -m unittest discover -s .\03_conic\C089_hyperbola_tangent_asymptotes_triangle_area_constant\manim -p test_model.py -v
.\scripts\manim\render.ps1 -Uid C089 -Scene C089TangentArea -SceneFile scene_area.py -Name tangent_area
.\scripts\manim\export_gif.ps1 -Uid C089 -Scene C089TangentArea -SceneFile scene_area.py -Name tangent_area -AssetName C089_tangent_area_constant.gif
```

在隔离预览完成数学、真实关键帧和全帧技术验收后，按用户本次要求
使用同一导出入口的 `-Publish` 将新文件放入本 UID 的 images/。
不得覆盖已有文件；不运行 Publisher、Content Package、Sync 或 APK 构建。
Android 真机效果由用户确认，本地检查不代表 Android PASS 或 FINAL FREEZE。
