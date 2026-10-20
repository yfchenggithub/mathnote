# C046 · 圆锥曲线通径

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

三类曲线分段展示真实过焦点通径，逐段变化参数；淡出后切换类别，不制造穿越退化曲线的假运动。

核心式：`L=2b²/a or 2p`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C046_conic_latus_rectum_length/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C046 -SceneFile scene_batch.py -Scene C046Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
