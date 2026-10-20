# C019 · 中心连线与切线的斜率乘积

本 UID 六段 TeX 与 `meta.json` 是只读事实源。模型、测试和分镜独立建立；共享 Task 13F 工具仅用于发现、渲染、导出和验证。

## 数学审计及分镜

标准横轴椭圆 x²/a²+y²/b²=1，a>b>0。取 P=(a cos θ,b sin θ)，必须排除坐标轴点。中心连线 OP 的斜率 y₀/x₀ 与切线斜率 −b²x₀/(a²y₀) 相乘后为 −b²/a²=e²−1。这里 O 必须为椭圆中心；OP 一般不是法线；轴点处两斜率之一不存在，乘积无定义。

示例取 a=4、b=3，与正式例题及 meta 一致；开场 θ=π/3，P=(2,3√3/2)。P 在第一象限的 20°～70° 参数弧内运动，不穿越轴点。紫色 OP 与橙色切线都随 P 变化，两个实时斜率分别按真实坐标和切线一般式计算；在运动后揭示实时乘积 −0.5625，再展示一般式和坐标相消的原因。最后以乘积不等于 −1 说明 OP 与切线一般不垂直，回到初始状态循环。

画面数值使用近似号，乘积从未舍入的两个斜率相乘得到，避免将两位小数读数的舍入误差误作数学变化。图形横纵等比例映射；切线在视窗边界裁切，不改变斜率。模型独立校验所有象限，但本 GIF 仅在一个象限内连续演示，未声称走遍整条椭圆。

## 复现命令

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C019_ellipse_slope_product_constant/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C019 -Name slope_product -Rebuild
```

输出在 `build/manim/C019/slope_product/`。本地审核后，按用户授权新增正式文件：

```powershell
.\scripts\manim\export_gif.ps1 -Uid C019 -Name slope_product -Publish -AssetName ellipse_slope_product_constant.gif
```

不使用 `-Overwrite`。正式 GIF 归 `../images/`。详细验收见 `VALIDATION.md`；Android 真机与用户视觉确认独立于本地生产。未执行 Publisher 内容包、Sync、APK 或 Git 提交。
