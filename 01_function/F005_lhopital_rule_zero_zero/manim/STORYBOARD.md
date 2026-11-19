# F005 动画分镜与数学审计

事实源：本 UID 正式六段 TeX 与 meta.json（2026-11-19 读取）；这些文件不修改。

目标：0/0 具体例子的可导变化率。

运动与关键状态：x²-1 与 x-1 共零点；割线跟随右侧靠近，再切换左侧靠近；实时比值为 2+h。

条件与边界：只解释满足条件的具体例子；切换左右时不采样 h=0；一般法则未冒充完整证明。

每个运动点均由本目录 model.py 计算；scene.py 独立解释本 UID，不导入其他 UID。统一字体、色板、页脚只是工程约定。

固定两行底部文案全程存在，标题、数学条件、坐标与结论避让页脚。

验证：test_model.py 的代数/参数与临界状态检查；渲染后检查真实关键帧、全帧解码、无限循环、非空帧和页脚稳定性。

LOCAL PRODUCTION PENDING；USER VISUAL PENDING；ANDROID DEVICE PENDING；FINAL FREEZE PENDING。
