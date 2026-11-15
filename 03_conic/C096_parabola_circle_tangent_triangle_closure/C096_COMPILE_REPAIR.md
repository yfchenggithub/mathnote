# C096 PDF 编译修复

日期：2026-11-14。仅修复 C096 的项目模板兼容性及既有图标签位置。

## 原因与修改

项目构建器先加载公共 `preamble.tex`、`settings.tex`，再在正文中引入 UID 的 `main.tex`。原 C096 入口却包含独立文档的 `documentclass`、宏包、重复框环境及 `begin/end document`。实际复现首个错误为 `LaTeX Error: Can be used only in preamble`，指向原 main.tex 第3行的 documentclass。

- main.tex 改为项目标准的 Conclusion、subsection 和六段正文引用，路径从仓库根目录解析。
- 02_explanation.tex 去掉仅由原独立宿主加载的 Needspace 命令，避免未定义命令；保留正文、两幅既有 TikZ 和全部数学推导。
- 核心图仅移动曲线、圆心、切点标签，避免与坐标轴、曲线及半径线相挤；几何坐标不变。
- meta.json 同步记录修复范围。未修改公共模板或构建脚本。

## 验证

标准单 UID 构建成功，输出 `pdfs/C096_parabola_circle_tangent_triangle_closure.pdf`，共10页、A4、未加密。使用独立预览映射：

```powershell
python -B scripts/build_conclusion_pdfs.py C096 --overwrite --output-to-conclusion-pdfs --map-json .tmp/C096_conclusion_pdf_map.preview.json
```

入口检查通过：无嵌套文档或宏包定义；六个引用均实际存在；meta.json 可解析。全部页面以180 DPI渲染检查，既有两图以300 DPI放大检查。正文中文显示正常。

本次为编译故障修复，未作整篇教学完善验收；首页和各证明方法的配图补齐不属于本次修改。未将编译通过表述为整篇已完善。
