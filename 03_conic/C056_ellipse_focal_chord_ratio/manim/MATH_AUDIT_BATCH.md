# C056 数学审计差异

正式条件指定右焦点 F(c,0)，A=F+r(cosθ,sinθ)，B=F−s(cosθ,sinθ)，r,s 为正距离。

将两点代入椭圆方程可得：

- AF=b²/(a+c cosθ)；
- BF=b²/(a−c cosθ)；
- AF/BF=(1−e cosθ)/(1+e cosθ)。

正式 01_statement.tex 的焦半径与比例公式把上述正负号颠倒。这不是渲染问题：例如 θ=0 时 A 是右顶点，AF=a−c，必小于 BF=a+c；原公式却给出相反结果。

本次 GIF 使用上述正确公式及真实右焦点模型，逐点验证两端点属于椭圆及实际距离比。正式 TeX、meta 与 PDF 未修改。通径处 AF=BF 和总弦长公式不受此问题影响。

此差异不影响动画本身的数学自动测试通过，但“与正式原文完全一致”不能标记 PASS；源文一致性记录为 FAIL（待另行修订原文）。Android 与用户视觉验收 PENDING。

## 2026-10-21 正式知识源修复补记

已按本次用户授权修正正式六段 TeX、meta.json，并重编译同步本 UID 的 PDF。上述历史记录中的源文差异已解决；详细错误与核验见 `docs/audits/03_conic_math_audit_20261021.md`。本次没有改动既有 GIF 或动画模型，未重新执行动画全帧验收；用户视觉、Android 与 FINAL FREEZE 状态仍为 PENDING。
