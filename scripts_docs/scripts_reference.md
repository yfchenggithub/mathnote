# Scripts 完整参考

---

## 一、搜索与索引脚本

### `build_search_bundle_js.py` ⭐ 主力

**状态：** 活跃，当前搜索引擎核心

**功能：** 从所有 `meta.json` 文件生成统一的 JS 搜索包 `search_bundle.js`。输出包含 termIndex（精确词索引）、prefixIndex（前缀索引）、suggestions（建议列表）、fieldMaskLegend（字段掩码）、docs（含排序权重）等完整搜索数据结构。

**用法：**
```bash
# 默认运行
python scripts/build_search_bundle_js.py

# 只处理指定模块
python scripts/build_search_bundle_js.py --module 07_inequality

# 只处理指定条目
python scripts/build_search_bundle_js.py --ids I001,I002,I005

# dry-run（不写文件）
python scripts/build_search_bundle_js.py --dry-run

# 调试模式（输出详细匹配信息）
python scripts/build_search_bundle_js.py --debug

# 严格 meta schema 校验
python scripts/build_search_bundle_js.py --strict
```

**输入：** 所有模块目录下的 `**/meta.json`
**输出：** `data/index/search_bundle.js`（CommonJS module）
**依赖：** Python 标准库

---

### `extract_backend_index_from_search_bundle.py`

**状态：** 活跃

**功能：** 将前端的 CommonJS `search_bundle.js` 提取为标准 JSON 格式的后端索引。使用递归下降解析器解析 JS 对象字面量。

**用法：**
```bash
python scripts/extract_backend_index_from_search_bundle.py
```

**输入：** `data/index/search_bundle.js`
**输出：** `backend_search_index.json`

---

### `verify_backend_index_extraction.py`

**状态：** 活跃

**功能：** 验证提取的后端 JSON 索引与原始 search_bundle.js 完全一致。通过深度结构化比较和 SHA256 指纹进行校验。

**用法：**
```bash
python scripts/verify_backend_index_extraction.py
```

---

### `build_all_indexes.py` ⚠ 旧版

**状态：** 旧版，保留向后兼容

**功能：** 旧的多文件搜索引擎索引构建器。生成 7 个独立 JSON 文件：keyword_index、prefix_index、pinyin_index、formula_index、ranking_index、meta_compact、suggestion_index。

**用法：**
```bash
python scripts/build_all_indexes.py
```

**依赖：** `pypinyin`
**取代者：** `build_search_bundle_js.py`（单文件，更高效）

---

### `build_search_index.py` ⚠ 旧版

**状态：** 旧版

**功能：** 最简单的倒排索引构建器，只生成关键字到结论 ID 的映射。

**用法：**
```bash
python scripts/build_search_index.py
```

**输出：** `search_index.json`
**取代者：** `build_all_indexes.py` → `build_search_bundle_js.py`

---

### `build_core_index.py` ⚠ 兼容包装

**状态：** 兼容包装器

**功能：** 导入并调用 `build_search_bundle_js.py` 的 `main()`。底部有一段注释掉的备用实现。

**用法：**
```bash
python scripts/build_core_index.py
```

**建议：** 直接使用 `build_search_bundle_js.py`。

---

## 二、内容构建脚本

### `build_detail_page_js.py` ⭐ 主力

**状态：** 活跃，当前详情页数据构建核心

**功能：** 从 `meta.json` 和 LaTeX 源文件构建微信小程序详情页所需的 JS 数据文件。包含字段映射、LaTeX 清理、展示友好格式化。

**用法：**
```bash
# 默认运行
python scripts/build_detail_page_js.py

# 只处理指定模块
python scripts/build_detail_page_js.py --module 07_inequality

# 只处理指定条目
python scripts/build_detail_page_js.py --ids I001,I002

# dry-run
python scripts/build_detail_page_js.py --dry-run

# 调试
python scripts/build_detail_page_js.py --debug
```

**输入：** `meta.json` + LaTeX 源文件
**输出：** `data/content/07_inequality.js`（JS module，export 结构化数据）

---

### `build_content_json.py` ⚠ 实验性/已弃用

**状态：** 已弃用

**功能：** 早期的最小 LaTeX→JSON 构建器。硬编码路径，`TARGET_MODULES` 只有 `"07-inequality"`，其他模块被注释。似乎是一次尝试后就被搁置了。

**用法：**
```bash
python scripts/build_content_json.py
```

**取代者：** `build_detail_page_js.py`

---

### `build_statement_card_js.py` ⚠ 兼容包装

**状态：** 兼容包装器

**功能：** 仅导入 `build_detail_page_js.py` 的 `main()` 并执行。无独立逻辑。

**建议：** 直接使用 `build_detail_page_js.py`。

---

### `migrate_detail_js_to_content_v2.py`

**状态：** 活跃（迁移时使用）

**功能：** 将旧版详情页 JS 数据迁移到跨端 canonical `content_v2` JSON 协议。输出结构化迁移报告，逐条标注状态。使用 Pydantic 进行 schema 校验。

**用法：**
```bash
python scripts/migrate_detail_js_to_content_v2.py
```

---

### `verify_detail_js_to_content_v2_integrity.py`

**状态：** 活跃（迁移时使用）

**功能：** 验证从 detail JS 到 canonical v2 JSON 的迁移完整性。生成 JSON 和 Markdown 两份报告。

**用法：**
```bash
python scripts/verify_detail_js_to_content_v2_integrity.py
```

---

### `content_v2.py`

**状态：** 活跃（模型定义）

**功能：** Canonical content v2 协议的 Pydantic 模型定义文件。定义 TextToken、MathInlineToken、MathDisplayToken、MathBlock、Section 等类型，使用 `extra="forbid"` 进行严格校验。

**用法：** 被 `migrate_detail_js_to_content_v2.py` 和 `verify_detail_js_to_content_v2_integrity.py` 导入使用。

---

## 三、元数据 Schema 与质量脚本

### `meta_schema.py` ⭐ 核心定义

**状态：** 活跃，整个项目的 schema 中心

**功能：** 定义 `META_SCHEMA` 字典，包含 35+ 个字段的类型、默认值、描述。涵盖搜索字段、内容字段、资产字段、渲染字段、统计字段等。每个 `meta.json` 都遵循此 schema。

**用法：** 被 `meta_schema_sync.py`、`check_meta_json.py`、`build_detail_page_js.py` 等导入。

---

### `meta_schema_sync.py`

**状态：** 活跃

**功能：** 按照 `META_SCHEMA` 同步/补全/清理所有 `meta.json` 文件。

**用法：**
```bash
# 默认（安全模式：只补全缺失字段，不删除额外字段）
python scripts/meta_schema_sync.py

# 严格模式（删除额外字段）
python scripts/meta_schema_sync.py --strict

# dry-run（预览变更）
python scripts/meta_schema_sync.py --dry-run

# 只处理指定模块
python scripts/meta_schema_sync.py --module 07_inequality

# 处理单个文件
python scripts/meta_schema_sync.py --file path/to/meta.json

# 检查重复 ID
python scripts/meta_schema_sync.py --check-duplicates
```

**输入：** 所有 `**/meta.json`
**输出：** 更新后的 `meta.json`（同步后）

---

### `check_meta_json.py`

**状态：** 活跃

**功能：** 只读校验所有 `meta.json` 文件。检查：schema 合规性、路径与 module/id 一致性、contentBlocks 结构。

**用法：**
```bash
python scripts/check_meta_json.py
```

**输出：** `meta_check_report.json`（校验报告）

---

### `meta_utils.py`

**状态：** 空占位文件（0 字节）

---

## 四、文本规范化脚本

### `normalize_text_typography.py`

**状态：** 活跃

**功能：** 全仓库范围的标点符号和排版规范化引擎。内置规则集处理引号、中文标点、空格等。

**用法：**
```bash
# dry-run（预览变更）
python scripts/normalize_text_typography.py --dry-run

# 实际修改
python scripts/normalize_text_typography.py

# 指定文件
python scripts/normalize_text_typography.py --file path/to/file.tex

# 自定义扩展映射
python scripts/normalize_text_typography.py --ext-map custom.json
```

**注意：** 会处理文件的编码标记（BOM），注意备份。

---

### `fix_math_punctuation.py`

**状态：** 活跃

**功能：** 专门修复 LaTeX 数学环境内的中文标点符号。将数学环境（`equation`、`align`、`gather` 等）中的 `。` 替换为 `.`，`，` 替换为 `,`。

**用法：**
```bash
# dry-run
python scripts/fix_math_punctuation.py --dry-run

# 实际修改
python scripts/fix_math_punctuation.py

# 指定结论 ID
python scripts/fix_math_punctuation.py --ids I001,I005
```

---

### `fix_prompt_quotes.py` ⚠ 兼容包装

**状态：** 兼容包装器（0.3 KB）

**功能：** 旧命令名兼容，代理到 `normalize_text_typography.py`。

**建议：** 直接使用 `normalize_text_typography.py`。

---

## 五、PDF / SVG / WebP 生成脚本

### `build_conclusion_pdfs.py`

**状态：** 活跃

**功能：** 将选定的结论编译为独立 PDF，并生成 ID→文件名映射 JSON。

**用法：**
```bash
# 全部结论
python scripts/build_conclusion_pdfs.py

# 指定模块
python scripts/build_conclusion_pdfs.py --module 07_inequality

# 指定 ID
python scripts/build_conclusion_pdfs.py --ids I001,I002,I005

# 按名称过滤
python scripts/build_conclusion_pdfs.py --name-filter "柯西"

# dry-run
python scripts/build_conclusion_pdfs.py --dry-run
```

**依赖：** XeLaTeX、latexmk

---

### `build_svg_dvisvgm.py`

**状态：** 活跃

**功能：** 将结论的 LaTeX 源文件编译为高质量 SVG。流程：合并 01-06.tex → 编译 PDF → pdfcrop 裁剪 → dvisvgm 转 SVG → SVGO 优化。

**用法：**
```bash
# 处理指定条目
python scripts/build_svg_dvisvgm.py --ids I001,I002

# 跳过 pdfcrop
python scripts/build_svg_dvisvgm.py --no-crop

# 水印淡化
python scripts/build_svg_dvisvgm.py --fade-watermark
```

**依赖：** XeLaTeX、pdfcrop、dvisvgm、SVGO（svgo.config.js）

**输出：** `*.final.clean.svg`

---

### `build_webp.py`

**状态：** 活跃

**功能：** 将结论的 LaTeX 源文件转换为 WebP 图片。流程：合并 01-06.tex → 编译 PDF → pdfcrop → ImageMagick 转换。

**用法：**
```bash
python scripts/build_webp.py --ids I001,I002
```

**参数：** 密度 300 DPI，质量 90，宽度 2000px（可在脚本内调整）

**依赖：** XeLaTeX、pdfcrop、ImageMagick

---

### `export_pdf_pages.py`

**状态：** 活跃

**功能：** 将 PDF 的特定页面/范围/全部导出为高分辨率图片。支持小红书 3:4 封面格式。

**用法：**
```bash
# 导出全部页面
python scripts/export_pdf_pages.py --input main.pdf

# 导出特定页面
python scripts/export_pdf_pages.py --input main.pdf --pages 1,3,5

# 导出页面范围
python scripts/export_pdf_pages.py --input main.pdf --pages 1-10

# 小红书封面格式
python scripts/export_pdf_pages.py --input main.pdf --xiaohongshu
```

**依赖：** Poppler (`pdftoppm`)

---

### `encrypt_pdf.py`

**状态：** 活跃

**功能：** 使用 pikepdf 给 PDF 设置权限保护（允许打印/复制，禁止修改）。

**用法：**
```bash
python scripts/encrypt_pdf.py <input.pdf> <output.pdf> <user_id>
```

**依赖：** pikepdf

---

## 六、目录脚手架与批量操作脚本

### `create_pipeline_input_dirs.py`

**状态：** 活跃

**功能：** 批量创建顺序编号的流水线输入目录及模板文件。支持 JSON 配置、占位符渲染。

**用法：**
```bash
# dry-run
python scripts/create_pipeline_input_dirs.py --dry-run

# 使用 JSON 配置
python scripts/create_pipeline_input_dirs.py --config example.json

# 指定起始编号和数量
python scripts/create_pipeline_input_dirs.py --start 1 --count 10
```

**占位符：** `[[id]]`、`[[number]]`、`[[number_padded]]` 等

**配置文件示例：** `scripts/create_pipeline_input_dirs.example.json`

---

### `create_prefixed_dirs_files.py`

**状态：** 活跃

**功能：** 在匹配模式的子目录内批量创建文件（如 `01_statement.tex`、`02_explanation.tex` 等）。

**用法：**
```bash
# dry-run
python scripts/create_prefixed_dirs_files.py --dry-run

# 指定模块
python scripts/create_prefixed_dirs_files.py --module 07_inequality

# 覆盖已存在文件
python scripts/create_prefixed_dirs_files.py --overwrite
```

**配置文件示例：** `scripts/create_prefixed_dirs_files.example.json`

---

### `clean_i_dirs_files.py`

**状态：** 活跃

**功能：** 在匹配模式的子目录内删除指定文件（保留目录结构）。

**用法：**
```bash
# 预览（安全，不实际删除）
python scripts/clean_i_dirs_files.py

# 实际删除（需确认）
python scripts/clean_i_dirs_files.py --apply
```

**配置文件示例：** `scripts/clean_i_dirs_files.example.json`

---

### `unify_module_naming.py` ✅ 已完成

**状态：** 已完成，保留备用

**功能：** 大规模重命名工具。规范化模块目录（`00-set` → `00_set`）和结论目录（`S01-` → `S001_`）。具有备份、TEMP 构建验证、回滚功能。

**用法：**
```bash
# dry-run
python scripts/unify_module_naming.py --dry-run

# 执行
python scripts/unify_module_naming.py --apply
```

**注意：** 对项目结构影响大，使用前确保备份。

---

### `upgrade_module_index.py` ✅ 已完成

**状态：** 已完成，保留备用

**功能：** 编号升级：`S01_xxx` → `S001_xxx`（2 位数字 → 3 位数字）。同步更新所有 `.tex` 文件中的引用。

**用法：**
```bash
# dry-run
python scripts/upgrade_module_index.py --dry-run

# 执行
python scripts/upgrade_module_index.py --apply
```

---

## 七、Node.js 脚本（KaTeX 渲染）

### `latex_to_html.js`

**状态：** 活跃

**功能：** 批量 LaTeX → HTML 渲染。从 stdin 读取 `[{id, text}]` JSON，输出 `{id: html}` JSON。自动拆分 statement/proof/examples 块，将 LaTeX 列表环境转换为 HTML `<ol>/<ul>`。内置 LRU 缓存。

**用法：**
```bash
node scripts/latex_to_html.js < input.json > output.json
```

**输入格式：**
```json
[{"id": "I001", "text": "\\section{...} ..."}]
```

**依赖：** KaTeX、`latex_block_splitter.js`

---

### `latex_to_html_single.js`

**状态：** 活跃

**功能：** 单条 LaTeX → HTML。从 stdin 读取原始 LaTeX 字符串，将 `$...$` 和 `$$...$$` 用 KaTeX 渲染，输出到 stdout。

**用法：**
```bash
echo "c = \sqrt{a^2 + b^2}" | node scripts/latex_to_html_single.js

# 或
node scripts/latex_to_html_single.js < formula.tex
```

**依赖：** KaTeX

---

### `latex_block_splitter.js`

**状态：** 活跃

**功能：** LaTeX 块拆分工具。按 `\item` 安全拆分 statement/proof，按 `\textbf{例题}` 拆分 examples。不破坏数学公式内的结构。被 `latex_to_html.js` 内部调用。

**用法：**
```bash
node scripts/latex_block_splitter.js < input.tex
```

---

### `test_katex.js`

**状态：** 活跃（测试工具）

**功能：** KaTeX 安装连通性测试。渲染 `c = \sqrt{a^2 + b^2}` 验证 KaTeX 正确安装。

**用法：**
```bash
node scripts/test_katex.js
```

---

## 八、配置文件

### `svgo.config.js`

**状态：** 活跃

**功能：** SVGO 优化配置，专为 LaTeX/dvisvgm 生成的 SVG 设计。禁用可能破坏几何精度的优化（合并路径、转换数据、组合分组）。保留 viewBox。精度设为 3。

**用法：** 被 `build_svg_dvisvgm.py` 通过 SVGO 自动调用。

---

### `meta.json`（scripts/ 目录下）

**功能：** 带默认值的空 `META_SCHEMA` 模板，用作新建结论的样板。

---

### `conclusion_record_v2.schema.json`

**功能：** 结论记录 v2 协议的 JSON Schema 定义（48 KB），供校验使用。

---

### 示例配置文件

- `create_pipeline_input_dirs.example.json`
- `create_prefixed_dirs_files.example.json`
- `clean_i_dirs_files.example.json`

以上为对应脚本的 JSON 配置示例文件，供首次使用时参考。
## 2026-05 Update: `build_detail_page_js.py` Formula Promotion

The rich-item parser in `build_detail_page_js.py` now performs an additional normalization/splitting step for generic sections (`explanation`, `proof`, `examples`, `traps`, `summary`):

- Detect display-like math (multi-line, environment-based, or long equation-chain).
- Promote those segments to standalone `{ latex }` items.
- Keep short math inline as `{ segments: [...] }`.
- Move trailing punctuation out of latex into adjacent text segments.

Why this change:

- Prevents core derivation formulas from being hidden inside inline mixed text.
- Improves migration quality to canonical v2 (`math_block` generation).
- Reduces inline overflow issues in mini-program detail rendering.
