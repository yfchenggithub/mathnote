# C057 · 双曲线焦点分弦

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

同支和异支分别选取有界真实焦点弦，不以屏幕截断代替远端交点；切换时隐藏构造后重设参数。

核心式：`same:1/AF+1/BF; opposite:|1/AF-1/BF|=2a/b²`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C057_hyperbola_focus_chord_reciprocal_sum_diff/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C057 -SceneFile scene_batch.py -Scene C057Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
