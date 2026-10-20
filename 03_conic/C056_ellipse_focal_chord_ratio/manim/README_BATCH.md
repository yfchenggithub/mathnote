# C056 · 椭圆焦点分弦比例

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。

标明两射线方向对应的 A、B，旋转焦点弦并读取真实分段长度比，在通径处停顿。

核心式：`AF/BF=(1-e cos theta)/(1+e cos theta)`。动画数学模型与测试独立放在本目录，无跨 UID 私有模型导入。

复现：
```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C056_ellipse_focal_chord_ratio/manim -p test_batch.py -v
.\scripts\manim\export_gif.ps1 -Uid C056 -SceneFile scene_batch.py -Scene C056Animation -Name animation -Rebuild
```

正式资源经数学测试、真实关键帧和全帧技术审核后显式写入 images；不覆盖已有资源。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 PENDING。不执行 Publisher 内容包、Sync、APK 或 Git 提交。

正式原文符号与右焦点约定冲突；模型采用正确符号，详见 MATH_AUDIT_BATCH.md。
