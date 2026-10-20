# C074 · 圆锥曲线角平分

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

三类曲线分段检验内角平分和真实切线法线。原文抛物线把“开口方向射线”的内角平分线误写为切线，动画采用正确的法线平分并记录差异，未修改正式数学源。

核心式：`ellipse normal; hyperbola tangent; parabola opening ray normal`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C074_conic_optical_angle_bisector/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C074 -SceneFile scene_batch.py -Scene C074Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
