# F008 动画分镜与数学审计

事实源：本 UID 正式六段 TeX 与 meta.json（2026-11-19 读取）；这些文件不修改。

目标：判别式候选与降次边界。

运动与关键状态：水平线从 3.4 降到 3 相切、2.5 和 2.1 相交；在 2 停顿展示 1=0；返回。

条件与边界：示例范围 (2,3]；y=2 虽使判别式为零，却因二次项消失而不可取。

每个运动点均由本目录 model.py 计算；scene.py 独立解释本 UID，不导入其他 UID。统一字体、色板、页脚只是工程约定。

固定两行底部文案全程存在，标题、数学条件、坐标与结论避让页脚。

验证：test_model.py 的代数/参数与临界状态检查；渲染后检查真实关键帧、全帧解码、无限循环、非空帧和页脚稳定性。

LOCAL PRODUCTION PENDING；USER VISUAL PENDING；ANDROID DEVICE PENDING；FINAL FREEZE PENDING。
