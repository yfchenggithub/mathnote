# C078 · 椭圆参数角

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

辅助圆上的点竖直投影到椭圆，区分参数角和一般的椭圆中心极角。

核心式：`x=a cos θ,y=b sin θ`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C078_ellipse_parametric_equation/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C078 -SceneFile scene_batch.py -Scene C078Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
