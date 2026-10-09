# Task 14C.2 Result — T021

Date: 2026-10-09. Scope: `08_trigonometry/T021_sine_transform_shift_order/` only. **Task 14C.2 — LOCAL PRODUCTION PASS. USER VISUAL PENDING / ANDROID DEVICE PENDING.** No formal Publisher, Sync, APK build or Git commit was run.

## 1. Pre-flight

The `main` worktree was clean at task start. T021's six numbered TeX sections, `meta.json`, `source.tex`, formal PDF, the Task 14C and 14C.1 reports, `scripts/manim/README.md`, `scripts/manim/TASK_13F_FREEZE.md`, and the architecture contract were inspected. The T021 image directory contained no target GIF; the shared Task 13F tools and other frozen GIFs were present. Before editing, SHA-256 hashes of 84 existing protected files were recorded in ignored `build/manim/T021/14C_2/freeze_baseline.json`.

## 2. Mathematical Source Freeze Verification

Task 14C.1's corrected source is consistent with `A≠0`, `ω>0`, `φ∈R`, signed vertical coefficient `A`, amplitude `|A|`, period `2π/ω`, signed left shift `φ` or `φ/ω`, and horizontal scale `1/ω`. The two shift distances coincide when `φ=0` or `ω=1`; otherwise they generally differ. For `A<0`, vertical scaling by `|A|` is followed by reflection about the x-axis. The old `A=-2` sign error, ordinary-commutativity claim and unconditional compression claim are absent from the frozen source and from this animation. Its formal PDF SHA-256 stayed `6ea968d8caa24fdc202ec18c3bb99418bdfafcd588c601432a5d831c6b861a6d`.

The formal TeX, metadata, supporting `source.tex` and PDF were read only. The final baseline comparison below confirms byte identity.

The existing Task 14C.1 source-math regression suite was rerun with `python -B -m unittest discover -s 08_trigonometry/T021_sine_transform_shift_order/tests -p test_*.py -v`: **5/5 passed**.

## 3. Teaching Goal

The learner follows the same source peak through two real geometric paths in one fixed coordinate system. Moving the original point left by `φ` and then scaling its x coordinate also scales that earlier displacement. Scaling first therefore needs a later shift of `φ/ω` to arrive at the same place. The end card explicitly says the adjusted compositions are equivalent and cannot be exchanged without changing the shift.

## 4. Demonstration Parameters

The scene uses `ω=2`, `φ=π/2`, `A=-2`, source point `t=π/2`. Path one visibly shifts by `π/2`; path two shifts by `π/4`; horizontal coordinates scale by `1/2`. The common horizontal peak is `(0,1)`, and the final signed peak is `(0,-2)`. A single 576×1024 axis keeps scale and alignment comparable on a phone. No unrelated parameter sweep is shown; generality is tested independently.

## 5. Independent Mathematical Model

`math_model.py` stores every geometric state as `CurveState(scale=s, shift=h, vertical=c)`, mapping `(t,sin t)` to `(st+h,c sin t)`. The plotted curve is derived from the same state by `y(x)=c sin((x-h)/s)`. Positive `s` is enforced, so the dynamic point remains on its actual dynamic curve at every sampled state. `Parameters` enforces `A≠0` and `ω>0`, and computes amplitude, period and both shift distances. The reflection interpolation through `c=0` is identified as a visual geometric process; it is not asserted as an admissible formal T021 parameter `A=0`.

## 6. Point Mapping Proof

For every source point `(t,sin t)`, path one has `P₁=(t−φ,sin t)` then `P₂=((t−φ)/ω,sin t)`. Path two has `Q₁=(t/ω,sin t)` then `Q₂=(t/ω−φ/ω,sin t)`. The horizontal results coincide exactly. Both final vertical operations give `((t−φ)/ω,A sin t)`. If its horizontal coordinate is `x`, then `t=ωx+φ`, yielding `y=A sin(ωx+φ)`. This proves whole-curve equality, not just the selected peak. The scene's orange endpoint and purple endpoint use these same state functions, with a wider orange trace under the narrower purple trace and an orange ring under the gold point at `(0,1)`.

## 7. Mathematical Regression Tests

`python -B -m unittest discover -s 08_trigonometry/T021_sine_transform_shift_order/manim -p test_*.py -v` passed **6/6**. The final-coordinate and target-function matrix covers 126 combinations: `A∈{-2,2}`, `ω∈{1/2,1,2}`, `φ∈{-π/4,0,π/2}` and seven source parameters. Additional tests check all intermediate point/curve identities at five interpolation fractions, the demonstration stage coordinates, required positive horizontal scale, equal-shift exceptions, adjusted composition versus unadjusted noncommutation, and the historic counterexample `A=-2, ω=2, φ=π/4, x=π/8`, where the correct value is `-2` rather than `+2`.

## 8. Teaching Storyboard

`README.md` records the approximately timed storyboard. The sequence is: common blue baseline; orange left shift and x compression; explicit reset to the same baseline; purple x compression and adjusted left shift; exact curve and peak overlap; common `|A|=2` vertical scaling; geometric x-axis reflection; final equation and return to the baseline for looping. Orange and purple intermediate curves differ, while their endpoint coordinates agree. Stage labels always name the current path. The final relation `S₂∘L_{π/2}=L_{π/4}∘S₂` appears alongside “调整平移量后等价；不能直接交换”.

## 9. Manim Implementation

`scene.py` is UID-local. It uses the state functions from `math_model.py` for both animated curves and the tracked source point; neither final point is hand moved into place. Blue/orange/purple/gold/green have fixed meanings. The production review corrected an initially invisible end formula, aligned a newly reset point label, and changed label transitions to sequential fade-out/fade-in so old and new formulas do not overprint. The frozen shared scripts were used unmodified.

## 10. MP4 / GIF Export

Executed from repository root:

```powershell
.\scripts\manim\render.ps1 -Uid T021 -Scene T021TransformOrderLesson -SceneFile scene.py -Name transform_order -BuildRoot build/manim/T021/14C_2
.\scripts\manim\export_gif.ps1 -Uid T021 -Scene T021TransformOrderLesson -SceneFile scene.py -Name transform_order -BuildRoot build/manim/T021/14C_2
.\scripts\manim\export_gif.ps1 -Uid T021 -Scene T021TransformOrderLesson -SceneFile scene.py -Name transform_order -BuildRoot build/manim/T021/14C_2 -Publish -AssetName t021_transform_order.gif
```

The rendered MP4 is `build/manim/T021/14C_2/T021/transform_order/transform_order.mp4`: 576×1024, 24 fps, 437 video frames, approximately 18.21 s. The final formal GIF is `images/t021_transform_order.gif`: 3,745,118 bytes (3.57 MiB), SHA-256 `e0d9dda85ae2f7e9f22890aa6d56e64822eae676c2b83b52099ee591487c4c21`. The first task-produced GIF was moved into ignored build storage after a review found overprinting during label transitions. The corrected GIF was generated in isolation, verified, and then published to the vacant formal name without `-Overwrite`; no pre-existing formal GIF was replaced.

## 11. Critical Frame Mathematical Audit

The contact sheet `build/manim/T021/14C_2/T021_14C_2_contact_sheet.png` and twelve full-resolution PNGs under `final_keyframes/` were decoded **from the final formal GIF**, never redrawn. The ignored `T021_14C_2_visual_report.json` records actual GIF frame indices and predicted point positions. Pixel checks found the gold point near the predicted coordinate in all 12 samples. Visual inspection checked the curve shapes and labels against the state equations:

| Final GIF time / frame | Stage | Analytic curve and tracked point |
| --- | --- | --- |
| 0.00 s / #0 | Baseline | `sin x`; `P=(π/2,1)`. |
| 2.75 s / #33 | Path one shift complete | `sin(x+π/2)`; `P=(0,1)`; signed left shift `π/2`. |
| 4.70 s / #56 | Path one scale complete | `sin(2x+π/2)`; `P=(0,1)`; x coordinates halved. |
| 5.50 s / #66 | Path two reset | Original purple `sin x` point `P=(π/2,1)` while orange endpoint remains for comparison. |
| 7.45 s / #89 | Path two scale complete | `sin(2x)`; `P=(π/4,1)`; differs from orange path-one intermediate. |
| 9.75 s / #117 | Path two shift complete | `sin(2x+π/2)`; `P=(0,1)`; signed left shift `π/4`. |
| 10.75, 11.40 s / #129, #136 | Curve and point overlap | Orange and purple use identical `s=1/2,h=-π/4,c=1`; both original-peak endpoints are `(0,1)`. |
| 13.00 s / #156 | Positive vertical scaling | `2 sin(2x+π/2)`; `P=(0,2)`; amplitude 2. |
| 15.50 s / #186 | Reflection complete | `-2 sin(2x+π/2)`; `P=(0,-2)`. |
| 16.40 s / #196 | Conclusion | Target equation and adjusted-shift reminder remain with final curve. |
| 18.00 s / #216 | Loop end | Returned to baseline `sin x`, `P=(π/2,1)`. |

## 12. Full-frame Visual Validation

All 218 GIF frames decoded. Contact-sheet review plus full-size inspection of the representative and transition frames found consistent fixed axes, no point/curve disagreement, no curve discontinuity outside the intentional stage reset, no clipped title or formula, and no residual transition overprint after the final correction. The final still returns to the opening blue baseline. The brief `c=0` frame in the reflection is labelled as a geometric flip process. This is local visual review; user desktop and Android device acceptance remain separate.

## 13. GIF Technical Validation

The frozen `verify_gif.py` was also run directly against the formal GIF with `--width 576 --height 1024`: **valid**, 218 frames, 196 distinct frames, 18.16 s, frame delays 80–90 ms, infinite loop, zero black frames. The final-GIF audit independently decoded all 218 frames and detected zero black frames. The manifest records the exact file byte count above.

## 14. Publisher Isolated Preview

The actual `scripts/zhishu/prepare_knowledge_images.mjs` worker was run with a single T021 job into ignored `build/manim/T021/14C_2/publisher_preview/`. The source directory contains only this GIF among production images, so no PNG/WebP name collision exists. The resulting manifest contains exactly one asset with `knowledgeId=T021`, source `08_trigonometry/T021_sine_transform_shift_order/images/t021_transform_order.gif`, output `images/T021/t021_transform_order.gif`, 576×1024, 218 frames, 18,160 ms and loop `0` (infinite). Source, isolated output and staging GIF SHA-256 are all `e0d9dda85ae2f7e9f22890aa6d56e64822eae676c2b83b52099ee591487c4c21`, proving multiframe GIF bytes were preserved rather than converted to a still image. No formal Publisher package or Sync was run.

## 15. Frozen Asset Integrity

After production, all **84** recorded pre-existing protected files matched their initial SHA-256; **0 changed, 0 missing**. This baseline included T021 formal math and PDF, C001/C002/F031 frozen assets, and shared Manim infrastructure. `git diff --check` passed. The only worktree additions are the six files listed below, all within T021.

## 16. Files Changed

Added: `manim/math_model.py`, `manim/test_math_model.py`, `manim/scene.py`, `manim/README.md`, `manim/TASK_14C_2_RESULT.md`, and `images/t021_transform_order.gif`. All MP4, contact-sheet, visual-report, Publisher-preview, baseline, and intermediate files remain under ignored `build/manim/T021/14C_2/`. No existing tracked file changed.

## 17. Known Issues

User desktop visual acceptance and Android device playback are pending. Formal Publisher/Sync release is outside this task and was not attempted. The contact sheet is a sampling of the final GIF; the direct GIF validator and separate audit decoded every frame. A user viewing the GIF on a phone may still request timing or typography refinements before final freeze.

## 18. Acceptance Gates

| Gate | Status | Evidence |
| --- | --- | --- |
| A — Source freeze | PASS | Corrected Task 14C.1 source re-read; 5 source-math tests; 84-file hash comparison. |
| B — Mathematical model | PASS | Shared point/curve state and coordinate proof. |
| C — Independent tests | PASS | 6 tests, 126 parameter/point final cases plus interpolation and regression. |
| D — Teaching storyboard | PASS | UID-local README and reviewed sequence. |
| E — Manim implementation | PASS | UID-local scene, frozen tools unmodified. |
| F — Render / GIF | PASS | Real MP4 and formal validated GIF. |
| G — Mathematical visual accuracy | PASS | 12 final-GIF keyframes, point-position checks, full-frame decode and visual review. |
| H — Resource compatibility | PASS | T021-only worker preview; identical GIF source/output hash. |
| I — Freeze integrity | PASS | 84 unchanged protected files; only six T021 additions. |
| J — User acceptance | PENDING | Desktop visual review and Android device check not performed by user. |

## 19. Final Status

**Task 14C.2 — LOCAL PRODUCTION PASS. USER VISUAL PENDING / ANDROID DEVICE PENDING.** The GIF is ready for independent user review. **T021 FINAL FREEZE** is reserved until those two acceptance steps are completed; formal Publisher/Sync remains a separate release action.
