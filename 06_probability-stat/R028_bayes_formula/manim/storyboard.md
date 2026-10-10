# R028 independent storyboard — medical screening

Source: frozen `04_examples.tex`, example 1. The earlier source audit and source freeze remain authoritative. Example 2 has three production branches and explains machine attribution; example 3 has two coin branches but no medical screening. Example 1 directly supports the requested change of condition space. Its finite decimals admit exact theoretical counts for 100,000 people: 100 with disease, 99,900 without, 99 true positives, 999 false positives, 1,098 positives in total. These are counts in a stipulated population model, not a random sample.

The two source rows are **symbolic group containers of equal screen width**, with explicit group counts. Each row's colored segment uses its *own group's* denominator: 99/100 and 999/99,900. They must not be interpreted as equally sized population masses. At the merge the animation explicitly changes scale and denominator. The new positive pool is a true proportional bar: widths 99/1098 and 999/1098. The displayed fraction 99/1098 and `P(D|+)=P(D∩+)/P(+)` name the numerator and denominator. Orange denotes true positives throughout; purple denotes false positives. Gray denotes other test outcomes.

1. **All people.** Ask the posterior question; show the exact stipulated population of 100,000.
2. **Prior partition.** Split the total into 100 with disease and 99,900 without. Show 0.1% prevalence. The rows are clearly labelled as symbolic group containers.
3. **First conditional filter.** On the diseased row, retain 99% in orange, show 99/100 true positives; the remaining 1% dims.
4. **Second conditional filter.** On the healthy row, retain 1% in purple, show 999/99,900 false positives; its small area has a pointer so it stays identifiable.
5. **Change the population studied.** Count badges 99 and 999 move into the new positive pool. The old population fades, the new bar appears, and 99 + 999 = 1,098 becomes the denominator.
6. **Read the positive pool.** In the new true-scale bar, orange is 99/1098 and purple 999/1098. A highlight frames the orange numerator within the complete bar denominator.
7. **Connect to Bayes.** Show `P(D|+)=P(D∩+)/P(+) = 99/1098 ≈ 9.02%`. End with “已知阳性，就在阳性人群中重新计算”. Hold, then loop.

Recommended staging: 576×1024, Manim 24 FPS MP4, shared FFmpeg exporter 12 FPS GIF. The 1% source strip is mathematically narrow; the pointer and count label explain it without widening its shape. Numerical group counts and branch rates remain visible while filtering. Key states and holds are defined by the scene's `MARKS` timing table for reproducible frame extraction.
