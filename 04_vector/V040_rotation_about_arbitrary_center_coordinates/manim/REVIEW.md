# V040 GIF 本地生产验收

日期：2026-11-09。状态：**LOCAL PRODUCTION PASS / STORED IN IMAGES**。

文件：`../images/rotation_coordinates.gif`，576×1024，22.58秒，271帧，221个不同画面，80–90ms/帧，无限循环，2,020,150字节（约1.93 MiB）。

SHA-256：`94a99cf262818d59e0ba06203bd4d8bc0d25c90044a336612f7f7f72917696a4`。
构建区与 images 中的文件哈希一致。写入前该目录为空，没有覆盖已有资源。

## 数学与教学审计

正式事实源是 V040 的六段 TeX 与 meta.json；本轮只读，没有改动数学知识源或 PDF。未引用其他 UID 的私有数学模型、Scene 或图像资产。

取 B=(1,1)、P=(4,2)，故(u,v)=(3,1)，BP=√10。
动画与公式均由独立模型 `model.py` 驱动：

- Q=(1+3cosθ−sinθ, 1+3sinθ+cosθ)。
- θ=45°：Q=(1+√2,1+2√2)；θ=90°：Q=(0,4)。
- θ=−45°：Q=(1+2√2,1−√2)，运动方向为顺时针。
- 分解路径为 B→H→Q，BH=(3cosθ,3sinθ)，HQ=(−sinθ,cosθ)。两段垂直，长度分别为3、1；端点始终与旋转模型一致。
- 图形横纵刻度等长，角度弧从原向量 BP 起算，中心 B 不移动。归零过程明确标作回到原位置，不把复位混称为继续逆时针旋转。

本 GIF 专注于相对坐标和公式来源。反求角度、整周歧义、椭圆例题保留在 PDF，避免压缩主图。数值例子用于解释机制，不冒称对全部参数的证明。

## 验收结果

| Gate | 状态 | 实际证据 |
| --- | --- | --- |
| M 数学自动测试 | PASS | `test_model.py` 4项通过：命名关键状态、1000组随机多圈正负角、中心重合/原点、全运动范围及两段合成 |
| M 真实关键状态 | PASS | 从GIF解码的8个状态，Q点的绿色像素均出现在模型投影位置附近；关键坐标与正文通式一致 |
| V 本地视觉 | PASS | 检查真实576×1024关键帧、0/45/90/−45度、分解阶段、首尾；无已见标签重叠、遮挡或裁切 |
| T 教学表达 | PASS | 先看定中心旋转和长度不变量，再看两段共同转动与公式颜色对应；关键角有停顿 |
| G 技术 | PASS | 冻结verify_gif全帧解码；271帧、221不同帧、零黑帧、非零时长、无限循环；附加检查无空图帧、无安全边缘侵入 |
| G 固定品牌 | PASS | 两行文案所有帧保留；567次场景布局采样无越界；GIF逐帧分别核对两行文字轮廓，最小IoU=0.9667 |
| G 循环 | PASS | 首尾数学对象和文案状态相同；真实首尾平均RGB差0.3928/255，仅有编码/量化差异；已检查真实首尾帧 |
| USER VISUAL | PENDING | 尚未收到用户对动态图视觉的确认 |
| D ANDROID DEVICE | PENDING | 需用户在Android真机确认清晰度、裁切与循环效果 |
| FINAL FREEZE | PENDING | 不以本地验收替代用户视觉和Android真机验收 |
| PUBLISHED / SYNCED | PENDING | 仅按用户要求存入images，未执行Publisher、Content Package、Sync或APK构建 |

编码说明：经H.264和GIF调色板处理，静止文案的抗锯齿像素不逐帧完全相同，54种像素签名；逐行轮廓核验与真实关键帧确认内容及位置固定。最大平均亮度差为1.5187/255，没有将像素签名不同误报为文案消失。

本地视觉评分90/100（作者自检）：图形23/25，层级18/20，可读性17/20，配色14/15，动效9/10，品牌9/10。辅助刻度较小且参考圆较淡；它们不承载主结论，手机实际可读性仍待真机确认。

## 可复现命令

在仓库根目录运行：

```powershell
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 04_vector/V040_rotation_about_arbitrary_center_coordinates/manim -p test_model.py -v
.\scripts\manim\render.ps1 -Uid V040 -Scene V040ArbitraryCenterRotation -SceneFile scene_rotation.py -Name rotation_coordinates
.\scripts\manim\export_gif.ps1 -Uid V040 -Scene V040ArbitraryCenterRotation -SceneFile scene_rotation.py -Name rotation_coordinates
.\.venv-manim\Scripts\python.exe -B 04_vector/V040_rotation_about_arbitrary_center_coordinates/manim/audit_gif.py build/manim/V040/rotation_coordinates/rotation_coordinates.gif
```

本次已在本地审核后通过冻结导出器 `-Publish -AssetName rotation_coordinates.gif` 首次写入images；未使用 `-Overwrite`。该命令再次写入同名文件会安全拒绝。

证据位于 `build/manim/V040/rotation_coordinates/`：`scene_audit.json`、`frame_audit.json`、`key_00.png`至`key_07.png`、`keyframes.png`、预览MP4和GIF。构建日志位于 `build/manim/V040_render.log`、`V040_export.log`、`V040_publish_local.log`。
