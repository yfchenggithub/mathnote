# C030 · 焦点弦三角形周长

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

绕左焦点转动弦，和另一焦点构成三角形；周长从三条实际边长计算，解释弦分解与两组椭圆定义。

核心式：`C=4a`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C030_ellipse_focal_triangle_perimeter_constant/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C030 -SceneFile scene_batch.py -Scene C030Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
