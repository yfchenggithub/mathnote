# C016 双曲线焦点三角形四心：四个独立 GIF

本 UID 六段 TeX 与 meta.json 为只读事实源；保留原有用户修改。
数学模型和分镜独立建立，不导入其他 UID 的模型或场景。

## 模型与数学审计

使用双曲线自己的参数 P=(σa cosh u,b sinh u)，σ=±1，u≠0，a,b>0。
本组示例 a=3,b=4,c=5。非顶点条件由模型拒绝 u=0 实现。
焦半径直接以欧氏距离计算，验证差为2σa、和为2e|x0|。
G由三个顶点坐标平均计算；I由三个对边长加权计算，半径由面积除以半周长计算；
H由竖直高线与点积方程计算；O′由底边中垂线和等距方程计算。
切点与高线垂足用实际正交投影，不预设在圆或边上。
19项测试覆盖两支、上下半部、四心公式、真实相切、高线正交、三顶点等距、
欧拉向量关系、例题数值、内心严格开区间及反求点验证轨迹充分性。

| Name / Scene | 独立分镜 | 正式文件 |
|---|---|---|
| centroid / C016Centroid | 两焦点坐标抵消；右支与左支分别运动，三个中线交点始终为P/3；分支切换淡出，不穿越退化顶点 | 01_hyperbola_focus_centroid.gif |
| incentre / C016Incentre | 先看右支真实内切圆与固定切点(a,0)，再移除三角形，只显示内心坐标平面；四条开线段、六个空心端点、两支与上下半部逐项展示 | 02_hyperbola_focus_incentre.gif |
| orthocentre / C016Orthocentre | 右支u=.95→ln3（H=F2）→1.22（H在底边下方）→.6（H在P上方）；补足真实边延长线，高线始终交于H | 03_hyperbola_focus_orthocentre.gif |
| circumcentre / C016Circumcentre | 右支u=.6时外心在下方；u=asinh(.8)时O′=O且顶角直角；u=1时外心移到上方；完整外接圆及三条真实半径 | 04_hyperbola_focus_circumcentre.gif |

内心轨迹阶段仅显示I，不把远处P钳制到画框里：u升至3.2，yI≈3.69<4，
选点与上端空心点保持可辨间隔。转到左支或下半部时先移除选点与读数，
更换离散分支或u符号后再显示，避免假装连续经过不允许的位置。
四条开线段的上下界与中间0均明确排除，不把顶点切线整体当作轨迹。

双曲线背景只画当前窗口内的部分，不把窗口端点当作曲线端点。
每个视图内部统一坐标比例；内心两种视图淡出切换，各有明确用途，不独立压缩横纵轴。
外部垂心与外接圆都由模型决定并完整容纳，不更改数学坐标。
颜色：橙P、绿当前中心及结论、蓝中线/半径/高线构造、深色三角形、灰色双曲线参考。

## 重建

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C016_Hyperbola_Focus_Triangle_Centers/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C016 -Scene C016Centroid -Name centroid -Rebuild
.\scripts\manim\export_gif.ps1 -Uid C016 -Scene C016Incentre -Name incentre -Rebuild
.\scripts\manim\export_gif.ps1 -Uid C016 -Scene C016Orthocentre -Name orthocentre -Rebuild
.\scripts\manim\export_gif.ps1 -Uid C016 -Scene C016Circumcentre -Name circumcentre -Rebuild
```

分别通过数学、真实关键帧与全帧技术检查后，使用相同Scene/Name加
`-Publish -AssetName` 和表中名称新增文件，不使用 Overwrite。
Android真机与用户视觉未经确认保持 PENDING，不作 FINAL FREEZE。
不执行 Publisher、Content Package、Sync 或 APK。
