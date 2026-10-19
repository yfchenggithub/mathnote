# C004 椭圆顶角最大值 GIF

## 数学来源与独立模型

已读取本 UID 当前六段正式 TeX 与 meta.json，两者一致。
任务开始时这些文件及 PDF 已有用户改动，本任务保持原样。
动画不读取 C003 的模型、场景或既有图像。

本题是长轴端点 A1=(-a,0)、A2=(a,0) 对 P 的普通内角，
不是焦点张角，也不是两条直线形成的锐夹角。
条件为 a>b>0，P 在同一椭圆上，且 P≠A1,A2。

通式：

```
alpha = 90° + arctan((a²-b²)|y| / (2ab²))
90° < alpha ≤ 2 arctan(a/b) < 180°
```

最大值恰在 (0,±b) 取得；没有最小值，90° 仅是下确界。
长轴端点处有一条零向量，因此角无定义，模型明确返回 None。
角度使用实际两射线的叉积、点积经 atan2 计算；
通式另行计算，用于测试交叉核对，不以通式自证通式。

示例取正式例 1：a=2、b=1，最大角约 126.8698976°，
读数保留一位小数显示 126.9°；最大角的正切为 -4/3。
全部几何共用 1.65 的横纵等比例显示变换。

## 教学分镜

1. 画长轴直径圆，椭圆在圆内；P 处两射线张成钝角。
2. P 沿上半椭圆靠近短轴端点，点到长轴的距离与顶角一起增大。
3. 上短轴端点停顿，作高 PO，标出 b、a 和原点处直角，
   展示顶角平分后的 tan(alpha_max/2)=a/b。
4. 向左长轴端点靠近，在端点前停止，说明趋近 90°但取不到。
5. 隐去动点图形，再切换到下半椭圆，避免描绘跨越无定义端点的轨迹。
6. 下短轴端点停顿，展示相同最大值和两个最大值位置。
7. 回到端点附近后再次隐去并复位；首尾恢复同一合法状态，循环。

运动参数分成两条开弧：
`[0.14, pi-0.14]` 和 `[pi+0.14, 2pi-0.14]`。
接近端点时的有限示例角约 95.975°，不冒充 90° 极限。
角弧取两射线间实际的钝角短弧，靠近端点时半径不超过较短边的 36%。
绿色虚线通常只表示高度；只有短轴端点处同时表示角平分线。

## 重建与首次交付

仓库根目录：

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C004_Ellipse_Max_Vertex_Angle/manim -p test_model.py -v
.\scripts\manim\export_gif.ps1 -Uid C004 -Name max_vertex_angle -Rebuild
```

隔离预览位于 `build/manim/C004/max_vertex_angle/`。
本地检查后按用户明确要求首次写入 images/：

```powershell
.\scripts\manim\export_gif.ps1 -Uid C004 -Name max_vertex_angle -Publish -AssetName ellipse_max_vertex_angle.gif
```

若文件已存在，工具拒绝覆盖。不得自动添加 `-Overwrite`。
用户视觉与 Android 真机验收分别记录；本地通过不等于 FINAL FREEZE。
本任务不运行 Publisher 内容包、Sync、Git 提交或 APK 构建。
实际验收证据见 `VALIDATION.md`。
