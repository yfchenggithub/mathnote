# C079 · 渐近线平行线

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

固定与渐近线平行的斜率，分别在截距正、负两个有界区间平移，不穿越无穷远；唯一交点实际代入验证且不是切点。

核心式：`y=(b/a)x+m,m≠0`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C079_hyperbola_asymptote_parallel_unique/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C079 -SceneFile scene_batch.py -Scene C079Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
