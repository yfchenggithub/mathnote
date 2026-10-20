# C025 · 椭圆旋转体

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

椭圆绕 x 轴真实三维旋转，以固定斜投影显示线框；再沿轴移动真实圆盘截面，说明积分体积。

核心式：`V_x=\frac43\pi ab^2`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C025_ellipsoid_volume_revolution/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C025 -SceneFile scene_batch.py -Scene C025Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
