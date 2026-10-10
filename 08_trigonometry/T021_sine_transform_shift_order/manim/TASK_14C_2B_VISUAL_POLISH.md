# Task 14C.2B Result — T021

Date: 2026-10-09. Scope: T021 Manim presentation, its single formal GIF, and local evidence. **Task 14C.2B — VISUAL POLISH LOCAL PASS. USER VISUAL PENDING / ANDROID DEVICE PENDING.** No formal Publisher, Sync, APK build, or Git commit was run.

## 1. Pre-flight

The worktree was clean. The exact T021 directory, existing Scene, mathematical model and tests, Task 14C/14C.1/14C.2/14C.2A reports, Task 13F README/freeze, rendering architecture contract, current GIF, and shared resource worker were inspected. The old formal GIF was 576×1024, 218 frames, 18.16 s, infinite loop, 3,754,599 bytes, SHA-256 `c76125b7c96c2ea25eaab676f5c8619f397f2956c4d91f4a653f5c88eb7c1812`. Its byte-identical backup is `build/manim/T021/14C_2B/baseline/t021_transform_order.gif`; its actual 12-frame sheet is `baseline/contact_sheet.png`. The prior 88-file protected hash baseline was copied to this task's `baseline/` and all 88 files matched the current tree before editing.

## 2. Existing GIF Visual Audit

The old GIF was decoded and reviewed through its actual contact sheet and full-resolution frames. Opening frame 0 has a large title, parameter row, bold phase heading, framed chart, legend, note, formula, and two full path descriptions at once. Path-one shift/scale frames 33/56 and path-two reset/scale/shift frames 66/89/117 retain both path descriptions, including inactive stages. The chart has a strong border and occupies less vertical space than the surrounding text. The current operation is embedded in the phase heading or a sentence while the repeated path list competes for attention. Overlap frames 129/136 add a second composition equation and caution under the existing formula and path list. Amplitude/reflection frames 156/186 and conclusion frame 196 keep those lower rows despite moving to a different teaching stage. The old first/last compositions (frames 0/216) were already broadly consistent. The corrected wording **“P 在 y 轴上不动”** was present at frame 56 and was preserved.

## 3. Apple-Inspired Design Principles

- Clarity: give the current transformation a single large operation line and keep the active formula adjacent to it.
- Deference: remove the chart card, constant legend, parameter row, and persistent path list so the curve and tracked P dominate.
- Depth: use restrained fades for stage text and reveal both path summaries only when their results meet. No decorative effect was added.

This is a design-principle reference, not a copy of an Apple screen or font.

## 4. Information Hierarchy Changes

The header now uses the short title **“顺序不同，结果相同”** and one contextual stage line. The graph is central. Below it, the operation, exact formula, and one concise explanation form three reading levels. The two complete path lines are introduced only during the shared-endpoint comparison, then removed before vertical scaling. The conclusion retains the target formula and the adjusted-shift lesson without replaying the whole storyboard.

## 5. Typography Changes

The verified Microsoft YaHei remains the Chinese font. The title is semibold at 36, contextual stage 28, current operation semibold at 30, supporting text 25, and formula 42–43 Manim font units. Real 576×1024 frames were reviewed, including long horizontal transformation formulas. No new font dependency was introduced.

## 6. Color and Graph Changes

The same semantic palette remains: blue baseline, orange path one, purple path two, gold P, green common/vertical result, neutral axes. Orange, purple, and gold were slightly deepened for readability. The axes use one fixed map for every path; x length changed from 7.46 to 7.78 scene units and y length from 5.23 to 6.25. Their mathematical x/y ranges stayed `[-3.3,3.3]` and `[-2.32,2.32]`. All curves and points still use the same `axes.c2p` map. The chart rectangle and constant legend were removed, while x/y axes and key ticks remained. No path-specific scaling was introduced.

## 7. Motion and Timing Changes

The model-driven curve and point progressions retain their original 1.55 s horizontal, 1.2 s vertical-scale, and 1.4 s reflection motions with linear progress. The two path summaries fade in during overlap and fade out before the vertical stage, adding 0.25 s to the GIF (18.16 → 18.41 s). The overlap still pauses 1.15 s; the conclusion still pauses 1.20 s. The opening and loop-end layouts match closely; first/last frames differ by a mean maximum-channel value of 0.52, with 1,930 of 589,824 pixels differing by over 20 in any channel.

## 8. Mathematical Preservation

`math_model.py`, formal TeX, `meta.json`, `source.tex`, PDF, and both mathematical test suites are unchanged. The Scene still imports the same `DEMO` (`A=-2`, `ω=2`, `φ=π/2`) and model functions. The paths remain `P₀=(π/2,1) → P₁=(0,1) → P₂=(0,1)` and `P₀ → Q₁=(π/4,1) → Q₂=(0,1)`. The curves and points coincide exactly at the horizontal endpoint. Vertical scaling and reflection remain `(0,1) → (0,2) → (0,-2)`. Intermediate reflection through zero is only the continuous geometric transition; it does not redefine the formal `A≠0` domain. The displayed composition is `S₂∘L_{π/2}=L_{π/4}∘S₂`; it does not claim unrestricted commutativity.

## 9. Manim Implementation

Only T021 `manim/scene.py` changed. It uses the existing model and Manim primitives, with one shared Axes instance, the same model-driven `always_redraw` curves and gold point, and UID-local text/layout changes. No shared tool, framework, or other UID Scene was edited.

## 10. Mathematical Regression

- Formal T021 source suite: `python -B -m unittest discover -s 08_trigonometry/T021_sine_transform_shift_order/tests -p test_*.py -v` — **5/5 PASS**.
- T021 Manim model suite: `python -B -m unittest discover -s 08_trigonometry/T021_sine_transform_shift_order/manim -p test_*.py -v` — **6/6 PASS**.
- Scene `py_compile` and `git diff --check` — **PASS**.

These include path endpoints, interpolation point/curve consistency, adjusted composition, negative `A`, and the formal parameter matrix. Twelve decoded candidate keyframes also found 95–195 gold pixels near the analytically mapped P coordinates. Those checks cover `(π/2,1)`, `(π/4,1)`, `(0,1)`, `(0,2)`, and `(0,-2)` at their corresponding stages.

## 11. MP4 / GIF Export

The unchanged Task 13F `render.ps1` and `export_gif.ps1` produced `build/manim/T021/14C_2B/candidate/T021/transform_order/transform_order.mp4` and `.gif`. `ffprobe` reported MP4 576×1024, 24 FPS, 443 frames, 18.457357 s, 918,360 bytes. The staged GIF is 576×1024, 221 frames, 18.41 s, infinite loop, 3,200,167 bytes, SHA-256 `00cd6977dcebb7fe24106135d262bfa8e3389c1a5e202c663ec015367143b48a`. After staging checks and backup verification, the frozen exporter with explicit `-Publish -AssetName t021_transform_order.gif -Overwrite` replaced only the named T021 formal GIF. Formal and staged hashes match.

## 12. Before / After Comparison

`build/manim/T021/14C_2B/comparison/T021_14C_2B_before_after.png` compares opening, both paths, overlap, reflection, and conclusion at matched times. The new graph has more vertical room and no heavy border; inactive path text is absent during single-path teaching. The operation is visually more prominent, while the exact formula remains readable. The two path colors appear together only when both are relevant. The file size fell by 554,432 bytes (14.8%); that is a technical observation, not proof of visual quality.

## 13. Actual Frame Validation

The candidate sheet `build/manim/T021/14C_2B/T021_14C_2B_contact_sheet.png` covers opening; path-one shift/scale; path-two reset/scale/shift; curve and point overlap; amplitude 2; reflection; conclusion; and loop end. Full-resolution PNGs are in `keyframes/`. The 12 selected candidate frame indices are 0, 33, 56, 66, 89, 117, 130, 138, 159, 188, 199, and 219. Full-resolution review of scale, overlap, reflection, and conclusion showed readable text, visible P, unclipped curves, and separated text lines. At the shared endpoint, orange and purple curves/points occupy the same mathematical coordinates; the orange ring preserves both path cues without moving either point.

## 14. GIF Technical Validation

The frozen `verify_gif.py` passed staged and formal GIFs: 221 frames, 200 distinct frames, 18.41 s, delays 80–90 ms, infinite loop, zero black frames. The one-off `build/manim/T021/14C_2B/audit_14c2b.py` independently decoded all 221 candidate frames and found zero black or white frames. Its JSON report is `T021_14C_2B_visual_report.json`. The contact sheet and full-size samples were inspected for clipping, text overlap, and abrupt stage changes; automated full-frame decoding does not replace user phone review.

## 15. Publisher Isolated Preview

The actual `scripts/zhishu/prepare_knowledge_images.mjs` worker was run first on a single-file candidate input and then on the formal T021 `images/` directory, each into ignored isolated build output. The formal preview manifest lists exactly one asset, `knowledgeId=T021`, `images/T021/t021_transform_order.gif`, 576×1024, 221 frames, 18,410 ms, loop `0` (infinite). Formal source and preview output hashes both equal `00cd6977dcebb7fe24106135d262bfa8e3389c1a5e202c663ec015367143b48a`. No formal package, Publisher command, or Sync ran.

## 16. Frozen Asset Integrity

All 88 files in `baseline/protected_baseline.json` matched again after formal GIF replacement: **0 changed, 0 missing**. The set includes frozen T021 TeX/PDF/metadata/model/tests, shared Manim tools, and named C001/C002/F031 frozen assets. The only worktree changes are the authorized T021 Scene, the single formal GIF, and this new report. The old GIF backup remains byte-identical to the old formal hash.

## 17. Files Changed

Modified tracked files: `manim/scene.py` and `images/t021_transform_order.gif`. New untracked file: this report. MP4, candidate/backup GIFs, keyframes, sheets, JSON, audit script, and isolated Publisher previews remain under ignored `build/manim/T021/14C_2B/`.

## 18. Known Issues

User desktop comparison and Android device playback are pending. Local visual inspection supports this design, but it is not user acceptance. Formal Publisher/Sync release remains separate. No other known local blocking issue remains.

## 19. Acceptance Gates

| Gate | Status | Evidence |
| --- | --- | --- |
| A Pre-flight | PASS | Clean tree; old GIF backup/hash/technical data and protected baseline. |
| B Visual audit | PASS | Actual old frames and concrete clutter/priority findings above. |
| C Design | PASS | Revised hierarchy, graph area, progressive route disclosure. |
| D Mathematics | PASS | Frozen model/source unchanged; same path and reflection states. |
| E Implementation | PASS | T021-only Scene presentation edit; shared tools unchanged. |
| F Render/GIF | PASS | Actual MP4 and validated staged/formal GIF. |
| G Visual regression | PASS | 12-frame sheet, full-size frame review, before/after image, all-frame decode. |
| H Mathematical regression | PASS | 5+6 tests and keyframe point mapping. |
| I Resource compatibility | PASS | Candidate and formal isolated worker previews; one T021 GIF and equal hashes. |
| J Frozen assets | PASS | 88 protected hashes unchanged. |
| K User acceptance | PENDING | User desktop visual comparison and Android real-device check. |

Visual gates V1–V8: **PASS in local review**, supported respectively by current-operation priority, larger fixed-coordinate graph, three text levels, stable semantic colors, reduced containers/text, unchanged model-driven motion with restrained fades, staged path comparison, and real-resolution keyframe inspection. User experience on a phone remains part of Gate K.

## 20. Final Status

**Task 14C.2B — VISUAL POLISH LOCAL PASS. USER VISUAL PENDING / ANDROID DEVICE PENDING.** The polished T021 GIF is ready for user comparison. Do not declare **T021 Mathematical Animation FINAL FREEZE** before those two acceptance checks.
