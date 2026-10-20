# C012 GIF 验收记录

日期：2026-10-20。仅新增本 UID manim/ 源码与 images/ellipse_tangent_origin_distance.gif。
保留原有六段 TeX、meta.json、PDF 和 PNG，包括开始前已有的工作树修改。

| Gate | 状态 | 实际证据 |
|---|---|---|
| M 数学自动测试 | PASS | unittest 6 项通过；三组轴长、全周采样，验证椭圆点、相切、真实垂足及正交关系、欧氏焦半径、乘积定值、距离范围、端点、一般式裁切与定义域 |
| M 数学关键状态 | PASS | a=3,b=2；t=45° 时几何平均数 √6.5≈2.55、d=6/√6.5≈2.35；长轴端点 d=3、几何平均数2；短轴端点 d=2、几何平均数3；端点 H=P |
| V 本地关键帧 | PASS | 从最终 GIF 提取 0、4.8、8、12、15.8、20.5、22.8、24.8 秒；查看 contact.png 与原尺寸开头、公式和端点帧；纵轴标签移到切线裁切区域外 |
| T 教学表达 | PASS | 虚线 OP 与真实垂距 OH 区分；两项反向变化保持乘积6；同一坐标表达式解释补偿；轴顶点展示正确最值，端点运动结束后才宣告 H=P |
| G 全帧技术 | PASS | 576×1024，305帧、229不同帧，25.41秒，80–90 ms/帧，无限循环，3,501,239 bytes，0黑帧；Pillow 再次全帧解码，0纯色帧；见 render.log / frame_review.json |
| LOCAL PRODUCTION | PASS | 共享冻结工具隔离生产、验证，随后显式新增 UID images 文件；没有覆盖已有正式资源 |
| USER VISUAL | PENDING | 待用户观看确认 |
| ANDROID DEVICE | PENDING | 待用户真机确认字体、线条、裁切与循环 |
| FINAL FREEZE | PENDING | 本地结果不代替用户与 Android 验收 |
| UID images 写入 | PASS | 正式新增 GIF 与隔离产物 SHA-256 相同 |
| Publisher / Content Package / Sync / APK | PENDING | 未执行，不在本次范围 |

本地视觉评分 91/100：数学图形24/25、层级18/20、可读性18/20、配色14/15、运动9/10、整体8/10。端点几条线真实重合，颜色区分随几何退化减弱；通过端点说明和数值读数辅助辨认。评分仅为本地判断。

证据：build/manim/C012/origin_distance/ 下的 math_tests.log、render.log、publish.log、protected_hashes.json、frame_review.json、contact.png、key_00.png 至 key_07.png。
原有12个文件的哈希复核无变化；共享工具和其他 UID 未改动。
隔离与正式 GIF 的 SHA-256 均为 D1A3D8B5C0DE0A6DEAB4037E4491A70241FE9821C75219748CFD5CA05814E6DD。
首尾 RGB 平均绝对差约 0.43/0.33/0.30（255量级），内容返回起始状态，调色板有轻微差异。
审计现行 prepare_knowledge_images.mjs：直接扫描 PNG/GIF，GIF 保留扩展名并原样复制，无同名冲突；本次没有运行包发布。
