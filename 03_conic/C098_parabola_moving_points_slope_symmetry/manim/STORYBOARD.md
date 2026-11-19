# C098 动画分镜与数学审计

事实源：本 UID 正式六段 TeX 与 meta.json（2026-11-19 读取）；这些文件不修改。

目标：相反斜率约束下的动弦不变量。

运动与关键状态：p=2；u 从 0 到 1.35，再到 -0.7，最后回到 0；v=-4-u。保持真实等比例坐标，绿色 MN 始终斜率 -1。

条件与边界：M,N,A 三点互异；斜率有限；一般 p 的模型测试覆盖。

每个运动点均由本目录 model.py 计算；scene.py 独立解释本 UID，不导入其他 UID。统一字体、色板、页脚只是工程约定。

固定两行底部文案全程存在，标题、数学条件、坐标与结论避让页脚。

验证：test_model.py 的代数/参数与临界状态检查；渲染后检查真实关键帧、全帧解码、无限循环、非空帧和页脚稳定性。

LOCAL PRODUCTION PENDING；USER VISUAL PENDING；ANDROID DEVICE PENDING；FINAL FREEZE PENDING。
