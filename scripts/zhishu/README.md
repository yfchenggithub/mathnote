# Zhishu Publisher — Canonical Content Package v2

The Task 8A source discovery, runtime mapping, and image/PDF DTO meanings stay
frozen. Task 14C.MP4.2A makes video aware schema v2 the formal default at the
Content Package → Validation/Diff boundary.

## Commands

```text
python scripts/zhishu/publish.py scan
python scripts/zhishu/publish.py init-source
python scripts/zhishu/publish.py map-runtime
python scripts/zhishu/publish.py prepare-assets
python scripts/zhishu/publish.py build-package
python scripts/zhishu/publish.py build-package --output <directory>
python scripts/zhishu/publish.py build-content
python scripts/zhishu/publish.py build-content --prepared-assets <directory> --output <directory>
python scripts/zhishu/publish.py build-content --allow-video-removal
python scripts/zhishu/publish.py diff <previous-package> <current-package>
```

Without `--output`, `build-package` writes to
`<repository>/build/zhishu-content-package`. An explicit `--output` still
overrides the default.

`build-content` is the formal producer command. It performs a complete Runtime
Image Preparation rebuild and freshness verification before package assembly.
`build-package` consumes an already prepared, verified staging directory and
fails if its manifest, source hashes, output hashes, tool version, or file
coverage is stale.

## Runtime image preparation contract

Source PNG and GIF files remain in each Conclusion `images/` directory and are
never modified. The generated mirror defaults to
`build/zhishu-runtime-assets/images/<knowledgeId>/`; PNG inputs become WebP,
while validated animated GIF inputs are copied byte-for-byte as GIF. The
directory is fully rebuilt, so source ADD/UPDATE/DELETE operations cannot leave
orphan runtime files.

- encoder: `sharp` at the version pinned by `package-lock.json` (currently
  0.34.5)
- format: real WebP
- quality: 85
- maximum width: 1440 px
- aspect ratio: preserved
- upscale: forbidden
- GIF: at least two decodable frames, valid timing, explicit infinite loop,
  and identical source/output SHA-256
- unstable timestamps and source machine paths: excluded from the manifest

The package continues to copy PDFs byte-for-byte from the source `pdfs/`
directories. Runtime image URIs are emitted truthfully as
`resources/images/<knowledgeId>/<name>.webp` or `.gif`; PDF URIs remain
`resources/pdfs/<knowledgeId>/<name>.pdf`.

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
- Runtime images come only from the generated PNG-to-WebP/GIF-pass-through
  mirror prepared from direct source files in `images/`; PDFs come directly
  from `pdfs/` unchanged.
- Canonical content is not a Publisher input.

## Frozen runtime compatibility

Publisher DTOs match the existing Zhishu App fields for `KnowledgeNode`,
`KnowledgeRelation`, and `KnowledgeAsset`. The App domain model and repository
interfaces are not modified by this Publisher.

### Optional knowledge sharing text

`meta.json.shareConfig.title` and `meta.json.shareConfig.shareDesc` are optional
strings on the corresponding knowledge node. `runtime_mapping.parse_share_config`
validates them, and the `KnowledgeNode.shareConfig` DTO passes through the normal
Full v2 JSON writer and Schema v4 module slicer. Structural nodes do not acquire
sharing defaults. The existing entity/file/package hashes and `contentVersion`
include this metadata; no schema version or capability flag changes are required.

Missing/null objects and fields are omitted. Empty strings, whitespace, Unicode
and punctuation are preserved exactly; fallback copy and whitespace handling
belong to the App. Non-object configurations and non-string, non-null values in
the two text fields are source-qualified mapping errors and block construction.
Package validation applies the same type rule. Other source-only keys such as
`imageUrl` are not copied into this text contract. No promotional suffix is added.

Re-export via `publish.py build-content` and `slice_modules.py`; never edit final
JSON/ZIPs and reseal them by hand. Use a higher `--package-version` when replacing
an installed module with changed content, even though the schema stays at v4.

## Package contract

A package contains `manifest.json`, four stable runtime JSON files,
`animation-shares.json`, and the registered files under `resources/images/`,
`resources/pdfs/`, and optionally `resources/videos/`. Entity hashes, asset-content hashes,
the package hash, and `contentVersion` use SHA-256 over deterministic content.
No timestamp, random ID, machine path, or file mtime participates in identity,
versioning, or diff decisions.

Diff compares stable entity IDs and content hashes and reports only `ADD`,
`UPDATE`, and `DELETE`. Package construction validates a complete staged package
before replacing the requested output directory.

## Canonical v2 video package (Task 14C.MP4.2A)

The no-argument `build-content` command is the single formal producer. It
always writes `schemaVersion: 2` to `build/zhishu-content-package` and scans
the whitelisted knowledge sources for `videos/share_assets.json`. Each source
registry must link a real Publisher GIF asset ID and URI to H.264 MP4 bytes,
with matching source hashes, size, MIME, and explicit video URI. No UID is
hardcoded. Unregistered video files, missing files, wrong MIME/codec, duplicate
or cross-animation links fail the build without replacing the previous valid
package. A removal from an existing v2 output also fails unless the operator
explicitly passes `--allow-video-removal` after reviewing the removed asset IDs.

The canonical package has `schemaVersion: 2`. Its four existing runtime JSON
files, existing `KnowledgeAsset` image/PDF rows, image sort orders, and search
documents retain their v1 meaning. It adds `animation-shares.json`,
`resources/videos/<UID>/<name>.mp4`, `manifest.files.animationShares`,
`manifest.counts.animationShares` / `videoAssets`, and
`manifest.shareAssetHashes`. The v2 package hash covers the new relation
entity hashes and video byte hashes. Validation rejects missing, extra, or
altered video resources. Diff reports an `AnimationShare` ADD/UPDATE/DELETE.
When no video is registered, `animation-shares.json` is `[]`, both video counts
are `0`, and `shareAssetHashes` is `{}`; the package remains valid v2. The
historical v1 writer is retained only for isolated migration tests and cannot
target the formal default output.

The existing Zhishu Sync (`D:/work/zhishu/scripts/zhishu/sync_knowledge_content.py`
as audited on 2026-10-10) requires `schemaVersion == 1`, scans only
`resources/images` and `resources/pdfs`, and cannot safely consume videos.
It accepts historical v1 packages and rejects v2 before writing. Upgrade Sync
and its video registry before feeding it the canonical package. This MathNote
Publisher task does not execute Sync.
