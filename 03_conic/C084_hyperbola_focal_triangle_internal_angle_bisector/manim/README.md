# C084 动画生产

入口 Scene：`scene.py:C084FocalBisector`。独立数学模型与测试均在本目录。

先看普通三角形等角，随后原位引入焦点和双曲线，沿曲线移动 P 并实时追踪 M；最后解释倒角公式的内外两个根。分镜见 `STORYBOARD.md`。动画只演示主结论及选根机制，不替代六段正文的完整证明。

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C084_hyperbola_focal_triangle_internal_angle_bisector/manim -p test_model.py -v
.\scripts\manim\render.ps1 -Uid C084 -Scene C084FocalBisector -SceneFile scene.py -Name focal_bisector
.\scripts\manim\export_gif.ps1 -Uid C084 -Scene C084FocalBisector -SceneFile scene.py -Name focal_bisector
.\.venv-manim\Scripts\python.exe -B 03_conic/C084_hyperbola_focal_triangle_internal_angle_bisector/manim/review_gif.py
```

隔离预览输出：`build/manim/C084/focal_bisector/focal_bisector.gif`。
该 GIF 使用 576×1024、12 FPS、无限循环；MP4 为24 FPS。制作过程不修改正式六段、meta、TikZ、PNG或PDF，不调用静态模块或其他 UID 的动画模型，不执行 Publisher/Sync/APK。

数学审计还包括：正负分支、上下半平面、近顶点、远点、竖直焦点连线、等半角、切线方程、垂直的内外分线及精确例题数字。`audit_sources.py` 保存与核对22个正式知识源／资源哈希；记录在隔离构建目录中。

验收状态及真实关键帧、全帧技术结果见本目录 `REVIEW.md` 与隔离目录 `review/`。本地生产、用户视觉、Android真机、最终冻结及发布是独立状态；未获用户确认的项目保持PENDING。
