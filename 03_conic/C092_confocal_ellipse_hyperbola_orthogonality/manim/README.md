# C092 动画：交点在变，直角不变

事实源：本 UID 正式六段 TeX 与 meta.json（只读，2026-11-01）。
固定 a=4、c=2、b²=12，双曲线 A 在 [0.65,1.55] 往返变化，B²=4−A²。
图形保持等比例坐标。每帧独立计算交点 (±2A,±√(12(4−A²))/2)、真实切向量和直角标记。
变化的是双曲线；点 P 不被描述为沿一条固定双曲线运动。

分镜：建立共焦曲线与四交点 → 显示 P 处切线 → A 增减、交点及切线同步变化 → 四点均标出直角 → 返回观察状态。
只突出切线夹角，不把焦角画作直角。固定两行入口文字全程显示。

测试：在本目录执行 `D:/mathnote/.venv-manim/Scripts/python.exe -B -m unittest test_model.py`。
渲染：`scripts/manim/render.ps1 -Uid C092 -Scene C092Orthogonality -Name orthogonality -BuildRoot build/manim/C092-production`
导出：同参数调用 `scripts/manim/export_gif.ps1`。检查后用 `-Publish -AssetName confocal_orthogonality.gif` 写入 images；不使用覆盖选项。

验收结果见 VALIDATION.md；Android 真机、用户视觉确认与 FINAL FREEZE 分开记录。
