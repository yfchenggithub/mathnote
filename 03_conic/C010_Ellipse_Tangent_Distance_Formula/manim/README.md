# C010 椭圆切线距离与主圆 GIF

## 数学审计与独立模型

已读取当前六段正式 TeX 与 meta.json，动画采用已核验的核心关系：
两焦点到同一切线的垂距乘积 d1*d2=b²、和为 2d0；
两焦点垂足均在半径 a 的主圆上；b≤d0≤a。
任务开始正式 TeX、元数据及 PDF 已有用户改动，本任务不写入这些文件。
数学模型与分镜独立建立，不导入其他 UID 的私有实现或使用其既有图像。

采用正式例 5 与元数据建议：a=5、b=4、c=3。
切线由外法向角 phi 驱动，n=(u,v)=(cos phi,sin phi)，
h=sqrt(a²u²+b²v²)>0，直线 ux+vy=h。

```
P=(a²u/h,b²v/h)
d1=h+cu, d2=h-cu
H1=(-c,0)+d1*n
H2=( c,0)+d2*n
Q=h*n, d0=h
```

一般式统一覆盖水平、竖直及斜切线，无除零或“无穷大斜率”。
所有几何共用等比例显示缩放 0.64 与平移，保持距离、角度、主圆和椭圆的真实比例。
显示窗口 x∈[-5.7,5.7]、y∈[-5.5,5.5] 仅裁切无限直线的可见长度。

初始法向角 atan2(5,3)，对应正式例 5 的切线 3x+5y=25。
P=(3,16/5)，H1=(0,5)，H2=(75/17,40/17)，
d1=√34、d2=16/√34。P 与两垂足确实不同。

## 教学分镜

1. 以黑色 P 标切点、橙/绿 H1/H2 标焦点垂足；绘真实垂线与直角标记，显示两垂距及乘积。
2. 转至水平切线 y=4，d1=d2=4，乘积 16。
3. 转至竖直切线 x=5，d1=8、d2=2，乘积仍为 16。
4. 显示主圆 OH1=OH2=5，再跟踪右焦点垂足一整周，展示完整轨迹 x²+y²=25。
5. 返回初始切线，加入中心垂足 Q，展示 4≤d0≤5 与 d1+d2=2d0。
6. 移去辅助圆、轨迹及中心垂线，恢复初始画面循环。

只有数值容差内真正竖直时才合并标注 P=H1=H2；
靠近竖直但仍不同的点使用错开的标签，不冒称相等。
左/右边界的合并标签均向画布内排布。
两垂距显示保留两位小数并使用近似号；乘积由未舍入的实际距离计算，
不以显示出来的四舍五入值计算乘积。

完整轨迹不仅依赖“点在圆上”的正向验证：模型测试另对主圆每个采样目标 H=(p,q)
作逆向切线 (p-c)x+qy=a²-cp，核对其相切并确认右焦点垂足确实为 H。
其一般式判定来自正式证明中的精确恒等式，采样测试是实现核验。

## 重建与交付

仓库根目录：

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C010_Ellipse_Tangent_Distance_Formula/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C010 -Name tangent_distance -Rebuild
```

隔离预览与证据在 `build/manim/C010/tangent_distance/`。
本地核验后按用户明确要求首次写入 images/：

```powershell
.\scripts\manim\export_gif.ps1 -Uid C010 -Name tangent_distance -Publish -AssetName ellipse_tangent_distance.gif
```

已有同名文件时工具拒绝覆盖，不自动添加 `-Overwrite`。
不执行 Publisher 内容包、Sync、APK 或 Git 提交。
本地、用户视觉、Android 真机和 FINAL FREEZE 分别记录，见 `VALIDATION.md`。
