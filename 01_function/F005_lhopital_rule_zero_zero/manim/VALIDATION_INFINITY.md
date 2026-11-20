# F005 无穷比无穷型 GIF 验收

日期：2026-11-20。状态：LOCAL PRODUCTION PASS。

事实源为本UID六段TeX与meta.json，采用04_examples.tex例5。未修改数学正文、metadata、原Scene、原模型、PDF或既有图片/GIF。

## 数学与教学

- Gate M PASS：4项新增自动测试；761个有理数精确核验比值恒等式，77处精确中心差分核验二次多项式导数，增长下界及误差界核验。原零比零模型测试亦PASS。
- f=2x²+3x+1、g=x²+1均趋于正无穷；g′=2x在所示正数范围非零。
- f/g=2+(3x−1)/(x²+1)，f′/g′=2+3/(2x)，均趋于2；在有限x处并不相等。
- Gate T PASS：函数增大后切到比值坐标；动点、数值与坐标同步，保留水平线2和有限位置说明。此片为具体例子的教学演示，不声称一般定理的证明。

## 图像与技术

- Gate V PASS（本地人工）：真实GIF关键帧0、36、72、90、132、168、195、224已查看；0、90、72、224还按原分辨率检查。修正首帧及转场初始数值定位后复验。
- Gate G PASS：576×1024，225帧，18.75秒，12FPS，无限循环；全帧完整解码，0黑帧，边缘无内容裁切，数值读数区域全帧存在（淡出转场不作此断言）。
- 两行品牌全程固定。GIF量化/视频压缩使品牌边缘抗锯齿像素有细微变化，不能用RGB逐像素哈希全相同作判据；实测深色字形差异最大0.212%，每帧可见深色像素至少2437，无位置变化。补充检查以0.5%字形差异阈值验证。
- 字号、曲线、颜色及公式已按576px宽本地检查。辅助刻度较小，仍待真机确认。

## 放置及保护

通过冻结export_gif.ps1显式-Publish写入images/infinity_ratio.gif，未使用-Overwrite。正式文件与验收预览SHA-256相同。任务前已有文件全部哈希不变，包括zero_ratio.gif。没有运行Publisher、Content Package、Sync或APK构建。

USER VISUAL PASS：PENDING；ANDROID DEVICE PASS（Gate D）：PENDING；FINAL FREEZE：PENDING。由用户实际设备查看确认后再更新状态。
