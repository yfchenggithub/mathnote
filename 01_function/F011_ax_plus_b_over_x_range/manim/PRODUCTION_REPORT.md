# F011 GIF 本地生产验收

日期：2026-11-06。状态：**LOCAL PRODUCTION PASS**。

## 交付

| 文件（相对本 UID） | 内容 | 尺寸 | 时长 | 帧数 | 文件字节数 |
| --- | --- | --- | --- | --- | --- |
| `images/F011_range.gif` | 正负支最值、纵坐标投影、两段值域及一般参数结论 | 576×1024 | 19.75 秒 | 237 | 2,023,638 |
| `images/F011_branch_distance.gif` | 两点独立移动、平行支撑线、公垂线与取等位置 | 576×1024 | 19.50 秒 | 234 | 2,111,992 |

两图均约 12 FPS、无限循环；每帧 80–90 ms。完整底部文案在开场、运动、停顿、转场与结尾保留：

> 查结论 · 看图解 · 学证明｜知树 App  
> 公众号 ok-shuxue｜获取入口

## 数学与教学审计

- 全部六段 TeX 与 meta.json 已阅读，作为事实源；本轮没有修改它们。
- 值域动画使用 A=B=1，画面明确标出示例条件；取等点 (1,2)、(−1,−2) 与真实曲线一致，结尾给出 A,B>0 的一般结论。负半轴最大值的语境始终明确。
- 换支时淡出后重置；运动路径不经过 x=0。未暗示函数在断点处连续。
- 距离动画使用 k=1，P=(a,1/a)、Q=(−b,−1/b)，先展示非对称点对的独立运动；未预设 Q=−P。
- 两条支撑线 x+y=±2、公垂线、直角标记、最近点 (±1,±1) 与最短距离 2√2 相符；最后给出 k>0 时的 2√(2k)。
- 实时数值取四舍五入，用约等号；最值公式和点坐标使用精确表达。
- 动画的额外教学价值是让学生观察最值前后的变化、实时距离与支撑线下界的关系。完整推导仍由 PDF 承担。

## 已执行的验证

| Gate | 状态 | 实际证据 |
| --- | --- | --- |
| M 数学自动测试 | PASS | `test_model.py` 的 5 项测试通过；含 960 个正负分支轨迹采样、360 个几何轨迹采样、一般参数与独立点对不等式、精确取等和非法条件。 |
| M 数学关键状态 | PASS | 实际 Scene 记录正支最小、负支最大、非对称点对与 a=b=1 状态，参数与显示值由 UID 模型驱动。 |
| G 全帧技术 | PASS | 冻结 `verify_gif.py` 完整解码共 471 帧；183 / 176 个不同画面；零黑帧，无零时长帧，无限循环。额外检查无空白帧。 |
| V 真实关键帧 | PASS | 从最终 GIF 提取开场、最值、支撑线、一般结论与首尾帧；修正负支坐标标签压线、开场 P/Q 标签未初始化等问题后重渲染检查。 |
| V 布局与品牌 | PASS | Scene 更新时执行 299 / 265 次文本安全区检查，零越界；真实全帧底部区域检查通过。MP4 压缩会产生轻微像素变化，固定区域最大通道平均差为 1.605 / 1.563（0–255），低于 2.5 容差；不是逐像素恒等声明。 |
| T 教学表达 | PASS | 动点在极值停顿、由例子回扣一般式；几何点先独立移动，再引入能取到的下界。 |
| 既有资产保护 | PASS | 本轮开始记录的 F011 根目录文件及 3 张 PNG，完成后 SHA-256 全部一致。共享工具未修改。 |
| images 写入 | PASS | 用户明确要求放入 images；使用冻结导出器 `-Publish` 创建新名称，无 `-Overwrite`；正式 GIF 与已审阅暂存 GIF 的 SHA-256 相同。 |
| USER VISUAL PASS | PENDING | 等待用户查看实际 GIF。 |
| ANDROID DEVICE PASS | PENDING | 用户尚未确认 Android 真机效果。 |
| FINAL FREEZE | PENDING | 未宣布最终冻结。 |
| Publisher / Content Package / Sync / APK | PENDING | 本轮未执行，不属于本次 images 写入。 |

本地视觉评分参考：89/100（图形焦点 22/25，信息层级 18/20，字体公式 17/20，配色克制 14/15，运动与停顿 9/10，品牌整体 9/10）。主要余量在一般参数公式的手机端实际阅读；此评分不代表用户或 Android 验收。

## 证据与复现

构建、日志、关键帧和全帧检查 JSON 在 `build/manim/F011-production/`。其下 `F011/range/`、`F011/branch_distance/` 分别保留 MP4、GIF、`scene_audit.json`、`frame_review.json` 和真实关键帧。

```powershell
.venv-manim/Scripts/python.exe -B -m unittest discover -s 01_function/F011_ax_plus_b_over_x_range/manim -p test_model.py -v
.\scripts\manim\render.ps1 -Uid F011 -Scene F011Range -SceneFile scene.py -Name range -BuildRoot build/manim/F011-production
.\scripts\manim\export_gif.ps1 -Uid F011 -Scene F011Range -SceneFile scene.py -Name range -AssetName F011_range.gif -BuildRoot build/manim/F011-production
.\scripts\manim\render.ps1 -Uid F011 -Scene F011BranchDistance -SceneFile scene.py -Name branch_distance -BuildRoot build/manim/F011-production
.\scripts\manim\export_gif.ps1 -Uid F011 -Scene F011BranchDistance -SceneFile scene.py -Name branch_distance -AssetName F011_branch_distance.gif -BuildRoot build/manim/F011-production
.venv-manim/Scripts/python.exe -B 01_function/F011_ax_plus_b_over_x_range/manim/check_frames.py
```

正式文件 SHA-256：

```text
F011_range.gif
1733981E87621E80B489E637D355E0A5BB118B5E4881CC0B39AE71532EB6872B
F011_branch_distance.gif
4F8ADA288AA819A361DA264DF0EE3E054706F83160C0D86DE73DC4814108D596
```
