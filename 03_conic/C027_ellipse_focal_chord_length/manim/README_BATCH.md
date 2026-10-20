# C027 · 椭圆焦点弦长

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

旋转真实过焦点直线，以解析二次方程求两个端点，展示长轴最长、通径最短；使用角度模型覆盖竖直弦。

核心式：`L=2ab^2/(a^2 sin^2(theta)+b^2 cos^2(theta))`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C027_ellipse_focal_chord_length/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C027 -SceneFile scene_batch.py -Scene C027Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
