# C064 · 端点连线斜率积

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

动点连接两条实轴端点，直接读取端点差所得斜率积；明确不同于中心连线与切线模型，排除端点。

核心式：`k1k2=-b²/a²`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C064_ellipse_slope_product_constant/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C064 -SceneFile scene_batch.py -Scene C064Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
