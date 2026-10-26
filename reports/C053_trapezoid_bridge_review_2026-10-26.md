# C053 方法一：先看纯梯形，再放回抛物线

## 本轮范围

按用户要求先输出理解，再修改。仅处理 C053 的方法一入口与相应元数据，保留全部既有 TikZ 文件。

- 新增总入口 `assets/tikz/C053_method_one_geometry_bridge.tex`。
- 入口依次调用 `C053_trapezoid_geometry.tex`、`C053_trapezoid_parabola_mapping.tex`。
- `03_conic/C053_parabola_focal_chord_length_inclination/03_proof.tex` 在原方法一前引入入口；原来的正、反投影图及其证明保留。
- 同步同目录 `meta.json` 的图形说明。
- 原 9 份 C053 TikZ 的 SHA-256 逐一比较均一致。记录位于 `.tmp/C053_tikz_review/existing_tikz_before_geometry_bridge.json`。

## 图像与教学目的

1. 第 4 页：纯直角梯形 MABN。普通点 P 在斜腰 AB 上，过 P 作平行线 PQ 与垂线 HK；图中无抛物线、准线、焦点或坐标轴。通过矩形和平行线得到 MH=NK=PQ=h，通过两个直角三角形得到 HA=r cosθ、BK=s cosθ，再看见 AM=h+r cosθ、BN=h−s cosθ。
2. 第 5 页：完全相同的梯形、位置与尺度，加上本题抛物线。P 对应焦点 F，左侧 MN 所在直线对应准线，h 对应 p；等距定义给出 AM=AF=r、BN=BF=s，从而把前页几何关系转成方法一的两个方程。

两图替代了从抛物线术语直接跳到投影方程的认知步骤。图示选择锐角代表状态；一般方向仍按有向投影处理。原来的两张逐端投影图随后作为对照保留。

## 实际核验

- PASS：48 个普通梯形状态，独立检查平行边、线段距离、两条投影及上底相加、下底相减；不预先假设底边等于斜腰分段。
- PASS：映射图端点代回 y²=4x，核对等距定义、焦准距、AF=4、BF=4/3 和 AB=16/3；新图绘图坐标仅作整体平移，不改变比例。
- PASS：纯图源码的可见内容无抛物线、准线、焦点概念；主标签字号 small。
- PASS：原数学审计重跑，2148 状态、六道编号例题及比值变式。
- 证据：`.tmp/C053_tikz_review/trapezoid_bridge_audit.json`、`math_audit.json`。
- PASS：独立预览映射构建成功，最终 17 页 A4；完整 PDF 以 190 DPI 渲染并逐页检查。
- PASS：两幅新增图以 300 DPI 裁切并包含完整外框，逐图检查标题净距、标签、投影、边框；修复 s 靠近垂线和 p 靠近曲线的问题，重新编译并复查两图。
- PASS：5 秒检查能分别识别“纯几何加减”和“抛物线等距对应”。原有图源未改，延续上一轮高清验收。
- PASS：范围内 `git diff --check`；元数据 JSON 解析。

预览：`build/conclusion_pdfs/C053_parabola_focal_chord_length_inclination.pdf`。
未覆盖正式 pdfs 资源、未提交或发布、未处理其他 UID；验收后清理临时 PNG。无已知未解决问题。
