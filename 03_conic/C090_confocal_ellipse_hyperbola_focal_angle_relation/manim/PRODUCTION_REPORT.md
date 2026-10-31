# C090 GIF 本地生产验收

日期：2026-10-30（Asia/Shanghai）。范围仅 C090。

交付：`../images/confocal_focal_angle.gif`。
状态：**LOCAL PRODUCTION PASS / LOCAL ASSET WRITTEN**。
USER VISUAL PASS、ANDROID DEVICE PASS、FINAL FREEZE 均未取得。
未执行正式 Publisher、Content Package、Sync 或 APK 构建。

## 数学审计与教学目标

已读取正式六段 TeX 和 meta.json。独立模型保存在 `model.py`，没有引用
其他 UID 的模型、场景或静态卡片实现。正式六段、meta.json、PDF 保持原样。

固定 c=2、aE=4，令 aH 在 [.6,1.65] 内变化。
每帧右上公共点严格使用

    x=aE*aH/c
    y=sqrt((aE²-c²)(c²-aH²))/c

椭圆与焦点固定，双曲线随 aH 变化；不是让交点在两条固定曲线上任意移动。
横纵坐标采用相同的 .78 场景单位比例，没有几何拉伸。
两腰为 aE±aH，和固定为8、差为2aH；余弦定理给出正式半角恒等式。
末段停于 aH=1：P=(2,3)，PF1=5、PF2=3，e1=.5、e2=2，sinθ=4/5，
两种上界表达均为5/2。等号仅可能在锐角时成立。

动画增加的教学价值是同时看见曲线、公共点、焦角、两腰和差及恒等式两项的联动；
显示取等号的精确例证，不将有限数值扫描当作一般证明。
变化中的长度、角度与 e2 使用近似号；两项显示到三位小数，在全轨迹采样中
舍入后仍相加为1。取等号段使用精确分数。

## 验证证据

| Gate | 状态 | 证据 |
|---|---|---|
| M 数学自动测试 | PASS | `test_model.py` 5项；577个时间状态、250组参数的四分支共1000状态、精确等号、直角/钝角严格性、无效参数与循环 |
| 关键数学状态 | PASS | aH=.6、1.65、1；点满足两条方程，焦半径和差、半角式及平方余量一致 |
| G 全帧技术检查 | PASS | 冻结的 `verify_gif.py` 全部288帧完整解码；无黑帧、无零时长帧、无限循环 |
| 全帧图形轨迹 | PASS | `verify_frames.py` 对288帧检查预测位置附近的金色P标记；最近金色像素距离最大0.682px；另有数学模型测试 |
| 固定品牌与安全边距 | PASS | 288帧文案包围盒一致；字形掩模最小IoU=.9676；平均RGB最大差1.2213（MP4压缩及GIF抖色）；安全边界无内容越界 |
| T 教学表达 | PASS（本地） | 同一图形渐进展示和差、恒等式及等号例证；不混淆焦角与切线角 |
| V 桌面视觉 | PASS（本地） | 检查真实GIF首尾、参数极值、恒等式、等号及切换帧；调整P和θ标签，公式先淡出后淡入，避免文字互相覆盖 |
| 用户视觉 | PENDING | 等待用户查看交付GIF |
| D Android真机 | PENDING | 必须由用户在真机上确认清晰度、裁切及循环 |
| FINAL FREEZE | PENDING | 用户视觉和Android验收未完成 |
| PUBLISHED / SYNCED | PENDING | 本轮只按用户授权写入本地images，未构建发布包或同步 |

实际GIF关键帧保存于：
`../../../build/manim/C090-production/C090/confocal_focal_angle/qa/`。
本地重点复核帧号：0、57、116、150、194、202、242、287（从0计数）。
首尾整幅图平均RGB差为0.4839，几何、文字及布局一致，差值来自编码。
底部所有阶段保留规定原文两行，包括淡出、淡入和循环两端。

## 产物规格与完整性

- 576×1024，24秒，288帧，229个不同帧；12FPS GIF，单帧80/90ms。
- 无限循环；5,841,341 bytes（约5.57MiB）；0黑帧。
- 源MP4为24FPS，只在隔离构建目录中保留。
- SHA256：`d3ae52c7be783d86d838451e11bc8c2228f12e761bc5cbdff15bcacd3f10a58b`。
- `images`交付文件与经检查的staging GIF哈希一致；写入前无同名正式GIF。
- Publisher实际资产代码核对：`scripts/zhishu/asset_preparation.py`发现
  `images/`直接PNG/GIF，GIF保持后缀与字节；本文件名符合冻结导出器的命名约束。

## 复现

在仓库根目录执行：

```powershell
./.venv-manim/Scripts/python.exe -B -m unittest discover -s 03_conic/C090_confocal_ellipse_hyperbola_focal_angle_relation/manim -p test_model.py -v
./scripts/manim/render.ps1 -Uid C090 -Scene C090ConfocalAngle -SceneFile scene.py -Name confocal_focal_angle -BuildRoot build/manim/C090-production
./scripts/manim/export_gif.ps1 -Uid C090 -Scene C090ConfocalAngle -SceneFile scene.py -Name confocal_focal_angle -BuildRoot build/manim/C090-production
./.venv-manim/Scripts/python.exe -B 03_conic/C090_confocal_ellipse_hyperbola_focal_angle_relation/manim/verify_frames.py build/manim/C090-production/C090/confocal_focal_angle/confocal_focal_angle.gif
```

首次写入使用冻结导出器的 `-Publish -AssetName confocal_focal_angle.gif`，未使用
`-Overwrite`。后续不能无授权覆盖本次交付。共享生产工具、静态模块及其他UID未修改。
