# P033 GIF 本地生产验收（2026-11-11）

状态：**LOCAL PRODUCTION PASS**。USER VISUAL、ANDROID DEVICE、FINAL FREEZE 均为 **PENDING**。
用户已明确要求写入本 UID 的 images，因此使用冻结导出器的显式 publish 分支新增三个文件；
没有使用 overwrite，没有执行知识包 Publisher、Zhishu Sync、APK 构建或 Git 提交。

## 产物

| images 中的新文件 | 尺寸 | 帧数 | 时长 | 字节数 |
|---|---|---:|---:|---:|
| P033_incenter_area.gif | 576×1024 | 254 | 21.16 秒 | 2,656,041 |
| P033_tangent_lengths.gif | 576×1024 | 254 | 21.16 秒 | 1,779,535 |
| P033_special_triangles.gif | 576×1024 | 216 | 18.00 秒 | 1,786,638 |

三条均无限循环，帧间隔 80—90 ms，真实变化帧数分别为 183、147、90。
新文件名称符合当前 Publisher 对直接 PNG/GIF 资源的命名与读取方式。
正式 GIF 与对应已审核 staging GIF 的 SHA-256 完全相同。

## 分别验收

| Gate | 状态 | 实际证据 |
|---|---|---|
| M 数学 | PASS | 8 项测试；连续运动 481 个状态；正交投影、三条半径、相切、面积和、切线段及特殊三角形核验 |
| V 本地视觉 | PASS | 实际 GIF 关键帧及首尾检查；字母、公式与图形对应；移动内心标签避开辅助线；ℓ 与数字 1 区分；斜边明确标为 w 或 √2t |
| T 教学表达 | PASS | 三个独立短动画；先构造再概括，面积分块和切线段配对逐步显示；特殊三角形明确建系条件 |
| G GIF 技术 | PASS | 正式文件完整解码，共 724 帧；无限循环；无黑帧；无空白教学区域帧；首尾同一状态 |
| A 架构 | PASS | 现有 2 项 rendering-boundary 测试通过；模型、Scene、测试均在 P033/manim；共享工具未改动 |
| D Android 真机 | PENDING | 未执行、未获用户确认；不能以本地检查代替 |

底部全程固定为：

> 查结论 · 看图解 · 学证明｜知树 App
>
> 公众号 ok-shuxue｜获取入口

Scene 中品牌对象不参与淡出。全帧比较底部区域，允许 MP4 有损编码与 GIF 调色板造成的
RGB 平均差小于 2/255；实际最大值小于 1/255。首尾全图平均差小于 1/255。
这是新增的 P033 专属检查；没有修改或削弱共享 verify_gif.py 的校验。
初版特殊三角形切换及面积循环曾出现短暂空白，已改为同步切换，重渲染后全帧检查通过。

## 测试与构建

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv-manim\Scripts\python.exe -B -m unittest discover -s 09_geometry-plane/P033_incenter_incircle_radius/manim -p test_model.py -v
.\.venv-manim\Scripts\python.exe -B -m unittest tests.test_rendering_boundaries -v
```

分别为 8/8、2/2 通过。边界测试首次在 Python 3.14 临时目录遇到 Windows ACL 拒绝访问；
以隔离的 build/manim/P033-production-20261111/test-temp 重跑并提升进程权限后通过，未修改测试。

三个 Scene 使用同一现有入口，每条独立绑定 Name：

```powershell
.\.venv-manim\Scripts\python.exe -B scripts/manim/production.py render --uid P033 --scene P033IncenterArea --scene-file scene.py --name incenter_area --build-root build/manim/P033-production-20261111
.\.venv-manim\Scripts\python.exe -B scripts/manim/production.py render --uid P033 --scene P033TangentLengths --scene-file scene.py --name tangent_lengths --build-root build/manim/P033-production-20261111
.\.venv-manim\Scripts\python.exe -B scripts/manim/production.py render --uid P033 --scene P033SpecialTriangles --scene-file scene.py --name special_triangles --build-root build/manim/P033-production-20261111
```

先执行对应 export 并人工检查实际 GIF，再加 --publish 与独立 --asset-name 显式写入 images。
默认重跑不得直接覆盖 images 中同名文件；正式源图的任何更新仍须明确授权。
render.ps1、export_gif.ps1 与上述 Python 命令调用的是同一冻结工具。

## 保留与证据

开始前记录了 17 个文件的 SHA-256：六段 TeX、meta.json、main/source、PDF、已有三张 PNG、
P033 的四个 TikZ 图源。结束后 **17 个均未改变**。
本轮只新增 P033 的 manim 源码/测试/文档与三个 GIF，不修改其他 UID。

隔离证据：build/manim/P033-production-20261111/

- baseline.json：原有内容和资源的基线哈希。
- final-audit.json：正式文件实际解码结果、哈希、staging 一致性及保护文件核对。
- review/：从实际 GIF 抽取的关键帧、联系表和全帧检查 JSON。
- 各 render/export/publish 日志及 Scene 时间标记位于对应独立构建目录。

下一步的真机验收只需播放三个 GIF，确认文字、图形、裁切和循环效果。
没有用户确认前，不标记 USER VISUAL PASS、ANDROID DEVICE PASS 或 FINAL FREEZE。
