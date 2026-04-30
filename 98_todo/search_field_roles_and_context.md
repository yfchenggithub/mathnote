# 搜索字段角色说明与待办（暂存）

更新时间：2026-04-30

## 一、当前上下文（为什么会有这份文档）

近期我们重构了 `scripts/build_search_bundle_js.py`，核心目标是让 `data/search_engine/search_bundle.js` 更干净、可解释、可调试：

1. 默认关闭粗暴 CJK n-gram（`--enable-cjk-ngrams` 才开启）。
2. suggestion 只允许来自“人类可读字段”，并增加质量过滤。
3. 新增了两个可配置字段入口：
   - `search.suggestTerms` / `search.suggest_terms` / `suggestTerms`
   - `search.searchTerms` / `search.search_terms` / `searchTerms`

因此，当前数据层需要明确：已有 `search` 字段如何分工，`suggestTerms` / `searchTerms` 是否必须，以及如何逐步落地。

## 二、结论（先给结论）

1. 现有 `keywords / synonyms / intents / query_templates / formulaTokens / pinyin` **不是不满足要求**，仍然有效。
2. `suggestTerms` / `searchTerms` **不是强制字段**，但在 500 条以内精品搜索场景下，强烈建议补齐。
3. 这两个字段的价值在于：把“展示质量”和“召回覆盖”解耦，减少机器噪声对联想词的影响。

## 三、字段角色关系（统一口径）

### 1) 展示层（给用户看的联想）
- `suggestTerms`：高质量、人工可控的联想词来源（优先推荐）
- 其他会参与展示的字段：`title / alias / keywords / tags`

说明：`suggestTerms` 的作用是“我希望用户在联想下拉里看到什么”。

### 2) 召回层（给系统找结果）
- `searchTerms`：召回增强词，不用于展示（可放口语、错拼、别称、变体）
- `keywords`：标准关键词主召回
- `synonyms`：同义叫法补充
- `intents`：意图型检索（如“求最值”“判定条件”）
- `query_templates`：长句问法召回
- `formulaTokens`：公式/符号入口
- `pinyin / pinyinAbbr`：拼音入口

说明：`searchTerms` 的作用是“我希望系统能搜到什么，即使不适合展示”。

### 3) 兜底层（可关闭）
- CJK n-gram（当前默认关闭）：仅作为低优先级兜底，不是主策略。

## 四、为什么建议补 `suggestTerms` / `searchTerms`

1. `keywords` 往往既承担召回又承担展示，语义会混杂。
2. 某些词适合召回但不适合展示（例如公式片段、口语错拼、长串拼音）。
3. 随条目数增长（目标约 500），纯靠自动展开更容易出现“可命中但不优雅”的建议词。
4. 人工分层后，调试成本更低：展示问题优先看 `suggestTerms`，召回问题优先看 `searchTerms/keywords`。

## 五、落地建议（按增量执行）

1. 新条目创建时默认补这两个字段：
   - `suggestTerms`: 3~8 个，短、可读、意图明确
   - `searchTerms`: 5~15 个，覆盖问法/别称/错拼/公式俗写
2. 老条目按高频模块补齐（先不全量回填）：
   - 先补 `07_inequality`、`03_conic`、`05_geometry-solid`
3. 建议词规范：
   - 不放超长句子
   - 不放机械片段
   - 不放仅符号或纯数字项
4. 公式类词优先进入 `searchTerms` 或 `formulaTokens`，避免污染展示。

## 六、推荐模板（meta.json 片段）

```json
"search": {
  "keywords": [],
  "synonyms": [],
  "intents": [],
  "query_templates": [],
  "formulaTokens": [],
  "pinyin": "",
  "pinyinAbbr": "",
  "suggestTerms": [],
  "searchTerms": []
}
```

## 七、相关文件（定位上下文）

- `scripts/build_search_bundle_js.py`
- `data/search_engine/search_bundle.js`
- `data/search_engine/search_audit.json`
- 示例条目：
  - `05_geometry-solid/G001_sphere_volume_surface_formula/meta.json`
  - `09_geometry-plane/P007_pqr_area_symmetric/meta.json`

