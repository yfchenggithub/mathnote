# FREE CONTENT SELECTION REPORT

日期：2026-11-15（Asia/Shanghai）。项目：当前 MathNote / Map Note 内容生产仓库。

结果：591 条真实二级结论中，180 条免费、411 条授权，免费比例 30.46%；A/B/C 分别为 108/45/27，A 类组成 15 条短学习路径。

## A. 数据审查与统计

正式发现以 `scripts/zhishu/source_discovery.py` 中 11 个模块白名单的直接子目录为准，逐条核对 meta.json、UID、目录前缀以及六段 TeX 的存在。591 个 ID 唯一；与规划数一致，没有新增或删除结论。未用目录最大编号、index.tex 中的引用条数或知识树节点总数替代结论数。

实际树中另有 1 个根节点、14 个一级章节、470 个其他章节/分类节点，共 485 个结构节点；它们不计入 591 或 180，也不赋予 isPro。源目录的 11 个模块与知识树的 14 个一级章节不同，因此标准 Export 产出 14 个模块 ZIP，而不是强行重排成 11 包。

每条结论的 ID、标题、源模块、knowledgeNode 完整章节路径、isPro 和源文件位置均记录在 [机器校验结果](reports/FREE_CONTENT_EXPORT_VALIDATION.json) 的 inventory 数组中。

源字段位置是各 UID 的 `meta.json` 顶层。修改前 591 条全部为整数 0，无缺失、无非法类型；`scripts/meta_schema.py` 与 `scripts/generate_missing_meta.py` 的现有源默认值也是 0。本次不改变生成模板或其他 metadata，只按清单更改现有 411 个 isPro 数值字符，180 份免费源文件保持原字节。

知识关联方面，正式 mapping 中存在 909 条去重 related 边；源数据还包含 prerequisites/similar，其中 prerequisites 多为知识名称文本。related 不是先修有向边，不能机械当学习顺序。清单保留真实 existingRelatedIds；15 条路径的顺序、每步作用与免费配套均来自正式结论和例题的教学编排，不冒称原有图谱已登记这些有向边。

| 源数学模块 | 总数 | 修改前免费 | 修改后免费 | 修改后授权 | 免费比例 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 集合与逻辑 `00_set` | 22 | 22 | 16 | 6 | 72.7% |
| 函数 `01_function` | 80 | 80 | 20 | 60 | 25.0% |
| 数列 `02_sequence` | 42 | 42 | 15 | 27 | 35.7% |
| 圆锥曲线 `03_conic` | 94 | 94 | 30 | 64 | 31.9% |
| 向量 `04_vector` | 40 | 40 | 16 | 24 | 40.0% |
| 立体几何 `05_geometry-solid` | 58 | 58 | 18 | 40 | 31.0% |
| 概率统计 `06_probability-stat` | 42 | 42 | 18 | 24 | 42.9% |
| 不等式 `07_inequality` | 64 | 64 | 11 | 53 | 17.2% |
| 三角函数 `08_trigonometry` | 39 | 39 | 12 | 27 | 30.8% |
| 平面几何 `09_geometry-plane` | 55 | 55 | 12 | 43 | 21.8% |
| 初中基础 `10_junior_basics` | 55 | 55 | 12 | 43 | 21.8% |
| **合计** | **591** | **591** | **180** | **411** | **30.46%** |

模块配额并非先验约束。集合与逻辑的运算、量词和条件链适合成套提供，故 16/22；圆锥曲线开放椭圆与抛物线连续专题及几何精品，共 30/94；不等式保留大量专题型进阶内容，仅选可独立使用的均值链及代表技巧，共 11/64。每个主要模块都有免费内容，未按编号、前 N 条、随机数或难度阈值划分。

## B. 完整免费结论名单

维护清单：[free-knowledge-selection.json](data/content/free-knowledge-selection.json)。这是内容编审依据，正式 isPro 仍在每个 UID/meta.json 中，不接入运行时权限判断。每条只计一个主类别；相近版本如焦半径、倒数和、容斥、球体积等确有独立 UID，保留原 ID 并尽量保持主题入口一致，未合并或新增结论。

| ID | 标题 | 源模块 | 类别 | 免费理由 |
| --- | --- | --- | --- | --- |
| S001 | 有限集合子集计数公式 | 集合与逻辑 | C | 子集、真子集与非空子集计数适合直接查询，避免逐个枚举。 |
| S003 | 德摩根律 | 集合与逻辑 | A | 路径「集合运算到容斥计数」第4步：在并交与补集之间转换。 |
| S005 | 两个集合的容斥原理 | 集合与逻辑 | A | 路径「集合运算到容斥计数」第5步：由重复计数引出两集合容斥。 |
| S008 | 命题否定形式转换 | 集合与逻辑 | C | 量词互换与谓词否定是命题判断的常用操作，适合快速核对。 |
| S009 | 四种命题关系 | 集合与逻辑 | A | 路径「充分必要条件与命题辨析」第3步：整理原逆否逆否四种命题关系。 |
| S010 | 充分必要条件判定 | 集合与逻辑 | A | 路径「充分必要条件与命题辨析」第1步：建立充分、必要及充要的判定方向。 |
| S013 | 三集合容斥原理 | 集合与逻辑 | A | 路径「集合运算到容斥计数」第6步：推广到三集合的重叠修正。 |
| S014 | 集合的并交运算律（交换律、结合律、分配律） | 集合与逻辑 | A | 路径「集合运算到容斥计数」第2步：掌握并交运算律以化简表达式。 |
| S015 | 双重补集还原律 | 集合与逻辑 | A | 路径「集合运算到容斥计数」第3步：理解双重补集还原。 |
| S016 | 容斥原理（两集合与三集合公式） | 集合与逻辑 | A | 路径「集合运算到容斥计数」第7步：以统一容斥表达回顾两集合和三集合。 |
| S017 | 子集个数公式 | 集合与逻辑 | C | 子集公式的约束选取版本与S001同时免费，方便含指定元素的计数查询。 |
| S019 | 全称命题否定规则 | 集合与逻辑 | C | 全称命题否定与S008配套开放，直接排查量词和否定方向。 |
| S020 | 存在量词命题的否定规则 | 集合与逻辑 | C | 存在命题否定补足全称否定的另一分支，形成完整量词速查。 |
| S021 | 命题的否定与否命题辨析 | 集合与逻辑 | A | 路径「充分必要条件与命题辨析」第4步：区分命题的否定与否命题，避免推理方向混淆。 |
| S023 | 子集法判定充要条件 | 集合与逻辑 | A | 路径「充分必要条件与命题辨析」第2步：用解集包含将条件判断具体化。 |
| S025 | 集合的基本运算 | 集合与逻辑 | A | 路径「集合运算到容斥计数」第1步：把并交补差翻译成元素归属。 |
| F001 | 导数判定单调性 | 函数 | A | 路径「求导—单调—极值—闭区间最值」第4步：用导数符号确定单调区间。 |
| F002 | 极值点与导数判定 | 函数 | A | 路径「求导—单调—极值—闭区间最值」第8步：综合极值候选点与符号判定。 |
| F007 | 一次分式函数值域公式：分离常数法 | 函数 | B | 分离常数把一次分式转为平移后的反比例函数，展示结构识别如何替代机械求值域。 |
| F010 | 单调函数在闭区间上的值域 | 函数 | A | 路径「求导—单调—极值—闭区间最值」第5步：把已知单调性转化为闭区间端点值域，承接导数符号的应用。 |
| F011 | 对勾函数值域公式（基本不等式） | 函数 | B | 把对勾函数最值与双曲线两支最短距离连接，展示代数与几何互译。 |
| F012 | 双根号函数值域：几何意义法（距离型） | 函数 | B | 将双根号和解释为折线距离，利用线段最短减少求导与平方运算。 |
| F019 | 奇偶单调等价转化：和式与绝对值比较 | 函数 | B | 把奇偶性和单调性合用，将函数值比较转化成自变量关系。 |
| F026 | 双对称性推周期：轴轴、点点、轴点三种情形 | 函数 | B | 用两次对称复合解释周期，展示从几何变换寻找抽象函数规律。 |
| F035 | 指数幂的运算法则 | 函数 | C | 指数运算法则是指对、数列与代数计算的公共工具，适合频繁查询。 |
| F036 | 对数运算法则（积商幂及换底公式） | 函数 | C | 对数积商幂与换底公式能直接缩短计算，支持免费函数专题。 |
| F037 | 对数恒等式 | 函数 | C | 指对互逆恒等式与运算法则成套查询，避免底数与真数混淆。 |
| F049 | 基本初等函数的导数公式 | 函数 | A | 路径「求导—单调—极值—闭区间最值」第1步：提供基本函数的求导入口。 |
| F050 | 导数四则运算法则 | 函数 | A | 路径「求导—单调—极值—闭区间最值」第2步：把基本导数推广到四则运算。 |
| F051 | 链式法则（复合函数求导） | 函数 | A | 路径「求导—单调—极值—闭区间最值」第3步：处理复合函数的内外层求导。 |
| F052 | 切线方程的点斜式公式 | 函数 | C | 已知切点与导数即可写切线，直接承接免费求导路径。 |
| F054 | 极值点的必要不充分条件：导数零点判定 | 函数 | A | 路径「求导—单调—极值—闭区间最值」第6步：先检查导数零点只是极值必要条件。 |
| F055 | 极值第一充分条件 | 函数 | A | 路径「求导—单调—极值—闭区间最值」第7步：用左右变号补足极值充分条件。 |
| F056 | 闭区间上连续函数最值定理 | 函数 | A | 路径「求导—单调—极值—闭区间最值」第9步：加入端点和不可导点完成闭区间最值。 |
| F076 | 同构脱壳原理（严格单调函数脱壳） | 函数 | B | 用严格单调性脱去相同外层函数，将复合方程降为内层比较。 |
| F080 | 倒数对称式与整体换元法 | 函数 | B | 用倒数对称的整体换元降低代数次数，并同时展示取值范围约束。 |
| L002 | 等差数列前n项和公式 | 数列 | A | 路径「通项与前项和到常见求和」第3步：掌握等差前项和并理解配对。 |
| L003 | 等比数列前n项和公式 | 数列 | A | 路径「通项与前项和到常见求和」第4步：掌握等比求和及公比为1的边界。 |
| L006 | 阶乘裂项求和公式 | 数列 | A | 路径「通项与前项和到常见求和」第9步：用阶乘差展示另一类裂项。 |
| L007 | 等差数列通项公式 | 数列 | A | 路径「通项与前项和到常见求和」第1步：建立等差通项与公差的关系。 |
| L008 | 等比数列通项公式 | 数列 | A | 路径「通项与前项和到常见求和」第2步：建立等比通项与公比的关系。 |
| L019 | 已知前n项和求通项公式 | 数列 | A | 路径「通项与前项和到常见求和」第5步：通过相邻前项和作差恢复通项。 |
| L022 | 一阶线性递推通项公式（不动点法） | 数列 | B | 通过减去不动点把线性递推化为等比数列，展示辅助数列构造。 |
| L023 | 一次函数型递推通项公式：等比构造法 | 数列 | B | 加入一次辅助项把含n的一阶线性递推化为等比，承接L022展示更深入的构造技巧。 |
| L025 | 分式递推倒数变换化线性 | 数列 | B | 分式递推取倒数后化线性，展示用代换将复杂递推降为熟悉模型。 |
| L032 | 裂项相消基本公式（分母为一次因式乘积） | 数列 | A | 路径「通项与前项和到常见求和」第7步：用有理式裂项展示首尾抵消。 |
| L033 | 根式型裂项相消公式 | 数列 | A | 路径「通项与前项和到常见求和」第8步：用有理化把根式求和化为裂项。 |
| L035 | 阶乘型裂项相消求和 | 数列 | A | 路径「通项与前项和到常见求和」第10步：保留同一阶乘裂项的对应版本以便交叉检索。 |
| L036 | 等差乘等比前n项和公式 | 数列 | B | 用正确的错位相减闭式计算等差乘等比前项和，展示节省重复计算的价值；L001的另一公式存在反例，未入选。 |
| L037 | 分组求和法（等差+等比拆分） | 数列 | A | 路径「通项与前项和到常见求和」第6步：把混合数列拆成可求和的部分。 |
| L038 | 倒序相加法（对称等和数列求和） | 数列 | A | 路径「通项与前项和到常见求和」第11步：推广等差配对到一般对称等和数列。 |
| C001 | 椭圆与圆周的距离最值 | 圆锥曲线 | B | 以距离区间统一椭圆与圆周的最近最远距离，展示连续几何模型与分类边界。 |
| C002 | 椭圆上点到直线距离最值公式 | 圆锥曲线 | B | 通过椭圆参数化把点线距离最值化为三角振幅，减少联立计算。 |
| C027 | 椭圆焦点弦长公式 | 圆锥曲线 | A | 路径「椭圆定义、焦半径与焦点弦」第8步：用斜率直接计算焦点弦长。 |
| C028 | 椭圆焦点弦长公式 | 圆锥曲线 | A | 路径「椭圆定义、焦半径与焦点弦」第9步：以倾斜角和离心率解释同一弦长。 |
| C029 | 椭圆焦半径公式 | 圆锥曲线 | A | 路径「椭圆定义、焦半径与焦点弦」第6步：先把焦点距离转化为横坐标一次式。 |
| C030 | 椭圆焦点弦三角形周长定值 | 圆锥曲线 | A | 路径「椭圆定义、焦半径与焦点弦」第11步：用定义消去动点距离得到周长定值。 |
| C032 | 阿波罗尼斯圆 | 圆锥曲线 | B | 把定距离比轨迹识别为圆，并用内外分点直径理解圆心半径，展示几何结构。 |
| C033 | 椭圆硬解定理（直线与椭圆联立韦达公式） | 圆锥曲线 | B | 系统整理直线与椭圆联立后的和积、交点存在性和弦长，提供可迁移计算工具。 |
| C036 | 椭圆的第一定义 | 圆锥曲线 | A | 路径「椭圆定义、焦半径与焦点弦」第1步：用两焦点距离和建立椭圆模型。 |
| C038 | 抛物线的定义：到焦点与准线距离相等 | 圆锥曲线 | A | 路径「抛物线定义、焦点弦与切线」第1步：建立焦点与准线的等距模型。 |
| C039 | 椭圆的第二定义 | 圆锥曲线 | A | 路径「椭圆定义、焦半径与焦点弦」第5步：用同侧焦点和准线统一距离比。 |
| C041 | 抛物线的第二定义（焦点与准线定义） | 圆锥曲线 | A | 路径「抛物线定义、焦点弦与切线」第2步：把定义写成标准坐标并说明开口方向。 |
| C042 | 椭圆基本关系：a²=b²+c² | 圆锥曲线 | A | 路径「椭圆定义、焦半径与焦点弦」第2步：连接半轴与半焦距三个参数。 |
| C044 | 离心率的几何定义与代数公式 | 圆锥曲线 | A | 路径「椭圆定义、焦半径与焦点弦」第4步：解释离心率及曲线形状。 |
| C045 | 圆锥曲线标准方程（焦点在x轴） | 圆锥曲线 | A | 路径「椭圆定义、焦半径与焦点弦」第3步：将距离模型落实到标准方程。 |
| C047 | 椭圆焦点三角形面积公式 | 圆锥曲线 | B | 用焦点三角形面积连接角度、纵坐标与椭圆参数，展示多个表达的互相校验。 |
| C049 | 椭圆焦半径公式（焦点在x轴） | 圆锥曲线 | A | 路径「椭圆定义、焦半径与焦点弦」第7步：保留焦半径公式的对应详细版本。 |
| C051 | 抛物线焦半径公式（坐标形式） | 圆锥曲线 | A | 路径「抛物线定义、焦点弦与切线」第3步：把焦半径转化为轴向坐标距离。 |
| C052 | 椭圆焦点弦长公式 | 圆锥曲线 | A | 路径「椭圆定义、焦半径与焦点弦」第10步：汇总角度、斜率、通径和最值应用。 |
| C053 | 抛物线的焦点弦长公式（倾斜角形式） | 圆锥曲线 | A | 路径「抛物线定义、焦点弦与切线」第4步：用倾角解释焦点弦长和通径最短。 |
| C054 | 抛物线焦点弦倒数之和定理 | 圆锥曲线 | A | 路径「抛物线定义、焦点弦与切线」第5步：由焦点弦研究两段倒数和定值。 |
| C055 | 抛物线焦点弦横纵坐标积公式 | 圆锥曲线 | A | 路径「抛物线定义、焦点弦与切线」第7步：从两端点坐标积连接到切线关系。 |
| C058 | 抛物线焦点弦倒数和定值 | 圆锥曲线 | A | 路径「抛物线定义、焦点弦与切线」第6步：保留倒数和的另一版本及四种开口说明。 |
| C063 | 圆锥曲线弦长公式 | 圆锥曲线 | B | 把弦长还原为投影直角三角形，再与韦达、判别式连接，形成通用求弦工具。 |
| C067 | 抛物线切线方程（切点式） | 圆锥曲线 | A | 路径「抛物线定义、焦点弦与切线」第8步：以切点式写切线并解释轴上对称关系。 |
| C078 | 椭圆参数方程 | 圆锥曲线 | B | 从圆伸缩得到椭圆参数方程，把两个坐标压缩为一个角参数。 |
| C088 | 双曲线两渐近线截点三角形面积 | 圆锥曲线 | B | 用底高与坐标乘积解释渐近线截点三角形面积，展示初中工具处理圆锥曲线。 |
| C089 | 双曲线切线与渐近线三角形面积定值 | 圆锥曲线 | B | 切线与渐近线形成面积定值及中点关系，展示无需逐次求面积的结构结论。 |
| C091 | 双曲线渐近线平行四边形面积定值 | 圆锥曲线 | B | 用渐近线方向的平行四边形解释面积不变量，展示多种证明如何对应同一构造。 |
| C096 | 抛物线与特定圆的三切边闭合性质 | 圆锥曲线 | B | 通过第三弦只需和积的结构证明三切线闭合，四种方法的专用图展示解题与阅读价值。 |
| V001 | 极化恒等式 | 向量 | B | 以极化恒等式将数量积转换为模长平方差，减少角度与坐标计算。 |
| V002 | 极化恒等式（三角形模型） | 向量 | B | 将同一极化思想落在三角形三边上，与V001成套开放便于直接应用。 |
| V008 | 三角形重心向量结论 | 向量 | B | 用等权向量和识别重心，连接代数系数与几何中心。 |
| V021 | 向量加法法则（三角形法则与平行四边形法则） | 向量 | A | 路径「向量运算到共线、垂直与封闭」第1步：用首尾相接理解向量加法。 |
| V022 | 向量减法的三角形法则 | 向量 | A | 路径「向量运算到共线、垂直与封闭」第2步：用共起点图形理解向量减法方向。 |
| V023 | 向量数乘的几何意义 | 向量 | A | 路径「向量运算到共线、垂直与封闭」第3步：理解实数数乘的长度与方向。 |
| V024 | 平面向量基本定理 | 向量 | A | 路径「向量运算到共线、垂直与封闭」第4步：用两个不共线向量唯一分解。 |
| V025 | 向量坐标运算法则：加减、数乘与点积 | 向量 | A | 路径「向量运算到共线、垂直与封闭」第5步：把加减、数乘和点积落到坐标。 |
| V026 | 向量模长公式 | 向量 | A | 路径「向量运算到共线、垂直与封闭」第6步：把模长与两点距离连接起来。 |
| V027 | 向量夹角余弦公式 | 向量 | A | 路径「向量运算到共线、垂直与封闭」第7步：由点积和模长求夹角。 |
| V028 | 向量平行与三点共线的坐标判定 | 向量 | A | 路径「向量运算到共线、垂直与封闭」第8步：用坐标判定平行和三点共线。 |
| V029 | 向量垂直的坐标判定（点积为零） | 向量 | A | 路径「向量运算到共线、垂直与封闭」第9步：用点积为零判定垂直。 |
| V031 | 定比分点坐标公式 | 向量 | B | 用有向分比直接得到分点坐标，并统一内分、外分与中点，减少联立求交计算。 |
| V032 | 平行四边形对角线平方和定理（向量恒等式） | 向量 | B | 把向量和差的模平方还原为平行四边形两条对角线，直观连接代数与几何度量。 |
| V033 | 坐标三角形面积公式 | 向量 | B | 从底高面积和辅助线推出坐标面积，连接向量、三点共线与C088的面积应用。 |
| V034 | 向量和为零与三角形封闭条件 | 向量 | A | 路径「向量运算到共线、垂直与封闭」第10步：将向量和为零读成三角形封闭。 |
| G001 | 球体体积与表面积公式 | 立体几何 | C | 球的体积表面积是几何计算的常见查表需求。 |
| G012 | 直线与平面平行的判定定理 | 立体几何 | A | 路径「空间平行、垂直到线面角」第1步：从线线平行建立线面平行。 |
| G013 | 线面平行性质定理：由线面平行推出与交线平行 | 立体几何 | A | 路径「空间平行、垂直到线面角」第2步：由线面平行提取交线平行。 |
| G014 | 面面平行判定定理 | 立体几何 | A | 路径「空间平行、垂直到线面角」第3步：用两相交直线建立面面平行。 |
| G015 | 面面平行性质定理（交线平行） | 立体几何 | A | 路径「空间平行、垂直到线面角」第4步：从面面平行返回截面交线关系。 |
| G016 | 线面垂直判定定理 | 立体几何 | A | 路径「空间平行、垂直到线面角」第5步：由两相交线的垂直建立线面垂直。 |
| G017 | 线面垂直的性质定理 | 立体几何 | A | 路径「空间平行、垂直到线面角」第6步：用同一平面的垂线得到线线平行。 |
| G018 | 面面垂直判定定理（线面垂直推面面垂直） | 立体几何 | A | 路径「空间平行、垂直到线面角」第7步：由面内垂线建立面面垂直。 |
| G019 | 面面垂直性质定理 | 立体几何 | A | 路径「空间平行、垂直到线面角」第8步：从面面垂直提取线面垂直。 |
| G021 | 线面角正弦公式：垂线段长度比斜线段长度 | 立体几何 | A | 路径「空间平行、垂直到线面角」第9步：用垂线段与斜线段之比求线面角。 |
| G025 | 等体积法求点到平面的距离 | 立体几何 | B | 等体积换底求高可避开难作的空间垂线，展示几何降维。 |
| G030 | 射影面积法求二面角 | 立体几何 | B | 用投影面积之比求二面角余弦的绝对值，将空间作角转为平面面积计算。 |
| G034 | 等体积法求高 | 立体几何 | B | 与G025同一体积换高思想的基础公式版本同时开放，保证检索入口一致。 |
| G035 | 墙角模型外接球半径公式 | 立体几何 | B | 将三条互相垂直侧棱补成长方体，用体对角线处理外接球。 |
| G045 | 球截面圆半径公式 | 立体几何 | C | 球截面半径直接用勾股关系计算，可减少重复作图列式。 |
| G049 | 柱体体积统一公式 | 立体几何 | C | 柱体统一底面积乘高用于常见空间体积计算。 |
| G050 | 锥体体积公式 | 立体几何 | C | 锥体体积既是直接计算工具，也是G025和G034等体积法的免费前置。 |
| G052 | 球体积公式 | 立体几何 | C | 球体积的独立条目与G001同时开放，避免同一公式不同入口分类不一致。 |
| R005 | 互斥事件的加法公式 | 概率统计 | A | 路径「概率运算到二项分布」第4步：区分互斥并用加法合并事件。 |
| R006 | 独立事件的概率乘法公式 | 概率统计 | A | 路径「概率运算到二项分布」第5步：区分独立并用乘法求同时发生。 |
| R007 | 二项分布概率公式 | 概率统计 | A | 路径「概率运算到二项分布」第6步：把独立重复试验与组合计数合成二项概率。 |
| R008 | 离散型随机变量的数学期望 | 概率统计 | A | 路径「离散分布的期望与方差」第1步：以取值和概率计算加权平均。 |
| R009 | 期望的线性性质 | 概率统计 | A | 路径「离散分布的期望与方差」第2步：用线性性质简化期望计算。 |
| R010 | 二项分布的数学期望公式 | 概率统计 | A | 路径「离散分布的期望与方差」第3步：从重复试验解释二项期望np。 |
| R012 | 离散型随机变量方差定义公式 | 概率统计 | A | 路径「离散分布的期望与方差」第4步：建立方差的加权偏差平方定义。 |
| R014 | 组合数公式 | 概率统计 | A | 路径「概率运算到二项分布」第1步：提供无序选取成功位置的组合数。 |
| R023 | 古典概型概率公式 | 概率统计 | A | 路径「概率运算到二项分布」第2步：以等可能样本计数建立概率。 |
| R024 | 对立事件概率公式（正难则反） | 概率统计 | A | 路径「概率运算到二项分布」第3步：正面难算时转算对立事件。 |
| R029 | 二项分布的期望与方差公式 | 概率统计 | A | 路径「离散分布的期望与方差」第5步：成对查询二项分布期望与方差。 |
| R030 | 超几何分布的期望公式 | 概率统计 | B | 把无放回抽样期望化为nM/N，图解抽样结构并避免逐项列分布求和。 |
| R031 | 两点分布的期望与方差公式 | 概率统计 | A | 路径「离散分布的期望与方差」第6步：把二项模型缩到一次试验检验均值与方差。 |
| R032 | 正态分布的3σ原则 | 概率统计 | B | 用正态分布中心区间与面积解释3σ经验区间，展示概率图像的查询价值。 |
| R033 | 描述统计量：平均数、方差、中位数、众数 | 概率统计 | C | 平均数、中位数、众数、方差集中速查，避免混淆统计量含义。 |
| R034 | 分层抽样比例分配样本量公式 | 概率统计 | C | 分层抽样人数按比例分配，适合基础统计题直接核算。 |
| R035 | 频率分布直方图的众数与中位数估计 | 概率统计 | C | 用直方图面积求中位数和读众数，是有明确操作步骤的实用查询。 |
| R037 | 标准差线性变换性质 | 概率统计 | C | 标准差的平移与伸缩规律可省去重新计算全部样本偏差。 |
| I002 | 基本不等式及其变形 | 不等式 | A | 路径「基本不等式到倒数和最值」第1步：掌握基本不等式及常见等价变形。 |
| I003 | 糖水不等式 | 不等式 | B | 用浓度混合解释分式增减的糖水不等式，将比较大小转为直觉模型。 |
| I013 | 对勾不等式（x+1/x≥2） | 不等式 | A | 路径「基本不等式到倒数和最值」第4步：用x与倒数的乘积定值求最小值。 |
| I022 | 二元分式和不等式（倒数和≥4/(和)） | 不等式 | A | 路径「基本不等式到倒数和最值」第5步：用和定值求二元倒数和下界。 |
| I027 | 互为倒数和不等式 | 不等式 | A | 路径「基本不等式到倒数和最值」第8步：在互为倒数的组合中复用同一思想。 |
| I045 | 穿根法（奇穿偶不穿）解高次不等式 | 不等式 | B | 将多项式因子的奇偶重数画成穿根规则，减少重复区间代入。 |
| I049 | 基本不等式一正二定三相等原则 | 不等式 | A | 路径「基本不等式到倒数和最值」第3步：检查正数、定值和取等可达性。 |
| I050 | 1的代换：正数和为1时倒数和的最小值 | 不等式 | A | 路径「基本不等式到倒数和最值」第6步：将和为1化为具体最值模型。 |
| I054 | 均值不等式（AM-GM不等式） | 不等式 | A | 路径「基本不等式到倒数和最值」第2步：用均值形式理解多元推广和等号。 |
| I059 | 正数和与倒数和的不等式 | 不等式 | A | 路径「基本不等式到倒数和最值」第7步：用正数和与倒数和乘积回验。 |
| I064 | 反向柯西不等式（二维） | 不等式 | B | 以完全平方解释反向柯西的平方差结构，开放有难度但可直接迁移的代数技巧。 |
| T005 | 诱导公式（奇变偶不变） | 三角函数 | A | 路径「三角恒等变换到辅助角」第3步：通过诱导公式统一角与函数名称。 |
| T006 | 二倍角公式 | 三角函数 | A | 路径「三角恒等变换到辅助角」第5步：由和角得到倍角变形。 |
| T007 | 余弦定理 | 三角函数 | C | 余弦定理支持三边求角与两边夹角求边，属于解三角形通用工具。 |
| T008 | 正弦定理 | 三角函数 | C | 正弦定理建立边角与外接圆半径的联系，适合直接查询与配套应用。 |
| T009 | 同角三角函数基本关系（平方关系和商数关系） | 三角函数 | A | 路径「三角恒等变换到辅助角」第1步：建立同角平方关系和商数关系。 |
| T010 | 两角和与差的正弦、余弦、正切公式 | 三角函数 | A | 路径「三角恒等变换到辅助角」第4步：把和差角展开到单角。 |
| T013 | 降幂公式 | 三角函数 | A | 路径「三角恒等变换到辅助角」第6步：用倍角反向完成平方降幂。 |
| T015 | 辅助角公式（合一变形公式） | 三角函数 | A | 路径「三角恒等变换到辅助角」第7步：把正弦余弦线性组合合成为单个函数。 |
| T020 | 同角三角函数的平方恒等式（1的代换） | 三角函数 | A | 路径「三角恒等变换到辅助角」第2步：把同角关系转化为1的代换工具。 |
| T026 | 正弦定理的边角互化 | 三角函数 | C | 正弦定理的边角互化版本与T008同时开放，保持等价工具入口一致。 |
| T027 | 余弦定理变形：三边求角与三角形形状判断 | 三角函数 | C | 余弦定理判形与T007配套，可直接判断锐直钝减少重复推导。 |
| T034 | 三角形内角平分线定理 | 三角函数 | B | 与P035同一内角平分线定比分段主题同时开放，保留三角与平几的两个入口。 |
| P004 | 点到圆距离极值统一模型 | 平面几何 | B | 用统一点圆距离模型替代外内圆上三类口诀，展示边界统一处理。 |
| P015 | 点到直线的距离公式 | 平面几何 | C | 点到直线距离是圆的位置判定与圆锥曲线距离题的公共计算前置。 |
| P019 | 圆的标准方程与一般方程 | 平面几何 | A | 路径「圆方程到直线与圆的位置」第1步：建立圆标准式与一般式的对应。 |
| P020 | 圆的一般方程与圆心半径公式 | 平面几何 | A | 路径「圆方程到直线与圆的位置」第2步：从一般式系数快速读圆心半径并检查成圆条件。 |
| P021 | 直线与圆的位置关系判定（d与r比较） | 平面几何 | A | 路径「圆方程到直线与圆的位置」第3步：以圆心距和半径比较判断位置。 |
| P028 | 圆内接四边形对角互补 | 平面几何 | A | 路径「圆周角到共圆和弦切角」第2步：由圆内接四边形得到对角互补。 |
| P030 | 三角形重心到三顶点距离平方和最小值 | 平面几何 | B | 用重心给出到三顶点距离平方和的最小值，展示几何中心的优化意义。 |
| P033 | 内心到三边距离相等及内切圆半径公式 | 平面几何 | B | 用三块同高三角形解释内心、面积和切线段关系，展示图形如何承载公式。 |
| P035 | 三角形内角平分线定理 | 平面几何 | B | 把角平分线分段比画成邻边权重，减少辅助线脑补并明确适用条件。 |
| P047 | 四点共圆的判定条件 | 平面几何 | A | 路径「圆周角到共圆和弦切角」第3步：反过来用角度条件判定四点共圆。 |
| P052 | 弦切角定理 | 平面几何 | A | 路径「圆周角到共圆和弦切角」第4步：把切线与弦所成角转回圆周角。 |
| P054 | 曲线轴对称的快速判定法 | 平面几何 | B | 用具体曲线及反射判据寻找对称轴，展示从候选猜测到验证的完整过程。 |
| J001 | A字型相似（平行截相似） | 初中基础 | A | 路径「相似判定到A字与8字模型」第3步：在A字模型中识别对应三角形。 |
| J002 | 8字型相似模型（平行线夹相交线） | 初中基础 | A | 路径「相似判定到A字与8字模型」第4步：把对应关系迁移到8字交叉模型。 |
| J004 | 平行线分线段成比例定理 | 初中基础 | A | 路径「相似判定到A字与8字模型」第2步：利用平行截线建立比例。 |
| J007 | 相似三角形面积比等于相似比的平方 | 初中基础 | A | 路径「相似判定到A字与8字模型」第5步：由相似比求面积比。 |
| J008 | 相似三角形的判定 | 初中基础 | A | 路径「相似判定到A字与8字模型」第1步：先掌握相似判定的最少条件。 |
| J009 | 圆周角定理 | 初中基础 | A | 路径「圆周角到共圆和弦切角」第1步：用同弧圆周角建立角度对应。 |
| J023 | 二次函数顶点坐标公式 | 初中基础 | C | 二次函数顶点与对称轴是最值和图像题的常用速查。 |
| J028 | 反比例函数系数k的几何意义 | 初中基础 | B | 反比例函数系数成为矩形或三角形的面积定值，为C088与C091的坐标面积提供直观入口。 |
| J029 | 二次三项式配方恒等式 | 初中基础 | C | 配方法解释顶点公式并支持逆向还原，避免只背公式无法操作。 |
| J032 | 将军饮马模型（对称点法求距离和最小值） | 初中基础 | B | 通过对称点将折线路程变为直线距离，完整展示将军饮马构造。 |
| J053 | 韦达定理（根与系数关系） | 初中基础 | C | 根与系数关系直接支撑弦、数列与方程的和积计算。 |
| J055 | 判别式Δ与二次函数交点个数及最值 | 初中基础 | C | 判别式同时关联交点数和最值，方便二次模型快速判断。 |

C 类的“高频实用”是基于这些工具在常规数学任务中的用途作出的教学判断；本次没有实际用户查询日志或题库统计，不把它表述为经数据测量的使用频次。

## C. 免费学习路径

以下为 A 类 108 个唯一 UID 的学习顺序。表外 supportingFreeIds 仅是已入选 B/C 或其他路径的配套入口，不在本路径重复计数；所有这些 ID 也经自动检查属于免费集合。学校已学的运算、角和函数定义仍是常规前置，不声称这些短路径取代整门课程。

### 集合运算到容斥计数（set-operations）

先理解元素归属与运算律，再用补集转化，最后完成两集合及三集合计数。

顺序：S025 → S014 → S015 → S003 → S005 → S013 → S016。

| 顺序 | ID | 在路径中的作用与联系 |
| ---: | --- | --- |
| 1 | S025 | 把并交补差翻译成元素归属 |
| 2 | S014 | 掌握并交运算律以化简表达式 |
| 3 | S015 | 理解双重补集还原 |
| 4 | S003 | 在并交与补集之间转换 |
| 5 | S005 | 由重复计数引出两集合容斥 |
| 6 | S013 | 推广到三集合的重叠修正 |
| 7 | S016 | 以统一容斥表达回顾两集合和三集合 |

### 充分必要条件与命题辨析（logic-conditions）

由条件判定到集合包含，再辨别逆否与命题否定，能解决条件关系判断题。

顺序：S010 → S023 → S009 → S021。

| 顺序 | ID | 在路径中的作用与联系 |
| ---: | --- | --- |
| 1 | S010 | 建立充分、必要及充要的判定方向 |
| 2 | S023 | 用解集包含将条件判断具体化 |
| 3 | S009 | 整理原逆否逆否四种命题关系 |
| 4 | S021 | 区分命题的否定与否命题，避免推理方向混淆 |

### 求导—单调—极值—闭区间最值（derivative-monotonicity）

求导法则与判定条件一同开放；保留极值必要性、充分性和反例对应，避免只背口诀。

顺序：F049 → F050 → F051 → F001 → F010 → F054 → F055 → F002 → F056。

| 顺序 | ID | 在路径中的作用与联系 |
| ---: | --- | --- |
| 1 | F049 | 提供基本函数的求导入口 |
| 2 | F050 | 把基本导数推广到四则运算 |
| 3 | F051 | 处理复合函数的内外层求导 |
| 4 | F001 | 用导数符号确定单调区间 |
| 5 | F010 | 把已知单调性转化为闭区间端点值域，承接导数符号的应用 |
| 6 | F054 | 先检查导数零点只是极值必要条件 |
| 7 | F055 | 用左右变号补足极值充分条件 |
| 8 | F002 | 综合极值候选点与符号判定 |
| 9 | F056 | 加入端点和不可导点完成闭区间最值 |

免费配套：F035, F036, T009, F052。

### 通项与前项和到常见求和（sequence-summation）

先掌握等差等比，再以差分、分组、裂项和倒序相加形成可迁移的求和工具。

顺序：L007 → L008 → L002 → L003 → L019 → L037 → L032 → L033 → L006 → L035 → L038。

| 顺序 | ID | 在路径中的作用与联系 |
| ---: | --- | --- |
| 1 | L007 | 建立等差通项与公差的关系 |
| 2 | L008 | 建立等比通项与公比的关系 |
| 3 | L002 | 掌握等差前项和并理解配对 |
| 4 | L003 | 掌握等比求和及公比为1的边界 |
| 5 | L019 | 通过相邻前项和作差恢复通项 |
| 6 | L037 | 把混合数列拆成可求和的部分 |
| 7 | L032 | 用有理式裂项展示首尾抵消 |
| 8 | L033 | 用有理化把根式求和化为裂项 |
| 9 | L006 | 用阶乘差展示另一类裂项 |
| 10 | L035 | 保留同一阶乘裂项的对应版本以便交叉检索 |
| 11 | L038 | 推广等差配对到一般对称等和数列 |

免费配套：F035, F036, J053。

### 椭圆定义、焦半径与焦点弦（ellipse-focus-chord）

从距离和定义到参数、焦准比、焦半径，再到焦点弦及周长定值，形成一个完整短专题。

顺序：C036 → C042 → C045 → C044 → C039 → C029 → C049 → C027 → C028 → C052 → C030。

| 顺序 | ID | 在路径中的作用与联系 |
| ---: | --- | --- |
| 1 | C036 | 用两焦点距离和建立椭圆模型 |
| 2 | C042 | 连接半轴与半焦距三个参数 |
| 3 | C045 | 将距离模型落实到标准方程 |
| 4 | C044 | 解释离心率及曲线形状 |
| 5 | C039 | 用同侧焦点和准线统一距离比 |
| 6 | C029 | 先把焦点距离转化为横坐标一次式 |
| 7 | C049 | 保留焦半径公式的对应详细版本 |
| 8 | C027 | 用斜率直接计算焦点弦长 |
| 9 | C028 | 以倾斜角和离心率解释同一弦长 |
| 10 | C052 | 汇总角度、斜率、通径和最值应用 |
| 11 | C030 | 用定义消去动点距离得到周长定值 |

免费配套：J053, T009, T007, T008, C078, C063。

### 抛物线定义、焦点弦与切线（parabola-focus-chord）

从等距定义构建焦半径，再理解弦长、倒数和、坐标积与切线，条件随公式一同学习。

顺序：C038 → C041 → C051 → C053 → C054 → C058 → C055 → C067。

| 顺序 | ID | 在路径中的作用与联系 |
| ---: | --- | --- |
| 1 | C038 | 建立焦点与准线的等距模型 |
| 2 | C041 | 把定义写成标准坐标并说明开口方向 |
| 3 | C051 | 把焦半径转化为轴向坐标距离 |
| 4 | C053 | 用倾角解释焦点弦长和通径最短 |
| 5 | C054 | 由焦点弦研究两段倒数和定值 |
| 6 | C058 | 保留倒数和的另一版本及四种开口说明 |
| 7 | C055 | 从两端点坐标积连接到切线关系 |
| 8 | C067 | 以切点式写切线并解释轴上对称关系 |

免费配套：J053, T009, T007, C063。

### 向量运算到共线、垂直与封闭（vector-geometry）

从位移合成到坐标，再到夹角、平行垂直和三角形闭合；后续精品极化和面积可直接承接。

顺序：V021 → V022 → V023 → V024 → V025 → V026 → V027 → V028 → V029 → V034。

| 顺序 | ID | 在路径中的作用与联系 |
| ---: | --- | --- |
| 1 | V021 | 用首尾相接理解向量加法 |
| 2 | V022 | 用共起点图形理解向量减法方向 |
| 3 | V023 | 理解实数数乘的长度与方向 |
| 4 | V024 | 用两个不共线向量唯一分解 |
| 5 | V025 | 把加减、数乘和点积落到坐标 |
| 6 | V026 | 把模长与两点距离连接起来 |
| 7 | V027 | 由点积和模长求夹角 |
| 8 | V028 | 用坐标判定平行和三点共线 |
| 9 | V029 | 用点积为零判定垂直 |
| 10 | V034 | 将向量和为零读成三角形封闭 |

免费配套：V001, V002, V031, V032, V033。

### 空间平行、垂直到线面角（solid-relations）

按判定与性质成对开放，避免会用性质却没有判定入口，再用垂直投影求线面角。

顺序：G012 → G013 → G014 → G015 → G016 → G017 → G018 → G019 → G021。

| 顺序 | ID | 在路径中的作用与联系 |
| ---: | --- | --- |
| 1 | G012 | 从线线平行建立线面平行 |
| 2 | G013 | 由线面平行提取交线平行 |
| 3 | G014 | 用两相交直线建立面面平行 |
| 4 | G015 | 从面面平行返回截面交线关系 |
| 5 | G016 | 由两相交线的垂直建立线面垂直 |
| 6 | G017 | 用同一平面的垂线得到线线平行 |
| 7 | G018 | 由面内垂线建立面面垂直 |
| 8 | G019 | 从面面垂直提取线面垂直 |
| 9 | G021 | 用垂线段与斜线段之比求线面角 |

免费配套：T007, G050, G025。

### 概率运算到二项分布（probability-binomial）

组合数支持成功位置计数，古典概型、对立、互斥和独立逐步服务于二项分布。

顺序：R014 → R023 → R024 → R005 → R006 → R007。

| 顺序 | ID | 在路径中的作用与联系 |
| ---: | --- | --- |
| 1 | R014 | 提供无序选取成功位置的组合数 |
| 2 | R023 | 以等可能样本计数建立概率 |
| 3 | R024 | 正面难算时转算对立事件 |
| 4 | R005 | 区分互斥并用加法合并事件 |
| 5 | R006 | 区分独立并用乘法求同时发生 |
| 6 | R007 | 把独立重复试验与组合计数合成二项概率 |

免费配套：S001, S017。

### 离散分布的期望与方差（expectation-variance）

从加权平均到线性性质，再比较二项和两点分布的均值与波动；承接上一条概率路径。

顺序：R008 → R009 → R010 → R012 → R029 → R031。

| 顺序 | ID | 在路径中的作用与联系 |
| ---: | --- | --- |
| 1 | R008 | 以取值和概率计算加权平均 |
| 2 | R009 | 用线性性质简化期望计算 |
| 3 | R010 | 从重复试验解释二项期望np |
| 4 | R012 | 建立方差的加权偏差平方定义 |
| 5 | R029 | 成对查询二项分布期望与方差 |
| 6 | R031 | 把二项模型缩到一次试验检验均值与方差 |

免费配套：R007, R033, R030。

### 基本不等式到倒数和最值（amgm-minimum）

将公式、正值条件、定值条件、取等可达性与倒数和应用一同开放，形成完整可用方法。

顺序：I002 → I054 → I049 → I013 → I022 → I050 → I059 → I027。

| 顺序 | ID | 在路径中的作用与联系 |
| ---: | --- | --- |
| 1 | I002 | 掌握基本不等式及常见等价变形 |
| 2 | I054 | 用均值形式理解多元推广和等号 |
| 3 | I049 | 检查正数、定值和取等可达性 |
| 4 | I013 | 用x与倒数的乘积定值求最小值 |
| 5 | I022 | 用和定值求二元倒数和下界 |
| 6 | I050 | 将和为1化为具体最值模型 |
| 7 | I059 | 用正数和与倒数和乘积回验 |
| 8 | I027 | 在互为倒数的组合中复用同一思想 |

免费配套：J029, F011。

### 三角恒等变换到辅助角（trig-transform）

同角关系与诱导先行，经和差角、倍角、降幂，再将线性组合合并成单一三角函数。

顺序：T009 → T020 → T005 → T010 → T006 → T013 → T015。

| 顺序 | ID | 在路径中的作用与联系 |
| ---: | --- | --- |
| 1 | T009 | 建立同角平方关系和商数关系 |
| 2 | T020 | 把同角关系转化为1的代换工具 |
| 3 | T005 | 通过诱导公式统一角与函数名称 |
| 4 | T010 | 把和差角展开到单角 |
| 5 | T006 | 由和角得到倍角变形 |
| 6 | T013 | 用倍角反向完成平方降幂 |
| 7 | T015 | 把正弦余弦线性组合合成为单个函数 |

免费配套：J029, F035。

### 相似判定到A字与8字模型（similarity-models）

先判形状，再用平行截线找对应关系，最后把线段比推广到面积比。

顺序：J008 → J004 → J001 → J002 → J007。

| 顺序 | ID | 在路径中的作用与联系 |
| ---: | --- | --- |
| 1 | J008 | 先掌握相似判定的最少条件 |
| 2 | J004 | 利用平行截线建立比例 |
| 3 | J001 | 在A字模型中识别对应三角形 |
| 4 | J002 | 把对应关系迁移到8字交叉模型 |
| 5 | J007 | 由相似比求面积比 |

免费配套：T034, P035。

### 圆周角到共圆和弦切角（circle-angle）

用圆周角作为角弧关系起点，再正反向判断共圆，最后把切线与弦的角联系起来。

顺序：J009 → P028 → P047 → P052。

| 顺序 | ID | 在路径中的作用与联系 |
| ---: | --- | --- |
| 1 | J009 | 用同弧圆周角建立角度对应 |
| 2 | P028 | 由圆内接四边形得到对角互补 |
| 3 | P047 | 反过来用角度条件判定四点共圆 |
| 4 | P052 | 把切线与弦所成角转回圆周角 |

免费配套：P035, P033。

### 圆方程到直线与圆的位置（circle-coordinate）

标准式读圆心半径，一般式配方还原，再用圆心距判定相交相切相离；点线距作为C类免费配套。

顺序：P019 → P020 → P021。

| 顺序 | ID | 在路径中的作用与联系 |
| ---: | --- | --- |
| 1 | P019 | 建立圆标准式与一般式的对应 |
| 2 | P020 | 从一般式系数快速读圆心半径并检查成圆条件 |
| 3 | P021 | 以圆心距和半径比较判断位置 |

免费配套：P015, J029, J055。

## D. 特色精品二级结论（B 类 45 条）

精品并非“难度最低”的同义词：选入同构脱壳、倒数对称降次、渐近线面积不变量、三切线闭合、反向柯西等；选择依据是结构简化、几何解释、可迁移方法与现有图解入口。未重新渲染或逐页验收它们的 PDF，不将内容筛选审查表述为全库数学/视觉验收。

| ID | 标题 | 入选价值 |
| --- | --- | --- |
| F007 | 一次分式函数值域公式：分离常数法 | 分离常数把一次分式转为平移后的反比例函数，展示结构识别如何替代机械求值域。 |
| F011 | 对勾函数值域公式（基本不等式） | 把对勾函数最值与双曲线两支最短距离连接，展示代数与几何互译。 |
| F012 | 双根号函数值域：几何意义法（距离型） | 将双根号和解释为折线距离，利用线段最短减少求导与平方运算。 |
| F019 | 奇偶单调等价转化：和式与绝对值比较 | 把奇偶性和单调性合用，将函数值比较转化成自变量关系。 |
| F026 | 双对称性推周期：轴轴、点点、轴点三种情形 | 用两次对称复合解释周期，展示从几何变换寻找抽象函数规律。 |
| F076 | 同构脱壳原理（严格单调函数脱壳） | 用严格单调性脱去相同外层函数，将复合方程降为内层比较。 |
| F080 | 倒数对称式与整体换元法 | 用倒数对称的整体换元降低代数次数，并同时展示取值范围约束。 |
| L036 | 等差乘等比前n项和公式 | 用正确的错位相减闭式计算等差乘等比前项和，展示节省重复计算的价值；L001的另一公式存在反例，未入选。 |
| L022 | 一阶线性递推通项公式（不动点法） | 通过减去不动点把线性递推化为等比数列，展示辅助数列构造。 |
| L025 | 分式递推倒数变换化线性 | 分式递推取倒数后化线性，展示用代换将复杂递推降为熟悉模型。 |
| C001 | 椭圆与圆周的距离最值 | 以距离区间统一椭圆与圆周的最近最远距离，展示连续几何模型与分类边界。 |
| C002 | 椭圆上点到直线距离最值公式 | 通过椭圆参数化把点线距离最值化为三角振幅，减少联立计算。 |
| C032 | 阿波罗尼斯圆 | 把定距离比轨迹识别为圆，并用内外分点直径理解圆心半径，展示几何结构。 |
| C033 | 椭圆硬解定理（直线与椭圆联立韦达公式） | 系统整理直线与椭圆联立后的和积、交点存在性和弦长，提供可迁移计算工具。 |
| C047 | 椭圆焦点三角形面积公式 | 用焦点三角形面积连接角度、纵坐标与椭圆参数，展示多个表达的互相校验。 |
| C063 | 圆锥曲线弦长公式 | 把弦长还原为投影直角三角形，再与韦达、判别式连接，形成通用求弦工具。 |
| C078 | 椭圆参数方程 | 从圆伸缩得到椭圆参数方程，把两个坐标压缩为一个角参数。 |
| C088 | 双曲线两渐近线截点三角形面积 | 用底高与坐标乘积解释渐近线截点三角形面积，展示初中工具处理圆锥曲线。 |
| C089 | 双曲线切线与渐近线三角形面积定值 | 切线与渐近线形成面积定值及中点关系，展示无需逐次求面积的结构结论。 |
| C091 | 双曲线渐近线平行四边形面积定值 | 用渐近线方向的平行四边形解释面积不变量，展示多种证明如何对应同一构造。 |
| C096 | 抛物线与特定圆的三切边闭合性质 | 通过第三弦只需和积的结构证明三切线闭合，四种方法的专用图展示解题与阅读价值。 |
| V001 | 极化恒等式 | 以极化恒等式将数量积转换为模长平方差，减少角度与坐标计算。 |
| V002 | 极化恒等式（三角形模型） | 将同一极化思想落在三角形三边上，与V001成套开放便于直接应用。 |
| V008 | 三角形重心向量结论 | 用等权向量和识别重心，连接代数系数与几何中心。 |
| V033 | 坐标三角形面积公式 | 从底高面积和辅助线推出坐标面积，连接向量、三点共线与C088的面积应用。 |
| G025 | 等体积法求点到平面的距离 | 等体积换底求高可避开难作的空间垂线，展示几何降维。 |
| G034 | 等体积法求高 | 与G025同一体积换高思想的基础公式版本同时开放，保证检索入口一致。 |
| G035 | 墙角模型外接球半径公式 | 将三条互相垂直侧棱补成长方体，用体对角线处理外接球。 |
| R030 | 超几何分布的期望公式 | 把无放回抽样期望化为nM/N，图解抽样结构并避免逐项列分布求和。 |
| R032 | 正态分布的3σ原则 | 用正态分布中心区间与面积解释3σ经验区间，展示概率图像的查询价值。 |
| I003 | 糖水不等式 | 用浓度混合解释分式增减的糖水不等式，将比较大小转为直觉模型。 |
| I045 | 穿根法（奇穿偶不穿）解高次不等式 | 将多项式因子的奇偶重数画成穿根规则，减少重复区间代入。 |
| I064 | 反向柯西不等式（二维） | 以完全平方解释反向柯西的平方差结构，开放有难度但可直接迁移的代数技巧。 |
| J032 | 将军饮马模型（对称点法求距离和最小值） | 通过对称点将折线路程变为直线距离，完整展示将军饮马构造。 |
| P004 | 点到圆距离极值统一模型 | 用统一点圆距离模型替代外内圆上三类口诀，展示边界统一处理。 |
| P030 | 三角形重心到三顶点距离平方和最小值 | 用重心给出到三顶点距离平方和的最小值，展示几何中心的优化意义。 |
| P033 | 内心到三边距离相等及内切圆半径公式 | 用三块同高三角形解释内心、面积和切线段关系，展示图形如何承载公式。 |
| P035 | 三角形内角平分线定理 | 把角平分线分段比画成邻边权重，减少辅助线脑补并明确适用条件。 |
| P054 | 曲线轴对称的快速判定法 | 用具体曲线及反射判据寻找对称轴，展示从候选猜测到验证的完整过程。 |
| T034 | 三角形内角平分线定理 | 与P035同一内角平分线定比分段主题同时开放，保留三角与平几的两个入口。 |
| L023 | 一次函数型递推通项公式：等比构造法 | 加入一次辅助项把含n的一阶线性递推化为等比，承接L022展示更深入的构造技巧。 |
| V031 | 定比分点坐标公式 | 用有向分比直接得到分点坐标，并统一内分、外分与中点，减少联立求交计算。 |
| V032 | 平行四边形对角线平方和定理（向量恒等式） | 把向量和差的模平方还原为平行四边形两条对角线，直观连接代数与几何度量。 |
| G030 | 射影面积法求二面角 | 用投影面积之比求二面角余弦的绝对值，将空间作角转为平面面积计算。 |
| J028 | 反比例函数系数k的几何意义 | 反比例函数系数成为矩形或三角形的面积定值，为C088与C091的坐标面积提供直观入口。 |

### 审查发现及范围内处理

以下是筛选时发现的既有内容问题，不由本任务修正。被排除不表示“授权内容可以忽略数学问题”；授权集合只是本轮免费名单之外的剩余 UID，并不是质量认证。后续数学修订应另按单 UID 处理。

| UID | 本次决定 | 发现 |
| --- | --- | --- |
| L001 | 未入选 | 01_statement.tex首个差比求和公式不成立：a_n=n、b_n=2^(n-1)、n=1时右式为2而实际和为1；用L023替代精品名额，正确的L036独立保留。 |
| V005 | 未入选 | 轨迹一概称为圆，未区分lambda+BC²/4为零或负数时的点或空集；用V031替代。 |
| V013 | 未入选 | 一般式m+n=1的必要性需要起点不在终点直线上的条件；A任意时系数可不唯一。用V032替代。 |
| G040 | 未入选 | 补成长方体的条件需确保原顶点共享该长方体外接球，仅可补形的概括不够明确；改选G030的投影面积模型。 |
| J033 | 未入选 | 所写A、B同在动点直线一侧的场景，不能直接保证k·PA等于P到过A所作射线的垂距；改选J028的面积定值模型。 |
| F057 | 未入选 | 把导数两侧恒异号写成一般极值的等价条件需额外限制；F002与F055足以提供正常判定路径，改选F010的端点值域应用。 |
| G052 | 保留免费 | 正式结论式为4/3·pi·R³，core.summary文字却写四分之三；本次仅改isPro，不修正文案。 |

## E. Export 与一致性验证

### 最小修改与原有契约

原正式源已存在 isPro，但当前 KnowledgeNode DTO 遗漏该字段。仅在 `runtime_mapping.py` 增加可选数值字段的原样传递，在 `content_package.py` 共用实体校验中验证显式字段为整数 0 或 1，并限制在 type=knowledge 的节点。模块切片本已原样复制节点，故不改 slicer。Full schemaVersion=2、模块 schemaVersion=4、ID、父子关系、排序、资源 URI 与原有摘要算法保持不变，isPro 自然被现有节点/文件/包 hash 覆盖。

为兼容历史包，旧源/旧包完全没有 isPro 时，原有通用 mapper/validator 仍可读取且不杜撰默认值；本轮生产校验器更严格，源数据和实际导出包的每个 knowledge 节点均必须显式存在合法整数 isPro，缺失、null、Boolean、字符串、浮点或范围外值都会使本轮审计失败。

完整包中的实际位置：`knowledge-nodes.json` 数组内 `type: "knowledge"` 节点的顶层 `isPro`。模块目录及 ZIP 根部的同名 JSON 保留相同位置；manifest、章节节点、分类节点、search-documents 和媒体资源不承载另一套分类标记。

### 实际执行

```powershell
python scripts/zhishu/publish.py init-source
python scripts/zhishu/publish.py build-content
python scripts/zhishu/slice_modules.py --input build/zhishu-content-package --output build/zhishu-module-packages-free-content-20261115-v5 --modules all --package-version 5
python scripts/check_free_knowledge_selection.py --full build/zhishu-content-package --modules build/zhishu-module-packages-free-content-20261115-v5 --baseline .tmp/free-content-selection/before.json --output reports/FREE_CONTENT_EXPORT_VALIDATION.json
python -m unittest discover -s tests -p 'test_zhishu_*.py' -v
python -m unittest tests.test_free_knowledge_selection -v
```

初次受限进程遇到 Python 3.14 / Windows 临时目录 ACL 错误，随后用获准的非受限进程执行相同原命令，没有改写导出逻辑或降低测试要求。Export 还发现 C096 缺少 images 目录；通过原有 init-source 仅创建该空目录，0 个新 PDF 目录，未新增/覆盖任何媒体。

模块包发行序号选 5：检查当前 build 中已有模块包最高 packageVersion 为 4，新包使用更高序号并写独立目录，旧模块包保留。此序号不是 App 发行或部署。

| 检查 | 结果 |
| --- | --- |
| 正式源 UID、类型、唯一性及清单一致性 | PASS：591 = 180 免费 + 411 授权 |
| A/B/C 唯一分类、路径与免费配套 | PASS：{'A': 108, 'B': 45, 'C': 27} |
| 其他 metadata 不变 | PASS：仅 411 个 isPro 数值字符改动 |
| 受保护正文、PDF、图像、动画及其他模块文件 | PASS：6610 个文件逐个 SHA-256 与操作前一致 |
| 完整包知识节点 | PASS：{'total': 591, 'free': 180, 'licensed': 411, 'structural': 485}；结构节点单独计数 |
| 模块 ZIP 的并集 | PASS：14 个包，结论无重复、无遗漏，逐 UID 与源数据一致 |
| 原有包校验 | PASS：Full 校验、每个模块 ZIP 独立及来源一致性校验均通过 |
| 原有 DTO 与关联保持 | PASS：与操作前 mapping 对比，除知识节点新增 isPro 外，节点原字段、关联和搜索记录完全一致 |
| 媒体 | PASS：Full/ZIP 原有资源完整性校验与源资源逐字节 hash 检查，无数学资产修改 |
| 原有 Export 回归测试 | {   "existingExportTests": {     "status": "PASS",     "tests": 147,     "seconds": 335.033,     "execution": "unrestricted process; unchanged test standards"   },   "selectionTests": {     "status": "PASS",     "tests": 6   },   "initialRestrictedRun": "failed due Windows temporary directory ACL; rerun above succeeded" } |
| 新增分类回归测试 | PASS：6 项，涵盖实际 Full→ZIP、非法类型、缺失字段、错误名单、遗漏节点及 hash 变化 |

### 实际导出模块统计

此表按现有知识树章节划包，与 A 节按源目录统计口径不同。

| Export 模块 | 二级结论 | 免费 | 授权 | 结构节点（不计免费） |
| --- | ---: | ---: | ---: | ---: |
| analytic-geometry | 120 | 36 | 84 | 95 |
| functions | 80 | 20 | 60 | 57 |
| inequalities | 64 | 11 | 53 | 34 |
| logic | 10 | 7 | 3 | 17 |
| plane-geometry | 31 | 7 | 24 | 22 |
| prerequisites | 55 | 12 | 43 | 59 |
| probability | 31 | 13 | 18 | 30 |
| sequences | 42 | 15 | 27 | 45 |
| sets | 12 | 9 | 3 | 13 |
| solid-geometry | 58 | 18 | 40 | 42 |
| statistics | 11 | 5 | 6 | 17 |
| triangle-solving | 13 | 4 | 9 | 8 |
| trigonometry | 24 | 7 | 17 | 20 |
| vectors | 40 | 16 | 24 | 39 |

完整包：[manifest](build/zhishu-content-package/manifest.json)。
模块包目录：`build/zhishu-module-packages-free-content-20261115-v5/`，含 14 个标准 ZIP 及其目录内容。

验证证据：[完整机器审计](reports/FREE_CONTENT_EXPORT_VALIDATION.json)、[原有测试日志](reports/FREE_CONTENT_EXPORT_TESTS.txt)、[新增测试日志](reports/FREE_CONTENT_SELECTION_TESTS.txt)。


### 与旧导出快照的区别

重建前的正式完整包实际只有 572 条结论，0 条携带 isPro；它不是当前 591 条正式源的最新快照。旧包遗漏当前源中的 21 个 UID，并残留已不在正式源中的 2 个 UID。因此本次正常重建会刷新到当前正式源，而不是只对旧 ZIP 打补丁。
旧包缺少的当前 UID：C084, C085, C086, C087, C088, C089, C090, C091, C092, C093, C094, C095, C096, F079, F080, G057, G058, P054, P055, V039, V040。
旧包残留的 UID：C025, C026。这些不是本次新增或删除的源结论；本次前后正式源 ID 集合均为 591。
操作前运行时图片镜像也滞后。现有 prepare→mapping 流程从未改动的正式媒体源刷新后，比旧镜像的 mapping 多 227 个 Asset ID、少 1 个已不在源中的 Asset ID，48 个存量资产因新增同 UID 图片而按既有规则更新 sortOrder。共同 Asset ID 的 URI 不变；源媒体逐字节未改。明细见 reports/FREE_CONTENT_EXPORT_REFRESH_DIFF.json。
节点原字段（不含本次新增 isPro）、全部 related 关系及搜索记录与操作前对当前源的 mapping 完全一致。未将这些既有快照滞后问题掩盖为“导出只有 isPro 变化”。

## F. 修改文件列表

除下列生产与校验文件外，仅修改后续列出的 411 份 meta.json 的 isPro；未改 updated_at、title、knowledgeNode、公式或其他 metadata。

- data/content/free-knowledge-selection.json
- scripts/zhishu/runtime_mapping.py
- scripts/zhishu/content_package.py
- scripts/zhishu/README.md
- scripts/check_free_knowledge_selection.py
- tests/test_free_knowledge_selection.py
- FREE_CONTENT_SELECTION_REPORT.md
- reports/FREE_CONTENT_SOURCE_VALIDATION.json
- reports/FREE_CONTENT_EXPORT_VALIDATION.json
- reports/FREE_CONTENT_SELECTION_TESTS.txt
- reports/FREE_CONTENT_EXPORT_TESTS.txt
- reports/FREE_CONTENT_TEST_SUMMARY.json
- reports/FREE_CONTENT_EXPORT_REFRESH_DIFF.json
- reports/FREE_CONTENT_BUILD_LOG.txt
- reports/FREE_CONTENT_MODULE_EXPORT_LOG.json

另外创建 C096 的空 images/ 目录，重新生成 build 下的运行时镜像、完整包和独立模块包；未修改 source、01–06、main.tex、index.tex、数学图源、图片、PDF、动画或任何 App 项目。开始时已有的 C096 内容与 03_conic/index.tex 改动均保留。未执行 Sync、Git commit 或 push。

### 仅改 isPro 的源文件

- `00_set/S006_Inclusion/meta.json`
- `00_set/S011_set_element_conditions/meta.json`
- `00_set/S012_empty_set_subset/meta.json`
- `00_set/S018_connectives_truth_table/meta.json`
- `00_set/S022_implication_equivalence_transitivity/meta.json`
- `00_set/S024_quantifier_extrema_conversion/meta.json`
- `01_function/F003_pade_common_functions/meta.json`
- `01_function/F004_common_taylor_approximations/meta.json`
- `01_function/F005_lhopital_rule_zero_zero/meta.json`
- `01_function/F006_abstract_function_domain_transfer/meta.json`
- `01_function/F008_quadratic_rational_discriminant_range/meta.json`
- `01_function/F009_radical_range_substitution/meta.json`
- `01_function/F013_composition_monotonicity_same_diff/meta.json`
- `01_function/F014_piecewise_monotone_condition/meta.json`
- `01_function/F015_even_odd_domain_symmetry/meta.json`
- `01_function/F016_odd_function_zero_at_origin/meta.json`
- `01_function/F017_parity_arithmetic/meta.json`
- `01_function/F018_composite_parity_rule/meta.json`
- `01_function/F020_function_axis_symmetry_condition/meta.json`
- `01_function/F021_point_symmetry_criterion/meta.json`
- `01_function/F022_function_period_formulas/meta.json`
- `01_function/F023_period_symmetric_condition/meta.json`
- `01_function/F024_period_opposite_sign/meta.json`
- `01_function/F025_reciprocal_period_condition/meta.json`
- `01_function/F027_parity_symmetry_period/meta.json`
- `01_function/F028_period_symmetry_chain/meta.json`
- `01_function/F029_quadratic_three_forms/meta.json`
- `01_function/F030_quadratic_interval_extrema/meta.json`
- `01_function/F031_quadratic_moving_axis_extrema/meta.json`
- `01_function/F032_quadratic_interval_extrema/meta.json`
- `01_function/F033_quadratic_positive_condition/meta.json`
- `01_function/F034_quadratic_root_distribution_criterion/meta.json`
- `01_function/F038_exponential_function_properties/meta.json`
- `01_function/F039_log_function_monotonicity_sign/meta.json`
- `01_function/F040_power_function_graph_features/meta.json`
- `01_function/F041_exp_power_log_growth_comparison/meta.json`
- `01_function/F042_logarithm_sign_rule/meta.json`
- `01_function/F043_horizontal_shift/meta.json`
- `01_function/F044_function_vertical_translation/meta.json`
- `01_function/F045_horizontal_scale_transform/meta.json`
- `01_function/F046_absolute_value_reflection/meta.json`
- `01_function/F047_absolute_value_reflection_even/meta.json`
- `01_function/F048_function_graph_symmetry_transform/meta.json`
- `01_function/F053_monotonicity_five_types/meta.json`
- `01_function/F057_extreme_point_sign_change_count/meta.json`
- `01_function/F058_cubic_discriminant_monotonicity/meta.json`
- `01_function/F059_cubic_symmetry_center/meta.json`
- `01_function/F060_cubic_zero_count_discriminant/meta.json`
- `01_function/F061_parameter_separation_max_min/meta.json`
- `01_function/F062_sign_varying_coefficient_classification/meta.json`
- `01_function/F063_existence_max_min_equivalence/meta.json`
- `01_function/F064_forall_exists_min_max_equivalence/meta.json`
- `01_function/F065_tangent_inequalities/meta.json`
- `01_function/F066_xf_construction_monotonicity/meta.json`
- `01_function/F067_f_over_x_monotonicity/meta.json`
- `01_function/F068_exponential_factor_monotonicity/meta.json`
- `01_function/F069_exponential_auxiliary_monotonicity/meta.json`
- `01_function/F070_exp_log_equivalence/meta.json`
- `01_function/F071_extreme_shift_log_mean/meta.json`
- `01_function/F072_homogeneous_substitution_ratio/meta.json`
- `01_function/F073_lhopital_endpoint/meta.json`
- `01_function/F074_parameter_inequality_necessary_condition/meta.json`
- `01_function/F075_exp_log_tangent_bounds/meta.json`
- `01_function/F077_exp_log_tangent_inequality/meta.json`
- `01_function/F078_continuous_monotonic_unique_zero/meta.json`
- `01_function/F079_rational_root_theorem_trial_factorization/meta.json`
- `02_sequence/L001_arithmetic_geometric_sum/meta.json`
- `02_sequence/L004_arithmetic_index_sum_equality/meta.json`
- `02_sequence/L005_geometric_index_sum_product/meta.json`
- `02_sequence/L009_arithmetic_mean_middle_term/meta.json`
- `02_sequence/L010_geometric_mean_square_equality/meta.json`
- `02_sequence/L011_arithmetic_sequence_term_relation/meta.json`
- `02_sequence/L012_geometric_terms_relation/meta.json`
- `02_sequence/L013_arithmetic_sum_quadratic/meta.json`
- `02_sequence/L014_ap_sum_extremum_sign/meta.json`
- `02_sequence/L015_arithmetic_progression_equidistant_segment_sum/meta.json`
- `02_sequence/L016_geometric_sequence_segment_sums/meta.json`
- `02_sequence/L017_arithmetic_mean_sequence/meta.json`
- `02_sequence/L018_geometric_series_partial_sum_ratio/meta.json`
- `02_sequence/L020_general_term_accumulation/meta.json`
- `02_sequence/L021_sequence_product_formula/meta.json`
- `02_sequence/L024_divide_power_construction/meta.json`
- `02_sequence/L026_second_order_linear_recurrence_characteristic_root/meta.json`
- `02_sequence/L027_fixed_point_fractional_recurrence/meta.json`
- `02_sequence/L028_alternating_recurrence_odd_even_terms/meta.json`
- `02_sequence/L029_sequence_induction_formula/meta.json`
- `02_sequence/L030_auxiliary_sequence_construction/meta.json`
- `02_sequence/L031_arithmetic_geometric_sum_formulas/meta.json`
- `02_sequence/L034_log_telescoping/meta.json`
- `02_sequence/L039_sequence_difference_ratio_monotonicity/meta.json`
- `02_sequence/L040_recurrence_periods/meta.json`
- `02_sequence/L041_arithmetic_series_max_sum_condition/meta.json`
- `02_sequence/L042_sequence_scaling_methods/meta.json`
- `03_conic/C003_Ellipse_Max_Focal_Angle/meta.json`
- `03_conic/C004_Ellipse_Max_Vertex_Angle/meta.json`
- `03_conic/C005_Ellipse_Eccentricity_Focal_Angle_Inequality/meta.json`
- `03_conic/C006_Ellipse_Eccentricity_Focal_Angle_Formula/meta.json`
- `03_conic/C007_Ellipse_Slope_Tangent_Condition/meta.json`
- `03_conic/C008_Ellipse_Tangent_Point_Formula/meta.json`
- `03_conic/C009_Ellipse_Tangent_Slope_Range/meta.json`
- `03_conic/C010_Ellipse_Tangent_Distance_Formula/meta.json`
- `03_conic/C011_Ellipse_Tangent_Slope_Product/meta.json`
- `03_conic/C012_Ellipse_Tangent_Origin_Distance/meta.json`
- `03_conic/C013_Ellipse_Endpoint_Tangent_Intersection/meta.json`
- `03_conic/C014_Ellipse_Focal_Tangent_Properties/meta.json`
- `03_conic/C015_Ellipse_Focus_Triangle_Centers/meta.json`
- `03_conic/C016_Hyperbola_Focus_Triangle_Centers/meta.json`
- `03_conic/C017_ellipse_tangent_condition/meta.json`
- `03_conic/C018_ellipse_tangent_equation/meta.json`
- `03_conic/C019_ellipse_slope_product_constant/meta.json`
- `03_conic/C020_ellipse_tangent_distance_product/meta.json`
- `03_conic/C021_ellipse_tangent_distance_focal_radius_product/meta.json`
- `03_conic/C022_ellipse_endpoint_tangent_intersection/meta.json`
- `03_conic/C023_ellipse_area_formula/meta.json`
- `03_conic/C024_ellipse_perimeter_ramanujan/meta.json`
- `03_conic/C031_point_line_symmetry_factor/meta.json`
- `03_conic/C034_line_hyperbola_direct_vieta/meta.json`
- `03_conic/C035_parabola_vieta_fixed_form/meta.json`
- `03_conic/C037_hyperbola_first_definition/meta.json`
- `03_conic/C040_hyperbola_focus_directrix_ratio/meta.json`
- `03_conic/C043_hyperbola_abc_relation/meta.json`
- `03_conic/C046_conic_latus_rectum_length/meta.json`
- `03_conic/C048_hyperbola_focus_triangle_area/meta.json`
- `03_conic/C050_hyperbola_focal_radius/meta.json`
- `03_conic/C056_ellipse_focal_chord_ratio/meta.json`
- `03_conic/C057_hyperbola_focus_chord_reciprocal_sum_diff/meta.json`
- `03_conic/C059_midpoint_chord_slope/meta.json`
- `03_conic/C060_ellipse_midpoint_chord_slope/meta.json`
- `03_conic/C061_hyperbola_midpoint_chord_slope/meta.json`
- `03_conic/C062_parabola_midpoint_chord_slope/meta.json`
- `03_conic/C064_ellipse_slope_product_constant/meta.json`
- `03_conic/C065_hyperbola_slope_product_constant/meta.json`
- `03_conic/C066_hyperbola_tangent_half_substitution/meta.json`
- `03_conic/C068_ellipse_contact_chord/meta.json`
- `03_conic/C069_hyperbola_chord_of_contact/meta.json`
- `03_conic/C070_parabola_contact_chord/meta.json`
- `03_conic/C071_ellipse_monge_circle/meta.json`
- `03_conic/C072_parabola_archimedean_triangle_vertex_area/meta.json`
- `03_conic/C073_parabola_tangent_intersection_midpoint_parallel/meta.json`
- `03_conic/C074_conic_optical_angle_bisector/meta.json`
- `03_conic/C075_polar_line_equation/meta.json`
- `03_conic/C076_pole_polar_conjugacy/meta.json`
- `03_conic/C077_pole_polar_principle/meta.json`
- `03_conic/C079_hyperbola_asymptote_parallel_unique/meta.json`
- `03_conic/C080_confocal_conic_family/meta.json`
- `03_conic/C081_affine_ellipse_area_slope/meta.json`
- `03_conic/C082_confocal_conic_family/meta.json`
- `03_conic/C083_external_point_to_ellipse_distance_extrema/meta.json`
- `03_conic/C084_hyperbola_focal_triangle_internal_angle_bisector/meta.json`
- `03_conic/C085_hyperbola_focal_parallel_asymptote_segment_ratio/meta.json`
- `03_conic/C086_hyperbola_focal_distance_ratio_eccentricity_range/meta.json`
- `03_conic/C087_hyperbola_focal_chord_length_range/meta.json`
- `03_conic/C090_confocal_ellipse_hyperbola_focal_angle_relation/meta.json`
- `03_conic/C092_confocal_ellipse_hyperbola_orthogonality/meta.json`
- `03_conic/C093_confocal_ellipse_hyperbola_intersection_focal_distances/meta.json`
- `03_conic/C094_confocal_ellipse_hyperbola_four_intersections/meta.json`
- `03_conic/C095_hyperbola_symmetric_secants_reflected_tangent_parallel/meta.json`
- `04_vector/V003_Polarization_Identity_rectangle/meta.json`
- `04_vector/V004_Polarization_Identity_rectangle_three_dimensional/meta.json`
- `04_vector/V005_Polarization_Identity_vector_product/meta.json`
- `04_vector/V006_Mercedes_Theorem/meta.json`
- `04_vector/V007_Mercedes_Theorem_Corollary/meta.json`
- `04_vector/V009_Incenter/meta.json`
- `04_vector/V010_Excenter/meta.json`
- `04_vector/V011_Circumcenter/meta.json`
- `04_vector/V012_Equal_Sum_Line/meta.json`
- `04_vector/V013_Claw/meta.json`
- `04_vector/V014_Dot_Product_Side_Formula/meta.json`
- `04_vector/V015_Hamilton/meta.json`
- `04_vector/V016_Euler_Line_Four_Points/meta.json`
- `04_vector/V017_Nine_point_Circle/meta.json`
- `04_vector/V018_Orthocenter_Properties/meta.json`
- `04_vector/V019_Orthocenter/meta.json`
- `04_vector/V020_projection_scalar_vector/meta.json`
- `04_vector/V030_unit_vector_normalization/meta.json`
- `04_vector/V035_point_line_distance_vector/meta.json`
- `04_vector/V036_vector_triangle_shape_detection/meta.json`
- `04_vector/V037_vector_cauchy_schwarz/meta.json`
- `04_vector/V038_vector_triangle_inequality/meta.json`
- `04_vector/V039_perpendicular_equal_segments_rotation_coordinates/meta.json`
- `04_vector/V040_rotation_about_arbitrary_center_coordinates/meta.json`
- `05_geometry-solid/G002_sphere_ratio_surface_volume/meta.json`
- `05_geometry-solid/G003_pyramid_circumsphere_center_altitude/meta.json`
- `05_geometry-solid/G004_spheroid_surface_area/meta.json`
- `05_geometry-solid/G005_cuboid_circumsphere_radius/meta.json`
- `05_geometry-solid/G006_cube_circumsphere_radius/meta.json`
- `05_geometry-solid/G007_right_prism_circumsphere_radius/meta.json`
- `05_geometry-solid/G008_regular_triangular_prism_circumradius/meta.json`
- `05_geometry-solid/G009_regular_pyramid_circumradius/meta.json`
- `05_geometry-solid/G010_regular_tetrahedron_circumradius/meta.json`
- `05_geometry-solid/G011_cone_circumradius/meta.json`
- `05_geometry-solid/G020_three_perpendiculars/meta.json`
- `05_geometry-solid/G022_parallel_transfer_chain/meta.json`
- `05_geometry-solid/G023_perpendicular_conversion_chain/meta.json`
- `05_geometry-solid/G024_point_plane_distance_vector/meta.json`
- `05_geometry-solid/G026_skew_lines_angle_cosine/meta.json`
- `05_geometry-solid/G027_line_plane_angle_vector/meta.json`
- `05_geometry-solid/G028_dihedral_angle_definition/meta.json`
- `05_geometry-solid/G029_dihedral_angle_normal_cosine/meta.json`
- `05_geometry-solid/G031_three_cosine_rule/meta.json`
- `05_geometry-solid/G032_skew_lines_distance_cross_product/meta.json`
- `05_geometry-solid/G033_parallel_case_point_plane_distance/meta.json`
- `05_geometry-solid/G036_disphenoid_cuboid_volume_radius/meta.json`
- `05_geometry-solid/G037_pyramid_perpendicular_edge_circumradius/meta.json`
- `05_geometry-solid/G038_right_prism_circumsphere_radius/meta.json`
- `05_geometry-solid/G039_regular_tetrahedron_height/meta.json`
- `05_geometry-solid/G040_cuboid_supplement_circumradius/meta.json`
- `05_geometry-solid/G041_polyhedra_circumsphere_diameter/meta.json`
- `05_geometry-solid/G042_cube_sphere_radii/meta.json`
- `05_geometry-solid/G043_regular_tetrahedron_height_insphere_ratio/meta.json`
- `05_geometry-solid/G044_inscribed_sphere_radius_formula/meta.json`
- `05_geometry-solid/G046_spherical_distance/meta.json`
- `05_geometry-solid/G047_right_cone_inscribed_radius/meta.json`
- `05_geometry-solid/G048_cylinder_inscribed_sphere_condition/meta.json`
- `05_geometry-solid/G051_frustum_volume/meta.json`
- `05_geometry-solid/G053_cavalieri_principle/meta.json`
- `05_geometry-solid/G054_edge_plane_intersection_parameter/meta.json`
- `05_geometry-solid/G055_cube_section_polygon_range_acute_triangle/meta.json`
- `05_geometry-solid/G056_tetrahedron_volume_scalar_triple/meta.json`
- `05_geometry-solid/G057_ellipsoid_volume_revolution/meta.json`
- `05_geometry-solid/G058_ellipse_y_rotation_volume/meta.json`
- `06_probability-stat/R001_permutation_recurrence/meta.json`
- `06_probability-stat/R002_permutation_recurrence/meta.json`
- `06_probability-stat/R003_permutation_recurrence/meta.json`
- `06_probability-stat/R004_permutation_recurrence/meta.json`
- `06_probability-stat/R011_geometric_distribution_mean/meta.json`
- `06_probability-stat/R013_permutation_formula/meta.json`
- `06_probability-stat/R015_binomial_symmetry/meta.json`
- `06_probability-stat/R016_pascal_identity/meta.json`
- `06_probability-stat/R017_binding_insertion_partition_exclusion/meta.json`
- `06_probability-stat/R018_binomial_general_term/meta.json`
- `06_probability-stat/R019_binomial_coefficient_sum/meta.json`
- `06_probability-stat/R020_binomial_even_odd_sum_equal/meta.json`
- `06_probability-stat/R021_binomial_coefficient_max_term/meta.json`
- `06_probability-stat/R022_binomial_recurrence_symmetry/meta.json`
- `06_probability-stat/R025_conditional_probability_definition/meta.json`
- `06_probability-stat/R026_probability_multiplication_rule/meta.json`
- `06_probability-stat/R027_total_probability_formula/meta.json`
- `06_probability-stat/R028_bayes_formula/meta.json`
- `06_probability-stat/R036_percentile_ceiling/meta.json`
- `06_probability-stat/R038_least_squares_regression/meta.json`
- `06_probability-stat/R039_regression_line_through_centroid/meta.json`
- `06_probability-stat/R040_pearson_r_range/meta.json`
- `06_probability-stat/R041_chi_square_independence_test/meta.json`
- `06_probability-stat/R042_chi_square_independence_test/meta.json`
- `07_inequality/I001_Compound_Inequality_Transformation/meta.json`
- `07_inequality/I004_Cubic_Mean_Inequality/meta.json`
- `07_inequality/I005_Cauchy_Schwarz_Inequality/meta.json`
- `07_inequality/I006_Weighted_Power_Sum_Inequality/meta.json`
- `07_inequality/I007_Triangle_Inequality/meta.json`
- `07_inequality/I008_Mean_Inequality_Chain/meta.json`
- `07_inequality/I009_Arithmetic_Geometric_Mean_Three/meta.json`
- `07_inequality/I010_Three_Square_Sum_Inequality/meta.json`
- `07_inequality/I011_Logarithmic_Linear_Inequality/meta.json`
- `07_inequality/I012_Exponential_Linear_Inequality/meta.json`
- `07_inequality/I014_Jensens_Inequality/meta.json`
- `07_inequality/I015_Exponential_Convexity_Inequality/meta.json`
- `07_inequality/I016_General_Exponential_Convexity/meta.json`
- `07_inequality/I017_Sine_Concavity_Inequality/meta.json`
- `07_inequality/I018_Cosine_Concavity_Inequality/meta.json`
- `07_inequality/I019_Tangent_Convexity_Inequality/meta.json`
- `07_inequality/I020_Logarithmic_Concavity_Inequality/meta.json`
- `07_inequality/I021_Power_Convexity_Inequality/meta.json`
- `07_inequality/I023_Entropy_Log_Convexity/meta.json`
- `07_inequality/I024_inequality/meta.json`
- `07_inequality/I025_inequality/meta.json`
- `07_inequality/I026_Three_Variable_Square_Chain/meta.json`
- `07_inequality/I028_Schur_Inequality/meta.json`
- `07_inequality/I029_Reciprocal_Sum_Inequality/meta.json`
- `07_inequality/I030_Bernoulli_Inequality/meta.json`
- `07_inequality/I031_Sin_X_Inequality/meta.json`
- `07_inequality/I032_Tan_X_Inequality/meta.json`
- `07_inequality/I033_Cos_X_Quadratic_Bound/meta.json`
- `07_inequality/I034_Sin_Tan_Combined_Inequality/meta.json`
- `07_inequality/I035_Logarithmic_Mean_Inequality/meta.json`
- `07_inequality/I036_Exp_Quadratic_Bound/meta.json`
- `07_inequality/I037_Ln_Quadratic_Bound/meta.json`
- `07_inequality/I038_Ln_Rational_Lower_Bound/meta.json`
- `07_inequality/I039_Jordan_Inequality_Basic/meta.json`
- `07_inequality/I040_Rational_Symmetric_Inequality/meta.json`
- `07_inequality/I041_Triple_Sum_Inverse_Product/meta.json`
- `07_inequality/I042_Andreescu_Symmetric_Rational/meta.json`
- `07_inequality/I043_quadratic_inequality_solution/meta.json`
- `07_inequality/I044_fractional_inequality_equivalence/meta.json`
- `07_inequality/I046_absolute_value_inequality_equivalence/meta.json`
- `07_inequality/I047_abs_sum_min_diff_max/meta.json`
- `07_inequality/I048_linear_inequality_solution_cases/meta.json`
- `07_inequality/I051_am_gm_splitting_minimum/meta.json`
- `07_inequality/I052_param_separation_extremum/meta.json`
- `07_inequality/I053_cauchy_equality_condition/meta.json`
- `07_inequality/I055_rearrangement_inequality/meta.json`
- `07_inequality/I056_fraction_substitution_identity/meta.json`
- `07_inequality/I057_jensen_equality_condition/meta.json`
- `07_inequality/I058_cauchy_schwarz_2d/meta.json`
- `07_inequality/I060_inequality_proof_methods/meta.json`
- `07_inequality/I061_sqrt_sum_maximum/meta.json`
- `07_inequality/I062_linear_programming_vertex_optimum/meta.json`
- `07_inequality/I063_log_sugar_water_inequality/meta.json`
- `08_trigonometry/T001_triangle_sine_square_identity/meta.json`
- `08_trigonometry/T002_cosine_square_sum_identity/meta.json`
- `08_trigonometry/T003_triangle_tangent_sum_product/meta.json`
- `08_trigonometry/T004_sine_squared_difference/meta.json`
- `08_trigonometry/T011_triple_angle_formula/meta.json`
- `08_trigonometry/T012_half_angle_formulas/meta.json`
- `08_trigonometry/T014_tan_half_angle_rational/meta.json`
- `08_trigonometry/T016_sum_to_product_formulas/meta.json`
- `08_trigonometry/T017_homogeneous_trig_to_tan/meta.json`
- `08_trigonometry/T018_sin_cos_sum_product_conversion/meta.json`
- `08_trigonometry/T019_triangle_angle_induction/meta.json`
- `08_trigonometry/T021_sine_transform_shift_order/meta.json`
- `08_trigonometry/T022_sinusoidal_period_monotone/meta.json`
- `08_trigonometry/T023_sine_symmetry_axis_center/meta.json`
- `08_trigonometry/T024_sine_interval_max_min_substitution/meta.json`
- `08_trigonometry/T025_trig_fundamentals/meta.json`
- `08_trigonometry/T028_side_angle_sine_equivalence/meta.json`
- `08_trigonometry/T029_angle_type_by_side_squares/meta.json`
- `08_trigonometry/T030_triangle_projection_theorem/meta.json`
- `08_trigonometry/T031_triangle_area_sas/meta.json`
- `08_trigonometry/T032_triangle_area_incircle_radius/meta.json`
- `08_trigonometry/T033_triangle_area_circumradius/meta.json`
- `08_trigonometry/T035_triangle_median_formula/meta.json`
- `08_trigonometry/T036_ssa_solution_count/meta.json`
- `08_trigonometry/T037_heron_formula/meta.json`
- `08_trigonometry/T038_acos_equals_bcos_triangle_shape/meta.json`
- `08_trigonometry/T039_chebyshev_first_kind/meta.json`
- `09_geometry-plane/P001_distance-extreme-from-external-point/meta.json`
- `09_geometry-plane/P002_distance-extreme-from-internal-point/meta.json`
- `09_geometry-plane/P003_distance-extreme-from-point-on-circle/meta.json`
- `09_geometry-plane/P005_distance-extreme-between-line-and-circle/meta.json`
- `09_geometry-plane/P006_distance-extreme-between-two-circles/meta.json`
- `09_geometry-plane/P007_pqr_area_symmetric/meta.json`
- `09_geometry-plane/P008_right_triangle_hypotenuse_median/meta.json`
- `09_geometry-plane/P009_pythagorean_theorem/meta.json`
- `09_geometry-plane/P010_triangle_projection_sum/meta.json`
- `09_geometry-plane/P011_line_equation_forms/meta.json`
- `09_geometry-plane/P012_slope_parallel_perp_condition/meta.json`
- `09_geometry-plane/P013_parallel_lines_general_form/meta.json`
- `09_geometry-plane/P014_lines_perpendicular_dot_zero/meta.json`
- `09_geometry-plane/P016_parallel_lines_distance_formula/meta.json`
- `09_geometry-plane/P017_line_pencil_intersection/meta.json`
- `09_geometry-plane/P018_point_line_symmetry_coordinate/meta.json`
- `09_geometry-plane/P022_circle_chord_length_formula/meta.json`
- `09_geometry-plane/P023_circle_family_linear_combination/meta.json`
- `09_geometry-plane/P024_circles_relative_position/meta.json`
- `09_geometry-plane/P025_circle_tangent_at_point/meta.json`
- `09_geometry-plane/P026_tangent_length_equality/meta.json`
- `09_geometry-plane/P027_circle_diameter_form/meta.json`
- `09_geometry-plane/P029_centroid_median_2_1/meta.json`
- `09_geometry-plane/P031_circumcenter_sine_law/meta.json`
- `09_geometry-plane/P032_orthocenter_perpendicular/meta.json`
- `09_geometry-plane/P034_euler_line_ratio/meta.json`
- `09_geometry-plane/P036_external_angle_bisector_ratio/meta.json`
- `09_geometry-plane/P037_median_length_formula/meta.json`
- `09_geometry-plane/P038_stewart_cevian_length/meta.json`
- `09_geometry-plane/P039_menelaus_theorem/meta.json`
- `09_geometry-plane/P040_ceva_concurrency/meta.json`
- `09_geometry-plane/P041_ptolemy_identity/meta.json`
- `09_geometry-plane/P042_cevian_sine_relation/meta.json`
- `09_geometry-plane/P043_triangle_area_sas/meta.json`
- `09_geometry-plane/P044_incircle_area_semiperimeter_radius/meta.json`
- `09_geometry-plane/P045_triangle_area_circumradius_formula/meta.json`
- `09_geometry-plane/P046_heron_formula/meta.json`
- `09_geometry-plane/P048_intersecting_chords/meta.json`
- `09_geometry-plane/P049_secant_secant_product/meta.json`
- `09_geometry-plane/P050_tangent_secant_power/meta.json`
- `09_geometry-plane/P051_power_of_point/meta.json`
- `09_geometry-plane/P053_intersecting_circles_common_chord_line/meta.json`
- `09_geometry-plane/P055_line_reflection_slope_transform/meta.json`
- `10_junior_basics/J003_right_triangle_altitude_projection/meta.json`
- `10_junior_basics/J005_three_equal_angles_similarity/meta.json`
- `10_junior_basics/J006_pythagorean_tiling/meta.json`
- `10_junior_basics/J010_arc_angle_equivalence/meta.json`
- `10_junior_basics/J011_angle_in_semicircle/meta.json`
- `10_junior_basics/J012_central_angle_arc_measure/meta.json`
- `10_junior_basics/J013_tangent_chord_angle/meta.json`
- `10_junior_basics/J014_cyclic_quad_opposite_angles_supplementary/meta.json`
- `10_junior_basics/J015_cyclic_quadrilateral_supplementary_angles/meta.json`
- `10_junior_basics/J016_tangent_perpendicular_radius/meta.json`
- `10_junior_basics/J017_circle_tangent_perpendicular/meta.json`
- `10_junior_basics/J018_intersecting_chords_product/meta.json`
- `10_junior_basics/J019_tangent_lengths_equal/meta.json`
- `10_junior_basics/J020_intersecting_secants_product/meta.json`
- `10_junior_basics/J021_tangent_secant_square/meta.json`
- `10_junior_basics/J022_diameter_perpendicular_chord/meta.json`
- `10_junior_basics/J024_quadratic_interval_extrema_classification/meta.json`
- `10_junior_basics/J025_quadratic_area_extremum_vertex/meta.json`
- `10_junior_basics/J026_quadratic_linear_intersection_discriminant/meta.json`
- `10_junior_basics/J027_linear_function_slope_intercept/meta.json`
- `10_junior_basics/J030_point_reflection_perpendicular_bisector/meta.json`
- `10_junior_basics/J031_rotation_congruence/meta.json`
- `10_junior_basics/J033_weighted_distance_minimum/meta.json`
- `10_junior_basics/J034_apollonius_circle/meta.json`
- `10_junior_basics/J035_rotation_scaling_locus/meta.json`
- `10_junior_basics/J036_fermat_point_min_distance/meta.json`
- `10_junior_basics/J037_bridge_crossing_translation/meta.json`
- `10_junior_basics/J038_isosceles_rotation_congruence/meta.json`
- `10_junior_basics/J039_median_extension/meta.json`
- `10_junior_basics/J040_cut_extend_construction/meta.json`
- `10_junior_basics/J041_square_half_angle_segment_sum/meta.json`
- `10_junior_basics/J042_cyclic_quadrilateral_rotation_congruence/meta.json`
- `10_junior_basics/J043_equilateral_triangle_rotation_relation/meta.json`
- `10_junior_basics/J044_angle_bisector_auxiliary_models/meta.json`
- `10_junior_basics/J045_triangle_midpoint_median_centroid/meta.json`
- `10_junior_basics/J046_isosceles_existence_two_circles_one_line/meta.json`
- `10_junior_basics/J047_right_triangle_two_lines_circle/meta.json`
- `10_junior_basics/J048_parallelogram_opposite_vertex_sum/meta.json`
- `10_junior_basics/J049_triangle_similarity_proportion_cases/meta.json`
- `10_junior_basics/J050_area_bisection_centroid/meta.json`
- `10_junior_basics/J051_special_product_formulas/meta.json`
- `10_junior_basics/J052_monic_quadratic_cross_factor/meta.json`
- `10_junior_basics/J054_nonnegative_sum_zero_all_zero/meta.json`

本次分类与 Export 工作完成；D 节列明的既有数学内容问题仍待另行处理，不在本任务中擅自修正。
