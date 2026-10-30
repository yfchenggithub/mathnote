# V033 GIF 本地生产验收

日期：2026-10-30。状态：LOCAL PRODUCTION PASS。

资源：`../images/triangle_area_four_auxiliary.gif`。
源码：`scene.py`、`model.py`；自动测试：`test_model.py`；分镜：`STORYBOARD.md`。
隔离构建根：`build/manim/v033-production/V033/four_auxiliary/`。

## 数学审计

事实源为本 UID 正式六段 TeX 与 meta.json，未修改。动画数值例子
O=(0,0)、A=(3,2)、B=(2,3) 是正式一般公式的合法实例，S=5/2。
四种交点依次为 Ev=(2,4/3)、Eh=(9/2,3)、Fv=(3,9/2)、Fh=(4/3,2)。
内部交点用共底面积和；延长线交点用大减小。运动阶段固定 A，B=(2,y)，
Δ=3y−4、S=|Δ|/2；y=4/3 时共线，y=1/2 时 Δ=−5/2、S=5/4。
所有几何坐标经同一等比例映射绘制，没有为布局修改数学关系。

4 项 unittest PASS：四种具体构造、2401 组整数坐标的四种构造
（含负坐标、延长线、退化和零分母）、603 个运动样本、交换与共线性质。
对应命令：

```powershell
.venv-manim/Scripts/python.exe -B -m unittest discover -s 04_vector/V033_triangle_area_cross_product/manim -p test_model.py -v
```

## 渲染与逐帧证据

冻结的 `scripts/manim/render.ps1`、`export_gif.ps1` 完成生产，未改共享工具。
GIF 为 576×1024，30.25 秒，363 帧（293 个不同帧），80–90 ms/帧，
无限循环，3,847,222 字节，完整解码且黑帧为 0。

`qa/full_frame_audit.json` 记录全帧边缘检查、静态标题/品牌区差异、
15 个真实关键帧及正式知识源 SHA-256。
`keyframe_times.json` 来自实际 Scene 时钟，包含帧率取整影响。
`qa/*.png` 为真实 GIF 解码帧；`qa/contact_sheet.png` 仅供导航，
验收实际查看各张 576×1024 原始关键帧。

全部 363 帧四边安全区域无内容侵入，教学内容区无空帧。
两行品牌节点从开场到结尾独立保留，未纳入教学内容淡出组。
有损 MP4 编码与 GIF 调色板会使静态区像素哈希不同，不能用位完全相同
代替文案稳定性检查：标题/品牌区最大平均像素差分别为 1.182/0.983（0–255），
差异超过 30 的像素占比最大分别为 0.033%/0.055%，低于 0.2% 门槛。
视觉检查确认两行完整、可读、不移位、不裁切。

首轮检查发现“共线/负行列式”的停顿说明曾保留到下一段运动中，
已修正为运动期间先切回中性观察提示，并重新渲染、导出与验收。
负数状态统一称“行列式变负”，不把它误称为普通面积。

## Gate 与发布范围

| Gate | 状态 | 证据 |
|---|---|---|
| M 数学 | PASS | 独立模型 4 项测试、四种构造与运动数值一致 |
| V 本地视觉 | PASS | 15 张真实关键帧逐张检查，边界、公式和标签无裁切遮挡 |
| T 教学表达 | PASS | 四种辅助线构造、区域加减、连续共线与反向变化 |
| G GIF 技术 | PASS | 全帧解码、无限循环、真实运动、无黑帧 |
| D Android 真机 | PENDING | 等待用户在真机中确认清晰度、裁切与循环 |

USER VISUAL PASS：PENDING。ANDROID DEVICE PASS：PENDING。
FINAL FREEZE：PENDING。本地新资源按用户“放在 images”的授权，经冻结导出器
显式安装；未覆盖任何已有 GIF。Publisher/Content Package/Sync/APK：未执行。
正式六段 TeX、meta.json、PDF、既有静态图及其他 UID 未修改。

## 重建与导出

```powershell
scripts/manim/render.ps1 -Uid V033 -Scene V033FourAuxiliaryArea -SceneFile scene.py -Name four_auxiliary -BuildRoot build/manim/v033-production
scripts/manim/export_gif.ps1 -Uid V033 -Scene V033FourAuxiliaryArea -SceneFile scene.py -Name four_auxiliary -AssetName triangle_area_four_auxiliary.gif -BuildRoot build/manim/v033-production
.venv-manim/Scripts/python.exe -B 04_vector/V033_triangle_area_cross_product/manim/audit_gif.py build/manim/v033-production/V033/four_auxiliary/triangle_area_four_auxiliary.gif build/manim/v033-production/V033/four_auxiliary
```

仅在获得正式资源写入授权且完成审核后添加 `-Publish`；现有文件会阻止覆盖。
