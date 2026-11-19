# F001 动画分镜与数学审计

事实源：本 UID 正式六段 TeX 与 meta.json（2026-11-19 读取）；这些文件不修改。

目标：导数符号与局部运动方向。

运动与关键状态：沿三次函数从左向右移动切点，在 x=-1 与 x=1 停顿，再返回；显示实际切线与实时导数。

条件与边界：两个递增区间分别判断，不能合并；导数为零仅是候选位置。

每个运动点均由本目录 model.py 计算；scene.py 独立解释本 UID，不导入其他 UID。统一字体、色板、页脚只是工程约定。

固定两行底部文案全程存在，标题、数学条件、坐标与结论避让页脚。

验证：test_model.py 的代数/参数与临界状态检查；渲染后检查真实关键帧、全帧解码、无限循环、非空帧和页脚稳定性。

LOCAL PRODUCTION PENDING；USER VISUAL PENDING；ANDROID DEVICE PENDING；FINAL FREEZE PENDING。
