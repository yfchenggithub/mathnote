"""Inspect every decoded C002 GIF frame and save actual-frame review artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

from PIL import Image, ImageChops, ImageDraw, ImageStat


ROOT = Path(__file__).resolve().parents[3]
GIF = Path(__file__).resolve().parent.parent / "images/ellipse_line_distance.gif"
OUT = ROOT / "build/manim/C002"
OUT.mkdir(parents=True, exist_ok=True)

with Image.open(GIF) as gif:
    frames = []
    durations = []
    for i in range(gif.n_frames):
        gif.seek(i)
        frames.append(gif.convert("RGB").copy())
        durations.append(gif.info.get("duration", 0))
    loop = gif.info.get("loop")

width, height = frames[0].size
bg = frames[0].getpixel((0, 0))
edge_insets = []
changes = []
black_fraction = []
for i, frame in enumerate(frames):
    # GIF palette dithering makes nominally solid background pixels differ by
    # one or two channels. Ignore differences below 12 before measuring bounds.
    difference = ImageChops.difference(frame, Image.new("RGB", frame.size, bg))
    content_box = difference.convert("L").point(lambda value: 255 if value > 12 else 0).getbbox()
    if content_box is None:
        raise ValueError(f"empty frame {i}")
    edge_insets.append([content_box[0], content_box[1], width-content_box[2], height-content_box[3]])
    black_fraction.append(sum(1 for r,g,b in frame.resize((72,128)).get_flattened_data()
                              if max(r,g,b) < 25) / (72*128))
    if i:
        changes.append(mean(ImageStat.Stat(ImageChops.difference(frame, frames[i-1])).mean))

timestamps = [0, 1.9, 3.85, 4.6, 6.1, 7.65, 9.4, 11.4, sum(durations)/1000-.1]
indices = []
for sec in timestamps:
    elapsed = 0
    for i, duration in enumerate(durations):
        elapsed += duration / 1000
        if elapsed >= sec:
            indices.append(i)
            break

thumb_w, thumb_h = 288, 512
sheet = Image.new("RGB", (3*thumb_w, 3*(thumb_h+25)), "#e8edf2")
draw = ImageDraw.Draw(sheet)
for pos, i in enumerate(indices):
    thumb = frames[i].resize((thumb_w,thumb_h), Image.Resampling.LANCZOS)
    x, y = (pos % 3)*thumb_w, (pos // 3)*(thumb_h+25)
    sheet.paste(thumb, (x,y))
    draw.text((x+8,y+thumb_h+4), f"t={sum(durations[:i])/1000:.2f}s / frame {i}", fill="#183047")
sheet.save(OUT / "C002_13E_contact_sheet.png")
for label, i in (("opening",indices[0]), ("tangent",indices[2]),
                 ("intersection",indices[4]), ("ending",indices[-1])):
    frames[i].save(OUT / f"C002_13E_{label}.png")

report = {
    "source": str(GIF.relative_to(ROOT)).replace("\\", "/"),
    "frame_count": len(frames), "size": [width,height],
    "duration_seconds": round(sum(durations)/1000,3), "loop": loop,
    "frame_duration_ms": sorted(set(durations)),
    "minimum_edge_insets_px": [min(x[k] for x in edge_insets) for k in range(4)],
    "maximum_black_fraction": max(black_fraction),
    "adjacent_change_mean_range": [min(changes), max(changes)],
    "sampled_frame_indices": indices,
    "first_last_change_mean": mean(ImageStat.Stat(ImageChops.difference(frames[0], frames[-1])).mean),
    "checks": {
        "all_frames_decoded": True,
        "nonempty_frames": True,
        "no_black_frame": max(black_fraction) < 0.05,
        "content_inside_frame": all(min(inset)>0 for inset in edge_insets),
        "continuous_motion": sum(v > .03 for v in changes) > 80,
    },
}
(OUT / "C002_13E_visual_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
