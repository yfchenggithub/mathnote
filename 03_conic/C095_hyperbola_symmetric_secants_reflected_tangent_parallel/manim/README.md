# C095 对称割线与镜像点切线：动态图

正式资源：`../images/C095_parallel_chord.gif`。

## 数学模型与分镜

事实源为当前 UID 的六段 TeX 和 meta.json。动画采用正文示例
`x²/2-y²=1`、`P=(2,1)`、`Q=(2,-1)`，仅展示右支，横纵单位等长。
Q 处切线为 `x+y=1`。斜率 k 的割线第二交点为
`(2+h,1+kh)`，其中 `h=-2(1-k)/(1/2-k²)`。
两割线取 `k=m,-m`，`1.25≤m≤2.5`，排除渐近线方向和切线重合。
两个第二交点满足 `x+y=(2m²+1)/(2m²-1)`，所以弦始终与切线平行。

先引入 Q 和切线，再让两条割线关于 x=2 对称转动。
颜色分别标明割线、弦、切线；读数由同一数学模型实时计算。
学生可同时观察“交点与位置改变”和“弦的方向不变”。
参数回到 m=2，淡出动态图形后回到开场，便于循环观看。
底部全程固定两行指定品牌及入口文字。

## 复现

在仓库根目录执行：

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C095_hyperbola_symmetric_secants_reflected_tangent_parallel/manim -p test_model.py
.\scripts\manim\render.ps1 -Uid C095 -Scene C095ParallelChord -SceneFile scene_secants.py -Name parallel_chord
.\scripts\manim\export_gif.ps1 -Uid C095 -Scene C095ParallelChord -SceneFile scene_secants.py -Name parallel_chord
.\.venv-manim\Scripts\python.exe -B 03_conic/C095_hyperbola_symmetric_secants_reflected_tangent_parallel/manim/verify_gif.py build/manim/C095/parallel_chord/parallel_chord.gif
```

## 实际验收（2026-11-13）

| Gate | 状态 | 证据 |
| --- | --- | --- |
| 数学自动测试与关键状态 | PASS | 4 项测试；1001 个参数采样验证曲线、割线斜率、弦方向、合法交点和画布范围；另验 m=2 精确例与排除条件 |
| 真实关键帧 | PASS | `build/manim/C095/parallel_chord/contact_sheet_final.png`，含 0、3、9、14、20 秒与末帧 |
| 全帧技术检查 | PASS | 280 帧全部解码；576×1024；23.33 秒；无限循环；无黑帧；215 个不同帧；2,322,010 字节 |
| 教学表达 | PASS（本地） | 切线先出现，随后割线转动；图形、读数与公式使用相同模型；明确仅展示右支 |
| 视觉质量 | PASS（本地） | 实际关键帧中文正常，图形及标签完整；两行底部文案固定；首尾平均通道差 0.361/255 |
| LOCAL PRODUCTION | PASS | 上述本地检查完成 |
| USER VISUAL | PENDING | 待用户查看 |
| ANDROID DEVICE | PENDING | 需用户真机确认 |
| FINAL FREEZE | PENDING | 不把本地通过等同于最终冻结 |
| PUBLISHED / SYNCED | PENDING | 未执行内容发布或同步 |

全帧报告为 `build/manim/C095/parallel_chord/frame_audit.json`。
底部区域最大平均通道差 1.108/255（GIF 调色板量化），图形区域每帧至少 1283 个彩色像素。
GIF SHA256：`9e5d5991ba21e66685638cc50bfb65dd5a56d87e257f78513d33bdfa3bbcaee9`。
本次仅新增本 UID 动画源码、测试、验收说明与 GIF，未修改 TeX、PDF、meta 或共享生产工具。
