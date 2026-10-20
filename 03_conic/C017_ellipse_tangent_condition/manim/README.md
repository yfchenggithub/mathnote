# C017 · 椭圆斜率式切线判定

事实源为本 UID 六段 TeX 与 `meta.json`，这些文件只读。动画数学模型独立于其他 UID，使用 Task 13F 冻结生产工具。

## 数学审计与分镜

对椭圆 x²/a²+y²/b²=1（a>b>0）和有限斜率直线 y=kx+m，令 D=a²k²+b²。代入后的二次方程判别式为 Δ=4a²b²(D−m²)，因此 m²<D、=D、>D 分别对应两个、一个、零个交点。相切时切点为 (−a²k/m,b²/m)，固定 k 有正负两条切线；竖直切线另为 x=±a。

本动画取 a=5、b=3、k=0.8，故 D=25。直线从 m=0 平移到 m=5，两交点合为 P=(−4,1.8)；继续到 m=6.3 后相离；再到 m=−5，展示第二条切线及正负截距公式；最后回到开场。所有交点由二次方程解析解驱动，统一坐标比例为每数学单位 0.6 场景单位。

只用一个 GIF 讲清核心充要条件，不同时展开焦点距离乘积或单位圆变换。正式解释文件中的个别焦点距离标号与证明的写法不一致；本动画不使用这些标号，未修改事实源。

## 复现

在仓库根目录执行：

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C017_ellipse_tangent_condition/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C017 -Name tangent_condition -Rebuild
```

隔离输出为 `build/manim/C017/tangent_condition/`。数学和实际关键帧审核通过后，本次按用户生成新 GIF 的授权执行：

```powershell
.\scripts\manim\export_gif.ps1 -Uid C017 -Name tangent_condition -Publish -AssetName ellipse_tangent_condition.gif
```

不使用 `-Overwrite`。正式 GIF 为 `../images/ellipse_tangent_condition.gif`。技术、本地视觉与 Android 用户验收状态见 `VALIDATION.md`。未运行 Publisher 包、Sync、APK 构建或发布。
