# Task 13G.4V — C043 V2 visual design pilot

Date: 2026-10-09 (Asia/Shanghai). Scope: C043 only. Status: **TASK 13G.4V — V2 VISUAL REVIEW PENDING**. This report records an isolated design experiment, not publication or a new freeze.

## 1. Pre-flight

Read `AGENTS.md`, the mathematics rendering architecture contract, the static-card README, both C051/C043 freeze manifests, the Task 13G stage review, the C043 formal source and the current renderer/label implementation. No Task 13G.4 implementation existed. The work tree had no existing changes before this task. V1 is under `03_conic/C043_hyperbola_abc_relation/static_cards/`; its formal PNGs are under the corresponding `images/`. V2 source is isolated in `scripts/static_cards/v2/` and the C043 private `static_cards_v2/`; outputs are only in `.build/static_cards_v2/C043/`.

The six formal PNG hashes were recorded before editing and matched the freeze manifests. They still matched after the final V2 build:

| UID | 001 | 002 | 003 |
| --- | --- | --- | --- |
| C043 | `f4a09f974c984fccba2fa0a6eda55bbba411aee9b157c1e01b9d5e399574fafb` | `eac8a4d0b9ed784f1616da48e89a6acc88f90310582596d9e139c9113560abac` | `558b584aa4b3d7fac632b980c53f991a4858ed83047bfdaae2152eb8986ef9d2` |
| C051 | `b835627c929140e5b36b34eb81714e66cbcabd75b74bc6a0abe67cdb11eedeb0` | `736e3a9497cf7f0a99bc49f387e4b0e57e59114f915b7f3ac7743b6694606af9` | `01eca6b6097468b36d9b44cda45e361acb44dd482654d70b21e23cc6150b0313` |

## 2. V1 visual audit

- **001 快记:** The formula shares a filled strip with the standard equation, while the large curve panel attracts similar attention. The parameter box occupies another large region. At phone width, the primary relation is not the unmistakable first stop. The curve and repeated notes ask for more reading than a recall card needs.
- **002 快懂:** The exact auxiliary triangle is present and its labels pass the existing gate, but its center sits inside a rectangle, asymptotes, blue branches, a formula strip and an explanation panel. The curve, construction and prose compete. The top formula strip takes height away from the geometry. The B/F₂ distinction is correct but requires careful scanning at phone width.
- **003 快用:** The calculation is mathematically sound, but three equally bordered steps resemble a compact textbook solution. The standardization, positive roots and final answer have similar visual weight; the actual answer is not the strongest endpoint.

## 3. V2 design language

The reusable tokens live in `scripts/static_cards/v2/theme.py`: paper `#FAFBFD`, text `#18283D`, secondary `#64748B`, blue `#2563EB` for `a` and the main curve, teal `#0F9D91` for `b`, amber `#C76A16` for `c`, and light structural lines. Neutral ink is used for full formulas; semantic colors identify segments, corresponding labels and parameter definitions. The system defines seven type roles, a 76 px safe margin, repeatable rule/section spacing and curve, construction, auxiliary, axis and emphasis strokes. Chinese uses the existing local Noto Sans SC or Microsoft YaHei fallback; mathematics uses Matplotlib MathText. No font is fetched at runtime.

`V2Canvas` provides a shared header/footer, text roles, rules and renderer-measured text overlap check. UID-specific diagram geometry and copy stay private. Rounded tint is used only once on the 003 answer. The three cards intentionally do not share one content template. See `scripts/static_cards/v2/README.md` for the design specification and reuse limits.

## 4. Three-card design

- **001 快记:** The relation `c²=a²+b²` occupies the primary visual field. The standard horizontal equation and `a,b,c>0` remain visible. A precisely scaled auxiliary triangle below explains the relation; the last line prevents interpreting `b` as a y-axis intercept.
- **002 快懂:** The exact hyperbola and construction occupy most of the card. `O=(0,0)`, `A=(a,0)`, `B=(a,b)`, `F₂=(c,0)`, `OA=a`, `AB=b`, `OB=c`, `OB=OF₂=c` and the standard equation are retained. B is a hollow auxiliary corner in meaning, distinct from the true focus and not on the curve. A restrained footer states the two essential conclusions.
- **003 快用:** An open three-step vertical flow shows the given equation, division by 144, positive roots, `c=5`, foci and asymptotes. One quiet blue result field replaces repeated bordered cards. The sequence ends with a transferable method sentence.

## 5. V2 preview

Run:

```powershell
python -m scripts.static_cards.v2.build --uid C043 --source-dir 03_conic/C043_hyperbola_abc_relation
python -m scripts.static_cards.v2.review
```

Use `--replace-preview` only when intentionally replacing a previous isolated V2 preview. The final full-size artifacts are `.build/static_cards_v2/C043/{001,002,003}.{png,svg}`, plus `contact_sheet.png`, `build_report.json` and `review_report.json`. PNG hashes are recorded in `build_report.json`. No formal `images/` file was written.

## 6. Mobile preview

The review script generated `{001,002,003}_mobile_390.png` and `{001,002,003}_mobile_360.png` using Pillow LANCZOS. All six were inspected at their actual pixel size. Primary formulas, titles, diagram labels and 003 final answers remain discernible. At 360 px, the small standard equation in 002 and secondary explanation text require more attention than the heroes; footer branding is intentionally subordinate. Device-specific comfort is a human review item, especially for readers with enlarged system text needs. These are image scale previews, not a live phone UI test.

## 7. Mathematical validation

The frozen C043 `Hyperbola` model supplies every plotted coordinate and curve point; V2 changes presentation only. Its eleven validation results all passed. The V2 source gate checked the standard form and positivity, relation, triangle explanation, formal worked example and axis warning against formal TeX. The three V2 tests passed, including exact `(3,4)` auxiliary corner versus `(5,0)` focus, `c²=25`, asymptote slope `3/4` for the worked example, required card copy and diagram label coverage. The V1 C043 model suite passed **7/7**. This is scoped evidence for the displayed claims, not an automatic theorem proof.

## 8. Quality gates

The build decoded all three PNGs at **1080×1440** and produced SVGs. The 001/002 diagrams registered **6/8** semantic labels respectively; all **14** plot texts were registered, with **0 uncovered**, **0 reported collisions** and required object association. The 003 card has no diagram. The V2 whole-card text audit recorded 21/20/18 visible text objects and **0 text overlaps or card-edge overflows**. The common architecture boundary suite passed **2/2**. These gates cover supported line, point and text artists. They do not certify paragraph meaning, visual balance, device rendering, unsupported raster/patch ink or every possible future UID.

## 9. V1/V2 comparison

Equal-scale audit sheets are `001_v1_v2.png`, `002_v1_v2.png`, `003_v1_v2.png`; each side is 390×520. The first glance now lands on the relation in 001, the construction in 002 and the calculation in 003. The design has more negative space and a steadier color/typography language. Tradeoffs: 001 no longer shows the two full branches and foci on the recall card; the information remains in 002. V2's smaller supporting copy may be less comfortable for some readers at 360 px. Whether the quieter page feels more useful than V1 requires user visual judgment; no subjective score was invented.

## 10. Freeze regression

All six formal C043/C051 PNG hashes remain identical to the frozen manifests (table above). A separate C043 V1 build in `.build/static_cards/13g4v_v1/C043/` succeeded; its three PNG hashes exactly matched C043 formal images. The normal V1 `--validate-only` entry passed mathematics and content. Git status showed only the newly added V2 directories and this report; no Task 13F, GIF, Publisher, TeX, PDF, metadata, app or formal asset source was modified. No publication was performed.

## 11. Reusability

The palette, type roles, spacing, frame and copy/line primitives can be reused for future individually authorized UIDs. Formula length, one/multiple/no diagram layouts, long titles, probability and solid geometry, and additional figure primitives need separate pilots and gates. Three C043 designs do not justify imposing one universal structure.

## 12. Files changed

- Added `scripts/static_cards/v2/{__init__,theme,components,build,review}.py` and `README.md`.
- Added `03_conic/C043_hyperbola_abc_relation/static_cards_v2/{__init__,cards,test_v2}.py`.
- Added this report.
- Generated preview/review artifacts only under ignored `.build/static_cards_v2/C043/`, plus an isolated V1 regression build under `.build/static_cards/13g4v_v1/C043/`.

## 13. Remaining issues

User visual approval is outstanding. Secondary text at 360 px and the relative value of 001's simplified graphic need real-device judgment. Source token checks confirm listed facts but cannot prove every wording implication. The generic collision gate is opt-in and still has unsupported graphic primitives, as noted in the Task 13G stage review. No broad UID design or automatic publishing capability is claimed.

## 14. Final status

**TASK 13G.4V — V2 VISUAL REVIEW PENDING.**
