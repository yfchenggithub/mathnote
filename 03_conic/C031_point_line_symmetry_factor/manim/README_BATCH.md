# C031 · 点关于直线对称

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

点与其对称点同步移动，强调垂直及垂足中点条件；运动避开标签重合。

核心式：`Pprime=P-2t(A,B)`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C031_point_line_symmetry_factor/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C031 -SceneFile scene_batch.py -Scene C031Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
