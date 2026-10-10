# Task 14E.2 Result — R028 Bayes Formula Animation

Date: 2026-10-10. Status: **R028 ANIMATION LOCAL PRODUCTION PASS**. User visual acceptance and Android device acceptance remain **PENDING**. This is not mathematical animation FINAL FREEZE, nor a formal Publisher / Content Package / Sync release.

## 1. Pre-flight and rules

- Branch `main`; initial `git status --short` was clean. R028 was `06_probability-stat/R028_bayes_formula/`; it had neither `manim/` nor a formal GIF, and `images/` was empty. `rg --files -g AGENTS.md` found only the root `AGENTS.md`, so there was no nested rule. No applicable rule conflict was found.
- Read root `AGENTS.md` (global rules, task routing, GIF production), `docs/architecture/math-rendering-boundaries.md` (directory responsibilities, build and publication), `scripts/manim/VISUAL_GUIDELINES.md` (sections 1–13), `scripts/manim/README.md` (environment and workflow), and `scripts/manim/TASK_13F_FREEZE.md` (frozen infrastructure). Read R028's six formal TeX sections, `meta.json`, Task 14E.0 audit and Task 14E.1 source freeze. The TeX was read solely as animation knowledge source; no PDF content or build was changed.
- `.\scripts\manim\check_env.ps1` returned `Environment PASS`: Python 3.14.3, Manim 0.21.0, Pillow 12.3.0, FFmpeg, TeX Live and Microsoft YaHei available.
- Task 14E.1's source freeze is the mathematical baseline. At start and after production, the 12 protected R028 source/PDF/report files had identical SHA-256 values. Representative values: `04_examples.tex` `7A1C3127F943E9E84CB6A61D7C8CEA68CF88652F0B44019F3B5A41FB7BFDA11E`, `meta.json` `005A54CFC5459695C942E2C35A8A04E5D50718D99EBDCA100747CA8E4D784334`, formal PDF `D24E933A6FB5C9BA95FDFDDEF1F28CE7B5C99F9BA63B8B58A50F913AE1A73658`.

## 2. Official example selection

| Frozen example (`04_examples.tex`) | Given data and answer | Animation fit |
| --- | --- | --- |
| 1 — medical test | `P(D)=0.001`, `P(+|D)=0.99`, specificity `0.99`, hence `P(+|not D)=0.01`; `P(+)=0.01098`, `P(D|+)≈0.0902` | **Selected.** Two source groups and positive-only reconditioning directly answer the lesson question; exact integer counts are possible. |
| 2 — three machines | Production shares `.5/.3/.2`, defect likelihoods `.01/.02/.03`; `P(defect)=.017`, posterior for A `≈.2941` | Sound Bayes example, but three branches and factory attribution are less direct for the requested medical-screening story. |
| 3 — two coins | Equal prior, likelihood `.25/1`; `P(two heads)=.625`, fair-coin posterior `.2` | Sound two-branch example, but no medical population to filter. |

The animation uses example 1's exact values; no new demonstration probabilities were invented. `D` means diseased, `not D` means healthy, and `+` means a positive test. These symbols rename formal example 1's `A`, `overline A`, and `B` without changing the events.

## 3. Exact mathematical model

`math_model.py` stores finite decimal probabilities as `Fraction`. For a stipulated theoretical population `N=100,000`:

| Quantity | Formula | Exact value |
| --- | --- | ---: |
| Diseased | `N × .001` | 100 |
| Healthy | `N × .999` | 99,900 |
| True positive | `N × .001 × .99` | 99 |
| False positive | `N × .999 × .01` | 999 |
| All positive | `99 + 999` | 1,098 |
| Positive probability | `.00099 + .00999` | `.01098` |
| Posterior | `99 / 1098 = 11 / 122` | `0.090163934… ≈ 0.0902 = 9.02%` |

Counts are exact within this stipulated theoretical population, not a random simulation. The two *source* group containers are equal screen width and explicitly labelled symbolic; each colored strip is scaled **within its own group** (`99/100` and `999/99,900`). At the condition-space change, count badges move to a new positive-only bar. Its orange and purple widths are `99/1098` and `999/1098` of the same 7-unit track. Actual raster sampling of the pool at keyframe 09 found 40 orange and 408 purple pixels across 448 pixels, consistent with the exact 9.016% share to pixel precision. The numerical label remains exact independent of raster rounding. There is no one-icon-to-one-person implication.

The numerator is `P(D∩+)=0.00099`; the denominator is `P(+)=0.01098`, comprising *both* positive sources. Thus `P(D|+)=P(D∩+)/P(+)=99/1098` with `P(+)>0`.

## 4. Teaching objective and independent storyboard

`storyboard.md` defines a UID-specific seven-beat story: all 100,000 people → partition 100/99,900 → retain 99% of the diseased group → retain 1% of the healthy group → move 99 and 999 positive count badges into a new group → display the positive-only proportional bar and numerator/denominator → obtain 9.02%. This uses no T021 model, layout or motion. The transition to “现在只研究阳性者” is the main cognitive event, and the moving count badges explain where the new denominator comes from.

The color roles are stable: orange true positive, purple false positive, gray other outcomes, green posterior result. The light background, restrained labels, one primary diagram, progressive disclosure and exact geometry follow `VISUAL_GUIDELINES.md` sections 1–8. A 9:16 scene coordinate system is explicitly set in the UID-local Scene to fill the portrait canvas.

## 5. Implementation and mathematical tests

All production source is in R028's `manim/`: `math_model.py`, `test_math_model.py`, `storyboard.md`, `scene.py`, `inspect_frames.py`, and `preview_publisher.py`. Shared Task 13F tools were not modified. `scene.py` contains one direct `Scene` subclass, `R028BayesScreening`.

`.\.venv-manim\Scripts\python.exe -B 06_probability-stat/R028_bayes_formula/manim/test_math_model.py` returned `Ran 12 tests ... OK`. M1 prior; M2 sensitivity, specificity and false-positive direction; M3 total probability; M4 true-positive mass; M5 false-positive mass; M6 posterior; M7 prior and posterior normalization (without falsely asserting `P(+)=1`); M8 integer population conservation; M9 formal example source literals; M10 `P(+)=1`, `P(+)=0`, and category probability 0/1 model boundaries; M11 four-decimal and percent rounding; M12 pool-width/count state consistency. The 0/1 edge cases exercise the model, while the fixed Scene renders frozen example 1 only.

## 6. MP4 and GIF production

Commands used:

```powershell
.\scripts\manim\render.ps1 -Uid R028 -Scene R028BayesScreening -SceneFile scene.py -Name bayes_formula -BuildRoot build/manim
.\scripts\manim\export_gif.ps1 -Uid R028 -Scene R028BayesScreening -SceneFile scene.py -Name bayes_formula -BuildRoot build/manim
```

The final MP4 is `build/manim/R028/bayes_formula/bayes_formula.mp4`: 576×1024, 482 frames, about 24 FPS, 20.083 s (`ffprobe`). Staged GIF is `build/manim/R028/bayes_formula/bayes_formula.gif`: 576×1024, 241 frames, 20.08 s, 80–90 ms/frame, 205 distinct decoded frames, 2,453,728 bytes (2.34 MiB), infinite loop. Shared `verify_gif.py` passed full-frame decode, nonzero durations, frame diversity and black-frame checks (`black_frames=0`).

The first draft exposed excess whitespace; setting the Scene's portrait world coordinates fixed it. A later full-frame review found a blank loop start. The final Scene draws the title in frame 0 and returns to the same title/subtitle composition at the end. The final render/export and all QA below were rerun after those fixes.

## 7. Actual keyframes and full-frame review

`inspect_frames.py` decoded the **actual GIF**, retained 14 PNG keyframes and `contact_sheet.png` under `build/manim/R028/bayes_formula/qa_frames/`. Actual GIF frames: 0 loop start, 16 total population, 42 partition, 52 diseased group before filtering, 72 after, 79 healthy group before, 98 after, 108 positives ready, 120 merging, 155 new positive population, 173 numerator focus, 194 formula/fraction, 215 final result, 240 loop end. Each was reviewed against model counts, color meaning, proportion, formula, label legibility, positioning and cropping. The complete contact sheet and individual full-size frames show no observed overlap or formula clipping. A 360×640 reduction of the two densest states (`06_h_after_360.png`, `12_result_360.png`) remains readable locally; it is not Android acceptance.

`qa_metrics.json` records 241 scanned GIF frames, **0 empty light frames**, minimum 515 foreground pixels per frame at 144×256 sampling, and **0 dark content pixels on the sampled 3-pixel border**. The first and last frames show the same title/subtitle composition; their differing palette pixels are not a visible transition. Real motion occurs during both filters, badge migration and formation of the new pool. Technical checks do not by themselves prove teaching value or Android display quality.

## 8. Teaching and visual acceptance

The final sequence answers all six requested questions: initial condition set is all people; a positive result changes the set to positive people; the positive set contains 99 true and 999 false positives; denominator `P(+)` is all 1,098 positives; numerator `P(D∩+)` is the 99 positive diseased people; posterior is 99/1098 ≈ 9.02%. The equal-width source rows are explicitly declared symbolic, while the new positive bar is truly proportional. This avoids visually confusing `P(+|D)=99%` with `P(D|+)≈9.02%`.

Local visual score using `VISUAL_GUIDELINES.md` section 13.1 on actual 576px and 360px frames: diagram focus **23/25**, hierarchy **18/20**, typography/formula **17/20**, semantic palette **14/15**, motion/critical holds **9/10**, overall finish **8/10** = **89/100**. Deductions reflect the small source-container clarification and dense fraction on a reduced phone-width preview. No critical readability or mathematical issue was found locally. User and Android acceptance remain separate.

## 9. Isolated Publisher compatibility

The existing `scripts/zhishu/prepare_knowledge_images.mjs` worker was run in R028-only isolated build directories, first against a staging copy and then against the newly added formal R028 `images/` directory. The formal-source run returned one runtime asset `images/R028/r028_bayes_formula.gif`, 241 frames, infinite loop, unchanged 2,453,728 bytes and identical source/output SHA-256 `B0E990B8FBFAF7F032381E2C2AC70EB7D9C1E6492173168C8215C29FECD0D914`. It retained GIF format, not WebP. The final isolated output is under `build/manim/R028/publisher-preview-d5d17c7b006146e4bb2c8f1ab914f791/output/`. No other UID entered the job. No formal Publisher, Content Package, Sync, App modification or APK build ran.

The Task 14E.1 source-freeze report records 55 unchanged historical errors from the legacy `scripts/check_meta_json.py` schema. This task did not rerun or repair that incompatible validator. The current image worker and R028 metadata ID/path checks passed. Formal package publication remains outside this task; this compatibility result does not claim the legacy validator is fixed.

## 10. Formal asset, integrity and files changed

After local mathematical, frame, visual, technical and isolated compatibility gates passed, the absent target name was rechecked (`Test-Path` false). The authorized command `.\scripts\manim\export_gif.ps1 ... -Publish -AssetName r028_bayes_formula.gif` **added** `images/r028_bayes_formula.gif` without `-Overwrite`. Formal and staged GIF SHA-256 are both `B0E990B8FBFAF7F032381E2C2AC70EB7D9C1E6492173168C8215C29FECD0D914`; the formal GIF independently passed `verify_gif.py --width 576 --height 1024`.

`git status --short` after publication shows only the new R028 `images/` and `manim/` directories. The 12 frozen R028 source/PDF/report hashes still match the initial baseline. No shared Manim, visual, Publisher or Sync code, other UID source or existing GIF was edited. The formal asset is present, but the wider Publisher/Sync release state is **not published/synced**.

Changed files: R028 `manim/math_model.py`, `test_math_model.py`, `storyboard.md`, `scene.py`, `inspect_frames.py`, `preview_publisher.py`, this report, and `images/r028_bayes_formula.gif`. Staged MP4/GIF, 14 keyframes, contact sheet, QA metrics and isolated Publisher previews are under ignored `build/manim/R028/`.

One failed attempt to create an isolated preview with Python's `tempfile.mkdtemp` left an access-restricted, unused directory `build/manim/R028/publisher-preview-mnfky5ae`; native PowerShell cleanup was denied. The preview script was changed to create a UUID-named directory and both subsequent isolated runs passed. The inaccessible directory is confined to ignored R028 build output and is not consumed by the GIF or worker. No protected or formal asset was affected.

## 11. Acceptance gates and final status

| Gate | Status | Evidence |
| --- | --- | --- |
| A Pre-flight | PASS | Clean initial tree, UID/asset inventory, actual rules, environment |
| B Mathematical source | PASS | Frozen TeX/meta/PDF/report hashes unchanged |
| C Example selection | PASS | Three formal examples compared, example 1 selected |
| D Mathematical model | PASS | Exact `Fraction` masses, counts and posterior |
| E Mathematical tests | PASS | M1–M12, 12/12 |
| F Independent storyboard | PASS | UID-specific condition-space change, no T021 copy |
| G Manim Scene | PASS | UID-local direct Scene, model-driven bars and counts |
| H MP4/GIF production | PASS | Real 482-frame MP4 and 241-frame GIF |
| I Actual frame validation | PASS | 14 real frames, contact sheet, 241-frame QA metrics |
| J Teaching value | PASS | Positive-only denominator is formed on screen |
| K Visual quality | PASS | Local score 89/100; 360px reduction reviewed |
| L GIF technology | PASS | Full decode, 20.08 s, loop, no blank/black frames |
| M Publisher compatibility | PASS | R028-only current worker, correct GIF URI and hash |
| N Frozen asset integrity | PASS | Protected hashes and Git scope checked |
| O User visual acceptance | PENDING | User has not reviewed the completed GIF |
| P Android device acceptance | PENDING | No user-confirmed real-device playback |

**Task 14E.2 — R028 ANIMATION LOCAL PRODUCTION PASS.**

**USER VISUAL ACCEPTANCE PENDING. ANDROID DEVICE ACCEPTANCE PENDING. R028 MATHEMATICAL ANIMATION FINAL FREEZE PENDING.**
