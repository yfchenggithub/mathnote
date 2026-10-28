# C087 GIF 本地验收

日期：2026-10-28。正式文件：`../images/C087_focal_chord_length_range.gif`。

## 数学与教学设计

依据本 UID 的六段 TeX 和 meta.json 独立建立 `model.py`。示例取 a=3,b=4,c=5，几何坐标采用相同横纵尺度。先看普通线段，再引入双曲线、焦点和弦长变化；水平异支弦取最小值 6，竖直同支弦取最小值 32/3。实时数值保留两位小数，用近似号显示。

接近渐近线方向时明确提示视图等比缩小；临界角用淡出切换，避免暗示交点沿有限路径穿过无穷远。临界状态仅画一个有限交点 P=(17/5,-32/15)，不画有限焦点弦。负斜率由关于 x 轴的对称说明覆盖。

按用户本次更新要求，最下方全程显示两行，包括过渡和结尾：

```text
查结论 · 看图解 · 学证明｜知树 App
公众号 ok-shuxue｜获取入口
```

第一行字号略大；结尾对称说明上移，给两行文案与底边保留间距。旧 GIF 备份位于 `build/manim/C087/footer_update_20261028/before.gif`。

## 验收记录

| 项目 | 状态 | 证据与实际检查 |
| --- | --- | --- |
| Mathematics | PASS | `test_model.py` 五项测试通过；核对 1806 个运动采样、60 个一般参数与反射情形、两个最小值、两个临界方向及双侧无界增长；逐一复核渲染产生的 audit.json 状态与图形边界。 |
| Teaching | PASS（本地） | 普通线段→异支旋转→同支旋转→临界区别→两个取值范围；关键取等处停留，公式与点位同步。 |
| Visual | PASS（本地） | 查看实际 GIF 的 11 个阶段关键帧及联系表；修正数值初始位置、端点标签和临界图焦点标签。缩小视图时 B 用引导线标注，避免挤到另一支曲线。 |
| GIF Technology | PASS | 576×1024；308 帧，218 个不同画面；约 25.66 秒、12 FPS、无限循环；完整解码，0 黑帧。最终文件以共享工具再次验证。 |
| Footer | PASS | `review_frames.py` 分别检查实际 GIF 所有 308 帧的两行文字区域，每行均存在；人工查看开场、运动和结尾实际关键帧，两行完整可读、无裁切。 |
| Architecture / source integrity | PASS | 模型、Scene、测试和分镜均在本 UID 的 manim/；复用冻结生产工具；9 个正式根文件与任务前哈希一致。未修改共享生产工具；本次按用户明确要求替换 C087 原 GIF。 |
| USER VISUAL PASS | PENDING | 尚未收到用户对该 GIF 的视觉确认。 |
| ANDROID DEVICE PASS | PENDING | 尚未收到 Android 真机播放、字形、裁切和循环效果确认。 |
| FINAL FREEZE | PENDING | 保持与真机、用户验收分离。 |
| 文件放入 images | PASS | 用户明确要求修改 C087 底部文案；预览验收后，通过 export_gif.ps1 的 Publish、Overwrite 开关替换原路径，正式文件与已审阅预览哈希一致。 |
| Content Package / Sync | 未执行 | 本任务仅生成并放置单 UID GIF。 |

状态：**LOCAL PRODUCTION PASS**；不声明用户视觉或 Android 真机通过。

## 复现与证据

```powershell
.\.venv-manim\Scripts\python.exe -B 03_conic/C087_hyperbola_focal_chord_length_range/manim/test_model.py
.\scripts\manim\render.ps1 -Uid C087 -Scene C087FocalChordRange -SceneFile scene.py -Name focal_chord_range
.\scripts\manim\export_gif.ps1 -Uid C087 -Scene C087FocalChordRange -SceneFile scene.py -Name focal_chord_range
.\.venv-manim\Scripts\python.exe -B 03_conic/C087_hyperbola_focal_chord_length_range/manim/review_frames.py
```

隔离证据目录 `build/manim/C087/focal_chord_range/`：MP4、预览 GIF、audit.json、frame_review.json、gif_validation.json、delivery.json、实际关键帧、contact.png、正式知识源基线及构建日志。更新后正式文件为 3,067,984 字节，与已审阅预览的 SHA-256 完全相同：`88ba9ee8df1debba4d78f68d2c9392bc8a678c17abb2bdea958531a9e4accf67`。Publisher 现行代码从 images 的直接 PNG/GIF 文件发现资产，GIF 保留原格式与字节；本资产名满足生产工具的 ASCII 文件名规则。
