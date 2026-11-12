# 重心与内心 GIF 验收（2026-11-12）

产物：images/centroid_incenter.gif，576×1024，24.33 秒，292 帧，222 个不同帧，4559248 字节，80–90ms 帧时长，无限循环。

| Gate | 状态 | 实际证据 |
| --- | --- | --- |
| M 数学 | PASS | test_centers.py 两项测试实际通过；三条形变路径各121个样本，核对中线分点、三边等距、权重插值轨迹及等边、直角精确状态。公式与当前正式知识源一致。 |
| V 本地视觉 | PASS | 修订后 GIF 的第0、70、130、150、185、225、260、291帧检查，无明显裁切；重合处使用 G=I 标签，中线虚线、角平分线实线。 |
| T 教学 | PASS | 一般→等边重合→直角分开→固定三角形改变权重；移动计算点明确记为 P，G、I保持各自数学身份。离开等边状态前切换三边相等说明。 |
| G 技术 | PASS | 冻结共享验证器全292帧解码通过，无黑帧，多帧真实运动、无限循环；真实首尾与关键帧已检查。底部两行由固定对象全程保留，关键帧可见。 |
| D Android | PENDING | 尚无用户真机确认。 |

LOCAL PRODUCTION PASS；USER VISUAL PENDING；ANDROID DEVICE PENDING；FINAL FREEZE PENDING。关键帧、拼图和渲染日志在 build/manim/V009/centroid_incenter/。

通过共享 export_gif 的 Publish 显式落盘新文件，不执行 Content Package、Sync 或 APK。原 incenter.gif 保留，记录 SHA256：AD0091DE17B427DB3B7FA76DA9C5A8B67F98E47091503F03705BF3C1743A678A。正式 TeX、meta.json、PDF和PNG未编辑。
