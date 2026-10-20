# C072 · 抛物线切线三角形

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

按两切点解析求切线交点与弦中点，动态改变弦的宽度与位置，独立面积行列式验证三次关系。

核心式：`S=|x1-x2|³/(8p)`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C072_parabola_archimedean_triangle_vertex_area/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C072 -SceneFile scene_batch.py -Scene C072Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
