# Task 13G.3 — Static Cards Stage Review & Batch Feasibility

Date: 2026-10-09 (Asia/Shanghai). Scope: read-only audit of the existing C051/C043 pilots, bounded `03_conic` inventory, and isolated benchmark builds. **TASK 13G.3 — STAGE REVIEW COMPLETE.** This is a review result, not Task 13G-wide FINAL FREEZE or authorization to produce/publish a batch.

## 1. Executive summary and pre-flight

**Decision:** controlled cross-module pilot **CONDITIONAL GO**; immediate large-scale production **NO-GO**. The project can repeatedly render three cards for an already authored UID. It cannot turn arbitrary six-part TeX and `meta.json` into mathematically reviewed, visually approved cards without substantial UID-specific work. The two successful conic pilots establish a reusable rendering layer, not an automatic mathematical-content factory.

The working tree was clean before this review. The applicable root rules, [architecture contract](../../docs/architecture/math-rendering-boundaries.md), [static-card README](README.md), both [C051](TASK_13G_1_C051_FREEZE.md) and [C043](TASK_13G_2_C043_FREEZE.md) freeze manifests, [13G.2A](TASK_13G_2A_REPORT.md) and [13G.2A.2](TASK_13G_2A_2_REPORT.md) reports, current code, tests, and actual Publisher image code were inspected. No production code, TeX, `meta.json`, formal image, Manim source, Publisher, or app file was edited.

| Work item | Current evidence and status |
| --- | --- |
| 13F | Shared Manim infrastructure **FINAL FREEZE**, per `scripts/manim/TASK_13F_FREEZE.md`; separate UID/device review limits remain. No GIF was rebuilt here. |
| 13G.0A | Architecture contract still explicitly says **ARCHITECTURE REVIEW PENDING**. Its old example text predates the implemented static cards; no architecture FINAL FREEZE was inferred. |
| 13G.0B | Current root `AGENTS.md` routes work by actual task type. The PDF guideline records the 13G.0B.1 rule migration; no separate global freeze manifest was found in the inspected locations. |
| 13G.1 | C051 **FINAL FREEZE — PASS** for its three formal cards and exercised preview interface. |
| 13G.2A / .2A.2 | Shared placement, collision, coverage, and association improvements are implemented and tested. Their contemporaneous preview reports say visual review pending; C043's later 13G.2B manifest supersedes that status for the reviewed 002 asset. |
| 13G.2B / 13G.2 | **Actually executed**: C043 freeze manifest records three formal hashes, isolated rebuild and Publisher evidence. All three formal hashes matched this review's isolated rebuild. C043 is **FINAL FREEZE — PASS** within its stated scope. |

The old `.build/static_cards/<UID>/build_report.json` values `VISUAL REVIEW PENDING` are preview-stage snapshots. The later human acceptance and formal publication are documented in the freeze manifests; the build reports themselves are not a current publication ledger.

## 2. Stage achievements and capability register

Evidence tags below refer to current implementation, current tests, and the two scoped freeze manifests. **FROZEN** applies only to the specified pilots or exercised interface, never to arbitrary UIDs.

| Capability | Status | Evidence and boundary |
| --- | --- | --- |
| Exact UID source loading; select one or all specified card numbers | IMPLEMENTED / TESTED / FROZEN in pilots | `build.py` checks source path/UID, card IDs, formal files and metadata; both pilot rebuilds passed. There is no UID discovery or batch queue in this entry. |
| 快记 / 快懂 / 快用 and common 1080×1440 template | IMPLEMENTED / TESTED / FROZEN in pilots | Six formal PNG hashes match isolated output; `CardCanvas` owns typography and card frame. The teaching text and drawings are UID-specific. |
| Isotropic mathematical coordinate mapping | IMPLEMENTED / TESTED | `MathFrame.xy` and UID model suites; only two-dimensional pilot geometry is demonstrated. |
| Chinese and MathText layout; PNG/SVG; contact sheet | IMPLEMENTED / TESTED / FROZEN in pilots | `canvas.py` export and `build.py`; every pilot card emitted PNG and SVG, three-card builds emitted a contact sheet. |
| Isolated preview, source/implementation/output SHA-256, build report | IMPLEMENTED / TESTED / FROZEN in pilots | Output confined to `.build/static_cards/.../<UID>`; changed preview needs `--replace-preview`. Report has no stage timings or formal approval history. |
| Formal publication and Publisher compatibility | IMPLEMENTED / TESTED / FROZEN for C051/C043 assets | Both freeze manifests record explicit human-authorized copying and source/preview hashes. `build.py` itself never publishes; Publisher discovery, PNG→WebP, and GIF copy are separate code paths. |
| Full diagram label collision, text coverage, and object association | PARTIAL | `LabelLayout` is used by **C043 card 002**. Other five pilot cards use targeted tests or fixed placements; they do not declare a full plot coverage gate. |
| Automatic TeX→three-card mathematical/teaching specification | MISSING | `SPECS`, drawing, copy and assertions live in each UID's `cards.py` and `model.py`. |
| Incremental/multi-UID build, durable approval ledger, failure recovery | MISSING | No batch scheduler, per-UID state machine, cache skip, resume or publication transaction in static builder. |

### Mathematical correctness actually checked

C051's exact `Fraction` model and **8/8** current tests cover positive `p`, vertex, upper/lower curve points, focus `F=(p/2,0)`, directrix `x=-p/2`, perpendicular foot `H`, `PF=PH=x₀+p/2`, formal example, invalid points, drawn curve continuation and targeted diagram clearance. C043's model and **7/7** current tests cover both branches, positive `a,b`, `c²=a²+b²`, vertices/foci, asymptotic slope, auxiliary rectangle and triangle, B distinct from curve/focus, and the `9x²−16y²=144` example. Both isolated full builds passed their implemented source-token and model checks. This proves those assertions for those inputs; it does not automatically interpret or prove another conclusion. C051 formal TeX's use of “半通径” for `p/2` remains a separate terminology issue recorded in its freeze manifest; card formulae are correct and the formal source was not changed.

### Visual failures seen during the pilots

| Pilot issue | Root cause and repair | Reusable regression coverage / remaining risk |
| --- | --- | --- |
| C051 `PF` label touched segment/curve | Fixed position lacked ink clearance; moved relative to the exact PF segment. | C051 test checks PF's padded text box against PF and parabola. It is a targeted assertion, not generic plot coverage. |
| C051 directrix label hit dashed line | Fixed text position was too near the line; offset and specific clearance were corrected. | C051 test checks named directrix text against line. New annotation forms can still escape that test. |
| C051 ordinary curve point looked like endpoint | Sampled drawing stopped at P; curve samples were extended beyond P. | Exact sample-continuation test exists. Other moving-point diagrams need their own check. |
| C043 `A` and `b` labels overlapped geometry | Fixed offsets and missing path collision detection; semantic `PointLabel`/`SegmentLabel` placement added. | Shared collision tests and C043 002 test reconstruct old bad positions. Only declared layouts receive the full gate. |
| C043 `B` drifted away from its corner | Candidate ordering preferred distant position; shortest-offset search, maximum anchor distance, wrong-object proximity, and optional checked leader were added. | Shared tests plus C043 002 test; association remains a geometric heuristic and human review is required. |
| C043 ordinary note crossed an asymptote | It was not registered as a semantic label; `finalize()` now enumerates all visible in-plot text, and the note moved to teaching copy below. | Current C043 002 report: 18 visible text artists, 8 in plot, 8 registered, 0 uncovered, 0 collisions. Unadopted UID drawings and unsupported patch/raster ink remain blind spots. |

## 3. Reuse assessment

`scripts/static_cards/` owns the 198-line preview builder, 111-line canvas, and 567-line label-layout module. Both UID directories import these common tools; common code does **not** import a UID's private model. C043 added semantic labels and plot coverage in common tooling to solve a recurring class of visual errors, plus C043-specific hyperbola logic. There is some deliberate low-level geometry repetition in private sources; it has not become a cross-UID dependency. New modules do not presently require changing common code for ordinary custom Matplotlib drawings, but new primitive types need gate adapters if automatic collision claims are desired.

The UID-specific production burden is material: C051 has 151 lines of `cards.py` and 70 of `model.py`; C043 has 186 and 93, plus 100 and 136 lines of respective model tests. These counts measure current source size, **not** development hours or automated generation rate. Each UID still authors its mathematics, examples, three pieces of teaching copy, plotting and assertions. Generic rendering reuse is high; automatic mathematical-content generation is low. **REUSE ASSESSMENT: MEDIUM** overall. The shared API is proven for two conics and scoped-frozen by C043's manifest, but not stable by evidence across other mathematical modules.

## 4. Three levels of batch feasibility and automation gap

| Level | Current state | Principal missing controls |
| --- | --- | --- |
| 1. Render already reviewed UID sources | A single UID can render one or three cards repeatedly in an isolated preview. **Conditional feasibility** for a scripted sequential loop. | No native multi-UID CLI, incremental skip, cache invalidation policy, durable per-UID failure ledger or resume. A partial preview replacement is not a cross-UID transaction. |
| 2. Create cards from formal TeX/metadata | **Not automatic.** `verify_sources` checks presence, UID, hashes and a few UID-specific text tokens; the mathematical interpretation, teaching target, card copy, figures and tests are human/Codex authored. | Structured specification, reusable figure families, reviewable example selection, evidence-linked math assertions and per-UID human mathematical review. “Codex can write the code” is not an unattended production system. |
| 3. Review and publish many UIDs | Existing UID-specific math tests, one partial collision gate, manual visual acceptance, explicit copying and Publisher compatibility proved for two UIDs. **Not batch-ready.** | Recorded approvals tied to hashes, complete visual gate coverage, independent failure quarantine, no-overwrite publication, versioned manifest, batch Publisher rehearsal and recovery policy. |

Step-by-step from formal source: interpret result/conditions (**human mathematical review**); choose objectives, three-card pedagogy, example and graphic (**UID-specific Codex authoring plus human review**); implement model/drawing/assertions (**UID-specific code**); run exact model and token tests (**automated only for declared claims**); build PNG/SVG (**common automated tool**); check covered plot text/collisions (**automated only where `LabelLayout` is declared**); inspect mathematics, association, legibility and teaching claims (**human**); publish and map through Publisher (**explicit controlled procedure**, no static batch entry). No current gate proves the whole chain from arbitrary TeX automatically.

The builder fails on mathematical assertion failure and on a declared layout's `LAYOUT_FAIL`/`COLLISION_FAIL`, and blocks a changed preview without `--replace-preview`. It has no general theorem verifier. Its content gate uses UID-specified substrings, so a relevant TeX edit outside those tokens can pass; source hashes reveal the edit but do not judge it. For C051 and C043 cards without a declared layout, `CardCanvas.export` checks card-edge clipping but not every geometry/text intersection. C043 002 checks line/marker/text geometry sampled from supported Matplotlib artists; arbitrary patches, raster elements, dashed-gap semantics and wrong teaching meaning require more work or review.

## 5. Inventory and remaining scale

The **current bounded `03_conic` inventory** contains 83 UID directories, all with six formal TeX files and `meta.json`. Twenty-three (`C001`–`C023`) have legacy PNGs (70 PNG total; C002 has four) and their educational-card structure/mathematical approval was **not** re-audited here. C043 and C051 have six programmatic PNGs and scoped freeze manifests. The remaining **58** (`C024`–`C083`, excluding C043/C051) have empty/no PNG `images/` and no programmatic static-card package. C001/C002 additionally have three GIFs. PNG existence alone is not evidence of three approved educational cards. No partially populated `03_conic` PNG set was found; beyond the two pilots, freeze status is unknown.

The current checked-in backend search index (`data/search_engine/backend_search_index.json`, generated 2026-08-29) lists **567** documents and 11 modules; it is older than C043's 2026-10-09 freeze, whose Publisher source discovery found **571** conclusions with no errors. The present all-module authoritative total and all-module image/card completeness are **UNKNOWN** without a fresh explicitly bounded inventory. The previously discussed “about 579” is not a verified total and is not used in estimates. The conic count 83 is a direct current inventory, while the 571 is a dated prior repository-discovery result.

| Inventory class within `03_conic` | UID count | Evidence level |
| --- | ---: | --- |
| Legacy PNG-bearing, educational structure unverified | 23 | MEASURED file inventory; acceptance UNKNOWN |
| Programmatic three-card pilots with scoped freeze | 2 | MEASURED hashes and freeze manifests |
| No static PNG | 58 | MEASURED file inventory; 174 PNG if three per UID |
| Total | 83 | MEASURED |

## 6. Benchmarks and cost baseline

Machine-readable observations: [TASK_13G_3_BENCHMARKS.json](TASK_13G_3_BENCHMARKS.json). Two isolated sequential full builds took **1.549 s** (C051) and **2.985 s** (C043). Six separate single-card commands took C051 **1.022/1.104/1.054 s** and C043 **1.083/2.600/1.117 s**; each command pays Python startup and full declared math/content validation. The C051/C043 model test subprocesses took **1.005/5.338 s**. One separately instrumented C043 002 draw spent **1.266 s** in label resolution/collision search and **0.324 s** in final visible-text coverage; these times are already part of that card's build, not extra work. These are one-sample warm-host wall times, not renderer-only timing or batch throughput. SVG export time was not separately instrumented. All six generated PNGs were SHA-256 identical to the formal frozen files. The 6 PNGs occupy **779,809 B**, the 6 SVGs **117,527 B**. The earlier isolated Publisher outputs total **375,862 B** of WebP, with no new Publisher conversion in this review. Preview contact sheets are 141,889 B and 156,605 B. Cache, memory peak, cold machine, concurrent load and failure/retry overhead were not measured.

Current verification: C051 model **8/8 PASS**, C043 model **7/7 PASS**. Initial in-sandbox shared-label/architecture suites had three Windows temporary-directory ACL cleanup errors; there were no reported failed mathematical assertions. The same unchanged test code and work tree then passed **20/20** outside the sandbox. No claim is made that the initial run passed. No PDF, Manim GIF, or formal resource was rebuilt.

There are no historical tracked time logs for **B. Codex development** or **C. human math/teaching/visual review**. Both are **UNKNOWN** as measured quantities. The pilots show several label-fix rounds; attributing exact hours or a percentage rework rate would be invented. For capacity sensitivity below only, assume **2–6 developer hours and 0.5–1.5 reviewer hours per new low/medium complexity UID**. These are **ESTIMATE planning inputs**, not observations or promises; complex conics, spatial geometry and probability visualizations may exceed them. The machine renderer's few seconds are unlikely to be the limiting resource under these assumptions.

### Complexity bands

| Band | Example work | Existing support and principal risk | Near-term priority |
| --- | --- | --- | --- |
| A | Formula, parameter correspondence, short worked example | Template/text support; mathematical conditions and line breaks still need review. | High after specification trial |
| B | Function graph or ordinary plane geometry | `MathFrame`, Matplotlib lines/points; curves, domains and labels need UID assertions and visual checks. | High pilot value |
| C | Conic, moving point, tangent, locus, extremum | Existing conic experience; degenerate cases, association and dense geometry raise review cost. | Selective |
| D | Probability, distributions, counting states | New bars/trees/state graphics and normalization/independence tests; current gate may need adapters. | Cross-module pilot |
| E | Solid geometry or spatial construction | Projection and hidden-edge semantics not exercised; two-dimensional renderer alone is insufficient evidence. | Pilot only, not early batch |

## 7. Batch scenarios and resources

For the *already-authored pilot-like shapes only*, use a loose **ESTIMATE 1.5–3.0 s/UID** full build interval based on the two observations. For storage, the two-pilot mean per UID is **389,905 B PNG + 58,764 B SVG + 187,931 B WebP ≈ 0.64 MB** in one copy of each format. Keeping isolated previews, contact sheets and duplicate formal PNGs adds about **0.54 MB/UID** on these samples; reports, logs, repeated builds and backups are extra/UNKNOWN. Real new UID sizes can differ greatly.

| Scenario | Cards at three/UID | Conditional machine render | ESTIMATE developer hours | ESTIMATE human review hours | Sample-based PNG+SVG+WebP |
| --- | ---: | ---: | ---: | ---: | ---: |
| 10 UIDs | 30 | 15–30 s | 20–60 h | 5–15 h | ~6.4 MB |
| 50 UIDs | 150 | 75–150 s | 100–300 h | 25–75 h | ~31.8 MB |
| 100 UIDs | 300 | 150–300 s | 200–600 h | 50–150 h | ~63.7 MB |
| 58 currently PNG-empty conic UIDs | 174 | 87–174 s | 116–348 h | 29–87 h | ~36.9 MB |

These scenarios are **not authorization to render or publish**. The 58-row case is only the current conic backlog; project-wide remaining UID count is UNKNOWN. Some UIDs may need fewer or more than three cards, especially if a single formula needs little graphical explanation or one result needs several distinct cases. The broad planning hours exclude new common primitive development, batch orchestration, Publisher work, and rework above the assumed band. Thus “300 PNG in minutes” must not be presented as “100 mathematical conclusions finished.”

## 8. Quality gates and batch readiness checklist

| Gate | What currently blocks an invalid build? | Gap before batch |
| --- | --- | --- |
| Mathematics | UID `validation_results()` rejects declared failed checks before rendering; C051/C043 suites passed. | No arbitrary-result proof, independent requirement checklist, or guaranteed domain/boundary coverage. **Human math approval required.** |
| Content | UID-specific source token checks run in builder. | Token presence does not prove three-card teaching content matches all formal conditions. **Human content approval required.** |
| Coverage | C043 002 `finalize()` rejects unregistered in-plot text. | Five other pilot cards and new unadopted cards are outside this full plot check. |
| Collision | C043 002 checks supported artist ink/path/point/text/bounds; targeted C051 assertions protect named prior failures. | Gate is opt-in, unsupported primitives and sampled-curve limitations remain. |
| Association | C043 002 anchor-distance/proximity rules and optional checked leader. | Heuristic cannot prove what a mathematical label denotes; other cards lack it. |
| Rendering | PNG decode/dimensions and card-edge text bounds checked; SVG produced. | Font/semantic legibility and page-scale visual judgment need human review. |
| Regression | Boundary tests and hashes were run; six formal hashes matched. | No automated frozen-UID matrix executed on every future build. |
| Publishing | Human-approved explicit copy, hashes and isolated Publisher conversion proven for two UIDs. | No batch approval ledger, fail isolation/resume or verified no-overwrite multi-UID release. Publisher maps all discovered PNG/GIF files, not a certified three-card set. |

**Batch readiness checklist:** require (1) scoped source and mathematics assertions for each UID; (2) explicit card-spec and reviewed example; (3) complete plot-text coverage or documented exemption; (4) collision and association tests including unsupported-artist inventory; (5) original-size and 360 px human visual review; (6) signed approval tied to source/PNG hashes; (7) isolated UID build/failure report and rerun policy; (8) no-overwrite publication procedure and Publisher mapping verification; (9) frozen UID hash regression; (10) recorded development/review/rework time. Present state satisfies parts of 1, 3–5, 8–9 for the two pilots only. A failed UID must be quarantined without publishing its products or altering a passed UID.

## 9. Cross-module pilot candidates

The dated search index supplied candidates; the following exact UID folders, formal six-part sources and `meta.json` were checked read-only. Their titles are from current `meta.json` core fields. These are proposed **future** tasks; no card was produced here.

| UID / formal title | Figure and new primitives | Verifiable mathematics, teaching risk, cost |
| --- | --- | --- |
| `L002` 等差数列前n项和公式 | Formula-to-parameter steps and a discrete term/partial-sum diagram; perhaps no new primitive beyond points and lines. | Check `S_n=n(a_1+a_n)/2`, indexing and example boundaries. Low/medium **ESTIMATE**; tests whether structured card spec lowers code work. |
| `F001` 导数判定单调性 | Function graph, derivative-sign interval chart, critical points; chart primitive and domain-aware axes. | Validate derivative sign by interval and strict/non-strict wording; avoid implying `f'=0` at isolated points rules out monotonicity. Medium **ESTIMATE**; tests graph semantics. |
| `R007` 二项分布概率公式 | Discrete probability bars or success/failure tree; bar/branch adapter for collision gate. | Test `0≤k≤n`, independence, `0<p<1`, formula and normalization; distinguish “恰好” from “至少”. Medium/high **ESTIMATE**; tests a non-geometric visual grammar. |
| `G001` 球体体积与表面积公式 | Sphere/section schematic and dimensional comparison; projection/occlusion support. | Verify `V=4πr³/3`, `S=4πr²`, units and scaling. High **ESTIMATE** because spatial meaning is not exercised; defer until first three types clarify interfaces. |

Two to three representative first pilots should span formula/discrete, function graph and probability; choosing another conic alone would add less evidence about generality.

## 10. Strategy comparison and recommended route

| Strategy | Accuracy/teaching | Development and throughput | Maintenance/reuse | Review and failure isolation |
| --- | --- | --- | --- | --- |
| A. Codex authors each UID | Best room for complex, precise mathematics when reviewed; current proven method. | Highest private source/test work; slowest to scale. | Common renderer reused, content remains private. | Clear UID boundary; every UID needs math/visual review. |
| B. Structured Card Specification plus templates | Strong for well-defined formula/graph families, but unproven across modules and can hide exceptional conditions. | Potentially faster only after spec, figure primitives and validators are built; premature abstraction cost high. | Highest potential reuse, also highest shared-system complexity. | Schema can expose decisions; generic validation cannot replace teaching review. |
| C. Layered hybrid | Simple types can use a validated spec; complex types retain private models and drawings. | Initial pilot/spec investment, then selective savings. | Moderate, controlled reuse with explicit escape hatch. | Per-UID isolation and common gates can be retained. |

**Recommend C**, implemented cautiously: keep A as the production method for complex results while piloting a small structured spec on genuinely simple cases. Do not commit to B as a universal engine from two conic examples. A alone leaves repeated low-complexity work; B alone lacks evidence of mathematical flexibility and quality gate coverage. Any extension must respect the current static/dynamic isolation contract; proposals to share models across those lines require separate user approval.

## 11. Phased route, decisions and next tasks

| Phase | Entry and output | Acceptance and stop condition | Advance? |
| --- | --- | --- | --- |
| 1. Cross-module pilot | Start from the two frozen conics. Implement 2–3 distinct future UIDs in individually authorized tasks; record model, spec, code and time. | Exact math, source agreement, full label/visual review, isolated hashes, no frozen regressions. Stop on unresolved mathematical error or unhandled graphic primitive. | Only after reviewed pilot evidence. |
| 2. Small trial batch | Once Phase 1 and approval ledger/coverage controls exist, propose **5–10** low/medium UIDs as separate authorized batch. | Measure true development/review/rework times, quarantine failures, verify hashes/Publisher mapping and repeatability. Stop if any unapproved publish, math error or cross-UID damage. | Conditional. |
| 3. Expanded batches | Only after a stable trial, plan **20–50** UIDs in waves. | Track quality escape rate, review burden, regression and storage; capacity budget and explicit publication approval each wave. Stop on systemic gate failure. | Conditional. |
| 4. Sustained production | Only after measured throughput and quality across modules. | Maintain per-UID evidence/version ledger and periodic gate audits. | Separate decision. |

Priority tasks: **P0** cross-module pilots and per-UID math/teaching acceptance record; **P0** opt-in coverage migration or equivalent check for every diagram; **P0** durable hash-linked review/publish ledger and failure isolation; **P1** small card specification for formula/discrete/graph families; **P1** batch runner with incremental skip, logs and resume; **P1** figure adapters and Publisher batch rehearsal; **P2** performance/cache tuning only after measured end-to-end cost. Each requires separate task authorization; none was implemented in this review.

Future metrics should be recorded by UID/card/build ID with `MEASURED` timestamps: authoring start/end, first render, math/content gate outcomes, visual findings, fix rounds, review minutes, approval/source/output hashes, formal publish result and rollback/failure reason, PNG/SVG/WebP sizes. Derive averages only after enough distinct modules are sampled. Current development hours, reviewer hours, issue detection rate, rework rate and publication success rate are **UNKNOWN**, not zero.

### GO / NO-GO

1. **Next controlled cross-module pilot: CONDITIONAL GO.** Conditions: exact UID scope and formal knowledge source, new model assertions, complete diagram coverage or documented exception, original-size human visual/mathematical approval, isolated build, frozen hash regression and explicit publish approval.
2. **Immediate large-scale production of remaining cards: NO-GO.** Only two programmatic conic UIDs have scoped freezes; content authoring, full visual coverage, approval ledger and batch failure recovery are incomplete. Architecture contract review is still pending. Rendering speed does not remove these quality and workflow gaps.

## 12. Direct answers to the decision questions

**Q1.** The project has reusable **single-UID rendering** for authored cards, not a complete unattended batch card-production line. **Q2.** A new UID currently needs its own three-card copy/specification, mathematical model, drawing code, content checks and mathematical tests; the pilots used 221 and 279 lines of UID model+card source respectively, which is evidence of scope, not a quota. **Q3.** Measured rendering is seconds; developer and human review time are unmeasured, but under the stated planning scenario they dominate. **Q4.** A structured Card Specification may reduce private code for simple families; significant savings are unproven and need a cross-module trial. **Q5.** Strengthen complete visual coverage/association, source-linked mathematical/content specification, and hash-linked approval plus batch isolation. **Q6.** First run cross-module pilots, then consider more conics in a controlled batch. **Q7.** Next recommended production scale is **2–3 individually reviewed cross-module pilots**, followed only conditionally by a **5–10 UID** trial; no immediate 50/100-UID run.

## 13. Files changed and final status

Only this review and its small machine-readable benchmark file were added under `scripts/static_cards/`. Benchmark previews were written only under ignored `.build/static_cards/13g3/`; formal PNG/GIF/PDF, six-part TeX, metadata, Manim, Publisher and app files were untouched. The benchmark's first wrapper stopped after C051 because Python decoded C043's Chinese console output as UTF-8 on a GBK terminal; C043 was rerun with the correct console encoding, and its three outputs matched formal hashes. This measurement-script error did not indicate a build failure.

**TASK 13G.3 — STAGE REVIEW COMPLETE.** The project-wide knowledge total and end-to-end human cost remain explicitly UNKNOWN; those limits are reflected in the conditional decision.
