# C093 动态 GIF 本地验收

日期：2026-11-01。状态：**LOCAL PRODUCTION PASS**。

## 产物

- GIF：`build/manim/C093/focal_distances/focal_distances.gif`
- 配套渲染 MP4：同目录 `focal_distances.mp4`，仅为本地构建中间产物。
- 规格：576×1024，21.58 秒，259 帧，194 个不同帧，无限循环。
- 体积：3,710,812 字节，约 3.54 MiB；帧延时 80–90 ms。
- GIF SHA-256：`bef2d3cb1662923900ae99c6297c94216a8f729b00fba556e19f2940526f5586`。

## 数学与教学审计

固定椭圆 a=4、c=2、b²=12，动态双曲线 A∈[0.6,1.5]，B²=4-A²。
同一公共点严格取 P=(s·aA/c,bB/c)，s 为支别符号。
焦半径与长度条均由真实距离计算；公式独立通过 a±A 核验。

| 状态 | PF1 | PF2 | 对应关系 |
|---|---:|---:|---|
| 右支，A=0.6 | 4.60 | 3.40 | a+A，a-A |
| 右支，A=1.5 | 5.50 | 2.50 | a+A，a-A |
| 右支，A=1 | 5.00 | 3.00 | a+A，a-A |
| 左支，A=1 | 3.00 | 5.00 | a-A，a+A |

改变 A 时，点始终属于椭圆与当前双曲线，焦半径和恒为 8，
差的绝对值恒为 2A。左右支通过淡出后重新选择另一个公共点切换，
未绘制穿过非交点位置的虚假轨迹。所有画面使用 a,b,A,B 记号体系。

5 项独立数学测试通过：正式例题；1001 组动画参数下的四个公共点与
距离关系；301 组参数下的双曲线采样点与视口；接近边界的参数；非法条件。

## Gate 记录

| Gate | 状态 | 实际证据 |
|---|---|---|
| M 数学自动测试与关键状态 | PASS | 5 项 unittest；双曲线、椭圆残差及距离恒等式检验 |
| G 全帧技术检查 | PASS | 冻结 verify_gif.py 完整解码 259 帧；0 黑帧；无限循环 |
| 真实关键帧 | PASS | 从最终 GIF 按时间提取 9 帧；逐一核对曲线、点、读数和支别 |
| T 教学表达 | PASS | 参数变化展示定和与定差；再选择左支解释焦点对应交换 |
| V 本地视觉质量 | PASS | 最终原尺寸关键帧检查；标签避开曲线，读数等号留间距，关键公式放大 |
| 底部与画布边缘 | PASS | 全 259 帧核对两行字形结构；最小左/上/右/下边距 42/53/29/31 px |
| USER VISUAL PASS | PENDING | 等待用户实际观看确认 |
| D ANDROID DEVICE PASS | PENDING | 等待用户在 Android 真机确认 |
| FINAL FREEZE | PENDING | 用户视觉与真机验收尚未完成 |
| PUBLISHED / SYNCED | PENDING | 本任务仅生成隔离本地预览，未发布或同步 |

MP4 压缩及 GIF 调色板会使固定底部的抗锯齿像素略有变化，因此底部核验
采用双向字形结构检查，容许 1 px 抗锯齿边缘变化；逐帧无缺失字形。
底部相对首帧 RGB 平均绝对差最大 0.779/255，首尾整帧差 0.307/255。
这些数值只证明技术稳定性，不能替代真机阅读验收。

## 范围与复现

全部新增源码和记录在本 UID 的 `manim/`。12 个既有正式 TeX、meta、PDF
及图像文件的前后 SHA-256 一致。未修改共享工具、其他 UID 或正式资源。

```powershell
.venv-manim/Scripts/python.exe -B -m unittest discover -s 03_conic/C093_confocal_ellipse_hyperbola_intersection_focal_distances/manim -p 'test_*.py' -v
./scripts/manim/render.ps1 -Uid C093 -Scene C093FocalDistances -SceneFile scene.py -Name focal_distances
./scripts/manim/export_gif.ps1 -Uid C093 -Scene C093FocalDistances -SceneFile scene.py -Name focal_distances
.venv-manim/Scripts/python.exe -B scripts/manim/verify_gif.py build/manim/C093/focal_distances/focal_distances.gif --width 576 --height 1024
.venv-manim/Scripts/python.exe -B 03_conic/C093_confocal_ellipse_hyperbola_intersection_focal_distances/manim/audit_preview.py build/manim/C093/focal_distances/focal_distances.gif --output build/manim/C093/focal_distances
```

真实帧证据位于产物目录 `keyframes/`；全帧检查记录为 `frame_audit.json`，
共享技术检查记录为 `technical_verification.json`，正式源保护基线为
`protected_before.json`。未执行 Publisher、Content Package、Sync 或 APK 构建。
