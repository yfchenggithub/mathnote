# C085 GIF 本地生产验收

日期：2026-10-27。状态：**LOCAL PRODUCTION PASS / SAVED TO UID IMAGES**。

## 交付

- GIF：`../images/focal_parallel_asymptote_ratio.gif`
- 576×1024，361 帧，265 个不同帧，30.08 秒，约 12 FPS（帧时长 80–90 ms），无限循环。
- 4,309,358 字节（约 4.11 MiB）。
- SHA256：`ac19a09254dd3a8cc4e94720c0425b3a069180638b1226a49e37ff69a59332df`。
- 构建与关键帧证据：`build/manim/C085-production/C085/focal_parallel_asymptote_ratio/`。

## 数学与教学

以本 UID 正式六段 TeX 和 meta.json 为事实源，独立建立 model.py 与 scene.py。先认普通线段 F—M—N，再映射到实际双曲线，固定 a=3 让 b 连续 4→2.25→3→4，观察 MN=1.5 与位置方向变化；最后以水平投影 t、c/2−t 推得比例和离心率公式。动画只讲一个主要结论及其低门槛解释，完整四法保留在 PDF。

5 个模型测试全部通过：481 个连续运动域采样、20 组一般参数与四向反射、标准精确状态、61 个首尾分段对应过渡状态、曲线方程与屏幕范围、无效参数。横纵始终等比例，初始分段过渡保持 16/9；强调平行关系时只变色，不缩放数学对象。

渲染后另核验 195 个实际模型采样状态的曲线方程、焦点线、另一渐近线、点序、长度、比例与标签范围。停顿帧由 Manim 复用，采样数不等于电影帧数。动态显示用近似号表示两位小数舍入，MN=1.50 是精确长度；三组停顿状态与数值一致。

## Gate 结果

| Gate | 状态 | 证据 |
| --- | --- | --- |
| M Mathematics | PASS | 5 个单元测试，195 个实际渲染模型状态；a=3,b=4 的交点、长度及比例精确核对。 |
| V Visual Quality | PASS（本地） | 原尺寸检查 10 幅真实关键帧及末帧；字母、曲线、两段颜色和公式一致，无遮挡或裁切。参数标注已移开坐标轴；近似号已修正。 |
| T Teaching Value | PASS（本地） | 从普通分段进入曲线构型，连续改变 b 可看见 MN 定长但不固定位置，水平投影给出比例原因。 |
| G GIF Technology | PASS | 冻结 verify_gif.py 全 361 帧解码，0 黑帧，265 个不同帧，正帧时长及无限循环；额外全帧内容边界 [68,47,526,991]，留在安全区域。 |
| D Android Device | PENDING | 尚无用户 Android 真机确认。 |
| USER VISUAL PASS | PENDING | 等待用户视觉反馈。 |
| FINAL FREEZE | PENDING | 不以本地验收代替用户/真机验收。 |
| Publisher / Content Package / Sync / APK | PENDING（未执行） | 本轮只按用户要求新建当前 UID 的 GIF 文件。 |

首末回到同一普通分段构型，无空白重置；首末像素不完全相同，已人工查看首尾，不宣称逐像素无缝。图像和数值的关键运动均由当前 UID 模型驱动。正式六段源、meta、main、source、PDF 与原三张 PNG 共 13 个文件的 SHA256 基线全部保持不变。

## 工具与复现

环境检查 PASS：Python 3.14.3、Manim 0.21.0、Pillow 12.3.0、FFmpeg、TeX Live/dvisvgm、Microsoft YaHei。未安装或升级依赖，未改共享工具。

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 03_conic/C085_hyperbola_focal_parallel_asymptote_segment_ratio/manim -p test_model.py -v
.\scripts\manim\render.ps1 -Uid C085 -Scene C085FocalAsymptoteRatio -SceneFile scene.py -Name focal_parallel_asymptote_ratio -BuildRoot build/manim/C085-production
.\scripts\manim\export_gif.ps1 -Uid C085 -Scene C085FocalAsymptoteRatio -SceneFile scene.py -Name focal_parallel_asymptote_ratio -BuildRoot build/manim/C085-production
.\.venv-manim\Scripts\python.exe -B 03_conic/C085_hyperbola_focal_parallel_asymptote_segment_ratio/manim/verify_render.py build/manim/C085-production/C085/focal_parallel_asymptote_ratio build/manim/C085-production/C085/focal_parallel_asymptote_ratio/focal_parallel_asymptote_ratio.gif
```

关键帧检查完成后，按用户“最后放在 C085 的 images 目录”授权，通过 export_gif.ps1 的 `-Publish -AssetName focal_parallel_asymptote_ratio.gif` 新建正式文件，未用 `-Overwrite`。隔离 GIF 与 images GIF 的 SHA256 完全一致。现行 Publisher 从 images 直接发现 PNG/GIF，GIF 保留原字节，文件名符合现行导出工具约束；本轮只审计代码，未执行 Publisher。没有操作其他 UID，也未提交 Git。
