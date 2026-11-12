# V009 内心动态图

事实源：本 UID 正式六段 TeX 与 meta.json（仅阅读）。

数学审计：非退化三角形，a=BC、b=CA、c=AB；I=(aA+bB+cC)/(a+b+c)。三条垂距均为 r，三块面积分别 ar/2、br/2、cr/2；因此面积比为 a:b:c，并得 a IA+b IB+c IC=0（各 IA 等均为向量）。

分镜：先识别三角形与内心；出现内切圆、垂足及直角标记；连接内心与顶点，呈现同高面积比；A 连续运动，内心和内切圆同步重算；收束向量等式并回到开场。运动参数 t 从 0 到 2π，固定 B、C，A=(-0.7+1.65 sin t, 3.9-0.65(1-cos t))。所有对象保持同一比例尺。

自动验证：`python -B 04_vector/V009_Incenter/manim/test_model.py`，覆盖 401 个运动状态，检查严格三角不等式、垂足位于边内、半径等距、垂直关系、面积比、内心向量恒等式及两次分点定位。测试适配当前 NumPy 的三维叉积接口。

构建：`scripts/manim/render.ps1 -Uid V009 -Scene V009Incenter -Name incenter`；导出使用冻结的 export_gif.ps1。临时资源在 build/manim/V009/incenter/。不运行 Content Package 或 Sync。
