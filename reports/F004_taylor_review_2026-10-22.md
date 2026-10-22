# F004 泰勒近似 PDF 精修验收记录

日期：2026-10-22。范围：仅 F004；保留原品牌、共享排版与正式 images 资源。

## 数学审计与修订

- 五条主公式核对正确。补齐展开条件、O/o 的定义和差别、零点退化情形、三角函数的弧度条件。
- 删除未限定意义的“局部最佳逼近”；区分多项式大小关系、局部阶数和数值误差。
- 四条路线：导数匹配与逐次导数比较；单位圆面积夹逼；对数有限恒等式及可选面积积分；正弦/余弦相除推导正切。
- 明确正弦的六阶零系数、余弦的五阶零系数，分别得到七阶和六阶余项界；不以奇偶性替代误差证明。
- 对数误差界 |R|≤|x|⁴/[4(1−r)]（固定0<r<1、|x|≤r）；证明 ln(1+x)≤L3(x) 对x>−1成立且仅x=0等号。
- 例1改用精确分数74501/375000，误差<2.54×10⁻⁹，整个区间保证舍入成0.1987；例2用除法后的误差界验证双侧极限1/24；例3以直接求导回验复合函数系数。
- 通式明确以C^n作为Peano展开的充分条件，以C^(n+1)调用拉格朗日余项；主要五式另有正文推导。

## 修改清单

- F004目录：01—06六段TeX、meta.json、pdfs/F004_common_taylor_approximations.pdf。
- 新增F004目录checks/verify_f004.py；新增assets/tikz/F004_*.tex共12幅、F004_samples.dat。
- source.tex主公式已经正确，保持；main.tex、共享工具/排版、其他UID及正式images保持。

## 主图逐幅验收

编辑前已输出六行视觉计划；先生成图形和高精度数据，再围绕图形重写正文。以下每图均生成含完整外框的275 DPI裁切图，按原分辨率逐幅检查。

| 主图 | 页 | 教学任务与替代文字 | 数学/视觉 |
|---|---:|---|---|
| F004_exp_contact.tex | 2 | 指数切线与二次修正：替代弯曲与接触的长段文字。 | PASS / PASS |
| F004_trig_contact.tex | 2 | 正弦/余弦同尺度对照：替代奇偶形状和起点的描述。 | PASS / PASS |
| F004_tan_contact.tex | 3 | 正切与三次近似：替代修正方向和局部走势的描述。 | PASS / PASS |
| F004_log_boundary.tex | 3 | 对数边界：替代靠近−1时真函数与多项式偏离的想象。 | PASS / PASS |
| F004_radian_circle.tex | 5 | 单位圆面积夹逼：替代三角形、扇形和外三角形的文字构造。 | PASS / PASS |
| F004_log_area.tex | 6 | 两导数之间面积：替代函数误差与积分之间的几何说明。 | PASS / PASS |
| F004_sin_accuracy.tex | 7 | 三次/五次正弦误差：替代精度随x变化的冗长比较。 | PASS / PASS |
| F004_cos_residual.tex | 8 | 余弦缩放残差：替代抵消后首项决定极限的口头想象。 | PASS / PASS |
| F004_composite.tex | 9 | 复合函数同轴对照：替代内外层展开结果的曲线描述。 | PASS / PASS |
| F004_exp_far.tex | 9 | 远离展开点的指数偏离：替代局部与全局精度的想象。 | PASS / PASS |
| F004_exp_residual.tex | 10 | 真实残差与错误截断：替代错误判零的文字对比。 | PASS / PASS |
| F004_wrong_sign.tex | 10 | 正弦正确/错号模型：替代符号把曲线推向哪一侧的描述。 | PASS / PASS |

标题与外框有净距，所有外框完整；图例已避开曲线；正切刻度疏化；单位圆等比例，并绘出三角形OAP、扇形OAP、外三角形OAT。曲线来自公式/60位Decimal计算，微小残差避免PGF低精度相消。每图均能从标题、曲线及标签直接读取主要关系，图后只保留必要观察和条件。

## 实际执行与结果

- PASS：python -B 01_function/F004_common_taylor_approximations/checks/verify_f004.py。精确系数恒等式、905项采样误差检查、舍入区间、双侧缩放残差检查通过。采样只是辅助核验，严格依据在正文。
- PASS：数据再生入口加 --write-data；321个采样横坐标，高精度三角函数由独立递推累加90项计算；指数/对数用Decimal函数。
- PASS：使用既有build_conclusion_pdfs.py，参数F004 --overwrite --output-to-conclusion-pdfs --map-json .tmp/F004_review/map.preview.json。仅使用独立预览映射。
- PASS：同一正式源的诊断包装文件连续两次XeLaTeX编译；最终日志无Overfull、Underfull、Missing character或Warning。
- PASS：pdfinfo确认11页、A4（595.28×841.89 pt）、无加密。
- PASS：最终PDF全11页200 DPI渲染并逐页检查；另275 DPI渲染后生成12幅完整外框裁切，全部逐幅检查。修正了首轮图例遮线、密集刻度、标签穿线及孤立标题问题。
- PASS：JSON可解析；12幅图全部实际引用且记录用途；has_diagram与更新时间同步；git diff --check通过。
- 本轮临时渲染、包装、日志和预览映射验收后清理。保留正式源、检查脚本、图形数据、本报告与最终PDF。

## 交付

PDF：01_function/F004_common_taylor_approximations/pdfs/F004_common_taylor_approximations.pdf
SHA256：ae079c67a8b4e2b6e36bc2074cabfd145549e17413651df0f6d69013f8373028
未解决问题：无。本轮止于F004。
