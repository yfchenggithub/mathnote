# Static card preview builder

The shared code owns layout, exact coordinate mapping, PNG/SVG export, source
hashes, and build reports. Each UID owns its own mathematical model, content
checks, card specifications, and drawings. No animation code is imported.

From the repository root:

```powershell
python -m scripts.static_cards.build --uid C051 --source-dir 03_conic/C051_parabola_focal_radius_coordinate
python -m scripts.static_cards.build --uid C051 --source-dir 03_conic/C051_parabola_focal_radius_coordinate --card 002
python -m scripts.static_cards.build --uid C051 --source-dir 03_conic/C051_parabola_focal_radius_coordinate --validate-only
python -m unittest discover -s 03_conic/C051_parabola_focal_radius_coordinate/static_cards -p test_model.py
python -m scripts.static_cards.build --uid C043 --source-dir 03_conic/C043_hyperbola_abc_relation
python -m scripts.static_cards.build --uid C043 --source-dir 03_conic/C043_hyperbola_abc_relation --card 002
python -m scripts.static_cards.build --uid C043 --source-dir 03_conic/C043_hyperbola_abc_relation --validate-only
python -m unittest discover -s 03_conic/C043_hyperbola_abc_relation/static_cards -p test_model.py
```

Output is restricted to `.build/static_cards/<UID>/`. Repeated builds with
identical output succeed. A changed preview requires `--replace-preview`.
This command never writes formal `images/` or calls the GIF builder. PNGs are
1080×1440; SVGs are kept as vector intermediates. `contact_sheet.png` appears
when all three cards are built. `build_report.json` records source/output hashes,
tool versions, checks, and review status. Human visual review remains required.
UID card modules can supply `REVIEW_STATUS` and `TERMINOLOGY_REVIEW` for the
build report; older modules retain the original report values.

Dependencies: Python, Matplotlib, Pillow. Chinese typography uses the local
Noto Sans SC font when available and Microsoft YaHei as a fallback.
