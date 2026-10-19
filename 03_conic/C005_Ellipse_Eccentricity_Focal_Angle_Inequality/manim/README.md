# C005 离心率与焦角不等式动画

## 数学审计与模型

已读取本 UID 当前正式六段 TeX 与 meta.json，核心关系一致：
`sin(theta/2) ≤ e`，等号恰在短轴两端点取得。
本任务开始时六段 TeX 与 PDF 已有用户改动，全部保留。
动画与模型独立建立在本 UID 下，不读取其他 UID 的私有实现或既有图像。

椭圆族采用 a=5，0<e<1，c=ae，b=a√(1-e²)。
P=(a cos t,b sin t)，焦点为 (±c,0)。
所有几何使用同一个横纵等比例显示缩放 0.65。
角度由两条实际焦点射线的叉积与点积经 atan2 求得。
比较条带分别表示 sin(theta/2) 和 e，共用固定 [0,1] 刻度，
没有随参数独立缩放。

已交叉核对正式证明中的恒等式：

```
sin²(theta/2) = 1 - b²/(r1*r2)
e² - sin²(theta/2) = (r1-r2)²/(4a²) * cos²(theta/2) ≥ 0
```

长轴端点角度为零，可以纳入定义域；与 C004 的顶角模型不同。
最大值为 2 arcsin(e)。固定 a 增大 e，b 减小而 c 增大，
动画比较的是最大焦角，未宣称不同椭圆上任意点的角度都按 e 排序。

## 分镜

1. 正式例 3：a=5、b=4、c=3、e=0.6，P=(3,16/5)。
   sin(theta/2)=3/√34≈0.514，与 e=0.600 比较，显示严格不等。
2. 移至上短轴端点，两焦半径相等，半角正弦达到 e；
   同时标记下短轴端点，说明两个取等位置。
3. 保持 P 为上短轴端点，固定 a 改变 e，图形、焦点、角度、比较条同步更新。
4. 在 e=√2/2 停顿，最大焦角恰为 90°。
5. 在 e=√3/2 停顿，最大焦角恰为 120°。
6. 增大至 e=0.9，先展示最大焦角超过 120°，再把 P 移至由模型求解的
   非短轴点，使实际焦角恰为 120°；此时比较条严格不等。
7. 返回 e=0.6，说明其所有焦角都小于 120°，恢复初始状态循环。

边界说明：存在 90° 焦角要求 e≥√2/2，存在钝角则须严格大于此界。
存在 120° 焦角等价于 e≥√3/2，且始终 e<1。
动画没有把 e=1 的退化曲线当成椭圆。

## 重建与交付

在仓库根目录执行：

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C005_Ellipse_Eccentricity_Focal_Angle_Inequality/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C005 -Name focal_angle_bound -Rebuild
```

隔离预览在 `build/manim/C005/focal_angle_bound/`。
本地检查通过后，按用户明确要求首次写入 images/：

```powershell
.\scripts\manim\export_gif.ps1 -Uid C005 -Name focal_angle_bound -Publish -AssetName ellipse_eccentricity_focal_angle_inequality.gif
```

已存在时工具会拒绝覆盖，不得自动添加 `-Overwrite`。
本任务不执行 Publisher 内容包、Sync、Git 提交或 APK 构建。
用户视觉与 Android 真机验收独立记录，不把本地通过当成 FINAL FREEZE。
最终验收见 `VALIDATION.md`。
