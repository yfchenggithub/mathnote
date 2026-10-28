# C086 GIF 本地验收 — 2026-10-27

状态：LOCAL PRODUCTION PASS。USER VISUAL PASS：PENDING；ANDROID DEVICE PASS：PENDING；FINAL FREEZE：PENDING。没有执行 Publisher、Content Package、Sync 或 APK 构建。

交付：`../images/focal_distance_ratio_range.gif`。576×1024，336帧，12 FPS，28秒，2,965,749字节，无限循环。循环采用结论回到初中线段问题的教学重启，不宣称无缝首尾运动。

已通过冻结exporter的`-Publish`写入images，正式GIF与验收候选文件SHA256一致：`7CEB38E9BD585ED53705B29537A5CD6A1B53C93C42BBFA609033B68741E828CF`。此操作仅复制新GIF到用户指定目录，不是内容包发布或同步。

## Gate M — PASS

- `test_model.py` 的5项测试通过：三种关键状态、128组一般参数存在性/曲线/距离检验、1501个动画参数状态、倒数比值镜像、非法参数与λ=1排除。
- 独立模型：r1=2aλ/|λ−1|，r2=2a/|λ−1|，x=(r1²−r2²)/(4c)，y²=r1²−(x+c)²；超过半径和时直接无解。
- 实际渲染记录227个模型状态：c∈[2,3.5]，交点数覆盖0、1、2；两焦半径、比值、焦半径差、曲线方程最大残差1.12×10⁻¹⁵以内。
- a=1、λ=2时，c=2有两点(1.5,±√15/2)，c=3外切于右顶点(1,0)，c=3.5无点。两圆是定半径焦点圆；不存在把阿波罗尼斯圆误作两个焦点圆的情况。
- 每帧采用等比例坐标，b²=c²−1随焦点运动更新。相切后不保留假交点。

## Gate V — PASS（本地视觉）

- 检查真实GIF关键帧与576×1024原尺寸画面：熟悉的普通三角形、拉直、引入双曲线、两点靠拢、外切顶点、分离、一般结论。
- 橙色长半径、紫色短半径、绿色双曲线/交点，标签与长度定义对应。
- 全336帧有效内容边界[74,44,502,992]，无超边与空白帧；首帧即有完整问题图，末帧保留一般公式。
- 视觉评分：数学图形23/25，层级19/20，文字18/20，配色14/15，动效9/10，整体9/10，共92/100。手机实机字体与播放效果尚未验收。

## Gate T — PASS

- 先用初中三角形不等式建立直觉，再引入焦点、比值与双曲线。
- 实际运动解释两个交点为何合并，以及上界等号为何能取；两个圆的交点构造解释范围内确实有点。
- 最后以两腰的和/差作比概括一般公式，保留λ>0、λ≠1与e>1。

## Gate G — PASS

- 冻结`verify_gif.py`：336帧完全解码、186个不同画面、零黑帧、帧时长80/90ms、显式无限循环。
- UID内`verify_render.py`额外核对全帧非空、内容安全边界、实际模型状态，以及10个原有正式源文件的SHA256不变。
- 所有构建与真实关键帧证据位于`build/manim/C086-production/`，不进入images。

## Gate D — PENDING

等待用户在Android详情页确认清晰度、裁切与循环播放。未标记用户视觉通过、Android通过或最终冻结。

## 复现

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s '03_conic/C086_hyperbola_focal_distance_ratio_eccentricity_range/manim' -p 'test_model.py' -v
.\scripts\manim\render.ps1 -Uid C086 -Scene C086FocalRatioRange -SceneFile scene.py -Name focal_distance_ratio_range -BuildRoot build/manim/C086-production
.\scripts\manim\export_gif.ps1 -Uid C086 -Scene C086FocalRatioRange -SceneFile scene.py -Name focal_distance_ratio_range -BuildRoot build/manim/C086-production
.\.venv-manim\Scripts\python.exe -B '03_conic/C086_hyperbola_focal_distance_ratio_eccentricity_range/manim/verify_render.py' 'build/manim/C086-production/C086/focal_distance_ratio_range' 'build/manim/C086-production/source_baseline.json'
```

复查通过后，用冻结exporter的`-Publish`将新文件写入本UID的images；不使用`-Overwrite`。正式六段TeX、meta.json、PDF及其他UID不作修改。
