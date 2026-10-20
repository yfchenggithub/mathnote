# C054 · 抛物线焦点弦性质

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

真实焦点弦旋转，两个端点始终由焦点射线与抛物线解析求交；各 UID 分别突出弦长最小、倒数和或坐标积。

核心式：`1/AF+1/BF=2/p`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C054_parabola_focal_chord_reciprocal_sum/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C054 -SceneFile scene_batch.py -Scene C054Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
