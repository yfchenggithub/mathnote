# C076 · 配极互换

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

固定极点 P，令 Q 在其极线上滑动，直接验证 Q 的极线恒过 P；屏幕只截取直线显示范围，不截断数学构造。

核心式：`P∈lQ iff Q∈lP`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C076_pole_polar_conjugacy/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C076 -SceneFile scene_batch.py -Scene C076Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
