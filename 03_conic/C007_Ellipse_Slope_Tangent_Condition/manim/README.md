# C007 椭圆斜率式切线判定 GIF

## 数学审计与独立模型

已读取本 UID 当前正式六段 TeX 和 meta.json，核心判定与位置关系一致。
任务开始时六段 TeX、meta.json 与 PDF 已有用户改动，全部保留。
本模型独立建立，不读取其他 UID 私有模型、动画或已有图像。

对 a>b>0、有限实斜率 k，记 S=a²k²+b²>0。
直线 y=kx+m 与椭圆的位置关系由 m² 与 S 的大小决定：

- m²<S：两个不同交点。
- m²=S：相切，唯一切点。
- m²>S：相离，无交点。

交点由真实联立方程求得：

```
S*x² + 2a²km*x + a²(m²-b²) = 0
x = [-a²km ± ab*sqrt(S-m²)] / S
y = kx+m
```

只在相切时使用 T=(-a²k/m,b²/m)。
模型另以椭圆法向量 (x/a²,y/b²) 与直线方向 (1,k) 正交来检验真实相切，
不以单纯“两个点看起来合并”判定。

示例采用正式例 3：a=3、b=2、k=1/2，S=25/4=6.25。
上切线 m=2.5，切点 (-1.8,1.6)；下切线 m=-2.5，切点 (1.8,-1.6)。
m=2 时有两个交点，m=3 时没有交点。

显示坐标为数学坐标的等比例平移，不分别缩放横纵轴。
无限直线按 x∈[-3.6,3.6]、y∈[-3.05,3.05] 的数学窗口裁切，
裁切只限制可见长度，不改变直线或交点。

## 教学分镜

1. 从 m=2 的两交点状态开始，同时显示 m、交点个数及 m²<S。
2. 固定 k=1/2，上移至 m=2.5，两个真实交点合并；停顿显示等号与切点 T。
3. 继续上移至 m=3，交点消失，显示 m²>S。
4. 下移穿过中心 m=0，再到 m=-2.5，展示负截距也可相切。
5. 保留橙色当前直线，加入蓝色虚线上切线与其切点标记，
   展示同一斜率对应两条平行切线 y=kx±sqrt(a²k²+b²)。
6. 移除参考虚线，回到初始状态循环。

交点个数始终针对橙色的当前直线 l；蓝色虚线只是正截距切线的参考。
两条交点很靠近时显示的截距、平方值可能因四舍五入提前相同，
数学分类依据实际参数，不依据格式化读数。

全程保留边界提示：竖直切线 x=±a 不在斜率式内。
本片只演示固定有限斜率；通式 C²=a²A²+b²B² 及竖直情况另经模型测试。

## 重建命令

仓库根目录：

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C007_Ellipse_Slope_Tangent_Condition/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C007 -Name slope_tangent_condition -Rebuild
```

隔离输出在 `build/manim/C007/slope_tangent_condition/`。
检查后按用户明确要求首次写入 images/：

```powershell
.\scripts\manim\export_gif.ps1 -Uid C007 -Name slope_tangent_condition -Publish -AssetName ellipse_slope_tangent_condition.gif
```

已有同名文件时工具拒绝覆盖，不自动添加 `-Overwrite`。
本任务不执行 Publisher 内容包、Sync、Git 提交或 APK 构建。
本地检查、用户视觉、Android 真机与 FINAL FREEZE 分别记录，见 `VALIDATION.md`。
