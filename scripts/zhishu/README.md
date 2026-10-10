# Zhishu Publisher — Task 8A Freeze

Task 8A is frozen at the Source Discovery → Source Initialization → Runtime
Mapping → Content Package → Validation/Diff boundary.

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
python scripts/zhishu/publish.py build-content --share-video-uid C002 --prepared-assets <isolated-directory> --output <isolated-directory>
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

## Package contract

A package contains `manifest.json`, four stable runtime JSON files, and
`resources/images/` plus `resources/pdfs/`. Entity hashes, asset-content hashes,
the package hash, and `contentVersion` use SHA-256 over deterministic content.
No timestamp, random ID, machine path, or file mtime participates in identity,
versioning, or diff decisions.

Diff compares stable entity IDs and content hashes and reports only `ADD`,
`UPDATE`, and `DELETE`. Package construction validates a complete staged package
before replacing the requested output directory.

## Optional C002 video package (Task 14C.MP4.1)

The default commands above retain the Task 8A `schemaVersion: 1` package byte
contract. Video packaging is explicit: `--share-video-uid C002` requires a
non-default isolated package output; `build-content` also requires a non-default
prepared-assets output. The selected UID's `videos/share_assets.json` must
link a real Publisher GIF asset ID and URI to one H.264 MP4, with matching
source hashes, size, MIME, and explicit video URI. Unregistered video files,
missing files, wrong MIME/codec, duplicate or cross-animation links fail.

The opt-in package has `schemaVersion: 2`. Its four existing runtime JSON
files, existing `KnowledgeAsset` image/PDF rows, image sort orders, and search
documents retain their v1 meaning. It adds `animation-shares.json`,
`resources/videos/<UID>/<name>.mp4`, `manifest.files.animationShares`,
`manifest.counts.animationShares` / `videoAssets`, and
`manifest.shareAssetHashes`. The v2 package hash covers the new relation
entity hashes and video byte hashes. Validation rejects missing, extra, or
altered video resources. Diff reports an `AnimationShare` ADD/UPDATE/DELETE.

The existing Zhishu Sync (`D:/work/zhishu/scripts/zhishu/sync_knowledge_content.py`
as audited on 2026-10-10) requires `schemaVersion == 1`, scans only
`resources/images` and `resources/pdfs`, and cannot safely consume videos.
It accepts the unchanged v1 package and rejects v2 before writing. Do not
point old Sync at a v2 package. Updating Sync and the App's video registry is
a separate Zhishu task; this Publisher task performs neither operation.
