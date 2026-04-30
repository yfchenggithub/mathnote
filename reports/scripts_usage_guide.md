# `scripts` 目录 + 根目录脚本功能与用法整理

生成时间：2026-04-30  
统计范围：`scripts/**` 下 `*.py` + `*.js`（35 个）+ 根目录 `*.bat`（9 个）+ 根目录 `*.py`（0 个）

## 使用前提示
1. 先在仓库根目录执行命令：`D:\mathnote`。
2. 批量改写类脚本（如 `clean_i_dirs_files.py`、`unify_module_naming.py`）建议先用 dry-run。
3. 需要外部工具的脚本已在“备注”里标出（如 `latexmk`、`dvisvgm`、`magick`、`svgo`）。

## 1) 搜索与索引
| 脚本 | 功能 | 常用命令 | 备注 |
|---|---|---|---|
| `scripts/build_search_bundle_js.py` | 从各结论 `meta.json` 生成单文件搜索包 `search_bundle.js` | `python scripts/build_search_bundle_js.py` | 主力脚本；支持 `--module`/`--item`/`--dry-run`/`--debug` |
| `scripts/extract_backend_index_from_search_bundle.py` | 从 `search_bundle.js` 抽取后端 JSON 索引 | `python scripts/extract_backend_index_from_search_bundle.py` | 默认输出 `data/search_engine/backend_search_index.json` |
| `scripts/verify_backend_index_extraction.py` | 校验抽取后的 backend JSON 与 bundle 一致性 | `python scripts/verify_backend_index_extraction.py --report reports/backend_index_verify_report.json` | 适合发布前一致性检查 |
| `scripts/build_all_indexes.py` | 旧版多索引构建器（生成 `keyword/prefix/pinyin/...` 多文件） | `python scripts/build_all_indexes.py` | 依赖 `pypinyin`，偏 legacy 流程 |
| `scripts/build_core_index.py` | 兼容入口，实际转发到 `build_search_bundle_js.py` | `python scripts/build_core_index.py` | 建议直接用 `build_search_bundle_js.py` |
| `scripts/build_search_index.py` | 旧版简单倒排索引（`search_index.json`） | `python scripts/build_search_index.py` | 只做基础关键词倒排 |

## 2) 内容构建与迁移
| 脚本 | 功能 | 常用命令 | 备注 |
|---|---|---|---|
| `scripts/build_detail_page_js.py` | 生成详情页展示用 JS 内容数据 | `python scripts/build_detail_page_js.py --module 07_inequality --dry-run` | 支持按模块/条目过滤 |
| `scripts/build_statement_card_js.py` | 兼容入口，当前行为与 `build_detail_page_js.py` 一致 | `python scripts/build_statement_card_js.py` | 推荐直接用 `build_detail_page_js.py` |
| `scripts/migrate_detail_js_to_content_v2.py` | 将 detail JS 迁移到 canonical `content_v2` JSON | `python scripts/migrate_detail_js_to_content_v2.py --input data/content/07_inequality.js` | 可输出迁移报告并做校验 |
| `scripts/verify_detail_js_to_content_v2_integrity.py` | 校验迁移结果完整性 | `python scripts/verify_detail_js_to_content_v2_integrity.py --source-js data/content/07_inequality.js --target-json data/content/canonical_content_v2.json --migration-script scripts/migrate_detail_js_to_content_v2.py` | 可输出 JSON/Markdown 报告 |
| `scripts/build_content_json.py` | 旧版 LaTeX -> 内容 JSON 生成器 | `python scripts/build_content_json.py` | 依赖脚本内硬编码 `ROOT_DIR`、`TARGET_MODULES` |
| `scripts/content_v2.py` | `content_v2` 的 Pydantic 数据模型定义 | `python -c "import scripts.content_v2"` | 模型库文件，供迁移/校验脚本导入 |
| `scripts/generate_toc_seed.py` | 从 `main/index` 结构生成 TOC seed TeX | `python scripts/generate_toc_seed.py --root main.tex --output data/toc_seed.tex` | 输出 `\SeedSection/\SeedSubsection` |

## 3) 目录脚手架与批量改名
| 脚本 | 功能 | 常用命令 | 备注 |
|---|---|---|---|
| `scripts/create_pipeline_input_dirs.py` | 批量创建 `Ixxx` 输入目录与模板文件 | `python scripts/create_pipeline_input_dirs.py 9 3 --apply` | 默认先 dry-run；可配 `scripts/create_pipeline_input_dirs.example.json` |
| `scripts/create_prefixed_dirs_files.py` | 在选中的二级目录内批量创建文件 | `python scripts/create_prefixed_dirs_files.py --module 07_inequality --file 07_notes.tex --apply` | 支持 `--pattern`、`--overwrite` |
| `scripts/clean_i_dirs_files.py` | 清理选中目录下文件（保留目录） | `python scripts/clean_i_dirs_files.py --module 12_pipeline/input --apply` | 有删除行为，务必先不带 `--apply` 预览 |
| `scripts/unify_module_naming.py` | 模块/子模块命名规范重构与回滚 | `python scripts/unify_module_naming.py --dry-run` | 变更大，执行前建议备份/分支 |
| `scripts/upgrade_module_index.py` | 模块编号升级（含引用替换） | `python scripts/upgrade_module_index.py --root D:\mathnote --dry-run` | 用 `--apply` 实际落盘 |

## 4) 元数据 Schema 与质量检查
| 脚本 | 功能 | 常用命令 | 备注 |
|---|---|---|---|
| `scripts/check_meta_json.py` | 校验全部 `meta.json`（不修改） | `python scripts/check_meta_json.py` | 输出 `meta_check_report.json` |
| `scripts/meta_schema_sync.py` | 按 `META_SCHEMA` 同步/补齐/严格清理 `meta.json` | `python scripts/meta_schema_sync.py --dry-run` | 支持 `--mode strict`、`--file` |
| `scripts/meta_schema.py` | `meta.json` 标准结构定义 | `python -c "from scripts.meta_schema import META_SCHEMA; print(len(META_SCHEMA))"` | 规范定义文件，不直接产出业务文件 |
| `scripts/meta_utils.py` | 预留工具模块 | 无 | 当前文件为空 |

## 5) 文本规范化与修复
| 脚本 | 功能 | 常用命令 | 备注 |
|---|---|---|---|
| `scripts/normalize_text_typography.py` | 中文排版符号统一（引号/标点/空格等） | `python scripts/normalize_text_typography.py --dry-run` | 支持 profiles、扩展名过滤 |
| `scripts/fix_prompt_quotes.py` | 旧命令兼容包装，实际调用 `normalize_text_typography.py` | `python scripts/fix_prompt_quotes.py --dry-run` | 建议直接用 `normalize_text_typography.py` |
| `scripts/fix_math_punctuation.py` | 修复数学环境中的中文标点 | `python scripts/fix_math_punctuation.py C019 C020 --dry-run` | 目标文件为结论目录 `01~06` tex |

## 6) PDF / SVG / WebP 与图像
| 脚本 | 功能 | 常用命令 | 备注 |
|---|---|---|---|
| `scripts/build_conclusion_pdfs.py` | 将选定结论编译成独立 PDF，并生成 ID->文件名映射 | `python scripts/build_conclusion_pdfs.py --ids I001 S001 --overwrite` | 默认输出到 `build/conclusion_pdfs` |
| `scripts/build_svg_dvisvgm.py` | `01~06.tex` 合并后编译并转 SVG（含可选 svgo） | `python scripts/build_svg_dvisvgm.py 07_inequality I001_Compound_Inequality_Transformation` | 依赖 `latexmk`/`pdfcrop`/`dvisvgm`/`svgo` |
| `scripts/build_webp.py` | `01~06.tex` 合并后编译并转 WebP | `python scripts/build_webp.py 07_inequality I001_Compound_Inequality_Transformation` | 依赖 `latexmk`/`pdfcrop`/`magick` |
| `scripts/encrypt_pdf.py` | PDF 加密 | `python scripts/encrypt_pdf.py input.pdf output.pdf user123` | 依赖 `pikepdf` |
| `scripts/png/mercedes_benz_theorem.py` | 生成“奔驰定理”示意图 PNG | `python scripts/png/mercedes_benz_theorem.py` | 依赖 `matplotlib`、`numpy` |
| `scripts/svgo.config.js` | SVG 优化配置（被其他流程读取） | `svgo --config scripts/svgo.config.js input.svg -o output.svg` | 配置文件，不是主入口脚本 |

## 7) Node LaTeX 渲染辅助
| 脚本 | 功能 | 常用命令 | 备注 |
|---|---|---|---|
| `scripts/latex_block_splitter.js` | 将 statement/proof/examples 拆块 | `const splitter = require('./scripts/latex_block_splitter')` | 供 `latex_to_html.js` 调用 |
| `scripts/latex_to_html.js` | 批量 LaTeX -> HTML（stdin JSON，stdout JSON） | `node scripts/latex_to_html.js < in.json > out.json` | 依赖 `katex` |
| `scripts/latex_to_html_single.js` | 单段 LaTeX -> HTML（stdin 文本） | `node scripts/latex_to_html_single.js < in.tex > out.html` | 依赖 `katex` |
| `scripts/test_katex.js` | KaTeX 安装连通性测试 | `node scripts/test_katex.js` | 用于环境自检 |

## 8) 根目录批处理入口（`.bat` / `.py`）
根目录 `.py`：当前无。  
以下为根目录 `.bat`：

| 脚本 | 功能 | 常用命令 | 备注 |
|---|---|---|---|
| `build.bat` | 项目主构建入口：编译整本或 TOC-only，并产出加密 PDF | `set USER_ID=user001 && build.bat full` / `set USER_ID=user001 && build.bat toc` | 支持参数 `full`/`toc`；`USER_ID` 为空也可运行，但加密文件名不含用户标识；这是全量/目录构建，不是按二级结论筛选构建 |
| `build_all_indexes.bat` | 运行旧版多索引构建 | `build_all_indexes.bat` | 实际调用 `scripts/build_all_indexes.py` |
| `build_content_js.bat` | 内容 JS 构建包装 | `build_content_js.bat --dry-run --module 08_trigonometry --item T001` | 已更新为调用 `scripts/build_detail_page_js.py`，支持参数透传 |
| `build_content_json.bat` | 运行旧版内容 JSON 构建 | `build_content_json.bat` | 实际调用 `scripts/build_content_json.py` |
| `build_core_indexes.bat` | 运行核心索引构建包装 | `build_core_indexes.bat` | 实际调用 `scripts/build_core_index.py`（会转发到 `build_search_bundle_js.py`） |
| `build_search_index.bat` | 运行旧版简单倒排索引构建 | `build_search_index.bat` | 实际调用 `scripts/build_search_index.py` |
| `check_meta_json.bat` | 校验全部 `meta.json` | `check_meta_json.bat` | 实际调用 `scripts/check_meta_json.py` |
| `encrypt_pdf.bat` | PDF 加密包装 | `encrypt_pdf.bat 99_build\\main.pdf 99_build\\encrypted\\main_enc.pdf user001` | 已更新为调用 `scripts/encrypt_pdf.py`，并增加参数校验 |
| `upgrade_meta.bat` | 元数据升级包装 | `upgrade_meta.bat --dry-run` | 已更新为调用 `scripts/meta_schema_sync.py`，支持参数透传；当前脚本规则下可能扫描到 0 个文件（取决于模块命名规则） |
## 附：常用示例配置文件
1. `scripts/create_prefixed_dirs_files.example.json`
2. `scripts/create_pipeline_input_dirs.example.json`
3. `scripts/clean_i_dirs_files.example.json`
4. `scripts/conclusion_record_v2.schema.json`


