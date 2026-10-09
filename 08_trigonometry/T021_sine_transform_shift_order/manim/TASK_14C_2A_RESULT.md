# Task 14C.2A Result — T021

Date: 2026-10-09. Scope: one T021 animation label, its regenerated MP4/GIF, local evidence, and this report. **Task 14C.2A — LOCAL CORRECTION PASS. USER VISUAL PENDING / ANDROID DEVICE PENDING.** No formal Publisher, Sync, APK build, or Git commit was run.

## 1. Pre-flight

The worktree was clean. The T021 UID directory, Task 14C.2 result, frozen Manim README and Task 13F report, architecture contract, Scene, old formal GIF, tests, and existing build evidence were inspected. The old GIF's actual frame 42 displays the incorrect label. Its SHA-256 was `e0d9dda85ae2f7e9f22890aa6d56e64822eae676c2b83b52099ee591487c4c21`; an identical backup is retained at `build/manim/T021/14C_2A/t021_transform_order_before.gif`. Before editing, 88 protected files were hashed in `build/manim/T021/14C_2A/protected_baseline.json`. All 84 files in the previous Task 14C.2 freeze baseline also still matched before this task.

## 2. Original Label Error

Old Scene text: **“P 在原点不动；整条曲线横坐标 ×1/2”**. In the actual old GIF frame 42 (`build/manim/T021/14C_2A/old_frame_042.png`), P lies on the y-axis at `(0,1)`, above the coordinate origin `(0,0)`. Path one has already shifted the source peak from `(π/2,1)` to `(0,1)`. Horizontal scaling maps `(x,y)` to `(x/2,y)`, so P remains at `(0,1)` during this phase.

## 3. Exact Source Correction

Only `manim/scene.py:142` changed, from **“P 在原点不动；整条曲线横坐标 ×1/2”** to **“P 在 y 轴上不动；整条曲线横坐标 ×1/2”**. The Git diff is one string replacement, one insertion and one deletion. No formula, model, path, parameter, color, timing, layout, or other label was changed. `git diff --check` passed.

## 4. Mathematical Regression

- Formal T021 source tests: `python -B -m unittest discover -s 08_trigonometry/T021_sine_transform_shift_order/tests -p test_*.py -v` — **5/5 PASS**.
- UID-local Manim model tests: `python -B -m unittest discover -s 08_trigonometry/T021_sine_transform_shift_order/manim -p test_*.py -v` — **6/6 PASS**.

The existing tests cover both transformation paths, 126 final parameter/point cases, interpolation consistency, the adjusted composition, and negative `A`. For the displayed example, path one is `(π/2,1) → (0,1) → (0,1)`; path two is `(π/2,1) → (π/4,1) → (0,1)`; the common horizontal point is `(0,1)` and the `A=-2` final point is `(0,-2)`.

## 5. MP4 / GIF Regeneration

The unmodified Task 13F scripts were run with `-Uid T021 -Scene T021TransformOrderLesson -SceneFile scene.py -Name transform_order -BuildRoot build/manim/T021/14C_2A`. `render.ps1` produced `build/manim/T021/14C_2A/T021/transform_order/transform_order.mp4` (576×1024, 437 frames, 18.207357 s). `export_gif.ps1` produced the staged `build/manim/T021/14C_2A/T021/transform_order/transform_order.gif`. Only after mathematical, technical, frame, comparison, backup, and freeze checks passed, the same exporter was called with `-Publish -AssetName t021_transform_order.gif -Overwrite` for the exact T021 formal asset. The formal GIF is `images/t021_transform_order.gif`; its SHA-256 equals the staged GIF: `c76125b7c96c2ea25eaab676f5c8619f397f2956c4d91f4a653f5c88eb7c1812`.

## 6. Corrected Frame Evidence

The actual corrected GIF frame 56 is `build/manim/T021/14C_2A/keyframes/02_path1_scale_frame_056.png`. It shows the complete new sentence without clipping or curve occlusion and P on the y-axis at `(0,1)`. Frames 39–45 are in `keyframes/adjacent_*.png`. Label entry frames 36–40 and exit/reset frames 56–66 are in `keyframes/transition_*.png`; `T021_14C_2A_transitions.png` shows representative transition frames. The label fades in and out without overprinting or jumping.

## 7. Visual Regression

`build/manim/T021/14C_2A/T021_14C_2A_contact_sheet.png` contains 12 real frames decoded from the new GIF: baseline, both path stages and reset, overlap, vertical scaling, reflection, conclusion, and loop end. Full-resolution frames are in `keyframes/`. The one-off `audit_14c2a.py` decoded all 218 frames and checked the gold point near analytically expected pixel locations in all 12 samples; all checks found at least 100 gold pixels nearby. Direct visual review found consistent curves, point motion, labels, composition, and loop endpoints.

The old/new GIFs have identical frame count and **identical duration for every frame**. The corrected text band changes as expected. Outside that band, pixels differing by over 20 in any RGB channel occupy 52,598 of 122,303,232 compared pixel positions (**0.043%**), consistent with palette re-encoding; no geometric, stage-order, or timing difference was seen. The per-frame comparison is in `build/manim/T021/14C_2A/visual_report.json`. File-size similarity was not used as evidence.

## 8. GIF Technical Validation

The frozen `verify_gif.py` passed on both staged and formal GIFs with `--width 576 --height 1024`: **valid**, 218 frames, 196 distinct frames, 18.16 s, frame delays 80–90 ms, infinite loop, zero black frames, 3,754,599 bytes. The independent audit decoded every frame and found zero black or white frames. Old GIF specifications were 576×1024, 218 frames, 18.16 s, infinite loop; all were retained.

## 9. Publisher Isolated Preview

The existing `scripts/zhishu/prepare_knowledge_images.mjs` worker ran with the one-T021 jobs file into ignored `build/manim/T021/14C_2A/publisher_preview/`. Its manifest lists exactly one asset, `knowledgeId=T021`, output `images/T021/t021_transform_order.gif`, 576×1024, 218 frames, 18,160 ms, loop `0` (infinite). Formal source and isolated output SHA-256 are both `c76125b7c96c2ea25eaab676f5c8619f397f2956c4d91f4a653f5c88eb7c1812`; no filename collision occurred. No formal Publisher or Sync was run.

## 10. Frozen Asset Integrity

All **88** protected files in the new baseline matched after publication: **0 changed, 0 missing**. This includes T021's six formal TeX sections, `meta.json`, `source.tex`, formal PDF, math model and tests, the Task 13F shared tools, and the previous C001/C002/F031 frozen assets. The T021 Scene and formal GIF are intentionally excluded from that protection comparison and reported separately. Their changes are limited to the authorized label and GIF replacement. The old GIF backup retains the original hash above.

## 11. Files Changed

Tracked changes: `manim/scene.py` (one string), `images/t021_transform_order.gif` (3,745,118 → 3,754,599 bytes), and this report. New MP4, staged GIF, backup, frame PNGs, contact sheets, audit scripts and JSON, Publisher preview, and hash baseline are under ignored `build/manim/T021/14C_2A/`. No other UID or shared tool changed.

## 12. Known Issues

User visual acceptance and Android device playback remain pending. This local review does not declare T021 animation FINAL FREEZE. Formal Publisher/Sync release is a separate action.

## 13. Acceptance Gates

| Gate | Status | Evidence |
| --- | --- | --- |
| A — Pre-flight | PASS | Clean initial worktree; old GIF/frame located; backup and baseline recorded. |
| B — Mathematical label | PASS | Corrected y-axis wording; P remains `(0,1)`. |
| C — Scope | PASS | One Scene string changed; model, paths, timing and other labels unchanged. |
| D — Mathematical regression | PASS | Existing 5 + 6 tests all passed. |
| E — Rendering | PASS | MP4/GIF generated; isolated validation before explicit formal overwrite. |
| F — Visual regression | PASS | Actual corrected, adjacent, transition and 12 key frames reviewed; all frames decoded. |
| G — Freeze protection | PASS | 88 protected hashes unchanged; other UIDs and shared tools untouched. |
| H — Resource compatibility | PASS | T021-only isolated preview; formal and preview GIF hashes identical. |
| I — User acceptance | PENDING | User visual review and Android real-device playback. |

## 14. Final Status

**Task 14C.2A — LOCAL CORRECTION PASS. USER VISUAL PENDING / ANDROID DEVICE PENDING.** The corrected formal GIF is ready for user visual review and Android device acceptance. Only after those checks may T021 animation FINAL FREEZE be declared.
