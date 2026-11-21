# 本条GIF编码与复核

已执行共享冻结render/export/verify。缩放预览曾疑似有公式笔画缺失；随后对原始关键帧做高倍裁切与像素对照，确认原始公式完整，未证实转码缺字。

本条最终副本采用UID内export_full_frames.py进行保守编码：完整调色板、关闭透明差分；不改变数学模型、Scene、运动、时长和品牌。调用冻结verify_gif.py，再以拒绝覆盖的原子创建方式写入新资源。没有修改共享工具，没有执行Content Publisher/Sync。

最终GIF按顺序完整解码复核，保留真实关键帧。
