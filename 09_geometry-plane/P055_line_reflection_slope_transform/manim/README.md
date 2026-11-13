# P055 镜面转动与斜率变换

数学源：当前 UID 的六段 TeX 与 meta.json。仅新增本 UID 的动画模型、Scene、测试及 GIF，不修改数学正文或 PDF。

## 独立分镜

固定原线经过原点，方向向量 (2,1)，斜率 1/2。镜面也经过原点，方向角为 α。像方向始终由真正的反射矩阵计算，不把插值旋转当作固定镜面的反射过程。

1. 水平镜面停留：像方向 (2,-1)，斜率 -1/2。
2. 镜面转到 45°：像方向 (1,2)，斜率 2，观察横纵交换。
3. 到 α=(90°+arctan(1/2))/2：像横增量为零，像线竖直，斜率不存在。
4. 到竖直镜面：像方向 (-2,1)，斜率 -1/2。
5. 平滑返回水平镜面并停留，与开头衔接。固定底部两行品牌文案始终显示。

蓝色原线、橙色像线、绿色虚线镜面；横纵单位等长。文字先淡出再淡入，避免过渡叠字。动画聚焦方向变化，具体位置及内外角判断保留在 PDF。

## 复现

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 09_geometry-plane/P055_line_reflection_slope_transform/manim -p test_model.py
.\scripts\manim\render.ps1 -Uid P055 -Scene P055MirrorSlope -SceneFile scene_reflection.py -Name slope_reflection
.\scripts\manim\export_gif.ps1 -Uid P055 -Scene P055MirrorSlope -SceneFile scene_reflection.py -Name slope_reflection
```

隔离预览：`build/manim/P055/slope_reflection/`。用户已明确要求放到 images，因此本地检查后用同一 exporter 的 `-Publish -AssetName P055_slope_reflection.gif` 写入；未使用覆盖开关。Publisher 实际消费契约已核对：images 下直接 GIF、合法 ASCII 文件名、原字节复制；未执行内容包、Sync 或 APK 构建。

## 2026-11-13 本地验收

| Gate | 状态 | 实际证据 |
| --- | --- | --- |
| M 数学 | PASS | 3项 unittest 通过；特殊镜面、竖直临界、361个镜面角度的长度、平行/垂直分量、反射两次还原及通式吻合检查 |
| V 本地视觉 | PASS | 查看最终 GIF 的 0、6、10.6、15.1、22.5 秒真实关键帧；中文正常，公式/图形/品牌未重叠裁切 |
| T 教学表达 | PASS | 固定原线只转镜面，像线实时保持对称；特殊状态各停留约2秒，临界状态明确写斜率不存在 |
| G 技术 | PASS | 冻结 exporter 全帧验证：576×1024，272帧，172个不同帧，22.66秒，80–90ms帧时长，无限循环，0黑帧，2923038字节 |
| 全帧补充 | PASS | 272帧均有数学图形，图区彩色像素最低1802；固定底部相对首帧的最大平均通道差0.885/255以内（GIF量化误差）。证据 frame_audit.json 在隔离预览目录 |
| USER VISUAL | PENDING | 待用户查看成品 |
| ANDROID DEVICE | PENDING | 待用户真机确认 |
| FINAL FREEZE | PENDING | 不以本地生产检查代替用户与真机验收 |

LOCAL PRODUCTION PASS。正式目录文件为 `../images/P055_slope_reflection.gif`；写入 images 不代表已发布到应用或已同步。
