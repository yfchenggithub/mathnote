# C009 椭圆切线斜率范围 GIF

## 数学审计与独立模型

已读取本 UID 当前正式六段 TeX 与 meta.json，核心结论与边界条件一致。
任务开始时这些文件及 PDF 已有用户改动，本任务不写入正式知识源或 PDF。
本模型、测试与分镜独立建立，不导入其他 UID 私有源码，也不使用其既有图像。

本片采用椭圆 x²/4+y²=1，即 a=2、b=1。
对任意有限实斜率 k，两平行切线为 y=kx±sqrt(4k²+1)。
动画用 k 从 -1 经 0 变到 2 作代表性展示；全集为 R 的结论依据通式，
不是宣称有限次数采样能穷尽实数。

过 M=(x0,y0) 的有限斜率满足

```
(4-x0²)k² + 2x0*y0*k + 1-y0² = 0.
```

二次项系数不为零时，实根数对应有限斜率数；系数为零时按一次或常数方程处理，
同时另查竖直切线 x=±2。
“切线条数”包括竖直线，不能与“实数斜率个数”等同。

实际绘图从缩放单位圆的几何接触条件独立求出切点，再绘一般式 Ax+By=C，
并验证切点在椭圆上、切线通过 M，以及 C²=4A²+B²。
绘图过程不使用会在竖直方向发散的斜率，不用“无穷大斜率”表示竖直线。
斜率方程实根独立求解，用于交叉核验几何模型和韦达关系。

横纵坐标统一缩放 1.4 并平移；无限直线裁切到数学窗口
x∈[-2.75,2.75]、y∈[-2.25,2.25]，不改变切点或直线。

## 教学分镜

1. 任取 k=-1，两侧各有一条平行切线；旋转至 k=0，再到 k=2。
2. 切换至固定外点 M=(0,2)：4k²-3=0，两个有限斜率为 ±√3/2。
3. M 在 y=2 上横移至 (2,2)，两条真实切线连续转动。
4. 在 M=(2,2) 停顿：二次项消失，8k-3=0 只给 k=3/8；
   同时图上保留竖直切线 x=2，说明仍有两条切线。
5. 沿 x=2 下移到长轴端点 (2,0)：两切线合并为唯一竖直线；
   斜率方程成为不可能成立的 1=0，说明没有有限斜率。
6. 移到内部 M=(1,0)：S=1/4<1，没有实切线。
7. 隐去定点图形，恢复初始自由方向状态循环。

本片聚焦斜率全集、过点约束、竖直分支与内/上/外点分类，未另行演示蒙日圆。

## 重建与交付

仓库根目录：

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C009_Ellipse_Tangent_Slope_Range/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C009 -Name tangent_slope_range -Rebuild
```

预览与构建证据在 `build/manim/C009/tangent_slope_range/`。
本地检查后按用户明确要求首次写入 images/：

```powershell
.\scripts\manim\export_gif.ps1 -Uid C009 -Name tangent_slope_range -Publish -AssetName ellipse_tangent_slope_range.gif
```

已有文件时工具拒绝覆盖，不自动添加 `-Overwrite`。
本任务不执行 Publisher 内容包、Sync、APK 或 Git 提交。
本地检查、用户视觉、Android 真机与 FINAL FREEZE 分别记录，见 `VALIDATION.md`。
