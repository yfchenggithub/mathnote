# C011 切线与中心连线的斜率积

数学事实源：本 UID 六段 TeX 与 meta.json（只读）。模型取
P=(a cos t,b sin t)，一般式切线 x0 x/a²+y0 y/b²=1。
当 x0 y0≠0，kOP=y0/x0，kℓ=−b²x0/(a²y0)，乘积为−b²/a²=e²−1。
轴顶点处有一条直线竖直，乘积无定义，不写 0×∞。
本动画不将 OP 当法线，不宣称非轴切点处垂直，不演示中点弦推广。

分镜独立围绕两个有限斜率的反向变化：a=2,b=1，第一象限
45°→20°→70°→45°；同屏实测斜率与定值−1/4。
再以一般式给出坐标消去，最后分别停留在 (2,0)、(0,1) 显示定义域例外。
前往顶点的过渡不显示斜率数值；直线始终用一般式裁切，不除以零。
图形统一等比例缩放，颜色蓝=OP、橙=切线、绿=结论。

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C011_Ellipse_Tangent_Slope_Product/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C011 -Name slope_product -Rebuild
.\scripts\manim\export_gif.ps1 -Uid C011 -Name slope_product -Publish -AssetName ellipse_tangent_slope_product.gif
```

只在本地数学、关键帧和全帧检查通过后执行最后一条。用户视觉、Android 真机与最终冻结另行确认。
