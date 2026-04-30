# backend_search_index.json 与 canonical_content_v2.json 构建流程

## 1) 目标产物与脚本入口

| 产物 | 默认路径 | 直接生成脚本 | 关键上游 |
|---|---|---|---|
| `backend_search_index.json` | `data/search_engine/backend_search_index.json` | `scripts/extract_backend_index_from_search_bundle.py` | `scripts/build_search_bundle_js.py` 先生成 `search_bundle.js` |
| `canonical_content_v2.json` | （默认与输入 detail js 同目录） | `scripts/migrate_detail_js_to_content_v2.py` | 通常先有 `data/content/<module>.js`（可由 `scripts/build_detail_page_js.py` 生成） |

---

## 2) backend_search_index.json 构建流程

### Step A1. 生成 search bundle（上游）

```powershell
python scripts/build_search_bundle_js.py --pretty --audit-report data/search_engine/search_audit.json
```

默认输出：
- `data/search_engine/search_bundle.js`
- （可选）`data/search_engine/search_audit.json`

### Step A2. 从 search bundle 抽取 backend JSON

```powershell
python scripts/extract_backend_index_from_search_bundle.py `
  --input data/search_engine/search_bundle.js `
  --output data/search_engine/backend_search_index.json `
  --pretty
```

说明：
- 默认会附加轻量 `meta`；如果不希望附加可加 `--no-meta`。

### Step A3. 一致性校验（建议每次都跑）

```powershell
python scripts/verify_backend_index_extraction.py `
  --bundle-js data/search_engine/search_bundle.js `
  --backend-json data/search_engine/backend_search_index.json `
  --report reports/backend_index_verify_report.json
```

通过标准：
- `passed = true`
- `mismatch_count = 0`

---

## 3) canonical_content_v2.json 构建流程

### Step B0. 准备 detail js（若已存在可跳过）

按模块构建 detail 数据：

```powershell
python scripts/build_detail_page_js.py --module 07_inequality
```

默认输出：
- `data/content/07_inequality.js`

### Step B1. 迁移 detail js -> canonical content v2

```powershell
python scripts/migrate_detail_js_to_content_v2.py `
  --input data/content/07_inequality.js `
  --output data/content/canonical_content_v2.json `
  --report data/content/conversion_report.json `
  --strict-validation
```

说明：
- 不传 `--output` 时，默认输出到输入文件同目录下的 `canonical_content_v2.json`。
- 不传 `--report` 时，默认输出到输入文件同目录下的 `conversion_report.json`。

### Step B2. 迁移完整性校验（建议）

```powershell
python scripts/verify_detail_js_to_content_v2_integrity.py `
  --source-js data/content/07_inequality.js `
  --target-json data/content/canonical_content_v2.json `
  --migration-script scripts/migrate_detail_js_to_content_v2.py `
  --report-json reports/migration_integrity_report.json `
  --report-md reports/migration_integrity_report.md
```

---

## 4) 推荐执行顺序（一次完整构建）

```powershell
# A. 搜索索引（backend_search_index.json）
python scripts/build_search_bundle_js.py --pretty --audit-report data/search_engine/search_audit.json
python scripts/extract_backend_index_from_search_bundle.py --input data/search_engine/search_bundle.js --output data/search_engine/backend_search_index.json --pretty
python scripts/verify_backend_index_extraction.py --bundle-js data/search_engine/search_bundle.js --backend-json data/search_engine/backend_search_index.json --report reports/backend_index_verify_report.json

# B. 内容 canonical（canonical_content_v2.json）
python scripts/build_detail_page_js.py --module 07_inequality
python scripts/migrate_detail_js_to_content_v2.py --input data/content/07_inequality.js --output data/content/canonical_content_v2.json --report data/content/conversion_report.json --strict-validation
python scripts/verify_detail_js_to_content_v2_integrity.py --source-js data/content/07_inequality.js --target-json data/content/canonical_content_v2.json --migration-script scripts/migrate_detail_js_to_content_v2.py --report-json reports/migration_integrity_report.json --report-md reports/migration_integrity_report.md
```

---

## 5) 常见注意事项

1. `backend_search_index.json` 必须和 `search_bundle.js` 同一轮构建产物，否则校验会出现大量 mismatch。  
2. `canonical_content_v2.json` 是“单输入 detail js 迁移”模型；输入文件换模块，输出也应跟着分开管理。  
3. `--strict-validation` 会把校验失败记录记为 failed 并从 canonical 输出中剔除，适合上线前使用。  

