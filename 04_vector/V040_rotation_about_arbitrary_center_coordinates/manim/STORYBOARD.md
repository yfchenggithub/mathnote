# V040 动态图：绕任意点旋转

数学源：本 UID 的六段 TeX、meta.json（只读）。中心 B=(1,1)，P=(4,2)，相对坐标(3,1)。

1. 建立原坐标轴、固定中心 B、原点 O、原向量 BP 和参考圆。Q 初始与 P 重合。
2. θ 从0变为45°再到90°，在关键角停顿；BP=BQ=√10 始终成立。圆弧从 BP 方向起算。
3. 回到0，再演示−45°的顺时针转动；角度符号与运动同步。
4. 回到0，将 BP 拆成横向3和纵向1，显示旋转后的首尾相接路径 B→H→Q，再共同转到45°。两段始终垂直；合成端点与 Q 完全一致。
5. 停顿展示 Q=(1+√2,1+2√2)，再真实旋转回0，恢复与首帧相同的教学状态，连续循环。

画布576×1024，数学横纵单位等长。上方短标题；中央图形；下方角度、不变量与相对坐标公式。品牌两行全程固定，不加入淡出组。

教学边界：一个固定数值例子解释通式的机制；不把数值示例冒称所有情形的证明，不在单张 GIF 塞入反求角度或椭圆例题。

预览构建：`scripts/manim/render.ps1 -Uid V040 -Scene V040ArbitraryCenterRotation -SceneFile scene_rotation.py -Name rotation_coordinates`。
完成本地审核后使用冻结 exporter 的 `-Publish -AssetName rotation_coordinates.gif` 写入用户指定 images；不覆盖、不执行 Publisher/Content Package/Sync。
