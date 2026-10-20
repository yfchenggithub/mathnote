# C022 · 端点切线交点定积与梯形最小面积

事实源是本 UID 六段 TeX 与 `meta.json`，只读使用。模型、场景与测试独立建立，不依赖其他 UID 私有实现；沿用 Task 13F 冻结生产工具。

## 数学审计与独立分镜

P=(a cos t,b sin t)，要求 sin t≠0。由 P 处切线 Ax+By=1，A=x₀/a²、B=y₀/b²，分别代入 x=−a、a，直接得到交点 P₁、P₂。取 hᵢ=|Pᵢ 的纵坐标|；两交点同在横轴一侧，有 h₁h₂=b²。四边形 A₁P₁P₂A₂ 的平行底边是两条竖直线段，底间距为 2a，因此 S=a(h₁+h₂)≥2ab。等号在 P=(0,±b) 取得，此时成为矩形。

模型从切线方程求两个交点，乘积由真实长度相乘得到；面积由四个顶点的鞋带公式独立计算，另用梯形公式、截距式、切点式和半角式交叉校验。模型拒绝长轴端点，检验上下半椭圆的绝对值处理；不把动画中有限的面积变化范围当作全局最大值。

GIF 选取正式例题的 a=3、b=2。初始 P=(1.8,1.6)，对应 h₁=4、h₂=1、S=15；P 移到上顶点 (0,2)，两高度均为 2、面积降到 12；再移到对称侧 P=(−1.8,1.6)，两高度交换但乘积仍为 4、面积回到 15；返回等高位置强调最小值，最终恢复初始状态。全程切点位于上半椭圆，两交点和绘制切线均在固定视窗内。

颜色：椭圆蓝色；左竖直高度橙色、右高度紫色；切点与定值/最值绿色。淡绿色区域准确使用四个顶点，不改变高度比；维度箭头说明平行底间距 2a。数学坐标统一缩放 0.95，不独立缩放横纵方向。

本 GIF 同时解释本 UID 两条核心结论，不展开短轴端点交换坐标轴的变式。

## 复现命令

在仓库根目录执行：

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C022_ellipse_endpoint_tangent_intersection/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C022 -Name endpoint_intersection -Rebuild
```

隔离构建目录为 `build/manim/C022/endpoint_intersection/`。完成本地审核后按用户授权新增正式资源：

```powershell
.\scripts\manim\export_gif.ps1 -Uid C022 -Name endpoint_intersection -Publish -AssetName ellipse_endpoint_tangent_intersection.gif
```

不使用 `-Overwrite`。正式 GIF 在 `../images/`，验收见 `VALIDATION.md`。本地生产通过不代表 Android 或最终冻结。未运行 Publisher 内容包、Sync、APK 构建/发布或 Git 提交。
