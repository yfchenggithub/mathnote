# C018 · 椭圆上一点的切线方程

事实源为本 UID 的六段 TeX 与 `meta.json`，仅作读取。数学模型、测试和分镜独立建立，不依赖其他 UID 的私有实现。

## 数学审计与教学分镜

设 a>b>0，P=(a cos t,b sin t) 在椭圆上。P 处切线系数为 (A,B,C)=(cos t/a,sin t/b,1)，即 x₀x/a²+y₀y/b²=1。椭圆上另一点 Q=(a cos s,b sin s) 的线性式取值为 cos(t−s)≤1，等号仅在 Q=P 时成立，故候选直线是支撑切线。四个轴端点直接给出 x=±a、y=±b，无需除以 y₀。

为展示割线趋向切线，使用真实弦方程：

`cos((t+s)/2) x/a + sin((t+s)/2) y/b = cos((s−t)/2)`。

本分镜 a=3、b=2、t=π/3，P=(1.5,√3)，与正式 meta 演示点一致。Q 从 (3,0) 沿椭圆靠近 P；当 s=t 时该弦方程连续变为切线方程。切线随后随 P 沿椭圆转动，依次停在上、左、下、右顶点，分别展示 y=2、x=−3、y=−2、x=3。返回初始切点后，将 Q 连续移开，恢复开场，构成无限循环。

所有坐标统一等比例映射。线段使用一般式 Ax+By=C 在视窗裁切；近竖直处不使用斜率，也不显示无穷大的数字。没有把 OP 画成椭圆的一般法线。本 GIF 聚焦已知切点的统一方程，不重复展开已知斜率或外点切线问题。

## 命令

在仓库根目录执行：

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C018_ellipse_tangent_equation/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C018 -Name tangent_equation -Rebuild
```

构建输出位于 `build/manim/C018/tangent_equation/`。审核后按用户授权新增正式资源：

```powershell
.\scripts\manim\export_gif.ps1 -Uid C018 -Name tangent_equation -Publish -AssetName ellipse_tangent_equation.gif
```

不使用 `-Overwrite`。正式资源在 `../images/ellipse_tangent_equation.gif`；验收记录见 `VALIDATION.md`。不执行 Publisher 内容包、Sync、APK 构建或发布。
