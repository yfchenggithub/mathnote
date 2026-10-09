# Task 14C.1 Result — T021

Date: 2026-10-09. Scope: mathematical source correction for `D:\mathnote\08_trigonometry\T021_sine_transform_shift_order`. **Task 14C.1 — T021 MATHEMATICAL SOURCE CONSISTENCY FINAL FREEZE.** This freezes the corrected mathematical facts and the corresponding T021 PDF. It does not authorize GIF production, Publisher/Sync, or claim a separate PDF teaching-diagram enhancement.

## 1. Pre-flight

The branch was `main`. At task start, the only working-tree item was the untracked `manim/TASK_14C_RESULT.md` from Task 14C; it was preserved verbatim. The exact-UID rule had found one T021 directory. All six TeX sections, `meta.json`, `source.tex`, `main.tex`, the existing PDF, and the prior audit were read. `main.tex` inputs the six numbered TeX files directly; `scripts/build_conclusion_pdfs.py` builds a wrapper around `main.tex` and does not generate the numbered sections from `source.tex`. Thus the six sections are the PDF's content source; `source.tex` is supporting text and was synchronized separately. No shared script was changed.

Before editing, SHA-256 hashes for 82 pre-existing files in T021, C001, C002, F031, and `scripts/manim/` were saved at `build/manim/T021/14C1/baseline.json`. This includes the previous Task 14C report and all named frozen GIFs. The prior 51-file Task 14C baseline was also retained.

## 2. Original mathematics findings

Task 14C's blockers were reproduced. The formal conditions allowed `A=-2`, yet the last operation was described as multiplying by `|A|`: for `ω=2`, `φ=π/4`, `x=π/8` it produced `+2` instead of the target `-2`. The statement also said shift distances always differed, contradicted by `ω=1` or `φ=0`. Supporting errors included calling signed `A` the amplitude, calling the adjusted composition ordinary commutativity, treating all `ω>0` as compression, and writing unconditional left shifts with negative `φ` allowed.

## 3. Corrected mathematical contract

From `y=sin x`, construct `y=A sin(ωx+φ)` with `A≠0`, `ω>0`, `φ∈ℝ`, `x∈ℝ`. `A` is the signed vertical coefficient; the amplitude is `|A|`; the period is `2π/ω`. The two horizontal paths are:

1. Move left by signed `φ`, multiply every x coordinate by `1/ω`.
2. Multiply every x coordinate by `1/ω`, move left by signed `φ/ω`.

Both then multiply every y coordinate by `A`. Positive `φ` means left, negative `φ` right, and zero means no movement. The shift distances are `|φ|` and `|φ|/ω`; they are equal exactly when `φ=0` or `ω=1`. `ω>1` compresses horizontally, `ω=1` leaves horizontal scale unchanged, and `0<ω<1` stretches. `A<0` is equivalent to scaling y by `|A|` and reflecting in the x-axis; it is not a negative amplitude. `A=0`, `ω≤0`, and vertical offsets remain outside the contract.

## 4. Composition proof and negative A correction

For a source point `(t,sin t)`, the first path ends at `((t−φ)/ω,A sin t)`; the second ends at `(t/ω−φ/ω,A sin t)`, the same point. Writing its final x coordinate as `x` gives `t=ωx+φ`, hence y is exactly `A sin(ωx+φ)`. This covers negative `A` and every permitted `t`. The relation is `Sω∘Lφ=L(φ/ω)∘Sω`. Generally `Sω∘Lφ≠Lφ∘Sω`; the shift must be adjusted.

## 5. Six-section and supporting-source changes

- `01_statement.tex`: signed final vertical operation, parameter roles and direction, correct equality condition, negative-`A` reflection.
- `02_explanation.tex`: point-displacement intuition, noncommutativity, all horizontal scaling regimes, amplitude distinction.
- `03_proof.tex`: two complete function chains and a point-coordinate proof that reaches the target for both signs of `A`.
- `04_examples.tex`: preserved and rechecked three positive-`A` examples; added both paths for `A=-2, ω=2, φ=π/4`, the `x=π/8` value check, and compact `ω=1`, `φ=0`, `0<ω<1`, negative-`φ` examples.
- `05_traps.tex`: corrected both shift-order mistakes and added equality, noncommutativity, negative-coefficient, and stretch/compression traps.
- `06_summary.tex`: concise contract and coordinate identity, matching the statement and proof.
- `source.tex`: corrected the amplitude definition, signed directions, both paths, equality condition and scaling regimes. It is not used as the PDF build input.
- `meta.json`: updated only mathematics-related string values plus `updated_at`; JSON field names, field types, UID, knowledge node, and asset references were preserved. `main.tex` was unchanged.

The T021 TeX still contained pre-existing literal Markdown `**` emphasis that the PDF printed as visible asterisks. In the touched explanation, proof and examples, those markers were converted to TeX `\textbf{}`. This removed a visible PDF defect without changing mathematical meaning.

## 6. Mathematical regression and consistency audit

`python -B -m unittest discover -s 08_trigonometry/T021_sine_transform_shift_order/tests -p test_*.py -v` passed **5/5 tests**. The independent point maps covered 126 combinations of `A∈{-2,2}`, `ω∈{1/2,1,2}`, `φ∈{-π/4,0,π/4}`, and seven source points, comparing both final coordinates against direct evaluation of `A sin(ωx+φ)`. Separate checks covered the original `-2` versus `+2` counterexample, equality of shift distances, signs, horizontal scaling regimes, adjusted composition versus unadjusted noncommutation, and all three original plus the new example cases at several x values.

The six updated sections, metadata and supporting source were read again against the contract above. Their descriptions now agree on `A`, `|A|`, direction, scale, shift amounts, equality conditions, and operation order. The metadata schema/type comparison against `HEAD` passed; `id`, knowledge-node association and asset references stayed fixed. `python -m json.tool` passed. `git diff --check` passed. Mathematical checks supplement rather than replace the source and PDF review.

## 7. PDF regeneration and page review

The existing single-UID builder was run only for `--modules 08_trigonometry --ids T021`, writing an isolated PDF and map under `build/conclusion_pdfs/T021/14C1/`. Compilation succeeded. `pdfinfo` reported **7 A4 pages**. All seven pages were rendered at 180 DPI and visually inspected: statement and explanation (pages 1–2), proof (page 3), examples (pages 3–5), traps (pages 6–7), and summary (page 7). The first render exposed literal `**` markers; after their correction, the isolated PDF was rebuilt, all affected pages re-rendered and inspected, and no remaining marker, clipped formula, overlap or broken box was seen. Text extraction from the rebuilt PDF confirmed the negative-coefficient example and x-axis reflection; no literal `**` remained.

The validated isolated PDF was copied to a temporary file beside `pdfs/T021_sine_transform_shift_order.pdf`, hash checked, then atomically replaced the **T021 PDF only**. The formal PDF is byte-identical to the isolated output: SHA-256 `6ea968d8caa24fdc202ec18c3bb99418bdfafcd588c601432a5d831c6b861a6d`. No Publisher or Sync was used. This task's PDF check establishes mathematical and page consistency; it does not claim the separate PDF guideline's full diagram-led teaching enhancement.

## 8. Protected assets and file differences

`build/manim/T021/14C1/after.json` and `comparison.json` hold the after-hashes and whitelist comparison. Of 82 baseline files, exactly **9 authorized T021 files changed**, **73 stayed byte-identical**, **0 were missing**, and **0 changed outside the whitelist**. Rechecking the historical 51-file Task 14C baseline gave the same nine authorized changes, 42 unchanged, zero missing. The earlier Task 14C report remained unchanged. C001/C002/F031 GIFs and UID-local sources, shared Manim tools, and all other protected files in the baseline stayed unchanged.

Modified pre-existing files: six T021 numbered TeX sections, `meta.json`, `source.tex`, and the single T021 formal PDF. Added files: `tests/test_t021_transform_math.py` and this report. The earlier untracked `manim/TASK_14C_RESULT.md` remains present and unmodified. No Manim scene, GIF, content package, or other UID file was created or changed.

## 9. Known issues and acceptance gates

No blocking mathematical or PDF consistency issue remains in this repair scope. The T021 PDF did not gain a new teaching diagram; diagram-led PDF enhancement is a separate quality task and is not represented as complete here. User desktop review and Android device review belong to later animation acceptance, not this source freeze.

| Gate | Status | Evidence |
| --- | --- | --- |
| A — pre-flight | PASS | Branch and worktree checked; prior report preserved; exact T021 source relation established. |
| B — negative A | PASS | Signed y map and x-axis reflection; `-2` counterexample and matrix regression. |
| C — translation order | PASS | Two path proof; signed direction, equality condition, noncommutation checks. |
| D — parameter conditions | PASS | Positive/negative `A`, three `ω` regimes, and three `φ` signs tested. |
| E — source synchronization | PASS | Six TeX sections, `meta.json` and `source.tex` reread; schema preserved. |
| F — independent tests | PASS | 5 tests; 126 parameter/point combinations plus example and edge checks. |
| G — PDF | PASS | Isolated build, 7-page render/review, byte-identical formal T021 update. |
| H — freeze integrity | PASS | 9 whitelisted changes; 73 protected files unchanged; none missing. |

**Task 14C.1 — T021 MATHEMATICAL SOURCE CONSISTENCY FINAL FREEZE.** Task 14C.2 may independently re-audit this frozen source before any animation production. No GIF or formal Publisher release occurred in Task 14C.1.
