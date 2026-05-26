# 根目录 BAT 文件参考

## 活跃的 BAT 文件 ⭐

### `build.bat` — 主 PDF 编译入口

**状态：** 活跃，核心入口

**功能：** 编译完整 LaTeX 文档，生成 PDF 并输出加密副本。

**用法：**
```bat
set USER_ID=user001
build.bat full       完整编译（全文档）
build.bat toc        仅目录编译（快速预览）
```

**流程：**
1. 清理 `99_build/` 目录
2. 如果 `toc` 模式：运行 `scripts/generate_toc_seed.py` 生成 TOC seed
3. 用 XeLaTeX + latexmk 编译
4. 保存原始 PDF
5. 用 `scripts/encrypt_pdf.py` 加密（允许打印/复制，禁止修改）
6. 输出到 `99_build/` 和 `99_build/encrypted/`

**依赖：** XeLaTeX、latexmk、Python（pikepdf）

---

### `build_content_js.bat` — 详情页 JS 构建

**状态：** 活跃

**功能：** 调用 `scripts/build_detail_page_js.py` 生成小程序详情页 JS 数据文件。

**用法：**
```bat
build_content_js.bat                     默认运行
build_content_js.bat --module 07_inequality    指定模块
build_content_js.bat --ids I001,I002           指定条目
build_content_js.bat --dry-run                 预览
```

**输出：** `data/content/` 下的 JS 数据文件

---

### `encrypt_pdf.bat` — PDF 加密工具

**状态：** 活跃

**功能：** 为单个 PDF 设置权限保护。

**用法：**
```bat
encrypt_pdf.bat <输入.pdf> <输出.pdf> <用户ID>
encrypt_pdf.bat 99_build/main.pdf 99_build/encrypted/enc.pdf user001
```

**依赖：** `scripts/encrypt_pdf.py`、pikepdf

---

### `upgrade_meta.bat` — Meta 同步

**状态：** 活跃

**功能：** 调用 `scripts/meta_schema_sync.py` 同步所有 meta.json 到最新 schema。

**用法：**
```bat
upgrade_meta.bat                  默认（安全模式）
upgrade_meta.bat --strict         严格模式
upgrade_meta.bat --dry-run         预览
upgrade_meta.bat --module 07_inequality  指定模块
```

---

### `check_meta_json.bat` — Meta 校验

**状态：** 活跃

**功能：** 调用 `scripts/check_meta_json.py` 校验所有 meta.json。

**用法：**
```bat
check_meta_json.bat
```

**输出：** `meta_check_report.json`

---

## 旧版 BAT 文件 ⚠

以下 bat 文件调用的都是已被取代的旧版脚本，建议不再使用。

### `build_search_index.bat` ⚠

**功能：** 运行旧的 `build_search_index.py`。

**取代者：** `build_search_bundle_js.py`（直接 `python scripts/build_search_bundle_js.py`）

**原用法：**
```bat
build_search_index.bat
```

---

### `build_all_indexes.bat` ⚠

**功能：** 运行旧的 `build_all_indexes.py`。生成 7 个独立 JSON 索引文件。

**取代者：** `build_search_bundle_js.py`（单文件，更高效）

**原用法：**
```bat
build_all_indexes.bat
```

---

### `build_core_indexes.bat` ⚠ 兼容包装

**功能：** 运行 `build_core_index.py`，而该脚本也只是代理到 `build_search_bundle_js.py`。

**建议：** 直接使用 `python scripts/build_search_bundle_js.py`

**原用法：**
```bat
build_core_indexes.bat
```

---

### `build_content_json.bat` ⚠

**功能：** 运行实验性的旧 `build_content_json.py`。该脚本硬编码配置，TARGET_MODULES 只有 `"07-inequality"`，其他模块被注释。

**取代者：** `build_content_js.bat`（调用 `build_detail_page_js.py`）

**原用法：**
```bat
build_content_json.bat
```

---

## 推荐工作流

日常使用顺序：

```bat
# 1. 修改内容后，校验 meta
check_meta_json.bat

# 2. 如有新增 meta 字段，同步 schema
upgrade_meta.bat

# 3. 构建搜索索引
python scripts/build_search_bundle_js.py

# 4. 构建详情页数据
build_content_js.bat

# 5. 如果需要编译 PDF
set USER_ID=user001
build.bat full

# 6. 文本规范化（可选）
python scripts/normalize_text_typography.py --dry-run
```
