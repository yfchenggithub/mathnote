# C050 · 焦点三角形与焦半径

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

真实三角形面积由底边与高度计算，焦点夹角由两向量夹角计算；运动避开退化顶点。双曲线焦半径版本显示绝对值一次式。

核心式：`r1=|a+ex|,r2=|a-ex|`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C050_hyperbola_focal_radius/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C050 -SceneFile scene_batch.py -Scene C050Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
