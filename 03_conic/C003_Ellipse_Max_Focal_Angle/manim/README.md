# C003 椭圆焦角最大值动画

## 数学审计与分镜

事实源：本 UID 的正式六段 TeX；已逐段读取，保持原文件不变。
`meta.json` 的旧公式 `tan(theta/2)=c/y_P` 与正式 TeX 冲突，
不作为动画公式使用；本任务不修改元数据。

正确通式为 `tan(theta/2)=c|y|/b²`。
由 `|y|≤b` 及半角正切的严格单调性，最大值恰在 `(0,±b)` 取得，
`theta_max=2 arctan(c/b)=2 arcsin(e)`。长轴端点的两条焦点射线同向，焦角为零。

动画采用独立示例 `a=3, b=2, c=√5`，保持横纵坐标等比例。
P=(3 cos t, 2 sin t)，焦点为 `(±√5,0)`。
实时角度由两条实际焦点向量的叉积、点积通过 atan2 求得；
半角公式独立计算并在测试中与几何角交叉核对。

分镜：

1. 从右长轴端点出发，焦角为零。
2. 沿上半椭圆靠近上短轴端点，虚线高度与焦角一起增大。
3. 在上短轴端点停顿，展示 `|y|=b` 与 `tan(theta_max/2)=c/b`。
4. 到达左长轴端点，焦角回到零。
5. 沿下半椭圆运动，在下短轴端点停顿，展示相同最大值与最终公式。
6. 返回起点，恢复初始文字，连续循环。

角弧使用实际两条焦点射线之间的有向短弧；零度时不绘制虚假角弧。
绿色虚线是 P 到 x 轴的垂线，不把一般点的垂线误作角平分线。

## 重建命令

在仓库根目录执行：

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C003_Ellipse_Max_Focal_Angle/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C003 -Name max_focal_angle -Rebuild
```

预览在 `build/manim/C003/max_focal_angle/`。
首次写入 `images/`（经本地验证后，用户已授权）：

```powershell
.\scripts\manim\export_gif.ps1 -Uid C003 -Name max_focal_angle -Publish -AssetName ellipse_max_focal_angle.gif
```

已有正式 GIF 时该命令会拒绝覆盖。不要自动添加 `-Overwrite`。
本任务不执行 Publisher 内容包、Sync 或 APK 构建。

## 验收记录（2026-10-19）

- 数学自动测试：PASS。5 项测试，包含四种椭圆各 721 个采样点、
  椭圆方程、焦半径和、半角通式、余弦式、最大值界、对称性、单调性、
  两个最大值端点、零度端点、正式例题和旧错误公式的反例。
- 数学关键状态：PASS。示例最大值约 96.3794°，画面显示 96.4°；
  两个短轴端点角度相同，两个长轴端点均显示 0.0°。
- 教学表达：PASS（本地审查）。展示高度、焦角与最大值的对应，使用 |y| 覆盖上下半椭圆。
- 用户视觉验收：PENDING。
- Android 真机验收：PENDING，须由用户确认。
- FINAL FREEZE：PENDING。

最终全帧技术检查、真实关键帧与本地视觉审查记录见 `VALIDATION.md`。
Publisher 代码审计：`publish.py` 调用 `asset_preparation.py`，
实际 worker `prepare_knowledge_images.mjs` 接受 images/ 下直接 PNG/GIF，
GIF 验证后按原始文件名逐字节保留；本文件名满足现行消费契约。
