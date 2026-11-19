# F006 动画分镜与数学审计

事实源：本 UID 正式六段 TeX 与 meta.json（2026-11-19 读取）；这些文件不修改。

目标：复合函数定义域的逆像。

运动与关键状态：t=2x-1 上的点进出允许输入带 [1,3]；在 x=1、2 闭端点停顿；状态与内层值同步。

条件与边界：已知 D_f；没有假定 f 的表达式；对外层取值范围不作臆测。

每个运动点均由本目录 model.py 计算；scene.py 独立解释本 UID，不导入其他 UID。统一字体、色板、页脚只是工程约定。

固定两行底部文案全程存在，标题、数学条件、坐标与结论避让页脚。

验证：test_model.py 的代数/参数与临界状态检查；渲染后检查真实关键帧、全帧解码、无限循环、非空帧和页脚稳定性。

LOCAL PRODUCTION PENDING；USER VISUAL PENDING；ANDROID DEVICE PENDING；FINAL FREEZE PENDING。
