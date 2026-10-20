# C013 端点切线截高积与梯形面积

事实源：本 UID 正式六段 TeX 与 meta.json（只读）。本地独立数学模型取
d1=b exp(u)、d2=b exp(−u)，有符号截高同为正或同为负。
由交点得到 k=(yR−yL)/(2a)、m=(yL+yR)/2，再独立计算
切点 P=(−a²k/m,b²/m)。验证 m²−a²k²=b²、P 在椭圆上且在两交点连线上。
两截高同侧，所以长度积 b²；多边形鞋带面积与 a(d1+d2) 一致。
u=0 时 d1=d2=b，切点为短轴端点，Smin=2ab。
有限 u 始终排除长轴端点；|u|→∞ 时面积无界，不声称动画扫描了无限范围。

独立分镜：a=2,b=1，上半椭圆，u 在 [−0.8,0.8] 内改变。
两根彩色竖段一长一短，淡绿梯形面积同步更新；平方差解释定值；
再停留水平切线，梯形变矩形，强调等长时面积最小。
下半椭圆不在画面中扫过，但模型测试验证其有符号高度为负、长度仍为正。
固定线严格为 x=±a，不画准线；所有坐标统一缩放。
蓝=d1，紫=d2，橙=动切线，绿=乘积与面积界。

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C013_Ellipse_Endpoint_Tangent_Intersection/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C013 -Name endpoint_intersection -Rebuild
.\scripts\manim\export_gif.ps1 -Uid C013 -Name endpoint_intersection -Publish -AssetName ellipse_endpoint_tangent_intersection.gif
```

本地数学、真实关键帧及全帧技术检查通过后才执行第三条，不使用 Overwrite。
用户视觉与 Android 真机验收独立记录，未经确认不作最终冻结。
