# C091 GIF 本地验收

日期：2026-10-30。状态：LOCAL PRODUCTION PASS。

交付文件：`../images/C091_constant_area.gif`；576×1024；22.08 秒；265 帧；224 个不同帧；无限循环；约 2.42 MiB。

| Gate | 状态 | 实际证据 |
| --- | --- | --- |
| M 数学 | PASS | 4 项 unittest，含 808 组曲线上状态，覆盖左右支、顶点、不同 a/b；核对曲线、Q/R 交点、两组平行关系、向量相加、行列式面积；正式例题及退化/共轭反例通过。 |
| V 本地视觉 | PASS | 从最终 GIF 提取 11 个真实关键帧，检查上方、顶点、下方、返回、公式、首尾；等比例坐标，P 标签有底色避让横轴；文字与图形无裁切。 |
| T 教学表达 | PASS | P 沿真实双曲线运动，四边形同步变形；实时面积恒为 3，顶点菱形停顿；一般点面积公式解释 ab/2 的来源。右支为演示范围。 |
| G 全帧技术 | PASS | 冻结 verify_gif.py 完整解码 265 帧，80—90 ms/帧，无黑帧、无限循环；UID check_artifact.py 检查全帧外侧 20 px 无内容、底部两行位置和文字持续保留。 |
| D Android 真机 | PENDING | 尚无用户真机确认。 |

底部文案逐字使用规范的两行。MP4 压缩与 GIF 量化导致少量像素变化，因此全帧文案检查使用固定位置墨迹 IoU≥0.95、平均通道差<2，未声称逐像素恒定；实测最低 IoU 0.96305、最大平均差约 1.41201。关键帧人工复核可读性与完整性。

视觉评分（本地自评）：92/100。图形焦点24/25、层级19/20、可读性18/20、配色14/15、动效9/10、品牌8/10。主要限制：小屏实际可读性待 Android 真机确认，GIF 调色板有轻微抖色。

完整证据位于 `build/manim/C091-production/C091/constant_area/`：隔离 MP4/GIF、render.log、protected_sources.json、visual_technical_audit.json、keyframes.png 与 key_*.png。11 个正式知识源和既有资源哈希保持不变；共享生产工具、其他 UID、PDF/TikZ 未修改。

按用户“放在 Images 目录”的明确要求，经本地检查后由冻结 export_gif.ps1 的 `-Publish` 写入本 UID 已有 `images/`，不覆盖任何既有 GIF。Windows 下目录名大小写不区分。

USER VISUAL PASS：PENDING；ANDROID DEVICE PASS：PENDING；FINAL FREEZE：PENDING。此处仅完成本地 GIF 文件交付；正式 Publisher/Content Package/Sync/APK 均未执行，PUBLISHED / SYNCED 不作通过声明。

复现：

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C091_hyperbola_asymptote_parallelogram_area/manim -p test_model.py -v
.\scripts\manim\render.ps1 -Uid C091 -Scene C091ConstantArea -SceneFile scene.py -Name constant_area -BuildRoot build/manim/C091-production
.\scripts\manim\export_gif.ps1 -Uid C091 -Scene C091ConstantArea -SceneFile scene.py -Name constant_area -AssetName C091_constant_area.gif -BuildRoot build/manim/C091-production
```

正式路径已有 GIF 后，复现保持隔离输出，不使用覆盖参数。
