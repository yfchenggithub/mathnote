# C062 · 中点弦斜率

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

真实两端点确定弦，中点由坐标平均计算，斜率由端点差独立求得；双曲线采用满足正式条件的异支弦，抛物线避开竖直弦。

核心式：`k=p/y0`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C062_parabola_midpoint_chord_slope/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C062 -SceneFile scene_batch.py -Scene C062Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
