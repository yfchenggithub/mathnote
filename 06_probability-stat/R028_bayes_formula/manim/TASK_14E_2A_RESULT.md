# Task 14E.2A Result — R028 Positive Population Polish

Date: 2026-10-10. **R028 MATHEMATICAL ANIMATION POLISH LOCAL PASS.** This report covers a local change to the existing R028 Scene and the one authorized formal GIF overwrite. The new GIF has not received user visual or Android device acceptance.

## 1. Pre-flight and baseline

- Initial `git status --short` was clean on `main`. `rg --files -g AGENTS.md` found only the root rule file, with no nested R028 instruction or rule conflict. Read actual `AGENTS.md`, `docs/architecture/math-rendering-boundaries.md`, `scripts/manim/VISUAL_GUIDELINES.md`, `scripts/manim/README.md`, `scripts/manim/TASK_13F_FREEZE.md`, Task 14E.1 source freeze, Task 14E.2 result, and R028 model, tests, storyboard, Scene and formal example 1. The TeX remained read-only knowledge source.
- Old formal GIF `images/r028_bayes_formula.gif`: SHA-256 `B0E990B8FBFAF7F032381E2C2AC70EB7D9C1E6492173168C8215C29FECD0D914`; 576×1024, 241 frames, 20.08 s, 2,453,728 bytes, 205 distinct frames, infinite loop. `verify_gif.py` passed. Before editing, an exact recoverable copy was saved at `build/manim/R028/14E_2A/baseline/r028_bayes_formula.before.gif`; its hash matches the old formal file. Old decoded keyframes and contact sheet are in `baseline/keyframes/`.
- Starting Scene SHA-256 `8237CE8A6971F83E8586DE44B61485C858B19C03555552C5DAA55FD31876C52B`. Unmodified mathematical model SHA-256 `CD265EC40283A520A13FFE2E156D561FEE19418D6C1277C9828BCA44FC30E358`; original 12-test file SHA-256 `0854A4A7932472D10B863BAE0E65ADFC73F318997E2BC5A1512F426CA4B36C31`. Original M1–M12: **12/12 PASS** before editing.
- All 12 frozen R028 TeX/meta/source/PDF/audit/freeze files matched the Task 14E.1 hashes before editing. The formal medical example remains `N=100,000`, 100 diseased, 99,900 healthy, 99 true positives, 999 false positives and 1,098 positives.

## 2. Old issue diagnosis

The old transition used `FadeOut` on source groups while moving the two count labels, followed by `FadeIn` of a new pool title and growth of the positive bar. The count labels moved only weakly relative to the new pool, and `99+999=1098` never appeared. In the old decoded GIF the 9–13 s transition therefore read mostly as old state disappearing and new state appearing.

The old source bars were equal width with a small note that their group sizes differed. The denominator of each conditional rate was not directly shown beside its 99% or 1% label.

The old *data* geometry was already model-driven and correct: before highlighting, raster scanline `y=520` showed 40 orange and 408 purple pixels (40/448 = 8.9286%, within one-pixel quantization of the exact 9.0164%). The previous `SurroundingRectangle` crossed the orange/right boundary when highlighted: the same scanline became 44 orange and 406 purple visible pixels (44/450 = **9.7778%**) in both the numerator and final frames. This explains the reported approximate 9.78% observation. It was a visible border effect, not a wrong Bayesian model or bar width. No arbitrary width correction was made.

## 3. Targeted transition and denominator changes

`scene.py` retains the prior layout, colors, source bars, final proportional bar, formula, result and loop. The local changes are:

1. Source headings now read “患病组 · 共 100 人” and “未患病组 · 共 99,900 人”; source rates read `99 / 100 = 99%` and `999 / 99,900 = 1%`. A short note says both bars represent 100% **within their respective group**. These labels, the opening prior TeX and the final formula TeX come from `display_labels(MODEL)`, which formats the existing exact model without introducing another probability source.
2. Before the badges move, detailed source labels retract to short group names; source bars remain in place. The same orange `真阳性 99 人` and purple `假阳性 999 人` mobjects then travel on continuous `CubicBezier` paths through `MoveAlongPath`. Colors, text and counts remain stable. The original two bars are never translated and concatenated, because they have different denominators.
3. After both badges arrive, `99 + 999 = 1,098 人` appears and holds for 0.75 s. Only then do the source bars fade, the positive-only title appear, and a new bar grow with 1,098 as its denominator. The sum disappears as that bar forms. No intermediate position is labelled as an intermediate probability.
4. The numerator highlight changed from a box around the orange segment to an arrow outside the bar. The arrow points to the orange segment without changing its visible data width. `test_polish.py` checks the pointer stays above the bar.

## 4. Mathematical geometry and tests

The existing model computes `P(D|+)=99/1098=11/122=0.090163934426…`; the display rounds this to 9.02%. For Scene bar width `W=7`, `MODEL.positive_pool_widths(W)` gives approximately `W_TP=0.6311475410` and `W_FP=6.3688524590`; their sum is 7. The Scene creates its two rectangles from these widths and uses no rounded 9% or 9.02% for geometry.

The original 12 M tests still pass **12/12**. New `test_polish.py` passes **8/8**: A1 count conservation; A2 original group ratios; A3 posterior; A4 actual Scene rectangle widths; A5 total bar width; A6 source-to-positive denominator switch; A7 model-derived displayed labels and TeX; A8 same count identity and the numerator pointer outside the bar. The mathematical model and original test file were not modified; their final hashes equal the baselines above.

Independent raster sampling by UID-local `measure_bar.py` reads decoded GIF PNG pixels without importing the Scene. At scanline `y=520`, three stable new frames have the same orange and purple segments:

| Stage | Old visible orange/total | New visible orange/total |
| --- | ---: | ---: |
| Positive bar complete | `40/448 = 8.9286%` | `40/448 = 8.9286%` |
| Numerator highlighted | `44/450 = 9.7778%` | `40/448 = 8.9286%` |
| Final result | `44/450 = 9.7778%` | `40/448 = 8.9286%` |

The new raster result is 0.08782 percentage points below the exact 9.01639%, corresponding to about **0.39 pixel** on the 448-pixel bar, as expected from integer pixel coverage and GIF palette quantization. All three new stable frames keep the same boundaries: orange x=64–103, purple x=104–511. The data segment is not visually enlarged during emphasis. **Model PASS; Scene geometry PASS; GIF raster PASS.**

## 5. MP4, GIF and real keyframes

Using the unchanged Task 13F tools, `render.ps1` produced `build/manim/R028/bayes_formula/bayes_formula.mp4` (576×1024, 517 frames, 21.540 s, approximately 24 FPS). `export_gif.ps1` produced the staged GIF (576×1024, 258 frames, 21.50 s, 80–90 ms/frame, 220 distinct frames, 2,733,678 bytes or 2.61 MiB, infinite loop). A retained copy is `build/manim/R028/14E_2A/candidate/r028_bayes_formula.candidate.gif` with matching SHA-256. After connecting the opening and final TeX to `MODEL`, I reran all 20 tests and rendered/exported again; the GIF was byte-identical, so the formal asset already matches the final Scene. No shared render/export code changed.

`inspect_polish_frames.py` decoded the **actual candidate GIF** and retained 19 keyframes, including total population; both source groups before and after filtering; source labels before movement; movement start, middle and arrival; the 99+999 sum; the new 1,098-person title; bar growth and completion; numerator arrow; formula; result; and loop end. Evidence:

- `build/manim/R028/14E_2A/candidate/keyframes/keyframes_contact.png` — all 19 selected states.
- `.../positive_population_transition_contact.png` — eight transition phases, including the middle of badge motion.
- `.../transition_every_motion_frame.png` — every decoded GIF motion frame from 9.60–10.95 s, reviewed for jumps, identity and overlap.
- `.../before_after_contact.png` and seven `compare_*.png` files — aligned old/new screens for filtering, transition start/middle, sum, final bar, numerator and posterior.
- `.../qa_metrics.json` — 258 scanned frames, 0 empty light frames, minimum 516 foreground pixels at 144×256 sampling, and 0 dark border pixels in the sampled 3-pixel edge.

The first and last GIF frames show the same title/subtitle state, with no blank flash. Review of the continuous movement contact sheet found no instantaneous label jumps, color changes, label crossings or premature shared-denominator claim. The 360×640 reductions of the group filter, `99+999` and final result remain locally legible. These are local visual checks, not Android device acceptance.

## 6. Teaching and visual regression

Q1: the source denominators are now explicitly 100 and 99,900. Q2/Q3: the orange 99 departs the diseased group and the purple 999 departs the healthy group. Q4: their arrival precedes a held `99+999=1,098`; the new group title then names all positives. Q5: the formula and bar use `99/1098`, because the subtitle has changed to “现在只研究阳性者”. The film does not require the report to explain where the new denominator comes from.

The existing light background, visual hierarchy, palette, typography and formula layout are retained. The new text is short, and the more prominent motion serves the conditional-population change. Local visual assessment from actual 576px and 360px frames: diagram focus 24/25, hierarchy 18/20, typography 17/20, semantic color 14/15, motion 9/10, finish 8/10 = **90/100**. The small explanatory line in the source stage and the fraction at reduced width account for most deductions. User review of this **new** version is still pending; the prior PASS WITH NOTES applies to the old GIF.

## 7. Isolated Publisher and formal overwrite

The existing `scripts/zhishu/prepare_knowledge_images.mjs` worker ran on the candidate in an R028-only isolated directory, then ran again on the new formal `images/` file. Each produced one animated GIF resource at `images/R028/r028_bayes_formula.gif`, preserved all 258 frames and infinite loop, and copied bytes with SHA-256 `A723A827E254FE5A13F6D89C581E9168885E3BC58625F21DF0D6AA51D13CB795`. The final formal-source preview is under `build/manim/R028/publisher-preview-f1d84e1a8b1c4903bde1fd56c92a147a/output/`. No other UID was included. No formal Publisher, Content Package or Sync ran. Task 14E.1's historical 55 legacy metadata-validator errors remain outside this GIF task and were not treated as new regressions or repaired.

Before formal update, the old formal GIF still matched the recoverable backup and all 12 protected R028 hashes matched the freeze baseline. With all local gates passed, the explicitly authorized `export_gif.ps1 -Publish -AssetName r028_bayes_formula.gif -Overwrite` replaced **only** R028's existing formal GIF. The new formal, staged and retained candidate GIF hashes match: `A723A827E254FE5A13F6D89C581E9168885E3BC58625F21DF0D6AA51D13CB795`. The formal GIF independently passed `verify_gif.py --width 576 --height 1024`.

## 8. Integrity, changed files and known limits

The 12 frozen TeX/meta/source/PDF/audit/freeze files retain their recorded SHA-256 values. `git status --short` shows only R028 formal GIF and `manim/scene.py` modified, plus R028-local `test_polish.py`, `measure_bar.py`, `inspect_polish_frames.py` and this report added. `math_model.py`, `test_math_model.py`, `storyboard.md`, Task 13F shared scripts, Task 14D visual rules, Publisher/Sync code and other UID assets are unchanged. `git diff --check` has no whitespace error; Git's existing LF-to-CRLF notice for `scene.py` is informational, with no format-wide rewrite in this task.

The formal R028 asset is updated, but wider content publication and sync are not part of this task. Android device playback and new-version user visual acceptance remain pending. The legacy metadata validator's 55 prior schema errors remain a separate known issue.

## 9. Acceptance gates

| Gate | Status | Evidence |
| --- | --- | --- |
| A Pre-flight | PASS | Rules, clean tree, source hashes, old GIF/Scene and backup |
| B Scope | PASS | R028 Scene, UID-local QA and one authorized GIF only |
| C Positive population transition | PASS | Continuous badge paths, held 99+999=1098, actual motion frames |
| D Denominator semantics | PASS | 99/100, 999/99,900, then 99/1098 |
| E Mathematical geometry | PASS | Exact model/Scene widths and stable 40/448 raster segment |
| F Mathematical tests | PASS | Original 12/12 and new 8/8 |
| G Actual keyframes | PASS | 19 keyframes, transition sheet and every motion frame |
| H Teaching clarity | PASS | New positive denominator explicitly formed on screen |
| I Apple-inspired quality | PASS | Local 90/100, 360px reductions reviewed |
| J GIF technology | PASS | 258-frame full decode, loop, no blank/black/cropped frames |
| K Before/after comparison | PASS | Seven paired screens and old/new raster measurements |
| L Publisher isolated preview | PASS | Candidate and formal-source worker previews, byte-identical GIF URI |
| M Frozen asset integrity | PASS | 12 protected hashes; R028-only Git scope |
| N User visual acceptance | PENDING | User has not accepted the revised full GIF |
| O Android device acceptance | PENDING | No user-confirmed real-device playback |

**Task 14E.2A — R028 MATHEMATICAL ANIMATION POLISH LOCAL PASS.**

**USER VISUAL ACCEPTANCE PENDING. ANDROID DEVICE ACCEPTANCE PENDING. R028 MATHEMATICAL ANIMATION FINAL FREEZE PENDING.**
