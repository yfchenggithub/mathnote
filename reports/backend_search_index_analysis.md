# backend_search_index.json 输入来源与字段说明

生成日期：2026-04-29

分析对象：`data/search_engine/backend_search_index.json`

## 1. 总体结论

`backend_search_index.json` 是后端可直接加载的搜索索引 JSON。它不是从 `scripts/build_all_indexes.py` 直接生成的旧式多文件索引，而是来自下面这条链路：

1. 原始业务数据：各知识点目录下的 `meta.json`。
2. 搜索 bundle 构建：`scripts/build_search_bundle_js.py` 读取 `meta.json`，生成 `data/search_engine/search_bundle.js`。
3. 后端 JSON 抽取：`scripts/extract_backend_index_from_search_bundle.py` 从 `search_bundle.js` 里的 `searchBundle` 对象抽取数据，写出 `data/search_engine/backend_search_index.json`。

当前 `backend_search_index.json` 自身记录的构建范围是：

- `targetModules`: `["07_inequality"]`
- `targetItems`: `[]`
- `documents`: 42
- `terms`: 9500
- `prefixes`: 19348
- `suggestions`: 500
- `moduleStats`: `07_inequality` 扫描 44 条，构建 42 条，跳过 2 条

本次快速检查发现，当前工作区中 `07_inequality/I043_Cyclic_Rational_Mean/meta.json` 与 `07_inequality/I044_Triple_Rational_Square_Sum/meta.json` 无法被标准 JSON 解析；这与索引内 `skipped: 2` 的统计相吻合。

需要注意：当前 `data/search_engine/search_bundle.js` 与当前 `backend_search_index.json` 不是同一轮产物。`search_bundle.js` 的 `generatedAt` 是 `2026-04-16T17:50:14+08:00`，统计为 1 篇文档；`backend_search_index.json` 的 `generatedAt` 是 `2026-04-06T10:46:48+08:00`，统计为 42 篇文档。运行 `scripts/verify_backend_index_extraction.py` 会报告两者不一致。

## 2. 输入来源

### 2.1 原始内容输入

核心输入是内容目录中的 `meta.json`。对于当前后端索引，构建配置显示只纳入了：

```text
07_inequality/*/meta.json
```

实际进入 `docs` 的文档 ID 为：

```text
I001, I002, I003, I004, I005, I006, I007, I008, I009, I010,
I011, I012, I013, I014, I015, I016, I017, I018, I019, I020,
I021, I022, I023, I024, I025, I026, I027, I028, I029, I030,
I031, I032, I033, I034, I035, I036, I037, I038, I039, I040,
I041, I042
```

### 2.2 构建脚本输入规则

`scripts/build_search_bundle_js.py` 通过 `FIELD_SPECS` 定义每类可搜索字段的来源、权重、是否生成前缀、是否加入联想、是否生成拼音、是否按公式归一化等规则。

主要字段来源如下：

| 索引字段 | `meta.json` 来源路径 | 含义 |
|---|---|---|
| `title` | `core.title`, `title` | 标题，最强召回信号 |
| `alias` | `core.alias`, `alias` | 别名、不同叫法 |
| `keyword` | `search.keywords`, `keywords` | 人工关键词 |
| `synonym` | `search.synonyms`, `synonyms` | 同义词、近义表达 |
| `intent` | `search.intents` | 用户搜索意图短语 |
| `query_template` | `search.query_templates`, `search.queryTemplates` | 接近自然语言的搜索句式 |
| `ocr_keyword` | `search.ocrKeywords`, `ocrKeywords` | OCR 或截图识别后的碎片关键词 |
| `category` | `core.category`, `category`, `chapter`, `section` | 分类、章节、栏目 |
| `tag` | `core.tags`, `tags` | 标签 |
| `formula_token` | `search.formulaTokens`, `search.formula_tokens`, `formulaTokens` | 人工挑选的公式关键 token |
| `formula` | `math.core_formula`, `search.latex_patterns`, `search.latexPatterns`, `math.related_formulas`, `formulas` | 核心公式或相关公式 |
| `summary` | `core.summary`, `summary`, `preview`, `content.intuition` | 摘要、直觉说明 |
| `statement_fragment` | `content.statement`, `statement` | 定理陈述拆出的短片段 |
| `usage` | `usage.problem_types`, `usage.scenarios` | 适用题型和使用场景 |
| `knowledge_node` | `knowledgeNode`, `altNodes` | 知识节点、备用节点 |
| `pinyin` | `search.pinyin`, `pinyin` | 人工维护的全拼 |
| `pinyin_abbr` | `search.pinyinAbbr`, `search.pinyin_abbr`, `pinyinAbbr` | 人工维护的拼音首字母 |

### 2.3 中间产物与后端抽取

`scripts/build_search_bundle_js.py` 的输出是 CommonJS 文件：

```text
data/search_engine/search_bundle.js
```

结构类似：

```js
const searchBundle = {
  version,
  generatedAt,
  stats,
  buildOptions,
  fieldMaskLegend,
  docs,
  termIndex,
  prefixIndex,
  suggestions
}
module.exports = searchBundle
```

`scripts/extract_backend_index_from_search_bundle.py` 会解析这个 JS 对象字面量，并写成标准 JSON。抽取脚本默认可附加 `meta` 字段记录来源文件、抽取时间、抽取器版本；但当前 `backend_search_index.json` 没有这个附加 `meta` 字段，说明它可能是用 `--no-meta` 或旧版本/旧参数生成的。

## 3. 顶层字段意义

| 字段 | 类型 | 含义 |
|---|---|---|
| `version` | number | 索引结构版本。当前为 `1`。 |
| `generatedAt` | string | 搜索 bundle 构建时间，不一定等于 JSON 抽取时间。 |
| `stats` | object | 构建统计，用于验收索引规模和模块扫描结果。 |
| `buildOptions` | object | 构建时关键参数快照。 |
| `fieldMaskLegend` | object | 字段名到 bit mask 的映射，用于反解 posting 的命中来源。 |
| `docs` | object | 文档主表，键是 `docId`，值是搜索结果展示和排序所需的轻量文档信息。 |
| `termIndex` | object | 精确倒排索引，键是构建期归一化后的检索词。 |
| `prefixIndex` | object | 前缀倒排索引，服务增量输入、半截输入、拼音前缀等场景。 |
| `suggestions` | array | 搜索联想列表，已经按分数排序并截断。 |

## 4. `stats` 字段

当前值与实际数组/对象数量一致：

| 字段 | 当前值 | 含义 |
|---|---:|---|
| `documents` | 42 | `docs` 中的文档数量 |
| `terms` | 9500 | `termIndex` 中的精确索引 key 数 |
| `prefixes` | 19348 | `prefixIndex` 中的前缀 key 数 |
| `suggestions` | 500 | `suggestions` 中的联想项数量 |
| `modules` | 1 | 本轮构建涉及的模块数量 |
| `moduleStats` | array | 每个模块的扫描、构建、过滤、跳过统计 |

`moduleStats` 中每项含义：

| 字段 | 含义 |
|---|---|
| `module` | 模块目录名 |
| `scanned` | 扫描到的 item 目录数量 |
| `built` | 成功进入索引的 item 数量 |
| `filtered` | 被 `--item` 或其他过滤条件排除的数量 |
| `skipped` | 因缺失/无效 `meta.json` 等原因跳过的数量 |

## 5. `buildOptions` 字段

| 字段 | 当前值 | 含义 |
|---|---:|---|
| `prefixDocLimit` | 32 | 每个 `prefixIndex` key 最多保留的 posting 数量，控制包体和噪声。 |
| `suggestionLimit` | 500 | 最终联想词数量上限。 |
| `targetModules` | `["07_inequality"]` | 本轮显式构建的模块。 |
| `targetItems` | `[]` | 本轮没有限定具体 item，因此构建模块下所有合法条目。 |

## 6. `fieldMaskLegend` 字段

`fieldMaskLegend` 用 bit 位记录 posting 来自哪些字段。posting 的第三位 `fieldMask` 是这些值的按位或。

| 字段 | mask | 说明 |
|---|---:|---|
| `title` | 1 | 标题命中 |
| `alias` | 2 | 别名命中 |
| `keyword` | 4 | 关键词命中 |
| `synonym` | 8 | 同义词命中 |
| `intent` | 16 | 搜索意图命中 |
| `query_template` | 32 | 查询模板命中 |
| `ocr_keyword` | 64 | OCR 关键词命中 |
| `category` | 128 | 分类命中 |
| `tag` | 256 | 标签命中 |
| `formula_token` | 512 | 公式 token 命中 |
| `formula` | 1024 | 公式命中 |
| `summary` | 2048 | 摘要命中 |
| `statement_fragment` | 4096 | 陈述片段命中 |
| `usage` | 8192 | 使用场景/题型命中 |
| `knowledge_node` | 16384 | 知识节点命中 |
| `pinyin` | 32768 | 拼音命中 |
| `pinyin_abbr` | 65536 | 拼音首字母命中 |

例子：`fieldMask = 5732` 可拆为 `keyword(4) + ocr_keyword(64) + formula_token(512) + formula(1024) + statement_fragment(4096)`，表示同一个 term/doc 命中了这些来源字段。

## 7. `docs` 字段

`docs` 是文档主表，结构为：

```json
{
  "I001": {
    "id": "I001",
    "module": "inequality",
    "moduleDir": "07_inequality",
    "title": "连不等式N<f(x)<M的四种等价形式",
    "summary": "...",
    "category": "不等式",
    "tags": ["..."],
    "coreFormula": "N < f(x) < M",
    "rank": 186,
    "difficulty": 2.0,
    "searchBoost": 0.75,
    "hotScore": 70.0,
    "examFrequency": 0.6,
    "examScore": 5.0
  }
}
```

字段意义和来源：

| 字段 | 来源 | 含义 |
|---|---|---|
| `id` | `meta.id`，没有则退回 item 目录名 | 文档主键，posting 都通过它回指文档。 |
| `module` | `meta.module`，没有则退回模块目录名 | 业务模块名。 |
| `moduleDir` | 模块目录名 | 文件系统定位用，例如 `07_inequality`。 |
| `title` | `core.title`, `title`，没有则退回 item 目录名 | 搜索结果主标题。 |
| `summary` | `core.summary`, `summary`, `preview`, `content.intuition`；没有则退回陈述片段 | 搜索结果摘要。 |
| `category` | `core.category`, `category`, `chapter`, `section` | 分类展示或筛选信息。 |
| `tags` | `core.tags`, `tags` 的前 8 个 | 结果标签，限制数量以控制体积。 |
| `coreFormula` | 公式来源列表中的第一项 | 结果页可展示的核心公式。 |
| `rank` | 构建期计算 | 静态排序分，用于查询结果排序微调。 |
| `difficulty` | `core.difficulty`, `difficulty` | 难度。 |
| `searchBoost` | `ranking.search_boost`, `ranking.searchBoost` | 人工/业务搜索加权。 |
| `hotScore` | `ranking.hot_score`, `ranking.hotScore` | 热度分。 |
| `examFrequency` | `usage.exam_frequency`, `usage.examFrequency`, `examFrequency` | 考频。 |
| `examScore` | `usage.exam_score`, `usage.examScore`, `examScore` | 分值或题目价值。 |

`rank` 的计算公式来自 `compute_rank_score`：

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

## 8. `termIndex` 字段

`termIndex` 是精确倒排索引，结构为：

```json
{
  "检索词": [
    ["docId", score, fieldMask]
  ]
}
```

posting 三元组含义：

| 位置 | 字段 | 含义 |
|---:|---|---|
| 0 | `docId` | 命中的文档 ID，对应 `docs[docId]`。 |
| 1 | `score` | 构建期相关性分数。精确索引中，同一 `(term, docId)` 多次命中会累加。 |
| 2 | `fieldMask` | 命中来源字段的 bit mask，用 `fieldMaskLegend` 反解。 |

`termIndex` 的 key 都是构建期归一化后的字符串，不一定等于原文。归一化包括：

- Unicode NFKC 归一化。
- 折叠连续空白并去首尾空白。
- 转小写。
- 中英文引号统一。
- 紧凑变体会移除所有空白。
- 公式字段会把部分 LaTeX 写法映射为统一符号，并移除空格。

同一原始文本会派生多个 exact 变体：

| 变体 | 分数系数 | 含义 |
|---|---:|---|
| `full` | 1.00 | 完整归一化文本 |
| `compact` | 0.96 | 去空白后的紧凑文本 |
| `token` | 0.72 | 中文片段或拉丁 token |
| `ngram` | 0.58 | 中文 n-gram 子串 |
| `pinyin` | 0.72 | 自动拼音 |
| `pinyin_abbr` | 0.62 | 自动拼音首字母 |

posting 排序规则：

1. `score` 降序。
2. `docs[docId].rank` 降序。
3. `docId` 升序，保证稳定。

## 9. `prefixIndex` 字段

`prefixIndex` 是前缀倒排索引，结构与 `termIndex` 相同：

```json
{
  "前缀": [
    ["docId", score, fieldMask]
  ]
}
```

差异在于：

- 只对适合前缀召回的字段生成。
- 中文前缀从 1 个字开始。
- 英文、拼音前缀从 2 个字符开始。
- 中文前缀最长 12 个字符；英文/拼音前缀最长 16 个字符。
- 分数额外乘以 `prefix_ratio`，默认 `0.70`。
- 同一 `(prefix, docId)` 多次命中时取最大分，不累加，避免前缀噪声过大。
- 每个 key 的 posting 最多保留 `buildOptions.prefixDocLimit` 条，当前为 32。

## 10. `suggestions` 字段

`suggestions` 是联想词数组，结构为：

```json
[
  ["展示文本", "docId", score]
]
```

字段含义：

| 位置 | 字段 | 含义 |
|---:|---|---|
| 0 | `displayText` | 展示给用户看的联想文本，尽量保留原始可读形式。 |
| 1 | `docId` | 联想项对应的主文档。 |
| 2 | `score` | 联想排序分，当前为字段权重加文档 `rank`。 |

只有适合直接展示的字段会进入联想，例如标题、别名、关键词、同义词、分类、标签。公式、长句式、OCR 关键词等默认不进入 suggestion。

当前前 5 个联想样例：

```json
[
  ["对数平均值不等式", "I033", 371],
  ["伯努利不等式", "I028", 369],
  ["柯西不等式", "I005", 369],
  ["基本不等式及其变形", "I002", 368],
  ["三元均值不等式", "I009", 366]
]
```

## 11. 字段权重与动态调权

基础权重定义在 `scripts/build_search_bundle_js.py` 的 `FIELD_SPECS`。部分字段可以被 `meta.json` 中的 `searchmeta` 或 `searchMeta` 调整：

| 动态键 | 默认值 | 影响字段 |
|---|---:|---|
| `titleWeight` | 10 | `title` |
| `keywordWeight` | 8 | `keyword` |
| `synonymWeight` | 6 | `synonym` |
| `ocrWeight` | 9 | `ocr_keyword` |
| `formulaWeight` | 7 | `formula_token`, `formula` |

脚本会按“配置值 / 默认值”的比例缩放该字段的基础权重。例如某条内容的 `searchmeta.keywordWeight` 高于默认值，则它的关键词命中分会相应提高。

## 12. 与旧索引脚本的关系

`scripts/build_all_indexes.py` 是较早的多文件索引方案，目标输出类似：

```text
search_engine/keyword_index.json
search_engine/prefix_index.json
search_engine/pinyin_index.json
search_engine/pinyin_short_index.json
search_engine/formula_index.json
search_engine/ranking_index.json
search_engine/meta_compact.json
search_engine/suggestion_index.json
```

当前 `data/search_engine/backend_search_index.json` 的结构是 `docs + termIndex + prefixIndex + suggestions`，来源和结构都对应 `scripts/build_search_bundle_js.py` 与 `scripts/extract_backend_index_from_search_bundle.py`，不应按 `build_all_indexes.py` 的旧结构理解。

## 13. 校验建议

如果要确认后端 JSON 与当前 bundle 完全一致，可运行：

```powershell
python scripts\verify_backend_index_extraction.py
```

本次运行结果是不一致，主要原因是当前 `search_bundle.js` 只包含 1 篇文档，而 `backend_search_index.json` 包含 42 篇文档。

如果要重新生成同一链路的后端索引，通常流程是：

```powershell
python scripts\build_search_bundle_js.py --module 07_inequality
python scripts\extract_backend_index_from_search_bundle.py --input data/search_engine/search_bundle.js --output data/search_engine/backend_search_index.json --pretty
```

重新生成前应先修复当前无法解析的 `I043`、`I044` 两个 `meta.json`，否则它们仍会被跳过，或在 strict 模式下导致构建失败。
