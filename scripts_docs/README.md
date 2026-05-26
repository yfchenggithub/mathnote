# Scripts 文档索引

## 项目概况

Mathnote 项目包含 **9 个 bat 文件**（根目录）和 **35 个脚本文件**（`scripts/` 目录），覆盖搜索索引构建、内容编译、元数据管理、PDF/SVG/WebP 生成、文本规范化等功能。

技术栈：Python（主力）、Node.js（KaTeX 渲染）、XeLaTeX（PDF 编译）

---

## 按使用频率排列

### 每次改内容必用 ⭐

| 脚本 | 调用方式 | 做什么 |
|------|----------|--------|
| `build.bat` | `build.bat full` / `build.bat toc` | 编译完整 LaTeX 文档 → PDF |
| `build_content_js.bat` | `build_content_js.bat` | 生成小程序详情页 JS 数据 |
| `scripts/build_search_bundle_js.py` | `python scripts/build_search_bundle_js.py` | 生成搜索索引 `search_bundle.js` |
| `check_meta_json.bat` | `check_meta_json.bat` | 校验所有 meta.json |
| `upgrade_meta.bat` | `upgrade_meta.bat` | 同步 meta.json 到最新 schema |

### 内容更新后偶尔用 🔧

| 脚本 | 调用方式 | 做什么 |
|------|----------|--------|
| `scripts/build_detail_page_js.py` | `python scripts/build_detail_page_js.py` | 构建详情页 JS（`build_content_js.bat` 的实际执行者） |
| `scripts/normalize_text_typography.py` | `python scripts/normalize_text_typography.py` | 全仓库标点/排版规范化 |
| `scripts/fix_math_punctuation.py` | `python scripts/fix_math_punctuation.py` | 修复 LaTeX 数学环境内中文标点 |
| `scripts/meta_schema_sync.py` | `python scripts/meta_schema_sync.py` | meta.json 同步补全 |
| `scripts/check_meta_json.py` | `python scripts/check_meta_json.py` | meta.json 校验 |
| `scripts/extract_backend_index_from_search_bundle.py` | `python scripts/extract_backend_index_from_search_bundle.py` | 从 search_bundle.js 提取后端 JSON 索引 |

### 媒体生成（需要时用） 🎨

| 脚本 | 调用方式 | 做什么 |
|------|----------|--------|
| `scripts/build_conclusion_pdfs.py` | `python scripts/build_conclusion_pdfs.py` | 选定的结论 → 独立 PDF |
| `scripts/build_svg_dvisvgm.py` | `python scripts/build_svg_dvisvgm.py` | LaTeX → PDF → SVG |
| `scripts/build_webp.py` | `python scripts/build_webp.py` | LaTeX → PDF → WebP 图片 |
| `scripts/export_pdf_pages.py` | `python scripts/export_pdf_pages.py` | PDF 页面导出为高清图片 |
| `encrypt_pdf.bat` | `encrypt_pdf.bat <in> <out> <user>` | PDF 权限加密 |

### 目录/脚手架（项目初始化/扩展时用） 🏗

| 脚本 | 调用方式 | 做什么 |
|------|----------|--------|
| `scripts/create_pipeline_input_dirs.py` | `python scripts/create_pipeline_input_dirs.py` | 批量创建 Ixxx 流水线目录 |
| `scripts/create_prefixed_dirs_files.py` | `python scripts/create_prefixed_dirs_files.py` | 批量创建子文件 |
| `scripts/clean_i_dirs_files.py` | `python scripts/clean_i_dirs_files.py` | 批量删除指定文件 |
| `scripts/unify_module_naming.py` | `python scripts/unify_module_naming.py` | 大规模重命名规范化 |

### Node.js KaTeX 渲染（流水线调用） 📐

| 脚本 | 调用方式 | 做什么 |
|------|----------|--------|
| `scripts/latex_to_html.js` | `node scripts/latex_to_html.js < input.json` | 批量 LaTeX → HTML |
| `scripts/latex_to_html_single.js` | `echo "c^2=a^2+b^2" \| node scripts/latex_to_html_single.js` | 单条 LaTeX → HTML |
| `scripts/latex_block_splitter.js` | `node scripts/latex_block_splitter.js` | LaTeX 块拆分（被 latex_to_html.js 调用） |
| `scripts/test_katex.js` | `node scripts/test_katex.js` | KaTeX 安装测试 |

### 旧版/已废弃（建议不再使用） ⚠

| 脚本 | 原用途 | 被什么取代 |
|------|--------|-----------|
| `build_search_index.bat` | 旧倒排索引 | `build_search_bundle_js.py` |
| `build_all_indexes.bat` | 旧多文件索引 | `build_search_bundle_js.py` |
| `build_core_indexes.bat` | 兼容包装器 | 直接用 `build_search_bundle_js.py` |
| `build_content_json.bat` | 旧内容 JSON | `build_detail_page_js.py` |
| `scripts/build_search_index.py` | 旧倒排索引 | `build_search_bundle_js.py` |
| `scripts/build_all_indexes.py` | 旧多文件索引 | `build_search_bundle_js.py` |
| `scripts/build_core_index.py` | 兼容包装器 | `build_search_bundle_js.py` |
| `scripts/build_content_json.py` | 实验性构建 | `build_detail_page_js.py` |
| `scripts/build_statement_card_js.py` | 兼容包装器 | `build_detail_page_js.py` |
| `scripts/fix_prompt_quotes.py` | 旧引号修复 | `normalize_text_typography.py` |

### 一次性/迁移脚本（已完成使命） ✅

| 脚本 | 用途 | 是否还需要 |
|------|------|-----------|
| `scripts/unify_module_naming.py` | 模块命名规范化 | 已完成，保留备用 |
| `scripts/upgrade_module_index.py` | 编号 2 位→3 位升级 | 已完成，保留备用 |
| `scripts/migrate_detail_js_to_content_v2.py` | 内容协议迁移 v1→v2 | 新增内容时可能需要 |
| `scripts/verify_detail_js_to_content_v2_integrity.py` | 迁移后校验 | 迁移时配套使用 |

### 空/占位文件

| 脚本 | 说明 |
|------|------|
| `scripts/meta_utils.py` | 0 字节，预留占位 |

---

## 根目录 bat 文件一览

| 文件 | 状态 | 功能 |
|------|------|------|
| `build.bat` | 活跃 | 主 PDF 编译入口 |
| `build_content_js.bat` | 活跃 | 详情页 JS 构建 |
| `encrypt_pdf.bat` | 活跃 | PDF 加密 |
| `upgrade_meta.bat` | 活跃 | Meta 同步 |
| `check_meta_json.bat` | 活跃 | Meta 校验 |
| `build_core_indexes.bat` | 旧版 | 兼容包装 |
| `build_search_index.bat` | 旧版 | 旧索引 |
| `build_all_indexes.bat` | 旧版 | 旧索引 |
| `build_content_json.bat` | 旧版 | 旧内容构建 |

---

## 核心数据流

```
meta.json (每个结论)
    │
    ├── build_search_bundle_js.py  ──→ data/index/search_bundle.js  (搜索索引)
    │
    ├── build_detail_page_js.py    ──→ data/content/07_inequality.js (详情页数据)
    │                                     │
    │                                     └── migrate_detail_js_to_content_v2.py
    │                                              │
    │                                              └── content_v2/*.json
    │
    ├── build_conclusion_pdfs.py   ──→ build/I001_xxx.pdf
    ├── build_svg_dvisvgm.py       ──→ *.final.clean.svg
    ├── build_webp.py              ──→ *.webp
    │
    └── latex_to_html.js           ──→ HTML (KaTeX 渲染)
```

详细参考见 `scripts_reference.md`。
