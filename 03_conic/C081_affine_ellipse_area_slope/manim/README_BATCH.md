# C081 · 椭圆仿射化圆

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

同一仿射变换同时作用于曲线、三角形与直线；运动中显示一般 s 关系，到达 a/b 时才宣告化圆。

核心式：`S_s=sS,k_s=sk`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C081_affine_ellipse_area_slope/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C081 -SceneFile scene_batch.py -Scene C081Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
