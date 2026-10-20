# C037 · 圆锥曲线第一定义

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

两焦点固定，动点沿真实曲线运动，以直接距离显示定义中的和或差；双曲线两支均自动校验。

核心式：`|r1-r2|=2a`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C037_hyperbola_first_definition/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C037 -SceneFile scene_batch.py -Scene C037Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
