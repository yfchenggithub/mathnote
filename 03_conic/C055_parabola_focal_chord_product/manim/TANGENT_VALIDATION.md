# C055 焦点弦两端切线动画

日期为 2026-11-19。本次按用户要求，新增一条独立 GIF 到当前 UID 的 `images/`。

## 数学源与模型

- 事实源为当前 UID 六段 TeX、`meta.json`，重点对应 `01_statement.tex` 中的切线推论和 `03_proof.tex` 中的切线推广证明。
- 图形取 `y²=4x`，即 `p=2`，焦点 `F=(1,0)`，准线 `x=-1`。
- 以 `x=my+p/2` 表示焦点弦。关于 `y` 的二次方程为 `y²-2pmy-p²=0`。按纵坐标正负分别取端点 A、B。
- 两端点切线为 `y_i*y=p*(x+x_i)`，其斜率积为 `p²/(y1*y2)=-1`。
- 两切线交点为 `T=(-p/2,pm)=(-p/2,(y1+y2)/2)`。在准线上的是切线交点 T。
- 模型独立位于 `model_tangents.py`，Scene 位于 `scene_tangents.py`。图上横纵坐标使用相同单位长度，直角方框由真实单位方向向量计算。

## 教学过程

先显示过焦点的弦，再出现两端切线、交点和准线。弦参数从 `m=3/4` 变化到 `0`，在竖直通径处停顿，再变到 `-3/4`，最后回到起始状态。

`m=3/4` 对应教材图中的 `A=(4,4)`、`B=(1/4,-1)`、`T=(-1,3/2)`。`m=0` 时两切线交于 `(-1,0)`。两个不变量分别由随动直角方框和固定准线呈现，底部公式解释其来源。

开场、运动、过渡、停顿、结尾全程显示规定的两行品牌与入口文案。首尾恢复相同的弦、标题和提示语。

## 验证结果

| Gate | 状态 | 实际证据 |
| --- | --- | --- |
| M 数学 | PASS | `test_tangents.py` 的 3 项测试覆盖 2404 组参数、1501 个实际运动状态、直角标记、参考状态及非法输入。加上原有 2 项测试，本 UID 共 5 项测试全部通过。 |
| V 本地视觉 | PASS | 检查 GIF 实际解码的 0、2、4、5.6、7.5、9.5、12、14、15.7 秒关键帧。正斜率、竖直通径、负斜率、返回状态均已检查。移开与切线相邻的原点标签，保留直角方框。 |
| T 教学表达 | PASS | 旋转焦点弦时，两端点、切线和直角方框由同一模型联动，T 沿准线上下移动。 |
| G 技术 | PASS | 576×1024，191 帧，164 个不同画面，15.91 秒，80/90 ms 帧时长，无限循环，零黑帧，2427008 字节。共享验证器完整解码通过。 |
| 全帧辅助检查 | PASS | 所有帧均保留底部文案，画布 12 px 边缘区域无显著前景。首尾全图平均像素差约 0.0041。该检查与关键帧视觉核对共同使用。 |
| USER VISUAL | PENDING | 等待用户观看 GIF 后确认。 |
| ANDROID DEVICE | PENDING | 等待用户在 Android 真机确认字体、图形、裁切与循环效果。 |
| FINAL FREEZE | PENDING | 用户视觉与真机验收尚待确认。 |

本次达到 **LOCAL PRODUCTION PASS**，并按用户明确要求新增到本地 `images/`。

## 文件与证据

- 新 GIF 为 `images/parabola_focal_chord_tangent_perpendicular.gif`。
- SHA-256 为 `a6d16c24c46b47d90982bf37be405ed1894a1fa1e96c1531681e21cc19485c75`。
- 构建、MP4、测试日志、全帧记录和真实关键帧位于 `build/manim/C055/tangent_perpendicular/`。全帧记录为其中的 `review/frame_review.json`。
- 已核对现行 Publisher 的 `publish.py` 入口及 `asset_preparation.py` 的 PNG/GIF 消费逻辑。新增文件满足 GIF 文件名约束，可由当前 `images/` 资源发现链路消费。
- 构建前记录的 14 个既有数学源、PDF 和图像文件经 SHA-256 复查，零变化。原坐标积 GIF 保留。
- 本次仅使用冻结的 UID 发现、渲染、GIF 导出与验证入口。正式 Publisher 内容包、Sync 和 APK 构建均未执行。

## 复现命令

在仓库根目录运行以下命令。重新发布同名正式 GIF 需要另外明确授权覆盖。

```powershell
./.venv-manim/Scripts/python.exe -B -m unittest discover -s 03_conic/C055_parabola_focal_chord_product/manim -p 'test*.py' -v
./scripts/manim/render.ps1 -Uid C055 -Scene C055TangentPerpendicular -SceneFile scene_tangents.py -Name tangent_perpendicular
./scripts/manim/export_gif.ps1 -Uid C055 -Scene C055TangentPerpendicular -SceneFile scene_tangents.py -Name tangent_perpendicular -AssetName parabola_focal_chord_tangent_perpendicular.gif
./.venv-manim/Scripts/python.exe -B 03_conic/C055_parabola_focal_chord_product/manim/review_tangents.py build/manim/C055/tangent_perpendicular/parabola_focal_chord_tangent_perpendicular.gif build/manim/C055/tangent_perpendicular/review
```
