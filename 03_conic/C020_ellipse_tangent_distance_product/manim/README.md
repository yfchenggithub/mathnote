# C020 · 焦半径几何均值与切线垂距

数学事实源为本 UID **更新后的**六段 TeX 与 `meta.json`，只读使用。动画数学模型、测试和分镜独立建立，不导入其他 UID 的私有实现。共享工具沿用 Task 13F 冻结入口。

## 数学审计与分镜

P=(a cos t,b sin t)，焦点 F₁=(−c,0)、F₂=(c,0)，c²=a²−b²。切线一般式为 Ax+By=1，A=x₀/a²、B=y₀/b²。中心到该切线的垂足为 H=(A,B)/(A²+B²)，因此 OH 垂直切线，d=|OH|。r₁、r₂ 分别直接用 P 到两焦点的欧氏距离计算。

独立参数校验：r₁r₂=b²cos²t+a²sin²t，d=ab/√(b²cos²t+a²sin²t)，因此 √(r₁r₂)d=ab。b≤d≤a、b≤√(r₁r₂)≤a；全部顶点均成立。动画的实时乘积从两点距离及正交投影独立计算，不用不变量反推某个距离。

本次重新读取用户修订的六段 LaTeX 与 meta：演示点为正确的 P=(2,3√3/2)，新版例 2 为可行的 d=2√5，新版例 3 明确原 d=2 条件无解。这些新版事实已纳入测试，未改动正式源。

分镜取 a=4、b=3，从 t=60° 的正式例点出发。先展示 r₁、r₂ 和中心垂线 OH，再让 P 移到 t=25°，随后到上顶点 t=90°（P=H），揭示实时乘积 12；接着移到 t=155°，观察焦半径几何均值减小、d 增大，给出核心及平方形式；最后回到开场状态。图形与线条等比例映射，切线准确裁切，重合状态显示 P=H，避免把切点与垂足的重合画成两个不同位置。

本 GIF 聚焦核心定值，不把焦点到切线的 h₁、h₂ 与中心垂距 d 混为一谈，也不展开新版源中所有几何推广。

## 复现

在仓库根目录执行：

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C020_ellipse_tangent_distance_product/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C020 -Name distance_product -Rebuild
```

构建产物在 `build/manim/C020/distance_product/`。通过本地数学与真实关键帧审核后，按用户授权新增正式 GIF：

```powershell
.\scripts\manim\export_gif.ps1 -Uid C020 -Name distance_product -Publish -AssetName ellipse_tangent_distance_product.gif
```

不使用 `-Overwrite`。正式 GIF 归 `../images/`。本地、用户视觉、Android 真机和最终冻结各自记录，详见 `VALIDATION.md`。未运行 Publisher 内容包、Sync、APK 或 Git 提交。
