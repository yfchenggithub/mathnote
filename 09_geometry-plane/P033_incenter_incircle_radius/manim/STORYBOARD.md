# P033 动画分镜与数学来源

事实源：当前 UID 的 01—06 六段 TeX 与 meta.json。只读；不反写正文或元数据。
独立模型在 model.py，场景在 scene.py，数学测试在 test_model.py。

## 1. P033IncenterArea / P033_incenter_area.gif

以正式例题的 13、14、15 三角形起步，A=(9,12)，B=(0,0)，C=(14,0)，
由边长加权计算 I=(8,4)，垂足用正交投影计算，r=4。
逐条作垂线，画内切圆；A 连续运动一周返回原位时，实时重算内心、垂足与圆。
三条垂线始终等长。固定图形后，依次填充 IBC、ICA、IAB，显示各块同高，
将面积合并为 S=r(a+b+c)/2=rp，再读出面积比 a:b:c。
运动不是对既有图形做不等比缩放，圆与切点全程由数学模型决定。

## 2. P033TangentLengths / P033_tangent_lengths.gif

同一组三边，保留 D、E、F 切点，与正文统一：x=AE=AF，y=BF=BD，z=CD=CE。
从 A、B、C 依次描出两条等长切线段，同色同字母，不能仅凭颜色识别。
沿边读出 y+z=a、x+z=b、x+y=c；相加得 x+y+z=p，分别减去对边得 x=p-a 等。
最后将图中 x、y、z 换成 7、8、6，以三边和回验。末尾退回原始图形形成循环。

## 3. P033SpecialTriangles / P033_special_triangles.gif

三个状态分别重建真实几何模型，不把三种半径公式施加到无关的中间形状。
等边三角形：B=(0,0)、C=(l,0)、A=(l/2,sqrt(3)l/2)，I=(l/2,sqrt(3)l/6)。
普通直角三角形：B=(0,0)、C=(u,0)、A=(0,v)，u,v>0，r=(u+v-w)/2，I=(r,r)。
等腰直角三角形：同样建系，u=v=t，r=(2-sqrt(2))t/2，x=z=t/sqrt(2)，y=r。
用两条半径分别指向坐标轴，显示横纵坐标的来源；只有等腰直角状态显示对称轴。

## 视觉与循环

576×1024 竖屏，浅底，中文使用 Microsoft YaHei，公式使用 MathTex。
三个主题拆分为短 GIF，不将全部推导挤入同一帧。每次只显示当前步骤。
底部固定两行品牌文案贯穿开场、过渡与结尾。
每条末帧恢复开场的图形和状态。正式 PNG、TeX、meta.json、PDF 均不改动。

## 构建与验收

使用 scripts/manim/production.py（render.ps1/export_gif.ps1 的同一入口），
隔离目录 build/manim/P033-production-20261111。每个 GIF 单独绑定 Scene 和输出名。
数学测试包含连续运动 481 个状态及全等距、相切、面积、切线段、特殊三角形。
GIF 使用冻结工具导出与全帧解码校验，检查真实关键帧、底部文案和首尾状态。
用户已授权将新 GIF 写入 images；不覆盖任何已有同名文件，不执行知识包 Publisher 或 Sync。
本地验证与用户视觉、Android 真机验收、FINAL FREEZE 分开记录。
