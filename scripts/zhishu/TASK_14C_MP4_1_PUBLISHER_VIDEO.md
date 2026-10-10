# Task 14C.MP4.1 — Publisher Video Asset Contract Extension

Date: 2026-10-10. Scope: C002's existing GIF and completed MP4, plus the MathNote Publisher contract. Result: **MATHNOTE DUAL ASSET PACKAGE PASS · ZHISHU SYNC PENDING**. This is a local, isolated Publisher result; no Zhishu Sync, Android build, App resource generation, or production release was run.

## 1. Pre-flight Audit

The MathNote working tree was clean before this task. The repository root `AGENTS.md`, `docs/architecture/math-rendering-boundaries.md`, the Task 14C.MP4 report (especially section 7), actual `scripts/zhishu/` Publisher code, and its tests were read before editing. The report proposed an optional `animation-shares.json`, a video resource root, manifest and hash registration, exact GIF-ID association, and a negotiated package version. The present authorization covers these changes for C002. The architecture and root rules were updated to record the approved narrow exception; no general video discovery or cross-UID production was introduced.

The existing C002 MP4 was reused. Its formal TeX, `meta.json`, Scene, original GIF, PDFs, and other knowledge resources were not modified. The default production package output was not overwritten. The Zhishu checkout at `D:/work/zhishu` was inspected read-only.

## 2. Frozen Contract Compatibility Audit

The Task 8A v1 package has four runtime JSON files (`knowledge-nodes.json`, `knowledge-relations.json`, `knowledge-assets.json`, `search-documents.json`), `resources/images/`, `resources/pdfs/`, image/PDF `KnowledgeAsset` rows, and `schemaVersion: 1`. Publisher validation checks exact resource coverage and deterministic entity, asset, file, and package hashes. A loose MP4 or a video row disguised as an image would violate that contract.

The actual old Sync in `D:/work/zhishu/scripts/zhishu/sync_knowledge_content.py` requires `schemaVersion == 1` before mutation. Its fixed runtime file list and resource groups contain only images/PDFs; its URI parser rejects a `resources/videos/` URI. `generate_knowledge_asset_registry.mjs` also supports only image/PDF `KnowledgeAsset` types and roots. Thus an unversioned optional video extension is not safe for the old consumer. Direct read-only validation accepted the unchanged v1 package and rejected the v2 package with `Unsupported source schemaVersion 2; expected 1` before Sync execution.

The default Publisher path remains v1, including its original hash calculation. Only explicit `--share-video-uid C002` creates v2. Legacy Content Packages remain valid. The new v2 package must be held outside the old Sync input until the consumer is upgraded.

## 3. Formal Schema / Contract Changes

`schemaVersion: 2` adds one root JSON file, `animation-shares.json`, whose top-level value is an array. Each association row has `displayAssetId`, `displayAssetUri`, `shareAssetId`, `knowledgeId`, `uri`, `mimeType`, `bytes`, and `sha256`. The v2 manifest adds `files.animationShares`, `counts.animationShares`, `counts.videoAssets`, `entityHashes.animationShares`, `fileHashes.animationShares`, and `shareAssetHashes` keyed by the MP4 share asset ID. The v2 package hash covers the relation entity hashes and video byte hashes along with the existing entities and assets.

The existing four JSON files and `KnowledgeAsset` image/PDF meanings are unchanged. Video is a separate resource identity, not an image/PDF `KnowledgeAsset`. Existing GIFs need no association. v1 packages need no new field or directory.

## 4. GIF / MP4 Association Design

The C002 source declaration at `videos/share_assets.json` is the UID-local authoring record. Publisher checks it against the real generated GIF asset ID/URI and source GIF hash, then issues the formal package relation in `animation-shares.json`. The consumer must read the package relation; it must not infer the MP4 name from the GIF filename.

| Field | Formal value |
| --- | --- |
| Knowledge ID | `C002` |
| GIF Asset ID | `C002:image:ellipse_line_distance.gif` |
| GIF logical URI | `resources/images/C002/ellipse_line_distance.gif` |
| MP4 Asset ID | `C002:share-video:ellipse_line_distance.mp4` |
| MP4 logical URI | `resources/videos/C002/ellipse_line_distance.mp4` |
| MIME | `video/mp4` |

The relation is one-to-one by exact GIF Asset ID and exact MP4 Asset ID/URI. Duplicate display links, duplicate video identities, crossed links, wrong types, missing resources, unregistered videos, and changed bytes fail validation. A fixture with two GIFs confirms that each resolves to its own MP4.

## 5. Publisher Changes

`share_videos.py` validates the selected UID's authoring record, physical GIF and MP4, IDs, URIs, hashes, byte count, and H.264 MP4 format. `content_package.py` copies the selected MP4 to `resources/videos/C002/`, generates and validates the public relation file, adds v2 manifest metadata, includes video data in the deterministic package hash, and reports `AnimationShare` changes in package diffs. `publish.py` exposes `--share-video-uid C002` for `build-content` and `build-package`. It refuses the default package output for v2; `build-content` also requires an isolated prepared-assets directory.

No image preparation rule was relaxed. The MP4 does not enter `images/` or `knowledge-assets.json`; no PDF, search document, or knowledge node mapping was changed.

## 6. C002 Dual Asset Package

The isolated producer command was:

```powershell
python -B scripts/zhishu/publish.py build-content --share-video-uid C002 --prepared-assets build/manim/C002/14C_MP4_1/runtime-assets --output build/manim/C002/14C_MP4_1/content-package
```

The package is at `build/manim/C002/14C_MP4_1/content-package/`, with MP4 at `resources/videos/C002/ellipse_line_distance.mp4` and the public relation at `animation-shares.json`. It has `schemaVersion: 2`, `contentVersion: sha256:a888e7e7b2e4f1ad8b4b5320922e45e4c08b5789c4406dc67ea9a897f1570c44`, and total size 127,099,285 bytes. Counts: 1,030 knowledge nodes, 32 relations, 667 existing image/PDF assets (96 images and 571 PDFs), 571 search documents, one animation share, and one video asset.

An independent `build-package` from the same prepared assets produced the same version, file set, and byte hashes. The isolated default v1 build remained `sha256:b289b18501c57d656580170b363d2cea38e790dcd9ac7a1ae5189ba0bce4ce1b`, size 126,552,702 bytes, matching the prior Task 14C.MP4 baseline. Its four runtime JSON files and C002 GIF are byte-identical to the v2 equivalents. The 546,583-byte package increase consists of the 545,671-byte MP4 plus relation and manifest metadata.

## 7. Manifest / Resource Validation

Publisher validation returned zero issues for both isolated v1 and v2 packages. The v2 manifest registers `animation-shares.json` and `shareAssetHashes[C002:share-video:ellipse_line_distance.mp4] = 1a09bc46118dff27770035efa4327588a4dc252730430862918cd98753f28c74`. The packaged MP4 is 545,671 bytes and has MIME `video/mp4`. The unchanged GIF SHA-256 is `1ad4d074699a3d193627bb0cbeadd7fdbedc53e833e8772fd9f0584494f9a5ad`.

Validation requires both physical resources to exist, checks MP4 size/hash and actual codec, resolves logical URIs to the matching package paths, checks the referenced display asset is a GIF image for C002, and rejects any extra or orphan resource. It verifies relation entity hashes, JSON file hashes, video hashes, counts, and the overall package hash. The existing C002 image sort orders remain unchanged; the GIF remains display sort order 50.

## 8. Old Consumer Compatibility

| Package | Old Sync | Future upgraded Sync | Image registry |
| --- | --- | --- | --- |
| v1, no video | Accepted by actual old source validator | Must continue to accept | Existing image/PDF behavior |
| v2, C002 video | Explicitly rejected before mutation | Must validate and consume the new relation and video | Existing image/PDF entries unchanged; video needs its own lookup |

This task does **not** claim old Sync can consume v2. Its refusal is the required safe boundary. Package Version was upgraded from schema 1 to schema 2 only for the explicit video build. Migration order: implement and test a Zhishu Sync reader for v1 and v2; add video resource copying, hash and relation checks, and a dedicated GIF-ID-to-MP4 lookup; then direct the upgraded consumer to the isolated v2 package. Keep v1 support and the original image registry. No old Sync job may read the v2 package during the transition.

## 9. Automated Test Results

- Existing 50 Publisher and rendering-boundary regressions, plus two CLI guards and eight video tests: **60 PASS**. Video tests cover deterministic output, legacy v1, missing or altered MP4, wrong type, crossed and multiple GIF links, manifest tampering, orphan resources, and v1-to-v2 diff.
- C002 mathematical model and local association tests: **7 PASS**; UID-local share verifier: **PASS**.
- Full isolated v2 build and package validation: **PASS**, zero errors and warnings. Repeated build: identical file set and SHA-256 hashes.
- Isolated v1 build and validation: **PASS**; v1 content version equals the previous baseline.
- Actual old Sync source validator, called read-only: v1 **ACCEPTED**, v2 **REJECTED** with explicit schema-version error. No Sync operation was run.
- Protected C002 source/asset diff and `git diff --check`: **PASS**.

## 10. Changed Files

- `03_conic/C002_ellipse_point_line_distance_extrema/videos/share_assets.json` — explicit formal MP4 URI in the source declaration.
- `03_conic/C002_ellipse_point_line_distance_extrema/manim/verify_share_assets.py` — checks that URI.
- `scripts/zhishu/share_videos.py` — source relation and video validation.
- `scripts/zhishu/content_package.py` — opt-in v2 packing, validation, hashing, and diff.
- `scripts/zhishu/publish.py` — guarded v2 CLI option.
- `tests/test_zhishu_share_videos.py`, `tests/test_zhishu_publish.py` — coverage and CLI guards.
- `AGENTS.md`, `docs/architecture/math-rendering-boundaries.md`, `scripts/zhishu/README.md` — approved boundary and contract documentation.
- This report.

The completed MP4 was already present at task start; it was not regenerated or changed here.

## 11. Zhishu Handoff Contract

The upgraded Sync should first require manifest schema 2 and verify the existing package checks plus `files.animationShares == "animation-shares.json"`, `fileHashes.animationShares`, `entityHashes.animationShares`, `shareAssetHashes`, `counts.animationShares`, `counts.videoAssets`, and `packageHash`. For each row, resolve `displayAssetId` in `knowledge-assets.json` to the exact GIF `displayAssetUri`, then resolve the share `uri` to the packaged MP4, verify `mimeType == "video/mp4"`, byte count, SHA-256, and uniqueness. Copy registered `resources/videos/` files, reject extras and dangling links, and expose a dedicated lookup keyed by the exact GIF Asset ID. The current image/PDF Registry must keep its existing entries and order; MP4 is not inserted there. The App sharing phase may use the local MP4 path and `video/mp4` after the upgraded Sync/Registry work is authorized and completed.

For C002, the only share relation is `C002:image:ellipse_line_distance.gif` → `C002:share-video:ellipse_line_distance.mp4`; its public URI is `resources/videos/C002/ellipse_line_distance.mp4`. The handoff artifact is the isolated v2 package above. This task stops before Zhishu Sync/Registry implementation.

## 12. Remaining Risks

Zhishu Sync and its Registry/App video lookup do not yet support v2; that work is **PENDING**. The old consumer is intentionally incompatible with v2 and must remain on v1. The isolated package has not been deployed, synced, or tested in Android; those gates remain **PENDING**. There is no unresolved Publisher or v1 compatibility block, and no Final Freeze is claimed.
