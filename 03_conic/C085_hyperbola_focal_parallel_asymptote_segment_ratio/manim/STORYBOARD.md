# C085 · 两段之比，为什么这样整齐？

事实源：本 UID 正式六段 TeX 和 meta.json。独立模型 model.py；不借用其他 UID 的模型、Scene、静态卡片或已生成图片。

## 教学目标与分镜

1. 先认普通共线分段 F—M—N，蓝 FM、橙 MN，取 a=3、b=4 的精确长度 8/3 与 3/2。
2. 把分段对应到右支双曲线；显示焦点 F、一对渐近线、交点 M 与 N，强调“过焦点、平行一条、交另一条”。只显示右焦点构型，左右及上下反射推广留在 PDF。
3. 固定 a=3，b 连续取 4→2.25→3→4。曲线、焦点、渐近线、两交点和数值由同一个独立数学模型驱动；坐标比例始终一致。橙段 MN 长 1.5，但位置方向改变；比值随 b²/a² 改变，不把跨不同双曲线的比值误称为同一定值。
4. 固定回 a=3、b=4，将两段投影到水平线。展示横向差 t、c/2−t，再给 t=b²/(2c)、c/2−t=a²/(2c)，共同距离系数约掉。
5. 收束为 FM/MN=b²/a²=e²−1 与 e=√(1+FM/MN)，再回普通分段进入循环。

## 画面与数值约定

576×1024，浅色背景，Microsoft YaHei + MathTex。蓝色 FM、橙色 MN、绿色曲线、紫色虚线渐近线；关键点另有字母与实线/虚线辅助辨认。坐标显示使用 screen(P)=(-3,1.7)+1.05P，横纵统一缩放，不按各状态单独缩放。

动态数值为两位小数近似；符号公式为精确关系。标准几何点 F=(5,0)、M=(17/5,−32/15)、N=(5/2,−10/3)。动画中一条焦点平行渐近线只产生一个有限曲线交点，不画成两端点焦点弦。

## 本地核验与交付边界

使用 scripts/manim/render.ps1、export_gif.ps1 和 verify_gif.py；隔离输出 build/manim/C085-production/C085/focal_parallel_asymptote_ratio。用户已明确要求最终 GIF 放当前 UID 的 images，因此在本地数学、视觉、技术检查通过后用 exporter 的 -Publish 新建；不覆盖原 PNG，不改正式数学源，不执行 Publisher、Content Package、Sync 或 APK 构建。

USER VISUAL、ANDROID DEVICE 与 FINAL FREEZE 的状态独立于本地产出；未获用户真机确认时保持 PENDING。
