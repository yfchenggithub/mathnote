# C043 · 半轴与半焦距关系

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

构造真实直角三角形并连续改变短边，突出椭圆 a 为斜边、双曲线 c 为斜边的区别。

核心式：`c²=a²+b²`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C043_hyperbola_abc_relation/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C043 -SceneFile scene_batch.py -Scene C043Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
