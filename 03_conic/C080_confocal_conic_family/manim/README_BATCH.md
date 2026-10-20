# C080 · 共焦曲线族

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

用半轴不变量独立构造共焦椭圆、双曲线族；两类在安全范围内分别变化，避开退化参数。画面不采用特定 λ 正负约定，可供符号相反但等价的 C082 复用。

核心式：`A²−B²=c² or A²+B²=c²`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C080_confocal_conic_family/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C080 -SceneFile scene_batch.py -Scene C080Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
