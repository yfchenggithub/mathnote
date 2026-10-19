# C008 椭圆切点式与极线 GIF

## 数学审计与独立建模

已读取当前六段正式 TeX 与 meta.json。主结论：椭圆上点 P(x0,y0)
处的切线为 x0*x/a²+y0*y/b²=1；外点 M 代入同型式得到两切点的连线，
不能称为 M 处切线。

发现并保留待修的原文笔误：`04_examples.tex` 例 5 的
M2=(1/2,0)，对 x²/4+y²=1，正确极线是 x/8=1，即 x=8；
原文写成 x/4=1，即 x=4。动画不使用该错误示例，数学模型与测试按正确值处理。
本任务只制作 GIF，不写入正式 TeX、元数据或 PDF。
任务开始这些文件已有用户改动；期间 main.tex、meta.json 和 PDF 又有并发更新，
本任务保留其当前状态，并重新读取 main.tex 与元数据，确认动画所用数学关系仍一致。

动画采用 a=2、b=1，P=(2 cos t,sin t)。
切线直接以一般式 (cos t/2)*x+(sin t)*y=1 绘制，
不通过斜率来构造，因此坐标轴端点没有除零问题。
显示坐标统一等比例缩放 1.4 后平移，未改变椭圆形状、方向或几何关系。
无限直线裁切到数学窗口 x∈[-2.75,2.75]、y∈[-2.25,2.25]，
裁切仅限制可见长度。

独立自动核验包括：切点在椭圆上；切线经过切点；
一般式相切判定；参数运动方向与法向量正交；
其他椭圆点位于支撑线同一侧；四个轴端点的水平/竖直切线。
未复用其他 UID 的私有模型、场景或数学图像。

## 分镜

1. 从 P=(√2,√2/2) 出发，写出 (√2/4)x+(√2/2)y=1。
2. P 沿椭圆运动；切线按切点式同步更新。
3. 上短轴端点停顿：y=1。
4. 左长轴端点停顿：x=-2，强调斜率不存在但切线存在。
5. 下短轴端点停顿：y=-1。
6. 右长轴端点停顿：x=2。
7. 切回外点例题 M=(2,2)，S=5>1；两切点为 T1=(2,0)、T2=(-6/5,4/5)，
   两条真实切线都通过 M。
8. 用绿色切点弦及虚线极线展示 x+4y-2=0；
   它通过两切点而不通过 M；最后恢复初始状态循环。

外点的切点从单位圆的极线交点模型独立求解，再缩放回椭圆。
M 在每个切点处的切线上、两切点在极线上均独立测试。
同时测试内部点无实切线，以及原点代换成 0=1 不构成普通实直线。
片中不展示内部点错误示例，不把内部点极线称为切点弦。

## 重建与首次交付

仓库根目录：

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C008_Ellipse_Tangent_Point_Formula/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C008 -Name tangent_point_formula -Rebuild
```

隔离预览在 `build/manim/C008/tangent_point_formula/`。
经本地检查后，按用户明确要求首次写入 images/：

```powershell
.\scripts\manim\export_gif.ps1 -Uid C008 -Name tangent_point_formula -Publish -AssetName ellipse_tangent_point_formula.gif
```

已有文件时工具拒绝覆盖，不自动添加 `-Overwrite`。
本任务不执行 Publisher 内容包、Sync、APK 或 Git 提交。
本地检查、用户视觉和 Android 真机验收独立记录；本地通过不代表 FINAL FREEZE。
实际验收证据见 `VALIDATION.md`。
