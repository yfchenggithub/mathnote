# C012 椭圆切线原心距

只读本 UID 六段 TeX 与 meta.json。数学审计：P=(a cos t,b sin t)，
切线 A x+B y=1，其中 A=x0/a²、B=y0/b²；垂足 H=(A,B)/(A²+B²)，
d=1/√(A²+B²)。两焦点为 (±√(a²−b²),0)，焦半径以欧氏长度独立计算。
由 r1 r2=a²−e²x0² 得 d√(r1 r2)=ab，且 b≤d≤a。
轴顶点均有效；长轴端点最大、短轴端点最小，均 H=P。

分镜：a=3,b=2。先用 OP 虚线与真实垂足区分距离，再以
45°→15°→75°→45° 展示反向补偿；两条关键等式解释定值；
依次停留 (3,0)、(0,2) 检验最值，最后返回起始状态。
OP 仅开头与结尾出现；H 接近 P 时隐去 H 标签，避免端点重叠。
同一坐标系统一缩放；焦半径蓝/紫、切线橙、垂距绿。
未演示焦点垂距乘积、反射证明或圆的极限，以保持单一教学重点。

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C012_Ellipse_Tangent_Origin_Distance/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C012 -Name origin_distance -Rebuild
.\scripts\manim\export_gif.ps1 -Uid C012 -Name origin_distance -Publish -AssetName ellipse_tangent_origin_distance.gif
```

第三条仅在本地数学及图像检查通过后执行，不使用 Overwrite。
Android 真机效果需用户确认，不能由本地验收代替。
