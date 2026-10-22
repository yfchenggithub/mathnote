# C042 椭圆基本关系验收（2026-10-22）

六段、source.tex、meta.json同步；main.tex加入C042并纳入跟踪。优先用短轴端点的对称性、第一定义与勾股定理三行证明；补充从方程构造候选焦点、验证距离和的代数角度，避免循环引用参数关系。明确a最大、b与c顺序不固定，长度取正根、全长与半长、横纵方向及圆边界条件。修正元数据中“圆无此关系”的原说法。

| 图（assets/tikz/） | 回答的问题与替代文字 |
|---|---|
| C042_right_triangle.tex | a为什么是斜边？直角三角形替代记忆式推导 |
| C042_circle_constructs_foci.tex | 已知轴长怎样构造焦点？作圆替代抽象开方 |
| C042_b_c_order.tex | b,c谁大？固定a三态同尺度替代排序文字 |
| C042_orientation.tex | 纵向椭圆a是否仍是长半轴？同尺度坐标交换对照 |
| C042_ellipse_hyperbola.tex | 哪个量最大？同a,b同尺度焦点位置替代加减号混淆 |

数学核验：`python -B 03_conic/C042_ellipse_abc_relation/checks/verify_c042.py` PASS。8664个独立距离和与正根状态，实际TikZ三组b,c数值、焦点坐标、作圆交点、三道例题与关联ID通过。采样用于辅助复核，正文给出完整证明。

官方单UID构建成功，使用独立预览映射。最终6页A4；200 DPI完整逐页检查、五图275 DPI全外框逐图检查。修正主三角形a标签、作圆焦点坐标标签和椭圆/双曲线比较图焦点标签靠线问题，重编重审第1、3、6页及三图；第2、4、5页与已审页面像素相同。最终两遍XeLaTeX无Overfull/Underfull/Warning/Missing character，无重叠、裁切或压框。

数学 PASS；编译 PASS；逐页视觉 PASS；逐图视觉 PASS。无已知未解决问题。未打包、发布或同步。

PDF SHA256: ffa3cc44ded3b3a1c578e36a62797309253af99c353b7ea837af8d5217c995ae
