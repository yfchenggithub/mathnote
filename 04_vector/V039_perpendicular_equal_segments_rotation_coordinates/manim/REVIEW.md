# V039 动态 GIF 本地生产验收

日期：2026-11-08。

本轮范围：独立新增本 UID 的 `manim/` 与 `images/V039_rotation_coordinates.gif`。正式六段 TeX、meta.json、PDF、TikZ 图源、共享生产工具及其他 UID 资产未修改。

## 产物与教学目的

- GIF：`04_vector/V039_perpendicular_equal_segments_rotation_coordinates/images/V039_rotation_coordinates.gif`。
- 576×1024，18.00 秒，216 帧（132 个不同帧），约12 FPS，无限循环，2,021,535 字节。
- Scene：`V039QuarterTurn`，由冻结的 `render.ps1`、`export_gif.ps1` 与 `verify_gif.py` 构建、导出、检查。
- 独立数学模型及测试在 `model.py`、`test_model.py`，分镜在 `STORYBOARD.md`。
- 以正式例2 B(2,-1)、P(5,3) 为起点；三角形整体转动，清楚区分相对位移与绝对坐标。逆时针终点 Q1(-2,2)，顺时针终点 Q2(6,-4)。不把整个 PDF 的四种证明与椭圆例题挤入一条 GIF。
- 转动中点称 R，只显示 BR=BP=5；转到90°后才改称 Q 并标出垂直。结尾定义 B(a,b)、P−B=(u,v)，给出两种一般公式，再回到开场。

底部全程固定：

查结论 · 看图解 · 学证明｜知树 App

公众号 ok-shuxue｜获取入口

## 实际验收

| Gate | 状态 | 实际证据 |
| --- | --- | --- |
| M 数学自动测试 | PASS | 4项 unittest；720个整坐标直角旋转分支，覆盖三个中心、各象限与轴向情形；721个连续角度，验证刚体运动的两直角边长3和4、斜边长5、内部直角及中心不动；检查零长度与非法方向 |
| M 渲染运动采样 | PASS | 实际 Scene 记录407个采样；长度平方误差最大7.11×10^-15，内部直角数量积绝对误差最大2.66×10^-15；运动由模型函数驱动，未用线性终点插值 |
| V 本地视觉质量 | PASS | 查看实际 GIF 的开场、两方向运动、两个直角终点、最终两位置、循环恢复等12幅关键帧及576px原尺寸主状态；修正坐标字号、分量标签压坐标轴问题；公式与品牌区分离 |
| T 教学表达 | PASS | 本地编辑检查：用真实刚体转动解释坐标分量交换，两个方向分别停顿；非直角中间帧没有标示 BP⊥BR。未做真实学生理解效果实验 |
| G GIF 技术 | PASS | 216帧完整解码，132个不同帧，无黑帧；帧时长80–90ms，无限循环；逐帧12像素边缘检查无深色内容触边 |
| G 底部及循环 | PASS | `review_gif.py` 检查全部帧；底部区域最大平均通道差约0.965/255、超过20的像素占比最高约0.133%，符合静态文字经MP4/GIF量化后的微小变化；首尾平均通道差约0.381/255，人工核对相同开场状态 |
| D Android 真机 | PENDING | 需用户在知树 App 真机中确认播放、字号、裁切及循环，本地验收不替代真机结果 |
| USER VISUAL PASS | PENDING | 尚无用户视觉确认 |
| FINAL FREEZE | PENDING | 未宣告最终冻结 |

状态：**LOCAL PRODUCTION PASS**。用户明确要求放入 images，因此在上述本地检查后，使用 `export_gif.ps1 -Publish` 新增文件；目标原先不存在，未使用 `-Overwrite`。

写入后再次运行冻结 GIF 检查器通过。images 文件与隔离预览文件的 SHA-256 一致：`0C5E327A0A346559ED7EC1C8F55038FCBB87828BA5981183895362FEA3988AB7`。

这次只完成本地 images 资源写入。Publisher / Content Package / Sync / APK 均未执行；不标记全链路 PUBLISHED / SYNCED。

## 可复核证据与命令

中间产物根目录：`build/manim/V039/rotation_coordinates/`。

- `rotation_coordinates.mp4`：实际渲染视频。
- `V039_rotation_coordinates.gif`：检查过的隔离 GIF。
- `media/v039_motion_audit.json`：实际渲染采样。
- `review/contact_sheet.png`、`review/frame-*.png`：从 GIF 解码取得的真实关键帧。
- `review/review.json`：逐帧底部、边缘及循环结果。字节严格相等并不适用于有损视频与调色板量化，因此检查的是变化幅度并配合实际关键帧审查。

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 04_vector/V039_perpendicular_equal_segments_rotation_coordinates/manim -p test_model.py -v
.\scripts\manim\render.ps1 -Uid V039 -Scene V039QuarterTurn -SceneFile scene.py -Name rotation_coordinates
.\scripts\manim\export_gif.ps1 -Uid V039 -Scene V039QuarterTurn -SceneFile scene.py -Name rotation_coordinates -AssetName V039_rotation_coordinates.gif
.\.venv-manim\Scripts\python.exe -B 04_vector/V039_perpendicular_equal_segments_rotation_coordinates/manim/review_gif.py build/manim/V039/rotation_coordinates/V039_rotation_coordinates.gif build/manim/V039/rotation_coordinates/review
.\scripts\manim\export_gif.ps1 -Uid V039 -Scene V039QuarterTurn -SceneFile scene.py -Name rotation_coordinates -AssetName V039_rotation_coordinates.gif -Publish
```

最后一条仅供复核本轮实际命令。文件现在已存在，再次执行会按工具契约拒绝覆盖；后续修改须先在隔离目录重做验证并处理既有文件授权。
