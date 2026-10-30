# C088 数学 GIF 本地生产验收

日期：2026-10-30。状态：**LOCAL PRODUCTION PASS**。

用户要求生成 C088 GIF 并放入图片目录。新文件已通过共享导出器的显式
`-Publish -AssetName C088_area_product.gif` 写入本 UID 的 `images/`，未使用
`-Overwrite`。此前该目录无 GIF；没有覆盖正式资源。
未执行 Zhishu Publisher、Content Package、Sync 或 APK 构建。

## 数学与教学

只读本 UID 的六段 TeX、meta.json，独立编写数学模型、测试和分镜。
七份知识源的 SHA-256 与构建前一致。共享工具、其他 UID、PDF、静态图均未改动。

主图使用 `a=3,b=2,k=2/3,x1=3`，B 沿 `y=-kx` 在 `x2∈[1.5,3]` 内运动。
初始竖直截线面积为 6，横坐标减半后面积为 3。
相似与横轴分块阶段固定在 `x2=1.5`，截点 `C=(2,0)`，两块面积为 2、1。
两条高均为垂直于横轴的真实距离。相似角、直角符号、曲线点均由模型坐标生成。
不在初始竖直截线构成的退化辅助三角形上使用相似比。
灰色背景曲线是真实双曲线右支，A、B 始终位于渐近线而非曲线上。

动态小数保留两位并使用近似号；“横坐标减半，面积也减半”仅出现在减半状态的停顿。
运动展示面积随截线变化，结尾给一般公式 `S=(b/a)|x1*x2|`，不暗示面积恒定。
本 GIF 演示同号情形；异号面积差、水平截线无 C 等边界由模型测试覆盖并在 PDF 说明。

## 验收 Gates

| Gate | 状态 | 实际证据 |
|---|---|---|
| M 数学自动测试与关键状态 | PASS | `test_model.py` 5 项测试；1001 个运动状态、175 组带符号坐标面积、30 组截距分块分类、关键值及参数拒绝测试 |
| G GIF 全帧技术 | PASS | 576×1024，285 帧、197 个不同帧，23.75 秒，80—90 ms 帧时长，无限循环，黑帧 0、空数学画面 0 |
| V 本地视觉 | PASS | 查看从真实 GIF 提取的首态、减半、运动、相似、分块、结论、循环末尾；标签无重叠、外缘 14 px 无内容进入 |
| T 教学表达 | PASS | B 的位移、面积读数同步；随后构造 C 并将原阴影分为共底的两块，解释乘积面积关系 |
| USER VISUAL PASS | PENDING | 等待用户观看成品 |
| D ANDROID DEVICE PASS | PENDING | 等待用户确认 Android 真机播放、字体与循环效果 |
| FINAL FREEZE | PENDING | 未标记冻结 |

底部全程固定两行：

> 查结论 · 看图解 · 学证明｜知树 App
>
> 公众号 ok-shuxue｜获取入口

全帧文案区域检查：最小文字掩膜 IoU 为 0.972015，最大平均 RGB 差为 0.710615/255。
这些微小色差来自中间 MP4 压缩；字形位置和内容保持稳定。首尾整帧平均差为 0.371036/255，
且首尾数学、数值、标注与布局一致，已分别查看真实帧。

## 产物与复现

- GIF：`../images/C088_area_product.gif`，2,588,419 字节（2.47 MiB）。
- SHA-256：`6187393868c39e920e525dd1d739d3a3cdb23b859be7bf0966ce84455c68bcb7`。
- 图像与全帧证据：`build/manim/C088_production/C088/area_product/evidence/`（仓库根目录相对路径）。
- 本地结构化记录：`validation.json`。
- 数学与分镜：`model.py`、`test_model.py`、`STORYBOARD.md`、`scene_area.py`。
- 实际技术检查：`validate_frames.py`，调用冻结的 `scripts/manim/verify_gif.py`。

环境检查通过：Python 3.14.3、Manim 0.21.0、Pillow 12.3.0、FFmpeg、TeX Live、dvisvgm、Microsoft YaHei。

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C088_hyperbola_asymptote_intersection_triangle_area/manim -p test_model.py -v
.\scripts\manim\render.ps1 -Uid C088 -Scene C088AreaProduct -SceneFile scene_area.py -Name area_product -BuildRoot build/manim/C088_production
.\scripts\manim\export_gif.ps1 -Uid C088 -Scene C088AreaProduct -SceneFile scene_area.py -Name area_product -BuildRoot build/manim/C088_production
.\.venv-manim\Scripts\python.exe -B 03_conic/C088_hyperbola_asymptote_intersection_triangle_area/manim/validate_frames.py build/manim/C088_production/C088/area_product/area_product.gif
```

上述复现命令仅构建隔离预览，不写正式图片目录。正式目录中的文件哈希已与验收预览核对一致。
