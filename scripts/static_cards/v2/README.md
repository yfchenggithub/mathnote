# Static card V2 visual language

This is an isolated C043 design experiment. Run `python -m scripts.static_cards.v2.build` as documented in the task report. It reads the C043 formal TeX and the existing C043 mathematical model, then writes only `.build/static_cards_v2/C043/`. It does not modify the V1 builder or the published images.

The token source is `theme.py`: warm white paper, deep slate text, blue `a`, teal `b`, amber `c`, 76 px safe margin, seven type roles and five line roles. Colors identify mathematical objects, not decoration. `components.py` contains a shared frame, header, footer, copy helpers and renderer measured text overlap audit. C043 owns its diagram and content in its private `static_cards_v2/` package.

The three compositions deliberately differ. 001 places the relation first, then a compact exact auxiliary triangle and parameter definitions. 002 reserves the largest region for exact hyperbola geometry; source linked labels use `LabelLayout`. 003 is a quiet vertical calculation flow ending in a result. At 390/360 px width the scale factors are 0.361/0.333; the smallest teaching text is 24 original pixels (8/8.7 displayed pixels), so mobile inspection remains a human review requirement. Supporting labels and the brand footer can be smaller than primary teaching copy.

For other UIDs, reuse tokens, frame, text roles and line roles. Formula wrapping, diagram scale, explanatory copy and any new primitives require UID specific design and checks. The current three samples do not establish a universal layout engine.
