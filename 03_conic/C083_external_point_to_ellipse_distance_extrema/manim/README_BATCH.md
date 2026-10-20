# C083 · 椭圆外点距离极值

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

真实外点距离函数；分区间二分隔离本例全部简单驻点，以驻点比较并用密集整周扫描交叉验证全局极值。画面显示端点处切线与极值距离垂直，不套圆的半径加减公式。

核心式：`min/max sqrt(F(θ)),F′=0`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C083_external_point_to_ellipse_distance_extrema/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C083 -SceneFile scene_batch.py -Scene C083Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
