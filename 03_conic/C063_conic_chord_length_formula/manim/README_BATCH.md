# C063 · 弦长与坐标投影

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

先用任意线段的水平与竖直投影解释距离公式；这条结论本质不依赖端点所属曲线，画面不虚构固定曲线上的端点。

核心式：`AB=sqrt(1+k²)|x1-x2|`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C063_conic_chord_length_formula/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C063 -SceneFile scene_batch.py -Scene C063Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
