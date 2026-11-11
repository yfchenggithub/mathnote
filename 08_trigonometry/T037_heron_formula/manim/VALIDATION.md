# T037 GIF 本地生产验收（2026-11-11）

状态：**LOCAL PRODUCTION PASS**。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均 **PENDING**；未执行知识包 Publisher、Sync、上传、APK 或 Git 提交。

## 产物

| 正式 GIF（UID 的 images/ 下） | 尺寸 | 帧数 | 时长 | 字节数 |
|---|---|---:|---:|---:|
| T037_heron_area.gif | 576×1024 | 243 | 20.25 秒 | 2,297,205 |
| T037_heron_incircle.gif | 576×1024 | 216 | 18.00 秒 | 2,034,762 |
| T037_heron_special.gif | 576×1024 | 250 | 20.83 秒 | 2,210,704 |

## 数学与教学核验

六段 TeX 与 meta.json 为事实源；逐条确认三角形不等式、正面积、a=BC/b=CA/c=AB、内切圆垂足 D/E/F、半周长差与切线段、S=pr，以及等边与直角两种特殊化简。

`test_model.py` 的 6 项测试通过，共核验 593 个有效三角形样本（361 个变底状态、121 个等边放大状态、5 组直角边、6 组正文数值和 100 组随机有效三角形），另拒绝 6 组无效/退化输入。用独立坐标面积核验海伦乘积，不只是重算同一公式；同时检查三边长度、三个垂足、垂直性、半径、六段切线长和面积分块。

- 第一张没有暗示底边越长面积必然越大；a=5、b=6 固定，c=7→10→7，坐标与数字取自同一模型。
- 第二张展示半周长差的几何含义，明确完整证明在 PDF，不把切线段对应本身当成海伦公式的全部证明；最后由同高分块求半径。
- 第三张中 c 始终是直角三角形斜边、C 为直角；四因子配对使用勾股关系，正值开方得 ab/2，并提醒直接底乘高的做题选择。

## Gate 与证据

| Gate | 状态 | 实际证据 |
|---|---|---|
| M 数学 | PASS | 6 项模型测试及上述 593 样本；正文数值核对 |
| T 技术 | PASS | 709 帧完整解码；12 FPS 的 80/90 ms 帧时长；无限循环；0 黑帧 |
| 全帧布局 | PASS | 0 空白图形帧、0 边缘裁切帧；页脚全帧比较；首尾 RGB 平均差 <1/255 |
| V 本地视觉 | PASS | 真实 GIF 首尾、暂停、运动状态和全部分镜关键帧；已移开边长标签并补 r 标记 |
| E 教学表达 | PASS | 三边代入、几何对应、特殊情形分开；逐步出现公式，图形不变形 |
| A 架构 | PASS | 2 项既有渲染边界测试；本 UID 独立模型/Scene；冻结工具未改 |
| USER VISUAL | PENDING | 等待用户查看实际 GIF |
| ANDROID DEVICE | PENDING | 用户真机验收尚未执行 |
| FINAL FREEZE | PENDING | 不以本地通过替代用户与设备验收 |

全帧检查脚本：`verify_media.py`；真实帧、接触表、技术 JSON 和源文件保护哈希：`build/manim/T037-production-20261111/`（忽略目录）。页脚因 MP4 压缩与 GIF 量化允许 <2/255 的 RGB 平均差，三张实测最大值均 <1/255；Scene 两行文字始终固定，不随内容淡出。

本地视觉评分（辅助 Gate V，不代表用户验收）：数学图形 22/25、信息层级 18/20、可读性 17/20、配色 14/15、运动 9/10、整体 9/10，共 89/100。复杂配对公式适合暂停阅读，真机清晰度仍待确认。

## 可复现命令

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 08_trigonometry/T037_heron_formula/manim -p test_model.py -v
.\.venv-manim\Scripts\python.exe -B -m unittest tests.test_rendering_boundaries

# 对另两张分别指定 T037HeronIncircle/heron_incircle 和 T037HeronSpecial/heron_special
.\.venv-manim\Scripts\python.exe -B scripts/manim/production.py render --uid T037 --scene-file scene.py --scene T037HeronArea --name heron_area --build-root build/manim/T037-production-20261111
.\.venv-manim\Scripts\python.exe -B scripts/manim/production.py export --uid T037 --scene-file scene.py --scene T037HeronArea --name heron_area --build-root build/manim/T037-production-20261111
.\.venv-manim\Scripts\python.exe -B 08_trigonometry/T037_heron_formula/manim/verify_media.py build/manim/T037-production-20261111

# 完成上述视觉核对后，受控写入新 GIF；不传 --overwrite
.\.venv-manim\Scripts\python.exe -B scripts/manim/production.py export --uid T037 --scene-file scene.py --scene T037HeronArea --name heron_area --build-root build/manim/T037-production-20261111 --publish --asset-name T037_heron_area.gif
```

边界测试首次受 Windows 沙箱临时目录权限限制，原样在隔离构建临时目录、经环境权限复核后重跑，2/2 通过；未改测试、未跳过断言。环境检查通过：Python 3.14.3、Manim 0.21.0、Pillow 12.3.0、FFmpeg、LaTeX、dvisvgm、Microsoft YaHei。

## 修改边界与资源消费

仅新增本 UID 的 `manim/` 源码、测试、分镜和验收记录，以及三张新命名 GIF。17 个既有正式源/PDF/TikZ 保护文件与基线逐字节比较；任务期间另一个工作流新增 `images/001.png`～`003.png`，本任务不修改它们，另记观察时哈希。

已查现行 `scripts/zhishu/publish.py` 与 `asset_preparation.py`：直接 images/ 的 GIF 按原后缀发现，输出逻辑路径为 images/T037/同名.gif，并校验字节完全相同；文件名仅 ASCII 字母、数字和下划线，符合现有导出器约束。此次仅使用冻结 GIF 导出器显式写入 images/，不构建 Publisher 知识包、不修改 App 或元数据。

最终写入复核：三张正式 GIF 全部可完整解码，SHA-256 与已验收的隔离 GIF 一致；17 个既有保护文件、另行观察的 3 张 PNG 均 0 改变。证据为隔离目录 `final-audit.json`。最终本任务新增 9 个文件（6 个 manim 源码/文档、3 张 GIF），工作树另有其他工作流新增的 3 张 PNG；未纳入本任务生成文件。`git diff --check` 通过。
