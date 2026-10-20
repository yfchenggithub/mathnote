# C015 焦点三角形四心：四个独立 GIF

事实源：本 UID 六段正式 TeX 与 meta.json，只读。原有用户改动保留。
全程要求 a>b>0 且 y0≠0；长轴端点三角形退化，四心模型拒绝此输入。

## 数学模型与独立审计

P=(a cosθ,b sinθ)，F1=(−c,0)、F2=(c,0)，c=√(a²−b²)。
重心由三个顶点坐标平均计算，独立验证三条中线的2:1分点。
内心按对边长对顶点加权计算，不强行指定公式；半径以面积除以半周长计算；
三个切点均用真实正交投影取得，核对位于边的内部、半径垂直边且三距离相等。
垂心由竖直高线与第二高线点积方程计算，测试三条高线。
外心由底边中垂线与三顶点等距条件计算，外接圆半径由欧氏距离取得。
17项测试另验证正式四心公式、重心和内心轨迹、欧拉向量关系、特殊直角、
等腰与等边区别、下半平面符号、退化极限与参数定义域。

## 分镜与文件

| Name / Scene | 独立数学分镜 | 正式 GIF |
|---|---|---|
| centroid / C015Centroid | a=5,b=4,c=3；三条中线随P移动，PG:GO=2:1；最后展示三分之一缩放的轨迹，空心标记排除的横轴端点 | 01_focus_triangle_centroid.gif |
| incentre / C015Incentre | 同一椭圆；真实内切圆与三个切点，底边切点T确定xI，S=sr确定r；保持内心与P同侧 | 02_focus_triangle_incentre.gif |
| orthocentre / C015Orthocentre | 同一椭圆；竖直高线与过F1的高线；停留P=(3,16/5)、H=F2，再到P=(4,12/5)、H=(4,−35/12)展示外部垂心 | 03_focus_triangle_orthocentre.gif |
| circumcentre / C015Circumcentre | 特意选正式例题中的a=5,b=3,c=4，使外心能跨过底边；真实外接圆三半径相等，先停O′=O的顶角直角构型，再停P=(0,3)、O′=(0,−7/6) | 04_focus_triangle_circumcentre.gif |

所有运动只在非退化范围内；只演示上半椭圆，数学测试覆盖上下半部。
坐标统一等比例缩放。不同GIF为容纳外接圆或外部垂心采用各自固定比例，
同一图内没有独立改变横纵比例，也没有对外部点做钳制或伪造裁切位置。
重心轨迹为理论参考曲线，空心端点不属于轨迹，不表示P经过退化点。
右角标记仅在真实正交处使用；外心顶角直角标记仅在O′=O的实际关键状态显示。
颜色：橙P、绿当前中心及核心结论、蓝几何构造、深色三角形、灰色椭圆参考。

## 重建

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C015_Ellipse_Focus_Triangle_Centers/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C015 -Scene C015Centroid -Name centroid -Rebuild
.\scripts\manim\export_gif.ps1 -Uid C015 -Scene C015Incentre -Name incentre -Rebuild
.\scripts\manim\export_gif.ps1 -Uid C015 -Scene C015Orthocentre -Name orthocentre -Rebuild
.\scripts\manim\export_gif.ps1 -Uid C015 -Scene C015Circumcentre -Name circumcentre -Rebuild
```

分别通过数学、真实关键帧与全帧技术检查后，使用对应Scene/Name加
`-Publish -AssetName` 与表中名称新增正式文件，不使用 Overwrite。
用户视觉与Android真机未确认时保持 PENDING，不作 FINAL FREEZE。
不运行 Publisher、Content Package、Sync 或 APK。
