# Manim production contract (Task 13F)

The six TeX sections and `meta.json` in each conclusion are the mathematical
source of truth. Keep its model, tests, storyboard, and `scene*.py` under that
conclusion's `manim/`. Shared tools here locate sources, render, export, and
check files; they contain no UID-specific mathematics. Published GIFs belong in
that conclusion's `images/`. Temporary output belongs under `build/manim/`.
Publisher discovers direct GIFs in `images/`, validates animation timing and
infinite loop, and copies them byte-for-byte; PNGs become WebP separately.

Visual guidance for new and refined GIFs is in
[VISUAL_GUIDELINES.md](VISUAL_GUIDELINES.md). It is a v1.0 candidate pending
validation across knowledge types and on Android devices.

## Environment

On Windows, install Python 3.14, FFmpeg, TeX Live (`latex` and `dvisvgm`), and
Microsoft YaHei. The verified environment used Python 3.14.3, Manim Community
0.21.0, Pillow 12.3.0, TeX Live 2025 and the installed FFmpeg. Preserve these
working versions unless a real compatibility issue calls for change.

```powershell
python -m venv .venv-manim
.\.venv-manim\Scripts\python.exe -m pip install -r .\scripts\manim\requirements.txt
.\scripts\manim\check_env.ps1
```

If a reused virtual environment lacks `pip`, run its Python with
`-m ensurepip` before the install command. The currently verified environment
renders successfully; package installation is only needed when setting up or
repairing an environment.

The scripts resolve the repository from their own location, so the caller's
working directory can differ. A failed tool exits nonzero and prints the cause.

## New conclusion workflow

Read its formal TeX, pick one mathematical relationship with teaching value,
and build an independent model and storyboard in its own `manim/`. Test the
geometry, constraints, formulas, extreme cases, and displayed numbers there.
Use a separate scene for each GIF. The shared tools recognize direct `Scene`,
`MovingCameraScene`, `ThreeDScene`, or `ZoomedScene` subclasses in `scene*.py`.
If there is more than one, specify the exact class (and file if needed).

```powershell
# C001 minimum; all outputs stay in isolated build/manim/freeze-validation/
.\scripts\manim\render.ps1 -Uid C001 -Scene C001DistancePilot -SceneFile scene.py -Name min_distance -BuildRoot build/manim/freeze-validation
.\scripts\manim\export_gif.ps1 -Uid C001 -Scene C001DistancePilot -SceneFile scene.py -Name min_distance -BuildRoot build/manim/freeze-validation

# C001 maximum; a second scene and a separate output name
.\scripts\manim\render.ps1 -Uid C001 -Scene C001MaxDistance -Name max_distance -BuildRoot build/manim/freeze-validation

# C002 has one discoverable scene
.\scripts\manim\render.ps1 -Uid C002 -Name primary -BuildRoot build/manim/freeze-validation
.\scripts\manim\export_gif.ps1 -Uid C002 -Name primary -BuildRoot build/manim/freeze-validation
```

`render.ps1` produces `<BuildRoot>/<UID>/<Name>/<Name>.mp4`.
`export_gif.ps1` uses that MP4 and writes a verified staging GIF next to it.
`-Rebuild` renders again before exporting. The output name is bound to its UID,
source file, and scene in `source.json`; a different scene cannot reuse it.
`-BuildRoot` must remain inside this repository's `build/manim/`.

To place a reviewed GIF in the formal `images/`, pass `-Publish -AssetName
chosen_name.gif`. An existing formal GIF is rejected unless `-Overwrite` is
explicit. Never use `-Overwrite` for regression tests or frozen C001/C002
assets. The exporter stages and verifies before atomic replacement. The
technical checker can also be run directly:

```powershell
.\.venv-manim\Scripts\python.exe -B .\scripts\manim\verify_gif.py build/manim/freeze-validation/C002/primary/primary.gif
```

It returns JSON with dimensions, frame count, distinct frames, timing, loop,
blank frames, and byte size. Technical validation cannot prove mathematics or
visual clarity. Inspect key frames on desktop and test on a real phone before
accepting an animation. In particular, C002 phone acceptance remains separate
from this infrastructure freeze. Publisher and Sync are separate release steps.

## Troubleshooting

- `check_env.ps1` identifies missing Python packages, FFmpeg, TeX, or font.
- An ambiguous Scene error requires `-Scene` (and sometimes `-SceneFile`).
- A missing MP4 requires `render.ps1` or export with `-Rebuild`.
- Failed FFmpeg or GIF validation leaves the formal asset untouched.
- A duplicate asset name needs a new name or explicit, reviewed overwrite.
- If a label clips or a displayed value disagrees with the model, fix that
  UID's scene or model after reviewing its formal mathematics; the shared
  tools do not repair mathematical content.
