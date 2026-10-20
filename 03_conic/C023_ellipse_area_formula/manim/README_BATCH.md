# C023 · 椭圆面积

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

单位圆先横伸长、再纵伸长；保持半轴乘积演示等面积椭圆，最后逆向还原。

核心式：`S=pi*a*b`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C023_ellipse_area_formula/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C023 -SceneFile scene_batch.py -Scene C023Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。
