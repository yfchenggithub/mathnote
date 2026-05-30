# 升级二级结论详情内容

修改模块下的 `.tex` 源文件（`01_statement.tex`、`02_explanation.tex` 等）后，运行以下四条命令即可将变更同步到前端数据。

## 命令顺序

### 1. 重建后端索引与规范内容

```bash
python.exe .\scripts\build_backend_and_canonical.py --module 07_inequality
```

从模块的 `.tex` 源文件 + `meta.json` 重新生成：
- `data/search_engine/backend_search_index.json` — 搜索索引
- `data/content/canonical_content_v2.json` — 前端详情页数据

`--module` 可重复指定多个模块，不传则全量构建。

### 2. 标记需要渲染为图片的公式

```bash
python.exe .\scripts\mark_need_image_by_latex_length.py --min-length 5
```

扫描 `canonical_content_v2.json`，对 `latex` 字段长度超过阈值的 `math_block` 节点添加 `need_image: "true"` 标记。

`--min-length 5` 表示公式 LaTeX 源码超过 5 个字符就标记（默认阈值 30，对二级结论内容偏宽松，5 能覆盖更多短公式）。

### 3. 渲染公式图片

```bash
node .\scripts\render_math_assets.mjs --in-place
```

根据上一步的 `need_image` 标记，将 `math_block` 节点中的 LaTeX 公式渲染为 PNG + WebP 图片，并原地改写为 `math_image` 节点（含图片路径和尺寸信息）。

`--in-place` 表示直接覆盖输入的 `canonical_content_v2.json`，无需指定额外输出路径。

### 4. 清理公式图片后的多余句号

```bash
python.exe .\scripts\remove_math_image_following_period.py --write
```

渲染后的 `math_image` 令牌在段落中可能紧跟一个中文句号 `。`，此命令将其移除。

不加 `--write` 为演练模式，只输出统计不写入文件。

## 典型场景

修改 `07_inequality/` 下某个结论的 `.tex` 文件后：

```bash
python.exe .\scripts\build_backend_and_canonical.py --module 07_inequality
python.exe .\scripts\mark_need_image_by_latex_length.py --min-length 5
node .\scripts\render_math_assets.mjs --in-place
python.exe .\scripts\remove_math_image_following_period.py --write
```

如果同时改了多个模块：

```bash
python.exe .\scripts\build_backend_and_canonical.py --module 07_inequality --module 08_trigonometry
python.exe .\scripts\mark_need_image_by_latex_length.py --min-length 5
node .\scripts\render_math_assets.mjs --in-place
python.exe .\scripts\remove_math_image_following_period.py --write
```

## 数据流

```
模块 .tex 源文件 + meta.json
        │
        ▼
build_backend_and_canonical.py
        │
        ├──────────────────────────────────┐
        ▼                                  ▼
canonical_content_v2.json          backend_search_index.json
        │
        ▼
mark_need_image_by_latex_length.py
        │
        ▼
render_math_assets.mjs
        │
        ▼
remove_math_image_following_period.py
        │
        ▼
  最终前端数据（math_image 节点 + 无多余句号）
```
