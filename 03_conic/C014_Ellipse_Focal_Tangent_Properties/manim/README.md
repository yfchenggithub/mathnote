# C014 五条焦点切线性质：五个独立 GIF

事实源为本 UID 正式六段 TeX 与 meta.json，只读。数学模型、场景和测试均独立归此 UID，未导入其他 UID 实现。

## 数学审计

以外单位法向量 n=(cosφ,sinφ) 建模，支撑距离
h=√(a² nx²+b² ny²)，切点 P=(a² nx/h,b² ny/h)，切线 n·X=h。
真实垂足 Hi=Fi+(h−n·Fi)n，di=h−n·Fi>0。
距离积 di 以投影独立计算，共圆与面积不通过强行指定半径或面积实现。
反射向量用入射向量 v−2(v·n)n 独立验证；光点按实际光程匀速 F1→P→F2。
截距由切线和法线独立验证，x0=0 时 N 不存在、y0=0 时 M 不唯一。
面积通过四点鞋带公式独立计算，再核对梯形式与分类最大值。

| 名称 / Scene | 独立分镜与关键范围 | 正式文件 |
|---|---|---|
| focal_distance_product / C014DistanceProduct | a=3,b=2，两个真实垂距变化；停留右顶点检验 (a+c)(a−c)=b²；覆盖顶点的有效性 | 01_focal_tangent_distance_product.gif |
| pedal_circle / C014PedalCircle | a=3,b=2，法线方向转动一周，垂足沿半径a的主圆运动，OH1与OH2作为半径；切点仍在椭圆上 | 02_focal_pedal_circle.gif |
| optical_reflection / C014OpticalReflection | a=3,b=2，三个非退化切点、三次光传播；法线内角平分，两条相等角弧对应焦点射线 | 03_focal_optical_reflection.gif |
| intercept_product / C014InterceptProduct | a=2,b=1，法线方向角40°至70°，避开轴顶点，切线/法线与x轴截点连续移动；单独显示条件 | 04_bisector_intercept_product.gif |
| area_maximum / C014AreaMaximum | a=2，先b=√3,c=1，再b=1,c=√3；前者水平切线最大2√3，后者倾斜切线达到4且水平时较小；总结含c=b边界 | 05_focal_pedal_area_maximum.gif |

第五张的取等法线满足 ny²=a²/(2c²)，仅当 c≥b 时可行；c<b 时最大值在 ny²=1。
两个示例间淡出切换，不把中间过渡伪装成参数连续运动。
所有图形统一坐标比例，不通过独立缩放伪造正交、距离或面积。原有 TeX/meta/PDF/PNG 保留。

## 重建与交付

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C014_Ellipse_Focal_Tangent_Properties/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C014 -Scene C014DistanceProduct -Name focal_distance_product -Rebuild
.\scripts\manim\export_gif.ps1 -Uid C014 -Scene C014PedalCircle -Name pedal_circle -Rebuild
.\scripts\manim\export_gif.ps1 -Uid C014 -Scene C014OpticalReflection -Name optical_reflection -Rebuild
.\scripts\manim\export_gif.ps1 -Uid C014 -Scene C014InterceptProduct -Name intercept_product -Rebuild
.\scripts\manim\export_gif.ps1 -Uid C014 -Scene C014AreaMaximum -Name area_maximum -Rebuild
```

分别审阅后，使用相同 UID/Scene/Name 加 `-Publish -AssetName` 与上表对应文件名。
不使用 Overwrite，不运行 Content Package、Publisher、Sync 或 APK。
每张独立记录数学、视觉、教学、技术与设备 Gate；用户视觉和Android真机未经确认保持 PENDING，不作 FINAL FREEZE。
