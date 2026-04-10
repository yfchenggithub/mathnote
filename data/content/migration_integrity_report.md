# migration_integrity_report

## Summary

- **total_source_records**: 42
- **total_target_records**: 42
- **matched_records**: 42
- **missing_in_target**: 0
- **extra_in_target**: 0
- **passed_records**: 42
- **warning_records**: 0
- **failed_records**: 0
- **field_warning_count**: 0
- **field_failed_count**: 0
- **uncovered_legacy_field_count**: 30

## Mapping Rules Summary

### Record Level
- **record_id**: source.id 优先；若缺失则回退 source_key
- **source_key_mismatch**: 当 source_key != source.id 时，采用 source.id 作为最终记录 id，并记 warning
- **slug**: 由 slugify_record(record_id, title) 生成
- **module_fallback**: source.module 优先；为空时回退 source_js 文件 stem

### Field Rules
- `id` -> `id`
- `schema_version` -> `固定 2`
- `type` -> `固定 conclusion`
- `status` -> `固定 published`
- `title` -> `meta.title`
- `module` -> `identity.module`
- `knowledgeNode` -> `identity.knowledge_node`
- `altNodes` -> `identity.alt_nodes（字符串按中英文逗号拆分，去重保序）`
- `alias` -> `meta.aliases（字符串按逗号/分号/换行拆分，或保留数组）`
- `difficulty` -> `meta.difficulty（解析为 0~10 整数，越界钳制，异常写 warning）`
- `category` -> `meta.category`
- `tags` -> `meta.tags`
- `core_summary` -> `meta.summary`
- `isPro` -> `meta.is_pro（宽松布尔转换）`
- `remarks` -> `meta.remarks`
- `core_formula` -> `content.primary_formula`
- `variables` -> `content.variables（{latex|name|symbol, description|desc|text, required} -> {name, latex, description, required}）`
- `conditions` -> `content.conditions[*]（统一包装为 cond_i + content[text]）`
- `conclusions` -> `content.conclusions[*]（统一包装为 conc_i + content[text]）`
- `sections` -> `content.sections（layout=text/theorem-list -> blocks）`
- `statement` -> `content.plain.statement`
- `explanation` -> `content.plain.explanation`
- `proof` -> `content.plain.proof`
- `examples` -> `content.plain.examples`
- `traps` -> `content.plain.traps`
- `summary` -> `content.plain.summary`
- `assets` -> `assets（识别 cover/svg/png/pdf/mp4，其余进入 assets.extra）`
- `shareConfig` -> `ext.share（title -> title, desc/shareDesc -> desc）`
- `relations` -> `ext.relations（prerequisites, related_ids, similar）`
- `usage.exam_frequency` -> `ext.exam.frequency`
- `usage.exam_score` -> `ext.exam.score`
- `usage` -> `ext.extra.usage（完整原值保留）`
- `interactive` -> `ext.extra.interactive`
- `related_formulas` -> `ext.extra.related_formulas`
- `display_version` -> `ext.extra.legacy_display_version`
- `unknown_legacy_fields` -> `ext.extra.unmapped_legacy_fields`

### Sections Rules
- **layout=text**: `['{text} -> paragraph(tokens=[text])', '{latex} -> math_block', '{segments:[...]} -> paragraph(tokens)', '{text, latex} -> paragraph(text + math_inline)，并写 warning', '未知形态 -> paragraph(降级文本)，并写 warning']`
- **layout=theorem-list**: `['items -> single theorem_group block', '{title, desc, latex} -> theorem item', '缺 latex 时尝试用 text，仍无则写 "\\text{N/A}" 并 warning']`
- **block_type**: `{'summary': 'summary', 'trap/warning/易错/陷阱/注意': 'warning_group', 'theorem-list': 'theorem_group', 'others': 'rich_text'}`

## Failed Records

无。
## Warning Records

无。