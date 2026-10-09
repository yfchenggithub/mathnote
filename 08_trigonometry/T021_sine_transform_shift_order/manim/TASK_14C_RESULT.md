# Task 14C Result — T021

Date: 2026-10-09. Scope: mathematical source audit for T021. **Status: MATH SOURCE BLOCKED.** No T021 mathematical model, Manim scene, MP4, GIF, contact sheet, or formal asset was produced. This follows Task 14C's explicit stop condition; it is not a local production pass or a final freeze.

## 1. Pre-flight and actual UID directory

- `git status --short` was empty before work. Existing changes were therefore not present to incorporate.
- The frozen `scripts/manim/production.py` `conclusion("T021")` discovery returned exactly one directory: `D:\mathnote\08_trigonometry\T021_sine_transform_shift_order`.
- All six `01_statement.tex`–`06_summary.tex` sections and `meta.json` were read. `source.tex`, the existing PDF, and the empty `images/` directory were checked. There was no T021 `manim/` before this audit.
- Task 13F's freeze and README, Task 14A's T021 backlog entry, the rendering architecture contract, and the applicable PDF content guideline were read. The F031 Task 14B report records `USER VISUAL PENDING / DEVICE PENDING`, not final freeze. None of those assets or tools was edited.
- SHA-256 baseline for 51 named files in T021, frozen C001/C002/F031 source and images, and shared Manim tools: `build/manim/T021/14C/freeze_baseline.json`.

## 2. Official mathematics audit

The actual topic is the order of horizontal translation and horizontal scaling when constructing

\[
y=A\sin(\omega x+\varphi),\qquad A\ne0,\quad \omega>0,
\]

from `y=sin x`. Here `A` is the **signed vertical coefficient**, `|A|` is the amplitude, `ω` is the positive angular frequency, `φ` is the phase parameter, and `x` is real. The period is `2π/ω`. There is no vertical offset `k` in this conclusion. `A=0` and `ω≤0` are excluded; `φ=0`, `ω=1`, and `0<ω<1` are allowed.

For the horizontal part, the source's two formulas are algebraically correct:

\[
\sin x\xrightarrow{\text{left by signed }\varphi}\sin(x+\varphi)
\xrightarrow{x\mapsto x/\omega}\sin(\omega x+\varphi),
\]

and

\[
\sin x\xrightarrow{x\mapsto x/\omega}\sin(\omega x)
\xrightarrow{\text{left by signed }\varphi/\omega}\sin(\omega x+\varphi).
\]

A negative signed displacement means a right shift. The respective *amounts* are `|φ|` and `|φ/ω|`; they are unequal only when `φ≠0` and `ω≠1`. The period and horizontal factor stated above are correct. The three worked examples in `04_examples.tex` all take `A>0` and do not test the permitted negative branch. `05_traps.tex` discusses shift order and direction but never covers the signed vertical coefficient.

## 3. Negative coefficient and reflection audit

**Blocking error 1 — missing reflection in a claimed general transformation.** `01_statement.tex:4` allows `A<0`. Its two conclusions at `:11` and `:22` say the final step only multiplies vertical coordinates by `|A|`, but the displayed endpoint is `A sin(ωx+φ)`. `03_proof.tex:19` repeats the same step; its second path and equality check at `:23–40` assume the endpoint instead of deriving it. `02_explanation.tex:9–10`, `06_summary.tex:4`, and `meta.json:124,127` carry the same general claim. `source.tex:5` additionally calls signed `A` the amplitude.

Independent counterexample: set `A=-2`, `ω=2`, `φ=π/4`, `x=π/8`. Then `sin(ωx+φ)=1`. The stated `|A|` step produces `+2`, while the target function gives `-2`. A Python `math.sin` calculation returned precisely `2.0` and `-2.0`. Thus the source transformation is false for an allowed parameter choice. This **blocks a GIF teaching the formal two paths**.

Correct relation: after multiplying by `|A|`, reflect in the **x-axis** when `A<0`, or describe one signed coordinate map `(x,y)→(x,Ay)` without calling `A` an amplitude. Here `k=0`, so the x-axis is the correct reflection line. For a different model with offset `k`, the comparison would be about `y=k`; that model is absent from T021. The identity `A sin θ=|A| sin(θ+π)` for `A<0` is another expression of the same final function, not the same geometric operation as the vertical reflection. Under `ω>0`, a phase increase by `π` corresponds to a left shift by `π/ω` of the positive-coefficient curve; this must be stated relative to that curve if used.

`A=0`, a negative `ω`, and a vertical offset are outside the formal conditions. No animation may introduce these as if they were T021 cases.

## 4. Other source mathematics risks

| Finding and source | Analysis and correct wording | Gate |
| --- | --- | --- |
| **Blocking error 2:** `01_statement.tex:31–37` and `02_explanation.tex:4` say the two shift amounts are different under the stated conditions. | With `ω=1`, `φ=π/4`, both amounts are `π/4`; with `φ=0`, both are zero for every allowed `ω`. Say they *can* differ and specify `φ≠0, ω≠1` for strict difference. The formulas themselves remain valid. | BLOCKED: an unrestricted formal conclusion is false. |
| **Misleading operation claim:** `02_explanation.tex:17` says the first shift is unaffected by subsequent scaling and calls the construction “几何变换的可交换性”. | Horizontal scaling changes the location of a previously shifted point. If `L_φ(x,y)=(x−φ,y)` and `S_ω(x,y)=(x/ω,y)`, then `S_ω∘L_φ=L_{φ/ω}∘S_ω`; generally `S_ω∘L_φ≠L_φ∘S_ω`. Describe *equivalent composite results after adjusting the shift*, not commutativity of the original operations. | SOURCE WARNING; material to the intended lesson. |
| **Wrong size adjective on an allowed branch:** `02_explanation.tex:9–10` and `03_proof.tex:19` call the horizontal change a compression. | For `ω=1/2`, the coordinate factor `1/ω=2` is a stretch, while `ω=1` leaves widths unchanged. Say “横坐标变为原来的 `1/ω` 倍”, with compression only for `ω>1`. | SOURCE WARNING. |
| **Missing direction in the core conclusion:** `01_statement.tex:11,22` gives absolute amounts without an adjacent sign rule. | State left for positive `φ`, right for negative `φ`; since `ω>0`, the second path has the same direction. `05_traps.tex` provides this rule, but the stand-alone statement and `meta.json:124,127` should also do so. | SOURCE WARNING. |
| **Source draft direction:** `source.tex:14–15` hard-codes “左移” although `φ<0` is allowed. | Use signed displacement or branch by sign. `source.tex` is supporting material; the six-section formal source and metadata must be fixed at their own locations. | SOURCE WARNING. |

The blockers are in `01_statement.tex` and `meta.json`, not just a visualization preference. Task 14C forbids editing those formal knowledge sources in this production pass. A separate single-UID content repair should correct the statement, proof, explanation, summary, metadata and supporting `source.tex` together; add an explicit negative-`A` example and trap. Then recheck all six sections and the published PDF before restarting production.

## 5. Animation value and prospective teaching goal

The existing PDF and equations can show the two endpoints and numeric shift amounts. A future animation could make the *different intermediate curves and the adjusted shifts* visible on common axes, then show both paths meeting the same target. It would need one consistent model state for curves, labels, and marked points. This is a prospective goal only. The storyboard and model remain **PENDING** until the formal mathematics is repaired and audited again; no positive-`A` subset GIF was produced as a workaround for the general false statement.

## 6. Production, visual, and Publisher status

No `math_model.py`, test module, `scene.py`, MP4, GIF, contact sheet, keyframe inspection, or Publisher isolated asset preview exists for T021 in this task. No formal Publisher, content package, Sync, Android build, or user/device acceptance was run. These are **BLOCKED** by the source mathematics, or **PENDING** after repair. The existing T021 PDF remains untouched; it was not recompiled or visually accepted in this task.

## 7. Frozen asset integrity and files changed

The named 51-file SHA-256 baseline covers T021's pre-existing formal files/PDF, the shared Manim files, C001/C002/F031 UID-local Manim files, and their images. Post-audit comparison is recorded in `build/manim/T021/14C/freeze_comparison.json`. The only intended tracked addition is this report. No frozen GIF, formal TeX, PDF, PNG, `meta.json`, shared script, or other UID file was edited.

## 8. Acceptance gates and final status

| Gate | Status | Evidence |
| --- | --- | --- |
| A — official content identified | PASS | Unique frozen-tool UID discovery; six TeX sections and metadata read. |
| B — negative coefficient/source mathematics | FAIL | Allowed `A=-2` counterexample; false unrestricted shift-difference claim. |
| C — independent mathematical model | BLOCKED | Production stopped before implementation. |
| D — teaching storyboard | BLOCKED | Prospective value identified; no approved storyboard. |
| E — Manim implementation | BLOCKED | No scene created. |
| F — MP4/GIF production | BLOCKED | No render or export. |
| G — actual frame and visual inspection | BLOCKED | No new frames exist. |
| H — Publisher isolated preview | BLOCKED | No new GIF to preview. |
| I — frozen assets | PASS | 51-file before/after SHA-256 comparison; see comparison evidence. |
| J — user desktop / Android device | PENDING | Neither check was performed. |

**Task 14C — MATH SOURCE BLOCKED.** Formal source repair and a fresh mathematical audit are required before independent animation production can resume. **USER VISUAL PENDING / ANDROID DEVICE PENDING.**
