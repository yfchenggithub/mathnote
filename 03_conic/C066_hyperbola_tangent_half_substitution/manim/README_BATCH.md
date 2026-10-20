# C066 · 过点切线方程

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

真实点沿单支双曲线或抛物线移动，以法向量绘制一般式切线，包含顶点竖直状态。

核心式：`x0x/a²-y0y/b²=1`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C066_hyperbola_tangent_half_substitution/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C066 -SceneFile scene_batch.py -Scene C066Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
