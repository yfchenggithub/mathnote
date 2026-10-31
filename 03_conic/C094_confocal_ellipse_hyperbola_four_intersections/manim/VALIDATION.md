# C094 GIF 本地生产验收 · 2026-10-31

交付：`../images/confocal_four_intersections.gif`。
用户明确要求“生成动态gif图，放在images目录下”；目录原为空。
经隔离渲染、真实 GIF 检查后，使用冻结 exporter 的 `-Publish` 新建文件，未使用 `-Overwrite`。
正式六段 TeX、meta.json、PDF、其他 UID 及共享生产工具均未修改。

## 数学审计和分镜

模型和分镜见 `model.py`、`STORYBOARD.md`。
本动画只讲四点存在、参数变化和坐标，不混入切线正交与焦角。
固定 a_E=4、c=2，a_H: 1→0.65→1.65→1；b_H 随 a_H 重新计算以保持共焦。
图形 x/y 等比例；两支真实双曲线按相同绘图区截取，不在画布边缘裁断。
实时参数保留两位小数；曲线与交点使用未舍入值。

## 已实际执行的检查

- `python -B -m unittest discover -s <UID>/manim -p test_model.py -v`：6 项 PASS。
  覆盖 995 组一般参数、四点双曲线/椭圆代回、焦半径和差、平方差及距离恒等式、
  独立线性消元、显示母题、共焦关系、曲线采样、退化条件拒绝、241 个可见区间状态。
- `check_env.ps1`：PASS，Python 3.14.3、Manim 0.21.0、Pillow 12.3.0、FFmpeg、TeX、字体可用。
- 冻结 `render.ps1`：PASS，576×1024、24 FPS，516 个 MP4 帧。
- 冻结 `export_gif.ps1` / `verify_gif.py`：PASS。
  GIF 576×1024、258 帧、188 个不同帧、21.5 秒、80/90 ms 帧延时、无限循环、0 黑帧。
  大小 3,624,940 字节（约 3.46 MiB）。
- Scene 每次更新执行文本安全区检查；实际渲染无越界错误。
- `verify_local.py`：检查实际 GIF 全部 258 帧，四个理论交点附近均检出金色点；
  264 个渲染记录的最大两曲线方程残差 1.33e-15。
- 两行品牌全程存在、未移动或淡出；实际压缩图像文本墨迹最小 IoU 为 0.9587，
  最大平均通道差 1.6214/255。MP4/GIF 编码产生少量颜色噪声，因此不把逐像素字节相同作为标准。
- GIF 首尾平均通道差 0.4521/255；曲线、交点、参数和文案回到相同状态。
- 人工查看 11 张从实际 GIF 解码的关键帧，包含初态、运动中、两个参数极值、
  焦半径、平方差、一般坐标、四种符号、淡入过渡及末态。
  标签无重叠或裁切，数学对象与公式对应，阅读顺序清楚。

隔离证据：`build/manim/C094-production/C094/confocal_four_intersections/`，
包含 `render.log`、`scene_audit.json`、`local_checks.json`、11 张 `key_*s.png`、MP4 与暂存 GIF。

正式 GIF SHA-256：`ce7cb0681c14f1c7f81561c9931941cba66fa8b04298e162c7ca8dbdd39a6ea6`。

## Gate 与发布状态

| Gate | 状态 | 证据 |
| --- | --- | --- |
| M 数学 | PASS | 独立模型、6 项测试及渲染状态/实际交点检查 |
| V 本地视觉 | PASS | 11 张真实关键帧与文本安全区检查 |
| T 教学 | PASS | 参数运动显示四点不消失；同一对焦半径解释坐标；四符号独立 |
| G GIF 技术 | PASS | 冻结验证器与全帧检查 |
| D Android 真机 | PENDING | 待用户在真机确认 |

- LOCAL PRODUCTION PASS。
- USER VISUAL PASS：PENDING。
- ANDROID DEVICE PASS：PENDING。
- FINAL FREEZE：PENDING。
- 本地 `images/` 写入：PASS（用户本次明确授权）。
- 正式 Publisher / Content Package / Sync / APK 发布：未执行。

已核对现行 `publish.py` 及 `asset_preparation.py` / `prepare_knowledge_images.mjs`：
直接发现 `images/` 下 GIF，校验多帧、正延时和无限循环，按原文件名、原字节消费。
本次文件名符合冻结 exporter 的安全命名规则，无已有资源冲突。
