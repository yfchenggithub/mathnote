# Task 14C.MP4 — C002 GIF + MP4 dual asset production

Date: 2026-10-10. Scope: only the existing `ellipse_line_distance.gif` animation in C002. Status: **MP4 PRODUCTION PASS · PUBLISHER INTEGRATION BLOCKED · ZHISHU INTEGRATION PENDING**.

## 1. Pre-flight Audit

`git status --short --untracked-files=normal` was empty before editing. The formal C002 TeX, `meta.json`, original GIF, Scene, mathematical model, PDF, and other images were left unchanged. `scripts/manim/` Task 13F tooling is frozen; no shared render/export code was changed. The Publisher is in this writable repository at `scripts/zhishu/`, but its Task 8A source and runtime contracts are frozen. No Zhishu App, MaxNodes, Sync, APK, default production package, or other UID asset was changed.

## 2. GIF Source Identification

- Formal knowledge ID: `C002`, from `03_conic/C002_ellipse_point_line_distance_extrema/meta.json`.
- Formal display asset: `03_conic/C002_ellipse_point_line_distance_extrema/images/ellipse_line_distance.gif`.
- Publisher asset ID: `C002:image:ellipse_line_distance.gif`.
- Publisher logical URI: `resources/images/C002/ellipse_line_distance.gif`.
- GIF: 576×1024, 161 frames, 13.410 s, explicit infinite loop, 1,721,935 bytes, SHA-256 `1ad4d074699a3d193627bb0cbeadd7fdbedc53e833e8772fd9f0584494f9a5ad`.

The identity was verified from `meta.json`, the actual Publisher mapping rule and an isolated package's `knowledge-assets.json`, not inferred from the filename's mathematical topic.

## 3. Original Manim / MP4 Source

- Scene: `03_conic/C002_ellipse_point_line_distance_extrema/manim/scene.py`, `C002DistanceLesson`.
- Mathematical model and regression tests: the same UID's `manim/math_model.py` and `manim/test_math_model.py`.
- Source video: `build/manim/C002/C002_ellipse_line_distance.mp4`, 545,671 bytes, SHA-256 `3cb4afeb251ab9d39fd889fa030f6e652491560cea810ea3c0856ecdcac7df5e`.
- The Task 13F isolated `build/manim/freeze-validation/C002/primary/primary.mp4` has the same source hash. This is the source used for the existing GIF; a new Scene render was unnecessary.

## 4. MP4 Production

The source was remuxed with FFmpeg using `-map 0:v:0 -c:v copy -an -movflags +faststart`. No video re-encoding, crop, scaling, music, or inserted frames were used. The source had `mdat` before `moov`; the final file has `moov` at byte offset 36 and `mdat` at 4667. The staged file was fully decoded with `ffmpeg -xerror -f null` before being copied to the UID's new `videos/` directory. The final file was not placed in `images/`, whose current worker rejects MP4.

Final source asset: `03_conic/C002_ellipse_point_line_distance_extrema/videos/ellipse_line_distance.mp4`, 545,671 bytes, SHA-256 `1a09bc46118dff27770035efa4327588a4dc252730430862918cd98753f28c74`. `ffprobe` confirms an MP4 container, one H.264 video stream, 576×1024, `yuv420p`, 24 FPS, 321 frames, 13.375 s, and no audio stream. The original GIF is unchanged.

## 5. Mathematical Consistency

The six formal TeX sections and `meta.json` were read. The Scene uses `E: x²/4+y²=1`, `l_C:3x+4y+C=0`, `C≥0`, `R=2√13`, so its displayed `C` correctly specializes the formal `|C|`. C002 model tests passed at separate, tangent and intersecting states, including an independent dense scan of distance extrema.

At 0%, 25%, 50%, 75% and near 100% (0.00, 3.25, 6.50, 9.75, 13.20 s), actual GIF and MP4 frames were decoded, compared and visually inspected. Their mean absolute RGB differences were 1.648, 1.840, 1.642, 1.643 and 1.647 on a 0–255 scale. Geometry, displayed formulas, points and line motion agree. At 3.25 s the samples differ by about one video frame in the moving line's position because GIF delays are quantized to 80–90 ms; the motion sequence is the same. GIF duration exceeds MP4 duration by 0.035 s for the same reason. Review image: `build/manim/C002/14C_MP4/comparison.png` (ignored build evidence).

The existing GIF checker passed full frame decode: 161 frames, 142 distinct, no black frame, valid loop. This is local mathematical and visual evidence; Android device playback and user visual approval remain PENDING.

## 6. Asset Mapping Design

`videos/share_assets.json` records the explicit one-to-one relation from `C002:image:ellipse_line_distance.gif` to local share identity `C002:share-video:ellipse_line_distance.mp4`, with the formal GIF URI, UID-local paths, MIME, size and SHA-256 hashes. `manim/verify_share_assets.py` checks IDs, safe paths, both physical files and hashes, duplicate relations, MP4 codec/pixel format, dimensions, frame rate, duration and faststart order. No runtime filename substitution is used.

**The share identity is currently local.** It is not a Publisher `KnowledgeAsset` ID or package URI, because the frozen Publisher has no video or companion relation contract. A proposed future URI is `resources/videos/C002/ellipse_line_distance.mp4`; it is not yet issued by Publisher.

## 7. Publisher Integration

Current `scripts/zhishu/asset_preparation.py` and `prepare_knowledge_images.mjs` accept direct `.png/.gif` inputs in `images/` and reject other extensions. `runtime_mapping.py` permits only `image/pdf` asset types and builds display image rows from the prepared image mirror. `content_package.py` copies only images/PDFs, uses schema version 1, checks exact resource coverage against `KnowledgeAsset` URIs, and requires exact image/PDF counts. There is no existing share relation or video-only resource mechanism.

Adding MP4 to `images/` fails image preparation. Adding a video row to `KnowledgeAsset` risks old consumers treating it as a display image and changes a frozen DTO. Adding the video file directly to `resources/` fails exact resource validation. An unreferenced sidecar cannot be relied on for Sync. Consequently, **formal Publisher integration is BLOCKED by the frozen Task 8A schema and unknown Zhishu consumer behavior**. No frozen Publisher code was changed and no package with a pretend MP4 reference was produced.

### Concrete extension requiring approval

Add a separate, optional `animation-shares.json` registry to a versioned Publisher package. Each row should carry `displayAssetId`, `shareAssetId`, `shareUri`, `mimeType`, `bytes`, and `sha256`, keyed by the exact existing GIF asset ID. Put MP4 bytes under `resources/videos/<UID>/`; add video file hashes, count and registry hash to the package manifest and package hash. Validate one-to-one links, GIF existence, MP4 existence/hash and no orphan resource. Keep `knowledge-assets.json` image rows and their order unchanged, and keep `search-documents.json` unchanged. Old GIFs have no required new field. A new package schema version or explicit compatible optional extension must be agreed with Zhishu Sync and the app's package reader before implementation. Check old-reader handling of unknown manifest fields/files and video resources; if it rejects them, use a negotiated schema-version transition rather than silently releasing an incompatible v1 package. Update Task 8A contract documentation and tests in that approved change.

## 8. Content Package Validation

An isolated `build-content` run used only `build/manim/C002/14C_MP4/publisher-runtime-assets` and `build/manim/C002/14C_MP4/content-package`. The existing Publisher completed with 0 errors and 0 warnings: 96 image assets, 571 PDFs, 667 total assets, 1030 knowledge nodes, 32 relations and 571 search documents. Package size: 126,552,702 bytes. Actual baseline `contentVersion`: `sha256:b289b18501c57d656580170b363d2cea38e790dcd9ac7a1ae5189ba0bce4ce1b`.

C002 retained `001.webp` through `004.webp` at image sort orders 10–40 and the original GIF at 50. Its package GIF hash matches the formal GIF. The package has **0 MP4 assets and 0 MP4 files**. This version is a validated legacy package, **not** a dual-asset package version. No default production package was overwritten.

## 9. File Size Comparison

| Asset | Bytes | Relative to GIF |
| --- | ---: | ---: |
| Original GIF | 1,721,935 | 100% |
| New MP4 | 545,671 | 31.69% |
| Both media files | 2,267,606 | 131.69% |

The one video adds 545,671 bytes of media, plus the small local registry. Scaling this to hundreds of animations would increase the offline package materially; the proposed Publisher should include only explicitly registered videos, never the `build/manim/` tree.

## 10. Changed Files

- `03_conic/C002_ellipse_point_line_distance_extrema/videos/ellipse_line_distance.mp4` — new MP4.
- `03_conic/C002_ellipse_point_line_distance_extrema/videos/share_assets.json` — local explicit association.
- `03_conic/C002_ellipse_point_line_distance_extrema/manim/verify_share_assets.py` — local validation.
- `03_conic/C002_ellipse_point_line_distance_extrema/manim/test_share_assets.py` — mapping failure tests.
- `scripts/manim/TASK_14C_MP4_DUAL_ASSET.md` — this report.

## 11. Automated Test Results

- `python -B -m unittest test_math_model test_share_assets` in C002 `manim/`: 7 tests PASS. The share tests reject duplicate mappings, a mismatched video hash and a missing video.
- `python -B manim/verify_share_assets.py` from C002: PASS, one association.
- `scripts/manim/verify_gif.py` on the formal GIF: PASS, full frame technical check.
- Full final video decode with `ffmpeg -xerror`: PASS (the identical staged bytes were decoded before copying).
- `python -B -m unittest tests.test_zhishu_asset_preparation tests.test_zhishu_runtime_mapping tests.test_zhishu_content_package tests.test_zhishu_publish tests.test_rendering_boundaries`: 50 tests PASS when run with usable temporary directory permissions. The first sandboxed run failed on temporary-directory `PermissionError`, before exercising the fixtures; it was rerun successfully.
- Isolated Publisher `build-content`: PASS for the existing image/PDF contract; dual-asset output BLOCKED as described above.
- `git diff --check`: PASS. `git diff --exit-code` on protected C002 TeX, `meta.json` and GIF: PASS.

## 12. Remaining Risks and Gate Status

| Gate | Status | Evidence / next step |
| --- | --- | --- |
| Mathematics | PASS | formal source review, 3 model tests, five visual comparisons |
| MP4 technology | PASS | ffprobe, full decode, faststart, no audio |
| Local GIF/MP4 association | PASS | hash-checked registry, 4 share tests |
| Publisher dual-asset integration | BLOCKED | frozen v1 image/PDF-only package contract |
| Dual-asset Content Package | BLOCKED | baseline package valid, but has no MP4 or association |
| User visual / Android device | PENDING | requires user and device review |
| Zhishu Sync and share feature | PENDING | separate Zhishu project work |

## 13. Zhishu Handoff Contract

| Field | Current value |
| --- | --- |
| Knowledge ID | `C002` |
| GIF Asset ID / URI | `C002:image:ellipse_line_distance.gif` / `resources/images/C002/ellipse_line_distance.gif` |
| MP4 local share ID | `C002:share-video:ellipse_line_distance.mp4` (not yet a Publisher ID) |
| MP4 package URI / path | **PENDING**; proposed `resources/videos/C002/ellipse_line_distance.mp4` |
| Association source | C002 `videos/share_assets.json`, keyed by exact GIF Asset ID |
| Current Content Package Version | `sha256:b289b18501c57d656580170b363d2cea38e790dcd9ac7a1ae5189ba0bce4ce1b` (legacy, excludes MP4) |
| MP4 MIME | `video/mp4` |
| MP4 bytes / SHA-256 | `545671` / `1a09bc46118dff27770035efa4327588a4dc252730430862918cd98753f28c74` |
| Sync requirements | after contract approval, copy registered video bytes and registry; verify package hash and offline local URI; expose exact GIF-ID lookup to the App |
| App adaptation | after Sync supports the registry, long press on the GIF's stable asset ID selects the paired local MP4 and invokes sharing with MIME `video/mp4`; no runtime conversion or filename guessing |

Publisher schema extension, Sync integration, and App work require a separate approved change. This task stops at the verified C002 local video and association.
