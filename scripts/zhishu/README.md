# Zhishu Publisher — Task 8A Freeze

Task 8A is frozen at the Source Discovery → Source Initialization → Runtime
Mapping → Content Package → Validation/Diff boundary.

## Commands

```text
python scripts/zhishu/publish.py scan
python scripts/zhishu/publish.py init-source
python scripts/zhishu/publish.py map-runtime
python scripts/zhishu/publish.py build-package --output <directory>
python scripts/zhishu/publish.py diff <previous-package> <current-package>
```

## Frozen source boundary

- Discovery uses only the explicit 11-module whitelist in
  `source_discovery.py`.
- Every direct child directory of a whitelisted module is a Conclusion Source.
- Discovery is non-recursive and does not infer modules or conclusions from
  file contents.
- Runtime mapping uses `knowledgeNode` for the single primary tree parent and
  `relations.related_ids` for related relations.
- `altNodes`, `relations.prerequisites`, and `relations.similar` are deliberately
  outside this frozen version and must not affect validation or output.
- Runtime assets come only from direct files in `images/` and `pdfs/`.
- Canonical content is not a Publisher input.

## Frozen runtime compatibility

Publisher DTOs match the existing Zhishu App fields for `KnowledgeNode`,
`KnowledgeRelation`, and `KnowledgeAsset`. The App domain model and repository
interfaces are not modified by this Publisher.

## Package contract

A package contains `manifest.json`, four stable runtime JSON files, and
`resources/images/` plus `resources/pdfs/`. Entity hashes, asset-content hashes,
the package hash, and `contentVersion` use SHA-256 over deterministic content.
No timestamp, random ID, machine path, or file mtime participates in identity,
versioning, or diff decisions.

Diff compares stable entity IDs and content hashes and reports only `ADD`,
`UPDATE`, and `DELETE`. Package construction validates a complete staged package
before replacing the requested output directory.
