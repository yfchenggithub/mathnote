# 全局说明 & 使用约定

highschool-math-notes/
│
├─ main.tex % 总入口（编译这个）
├─ preamble.tex % 宏包、环境、自定义命令
├─ settings.tex % 版式、页眉页脚、定理编号
│
├─ assets/ % 全局资源
│ ├─ figures/ % 通用图片
│ ├─ tables/ % 通用表格
│ └─ fonts/ % 若将来用到自定义字体
│
├─ function/ % 函数
│ ├─ F01_monotonicity/
│ ├─ F02_extrema/
│ ├─ F03_zero-points/
│ └─ index.tex % 函数模块目录入口
│
├─ sequence/ % 数列与不等式
│ ├─ S01_arithmetic-seq/
│ ├─ S02_geometric-seq/
│ ├─ I01-basic-inequality/
│ └─ index.tex
│
├─ conic/ % 圆锥曲线
│ ├─ C01-ellipse-definition/
│ ├─ C02-hyperbola-focus/
│ └─ index.tex
│
├─ geometry-plane/ % 平面几何与三角函数
│ ├─ G01-triangle-sine-law/
│ ├─ G02-cosine-law/
│ └─ index.tex
│
├─ geometry-solid/ % 立体几何
│ ├─ SG01-line-plane-angle/
│ ├─ SG02-volume-model/
│ └─ index.tex
│
├─ probability-stat/ % 概率与统计
│ ├─ P01-classical-prob/
│ ├─ P02-conditional-prob/
│ └─ index.tex
│
├─ templates/ % 模板（非常重要）
│ ├─ theorem.tex % 定理环境模板
│ ├─ example.tex
│ └─ fxx-template.tex % 二级结论标准模板
│
└─ build/ % 编译输出（git 忽略）

结论编号-结论名/
├─ statement.tex # 结论表述（可直接背）
├─ explanation.tex # 直观解释（讲给学生听）
├─ proof.tex # 严谨证明（你自己用）
├─ examples.tex # 典型例题（1–3 题）
├─ traps.tex # 易错点 / 反例
└─ summary.tex # 一句话总结（考试用）

assets/
└─ figures/
├─ geo/ # 平面 / 立体几何通用图
├─ plots/ # 函数图、导数图
└─ stats/ # 概率统计示意图
适合放什么？
正方体、长方体、常规圆锥曲线
标准函数图像
会被多个结论反复引用的图

② 二级结论私有图（只给它自己用）
F01-单调性判定定理/
└─ figures/
├─ mono-example1.tikz
└─ mono-counterexample.png
