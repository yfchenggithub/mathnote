# C092 GIF 本地验收（2026-11-01）

主题：交点在变，直角不变。正式目标为 `../images/confocal_orthogonality.gif`。
本次用户明确要求生成并放入 images；该目录原无同名 GIF，未使用覆盖选项。

| 验收项目 | 状态 | 实际证据 |
| --- | --- | --- |
| Gate M 数学模型 | PASS | `python -B -m unittest test_model.py`，3项测试通过；181组运动参数×4象限核验交点代回、焦半径和差、切向量、单位向量和差与切线的垂直关系、斜率积−1；另测近边界、非法条件与曲线采样 |
| 关键状态 | PASS | A=1时 P=(2,3)、斜率−1/2和2；A=0.65、1.55及往返中间态均用真实模型驱动，无手设假交点 |
| 真实关键帧 | PASS | 导出的GIF抽取0、2.8、6.5、9、11.3、14.6、17.5、18.9秒帧；检查八帧总览以及参数端点、四点直角的原尺寸帧；P标签避开切线，公式与曲线同步 |
| Gate G 全帧技术 | PASS | 576×1024，228帧、179个不同帧，19秒，80–90ms帧延时，无限循环，0黑帧；所有帧完整解码 |
| 全帧版面与品牌 | PASS | `verify_output.py`遍历228帧：图形区域始终非空，12像素安全边缘无内容；底部两行文案固定；允许MP4压缩/调色板抖动后，平均像素误差0.980/255，字形掩码差0.244%，无位移或消失 |
| Gate T 教学表达 | PASS | 明确椭圆固定、双曲线改变形状而焦点不变；展示切线夹角而非焦角；末尾四个公共点均标直角。图形以同一比例缩放，未以拉伸制造垂直 |
| Gate V 本地视觉 | PASS | 浅底、蓝橙曲线、绿色直角；正文及入口文案清晰；图形为主视觉；循环前撤去切线，回到开场状态。局部标签避让已修正并重渲染复核 |
| USER VISUAL PASS | PENDING | 等待用户观看GIF确认 |
| Gate D / ANDROID DEVICE PASS | PENDING | Android真机播放与可读性须用户确认 |
| FINAL FREEZE | PENDING | 未获得用户视觉与Android确认 |
| PUBLISHED / SYNCED | PENDING | 未运行Publisher、Content Package或Sync |

总体状态：**LOCAL PRODUCTION PASS**。写入 UID 的 images 仅为本次明确要求的本地资源交付，不等于应用发布或最终冻结。

构建证据位于 `build/manim/C092-production/C092/orthogonality/`：MP4、暂存GIF、source.json、qa/contact.png及full_frame_checks.json。
共享渲染、导出和技术检查工具保持原样；已核对现行Publisher从images直接发现GIF、要求正帧时长和无限循环、原字节复制的契约。
正式六段TeX和meta.json的7个SHA256与制作前一致；未改数学源、PDF、其他UID或共享工具。

底部固定文字：

```
查结论 · 看图解 · 学证明｜知树 App
公众号 ok-shuxue｜获取入口
```
