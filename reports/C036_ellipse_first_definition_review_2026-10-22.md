# C036 椭圆的第一定义验收（2026-10-22）

已完成六段正文、source.tex、meta.json 的同步完善。main.tex 原有正确 C036 前缀，保留。

- 数学：区分定义与方程等价性；新增优先的距离平方差法，保留直接平方法，补齐反向取正根证明；短轴端点直角三角形解释参数。修正把所有焦点三角形当作非退化三角形的措辞，补齐闭线段、空集、焦点重合边界。
- 例题：三题均独立回验；例 3 的绘图坐标、60 度夹角、两焦半径和及面积一致。

| 教学图（assets/tikz/） | 学生问题 / 替代文字 |
|---|---|
| C036_constant_sum.tex | 两条距离如何互补？替代抽象距离和的重复说明 |
| C036_axes_triangle.tex | a,b,c 是什么长度？替代参数关系的记忆性解释 |
| C036_sum_boundary.tex | 为什么需要严格大于焦距？替代三类轨迹的纯文字描述 |
| C036_focus_orientation.tex | 焦点为何随长轴方向变化？替代横纵方程死记 |
| C036_example_triangle.tex | 例 3 怎样列式？替代焦点三角形的脑补 |

验证：`python -B 03_conic/C036_ellipse_first_definition/checks/verify_c036.py` PASS。2884 个采样椭圆状态（含坐标轴、近退化参数），检查实际 TikZ 坐标、角度、面积、例题存在性、边界、元数据与关联 ID。

构建：单 UID 官方构建脚本成功，独立预览映射。PDF 8 页，A4；200 DPI 完整逐页检查，五幅图均以 275 DPI 全外框裁切逐图检查。修复例 3 后易错提醒孤行以及横纵对照图公式与页内说明间距；最终前四页与首次已审页面像素一致，后四页重审。两遍 XeLaTeX 诊断无 Overfull、Underfull、Warning 或 Missing character。图形比例、焦点、曲线、文字、外框无重叠或裁切。

数学 PASS；编译 PASS；逐页视觉 PASS；逐图视觉 PASS。无已知未解决问题。未执行打包、发布或同步。

PDF SHA256: f06c93e91a3021f23e0f669f322942739c72d7f219be52e90b51f9f633b8b6a0
