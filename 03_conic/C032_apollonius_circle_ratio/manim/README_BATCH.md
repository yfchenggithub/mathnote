# C032 · 阿波罗尼斯圆

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

固定距离比 2，以真实长度比验证圆轨迹，动态描迹；不跨越 λ=1 的无界变化。

核心式：`PA/PB=lambda`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C032_apollonius_circle_ratio/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C032 -SceneFile scene_batch.py -Scene C032Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
