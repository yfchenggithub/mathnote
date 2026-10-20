# C040 · 焦点—准线定义

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

焦点和对应准线固定，移动曲线点并绘制真实垂足，直接计算焦准距离比；抛物线同时展示焦半径坐标式。

核心式：`PF/PH=e`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C040_hyperbola_focus_directrix_ratio/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C040 -SceneFile scene_batch.py -Scene C040Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
