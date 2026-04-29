# data/search_engine/search_bundle.js 生成逻辑说明

生成日期：2026-04-29

分析对象：`data/search_engine/search_bundle.js`

核心脚本：`scripts/build_search_bundle_js.py`

## 1. 总体定位

`search_bundle.js` 是给小程序端直接 `require` 使用的单文件搜索包。它把原来分散在多个索引文件里的能力合并到一个 CommonJS 模块中：

```js
const searchBundle = { ... }
module.exports = searchBundle
```

它的设计目标是把搜索运行时的重活前移到构建期，包括：

- 读取各知识点目录下的 `meta.json`。
- 提前抽取标题、别名、关键词、公式、摘要、知识节点等字段。
- 构建精确倒排索引 `termIndex`。
- 构建前缀倒排索引 `prefixIndex`。
- 构建搜索联想 `suggestions`。
- 预先计算文档静态排序分 `docs[docId].rank`。
- 将字段来源压缩为 `fieldMask`，减少端上包体和运行时解析成本。

当前文件头显示，现有 `data/search_engine/search_bundle.js` 是由 `scripts/build_search_bundle_js.py` 自动生成的，不应直接手工编辑。

## 2. 入口与命令

主入口：

```powershell
python scripts\build_search_bundle_js.py
```

兼容入口：

```powershell
python scripts\build_core_index.py
```

`scripts/build_core_index.py` 当前会导入并转发到 `build_search_bundle_js.py` 的 `main()`，所以历史命令仍可生成同一类 bundle。

常用参数：

| 参数 | 含义 |
|---|---|
| `--base-dir` | 项目根目录，默认是脚本所在目录的上一级。 |
| `--output-file` | 输出文件，默认 `data/search_engine/search_bundle.js`。 |
| `--module` | 只构建指定模块目录，可重复传入。 |
| `--item` | 只构建指定 item 目录名或文档 id，可重复传入。 |
| `--dry-run` | 只在内存中构建并打印统计，不写文件。 |
| `--debug` | 输出更详细的扫描、过滤、跳过日志。 |
| `--strict` | 遇到缺失 `meta.json`、非法 JSON、重复 id 等问题时直接失败。 |
| `--pretty` | 输出带缩进的 JS，便于人工查看。 |
| `--embed-debug` | 将调试数据嵌入 bundle，文件会变大。 |
| `--debug-doc` | 打印某个文档的字段展开详情。 |
| `--debug-term` | 打印某个查询词在 exact/prefix 索引里的命中情况。 |
| `--prefix-doc-limit` | 每个前缀 key 最多保留多少条文档 posting，默认 32。 |
| `--suggestion-limit` | 联想词最多保留多少条，默认 500。 |

## 3. 当前 search_bundle.js 的构建状态

当前 `data/search_engine/search_bundle.js` 文件头与载荷显示：

| 字段 | 当前值 |
|---|---:|
| `generatedAt` | `2026-04-16T17:50:14+08:00` |
| `docs` | 1 |
| `terms` | 416 |
| `prefixes` | 1005 |
| `suggestions` | 27 |
| `prefixDocLimit` | 32 |
| `suggestionLimit` | 500 |
| `targetModules` | `[]` |
| `targetItems` | `["I001"]` |

这说明它不是全量索引，而是一次只构建 `I001` 的局部 bundle。因为没有指定 `--module`，脚本先自动发现模块，再用 `--item I001` 过滤 item。

当前模块统计：

| 模块 | scanned | built | filtered | skipped | 解释 |
|---|---:|---:|---:|---:|---|
| `03_conic` | 17 | 0 | 17 | 0 | 扫描到 17 条，但都不是 `I001`，被 item 过滤。 |
| `04_vector` | 19 | 0 | 0 | 19 | 扫描到 19 个目录，但构建时被跳过。 |
| `07_inequality` | 44 | 1 | 41 | 2 | 构建了 `I001`，41 条被过滤，2 条被跳过。 |

当前 `docs` 里只有：

```text
I001
```

当前前 5 条 suggestion：

```json
[
  ["不等式等价变形", "I001", 282],
  ["函数值域不等式", "I001", 282],
  ["区间不等式", "I001", 282],
  ["连不等式转化", "I001", 282],
  ["不等式等价", "I001", 270]
]
```

## 4. 构建主流程

`scripts/build_search_bundle_js.py` 的主流程在 `run_build(config)` 中，分为 5 步：

1. 解析构建范围。
2. 扫描模块并读取每个 `meta.json`。
3. 组装 bundle 载荷。
4. 输出调试报告。
5. 写入文件，或在 `--dry-run` 下只输出统计。

流程展开如下：

```text
parse_args()
  -> build_config()
    -> run_build()
      -> resolve_module_dirs()
      -> for each module_dir
        -> for each item_dir
          -> read item_dir/meta.json
          -> resolve doc_id
          -> matches_item_filter()
          -> build_doc_record()
          -> for each FIELD_SPECS
            -> extractor(meta)
            -> compute_field_weight()
            -> build_feature_variants()
            -> add_exact_posting()
            -> add_prefix_posting()
            -> collect suggestions
      -> serialize_postings()
      -> write_bundle()
```

## 5. 模块发现与 item 过滤

如果没有传 `--module`，脚本会自动发现项目根目录下的内容模块。自动发现规则：

- 跳过 `.git`、`.github`、`.vscode`、`assets`、`data`、`misc`、`node_modules`、`scripts`、`search_engine`、`templates` 等目录。
- 只把“子目录中存在 `meta.json`”的顶层目录视为内容模块。

如果传了 `--module`，则只构建指定目录，例如：

```powershell
python scripts\build_search_bundle_js.py --module 07_inequality
```

如果传了 `--item`，则 item 目录名或 `meta.id` 必须命中目标列表，否则计入 `filtered`。例如：

```powershell
python scripts\build_search_bundle_js.py --item I001
```

## 6. meta.json 读取与容错

每个 item 目录必须有：

```text
<module>/<item>/meta.json
```

读取逻辑：

- 使用 UTF-8 读取 JSON。
- JSON 根节点必须是对象。
- 默认模式下，缺失、非法或空 JSON 会 warning 后跳过该 item。
- `--strict` 模式下，这类问题会直接导致构建失败。
- `docId` 优先来自 `meta.id`，没有则退回 item 目录名。
- 如果出现重复 `docId`，构建失败。

## 7. 字段配置 FIELD_SPECS

`FIELD_SPECS` 是搜索字段配置中心。每个字段由 `FieldSpec` 描述：

| 属性 | 含义 |
|---|---|
| `name` | 字段名，会写入 `fieldMaskLegend`。 |
| `extractor` | 从 `meta.json` 抽取原始文本的函数。 |
| `base_weight` | 字段基础权重。 |
| `searchmeta_key` | 可被 `meta.searchmeta` 或 `meta.searchMeta` 动态调权的键。 |
| `include_prefix` | 是否生成前缀索引。 |
| `include_suggest` | 是否进入联想词。 |
| `include_pinyin` | 是否自动生成中文拼音和拼音首字母。 |
| `include_ngrams` | 是否生成中文 n-gram 子串。 |
| `treat_as_formula` | 是否按公式规则归一化。 |
| `prefix_ratio` | 前缀索引相对 exact 索引的分数折扣，默认 0.70。 |

当前字段来源与策略：

| 字段 | 来源路径 | 基础权重 | prefix | suggest | pinyin | n-gram | formula |
|---|---|---:|---|---|---|---|---|
| `title` | `core.title`, `title` | 120 | 是 | 是 | 是 | 是 | 否 |
| `alias` | `core.alias`, `alias` | 96 | 是 | 是 | 是 | 是 | 否 |
| `keyword` | `search.keywords`, `keywords` | 84 | 是 | 是 | 是 | 是 | 否 |
| `synonym` | `search.synonyms`, `synonyms` | 68 | 是 | 是 | 是 | 是 | 否 |
| `intent` | `search.intents` | 56 | 是 | 否 | 是 | 否 | 否 |
| `query_template` | `search.query_templates`, `search.queryTemplates` | 38 | 否 | 否 | 是 | 否 | 否 |
| `ocr_keyword` | `search.ocrKeywords`, `ocrKeywords` | 42 | 是 | 否 | 是 | 否 | 否 |
| `category` | `core.category`, `category`, `chapter`, `section` | 48 | 是 | 是 | 是 | 是 | 否 |
| `tag` | `core.tags`, `tags` | 44 | 是 | 是 | 是 | 是 | 否 |
| `formula_token` | `search.formulaTokens`, `search.formula_tokens`, `formulaTokens` | 78 | 是 | 否 | 否 | 否 | 是 |
| `formula` | `math.core_formula`, `search.latex_patterns`, `search.latexPatterns`, `math.related_formulas`, `formulas` | 66 | 是 | 否 | 否 | 否 | 是 |
| `summary` | `core.summary`, `summary`, `preview`, `content.intuition` | 30 | 否 | 否 | 是 | 否 | 否 |
| `statement_fragment` | `content.statement`, `statement` | 18 | 否 | 否 | 否 | 否 | 否 |
| `usage` | `usage.problem_types`, `usage.scenarios` | 28 | 是 | 否 | 是 | 否 | 否 |
| `knowledge_node` | `knowledgeNode`, `altNodes` | 40 | 是 | 否 | 是 | 是 | 否 |
| `pinyin` | `search.pinyin`, `pinyin` | 72 | 是 | 否 | 否 | 否 | 否 |
| `pinyin_abbr` | `search.pinyinAbbr`, `search.pinyin_abbr`, `pinyinAbbr` | 64 | 是 | 否 | 否 | 否 | 否 |

## 8. 字段权重与 searchmeta

字段基础权重可被 `meta.searchmeta` 或 `meta.searchMeta` 调整。默认动态权重基准：

| 动态键 | 默认值 | 影响字段 |
|---|---:|---|
| `titleWeight` | 10 | `title` |
| `keywordWeight` | 8 | `keyword` |
| `synonymWeight` | 6 | `synonym` |
| `ocrWeight` | 9 | `ocr_keyword` |
| `formulaWeight` | 7 | `formula_token`, `formula` |

计算方式：

```text
final_field_weight = base_weight * configured_weight / default_weight
```

结果会四舍五入，并至少为 1。

## 9. 文档记录 docs 的生成

每个成功构建的 item 会生成一条 `docs[docId]` 轻量记录。它不是完整 `meta.json`，只保留端上搜索结果展示和排序需要的信息。

| docs 字段 | 来源或计算方式 |
|---|---|
| `id` | `meta.id`，没有则退回 item 目录名。 |
| `module` | `meta.module`，没有则退回模块目录名。 |
| `moduleDir` | 模块目录名。 |
| `title` | `core.title`, `title`，没有则退回 item 目录名。 |
| `summary` | `core.summary`, `summary`, `preview`, `content.intuition`，没有则退回陈述片段。 |
| `category` | `core.category`, `category`, `chapter`, `section`。 |
| `tags` | `core.tags`, `tags` 的前 8 个。 |
| `coreFormula` | 公式来源列表中的第一项。 |
| `rank` | 构建期计算的静态排序分。 |
| `difficulty` | `core.difficulty`, `difficulty`。 |
| `searchBoost` | `ranking.search_boost`, `ranking.searchBoost`。 |
| `hotScore` | `ranking.hot_score`, `ranking.hotScore`。 |
| `examFrequency` | `usage.exam_frequency`, `usage.examFrequency`, `examFrequency`。 |
| `examScore` | `usage.exam_score`, `usage.examScore`, `examScore`。 |

`rank` 公式：

```text
rank =
  search_boost * 100
+ hot_score
+ click_rate * 30
+ success_rate * 40
+ exam_frequency * 20
+ exam_score * 5
+ difficulty * 2
```

最后四舍五入为整数。

## 10. 文本归一化

构建索引前会对文本做多层归一化：

| 函数 | 用途 |
|---|---|
| `normalize_display` | NFKC 归一化、折叠连续空白、去首尾空白，保留可读展示形式。 |
| `normalize_text` | 在展示归一化基础上转小写，并统一常见中英文引号。 |
| `normalize_compact` | 移除所有空白，处理用户不输入空格的情况。 |
| `normalize_formula` | 对公式做 LaTeX 符号替换并移除空格。 |

公式替换包括：

| 原写法 | 统一为 |
|---|---|
| `\geqslant`, `\geq` | `>=` |
| `\leqslant`, `\leq` | `<=` |
| `\neq` | `!=` |
| `\times`, `\cdot` | `*` |
| `\left`, `\right` | 空字符串 |

## 11. 特征展开 build_feature_variants

每条原始字段文本会被展开为：

```text
source: 原始展示文本
exact:  精确倒排候选 [(term, multiplier, kind)]
prefix: 前缀倒排候选 [(term, multiplier, kind)]
suggest: 联想展示文本
```

exact 变体：

| kind | 系数 | 说明 |
|---|---:|---|
| `full` | 1.00 | 完整归一化文本。 |
| `compact` | 0.96 | 去空白文本。 |
| `token` | 0.72 | 中文片段或拉丁 token。 |
| `ngram` | 0.58 | 中文 n-gram 子串，仅部分字段启用。 |
| `pinyin` | 0.72 | 自动全拼，仅包含中文且字段启用拼音时生成。 |
| `pinyin_abbr` | 0.62 | 自动拼音首字母，仅包含中文且字段启用拼音时生成。 |

prefix 变体来自启用 `include_prefix` 的字段，并复用 full/compact/token/pinyin 等候选。

suggest 生成条件：

- 字段启用了 `include_suggest`。
- 展示文本长度在 2 到 32 之间。
- 文本不像公式。

## 12. termIndex 生成逻辑

`termIndex` 是精确倒排索引：

```js
termIndex: {
  [term]: [
    [docId, score, fieldMask]
  ]
}
```

构建逻辑：

1. 遍历每个字段的 exact 候选。
2. 分数为 `field_weight * variant_multiplier`，四舍五入，至少为 1。
3. 同一 `(term, docId)` 如果来自多个字段或多种变体，分数累加。
4. `fieldMask` 取所有命中字段 mask 的按位或。

精确倒排强调“多来源重复命中说明更相关”，所以采用累加策略。

## 13. prefixIndex 生成逻辑

`prefixIndex` 是前缀倒排索引：

```js
prefixIndex: {
  [prefix]: [
    [docId, score, fieldMask]
  ]
}
```

构建逻辑：

1. 只有启用 `include_prefix` 的字段会进入。
2. 候选词先进入 `prefix_terms(term)` 展开。
3. 中文前缀从 1 个字开始，最长 12 个字符。
4. 英文和拼音前缀从 2 个字符开始，最长 16 个字符。
5. 分数为 `field_weight * prefix_ratio * variant_multiplier`，默认 `prefix_ratio = 0.70`。
6. 同一 `(prefix, docId)` 多次命中时取最大分，不累加。
7. 序列化时每个 prefix key 最多保留 `prefixDocLimit` 条。

前缀倒排强调“输入中途也能召回”，但为抑制噪声和包体，采用最大分策略和截断策略。

## 14. suggestions 生成逻辑

联想词结构：

```js
suggestions: [
  [displayText, docId, score]
]
```

构建逻辑：

1. 只收集 `include_suggest=True` 且通过长度/公式过滤的字段。
2. 去重 key 使用 `normalize_text(displayText)`。
3. suggestion 分数为：

```text
score = field_weight + docs[docId].rank
```

4. 如果同一个 suggestion key 命中多次，只保留分数最高的一条。
5. 最终按 `score` 降序、`displayText` 升序、`docId` 升序排序。
6. 截断到 `suggestionLimit`，默认 500。

## 15. fieldMaskLegend 与 posting 压缩

`fieldMaskLegend` 由 `FIELD_SPECS` 顺序生成：

```text
fieldMaskLegend = { spec.name: 1 << index }
```

当前映射：

| 字段 | mask |
|---|---:|
| `title` | 1 |
| `alias` | 2 |
| `keyword` | 4 |
| `synonym` | 8 |
| `intent` | 16 |
| `query_template` | 32 |
| `ocr_keyword` | 64 |
| `category` | 128 |
| `tag` | 256 |
| `formula_token` | 512 |
| `formula` | 1024 |
| `summary` | 2048 |
| `statement_fragment` | 4096 |
| `usage` | 8192 |
| `knowledge_node` | 16384 |
| `pinyin` | 32768 |
| `pinyin_abbr` | 65536 |

posting 不保存字段名，而保存整数 `fieldMask`。端上需要展示命中来源时，可用 `fieldMaskLegend` 按位反解。

## 16. posting 序列化与排序

`serialize_postings()` 把内存中的 posting map 压缩为数组：

```js
[docId, score, fieldMask]
```

排序规则：

1. `score` 降序。
2. `docs[docId].rank` 降序。
3. `docId` 升序。

`prefixIndex` 序列化时额外传入 `prefixDocLimit`，每个前缀只保留前 N 条。

## 17. 输出文件写法

`write_bundle()` 会：

1. 创建输出目录。
2. 用 `json.dumps(..., ensure_ascii=False)` 序列化 bundle。
3. 如果传 `--pretty`，使用 2 空格缩进；否则用紧凑格式。
4. 在文件头写入生成脚本、生成时间、统计数字、schema 说明。
5. 写出 CommonJS 模块：

```js
const searchBundle = { ... }

module.exports = searchBundle;
```

输出文件默认是：

```text
data/search_engine/search_bundle.js
```

## 18. 输出结构

最终 bundle 顶层字段：

| 字段 | 含义 |
|---|---|
| `version` | 结构版本，当前为 1。 |
| `generatedAt` | 构建时间。 |
| `stats` | 文档数、倒排 key 数、联想数、模块统计。 |
| `buildOptions` | 构建参数快照。 |
| `fieldMaskLegend` | 字段名到 bit mask 的映射。 |
| `docs` | 搜索结果展示和排序所需的轻量文档表。 |
| `termIndex` | 精确倒排索引。 |
| `prefixIndex` | 前缀倒排索引。 |
| `suggestions` | 搜索联想数组。 |
| `debug` | 可选，仅 `--embed-debug` 时存在。 |

## 19. 调试方式

查看某篇文档如何展开索引：

```powershell
python scripts\build_search_bundle_js.py --item I001 --debug-doc I001 --dry-run
```

查看某个查询词命中哪些 exact/prefix 候选：

```powershell
python scripts\build_search_bundle_js.py --debug-term 柯西不等式 --dry-run
```

生成带调试载荷的 bundle：

```powershell
python scripts\build_search_bundle_js.py --pretty --embed-debug
```

## 20. 与 backend_search_index.json 的关系

`search_bundle.js` 是前端/小程序端 bundle；`backend_search_index.json` 是后端可直接加载的 JSON。

后端 JSON 不是由 `build_search_bundle_js.py` 直接写出的，而是由：

```powershell
python scripts\extract_backend_index_from_search_bundle.py --input data/search_engine/search_bundle.js --output data/search_engine/backend_search_index.json
```

从 `search_bundle.js` 中解析 `searchBundle` 对象并转换得到。

因此两者应当来自同一轮构建才一致。当前工作区中，`search_bundle.js` 是 1 篇文档的局部 bundle，而 `backend_search_index.json` 是 42 篇文档的后端索引，两者并不是同一轮产物。

## 21. 维护入口

最常需要改的地方：

| 目标 | 建议修改位置 |
|---|---|
| 新增可搜索字段 | 新增 extractor，并把字段加入 `FIELD_SPECS`。 |
| 调整字段权重 | 修改 `FIELD_SPECS` 的 `base_weight` 或 `DEFAULT_SEARCHMETA_WEIGHTS`。 |
| 调整召回变体 | 修改 `build_feature_variants()`。 |
| 调整文档展示字段 | 修改 `build_doc_record()`。 |
| 调整静态排序 | 修改 `compute_rank_score()`。 |
| 调整输出结构 | 修改 `run_build()` 中的 bundle 组装逻辑。 |
| 调整 JS 文件头或 CommonJS 包装 | 修改 `write_bundle()`。 |

推荐的改动原则：

- 新字段优先通过 `FieldSpec` 接入，不要把字段逻辑散落在主循环里。
- 公式字段要明确设置 `treat_as_formula=True`，否则端上查询归一化很难对齐。
- 长文本字段慎用 `include_prefix` 和 `include_suggest`，否则容易增加噪声和包体。
- 调整 `prefixDocLimit` 和 `suggestionLimit` 前，先用 `--dry-run` 对比统计变化。
