# 重心与内心补充动态图

数学事实源为 V009 六段 TeX 与 meta.json，重点为 explanation 的重心比较、examples 例5与 summary 的系数比较；不修改正式知识源。

分镜：一般三角形同时画橙色中线、绿色角平分线、内切圆与 G、I。固定 B、C，移动 A 到等边位置，G、I 按公式逐帧重算并重合；再移动 A 到直角位置，显示直角标记与分开的 G、I。最后固定三角形，计算点 P 从 G 沿 GI 移到 I，明确 G、I 不动，然后回到开场。

G=(A+B+C)/3；I=(aA+bB+cC)/(a+b+c)。设归一化内心权重为 w=(a,b,c)/(a+b+c)，P 的权重为 (1-t)(1,1,1)/3+t w，因此 P=(1-t)G+tI。此为计算权重的连续改变，不把中间 P 称为重心或内心。

B=(-2.6,-0.7)，C=(2.6,-0.7)；一般 A=(-1.5,3.8)，等边 A=(0,-0.7+2.6√3)，直角 A=(-2.6,3.2)。直角状态是 6-8-10 三角形的等比例缩放与平移，G=(-2.6/3,0.6)，I=(-1.3,0.6)。所有绘图使用同一比例尺。

重合判定：非退化三角形的重心归一化权重唯一且均为 1/3，内心归一化权重为 a:b:c，因此 G=I 当且仅当 a=b=c。

运行 `python -B 04_vector/V009_Incenter/manim/test_centers.py`：2 项测试，涵盖三段形变各121个状态，核对中线分点、内切圆三边等距、正权重、P 的线性轨迹，以及等边和直角的精确状态。

构建入口：`scripts/manim/render.ps1 -Uid V009 -Scene V009CentroidIncenter -SceneFile scene_centers.py -Name centroid_incenter`。使用冻结 export_gif 工具，在关键帧审核后以新文件名 centroid_incenter.gif 显式写入 images，不覆盖原 incenter.gif。
