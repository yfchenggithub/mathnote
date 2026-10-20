# C069 · 切点弦或蒙日圆

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

独立解析求解真实切点，以曲线方程、切向正交和切点弦双线性方程分别校验。双曲线选取确有两条实切线的点，不以含糊的“外部”代替条件。

核心式：`polar/contact geometry`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C069_hyperbola_chord_of_contact/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C069 -SceneFile scene_batch.py -Scene C069Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
