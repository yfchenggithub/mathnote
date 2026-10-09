"""Decode the final F031 GIF, make a real-frame contact sheet and QA metrics."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat
import numpy as np

from math_model import QuadraticSpec, analytic_state


KEY_TIMES = [
    (0.3, "opening_left_outside"),
    (2.45, "at_L"),
    (3.8, "inside_left_half"),
    (5.7, "at_midpoint_tie"),
    (7.4, "inside_right_half"),
    (9.1, "at_R"),
    (10.3, "right_outside"),
    (13.7, "downward_midpoint"),
    (15.4, "loop_return"),
]


def expected_spec(seconds: float) -> QuadraticSpec | None:
    """Timeline independently reconstructed from the scene's stated segments."""
    # GIF timestamps mark the start of a 12 FPS frame; the last interpolation
    # sample can already be the exact midpoint before its nominal end time.
    if 5.02 <= seconds < 5.10:
        return None
    if seconds < .65:
        h = -2.8
    elif seconds < 2.10:
        h = -2.8 + .8 * (seconds - .65) / 1.45
    elif seconds < 2.75:
        h = -2
    elif seconds < 5.10:
        h = -2 + 2 * (seconds - 2.75) / 2.35
    elif seconds < 6.39:
        h = 0
    elif seconds < 8.74:
        h = 2 * (seconds - 6.39) / 2.35
    elif seconds < 9.39:
        h = 2
    elif seconds < 10.64:
        h = 2 + .8 * (seconds - 9.39) / 1.25
    elif seconds < 10.99:
        h = 2.8
    elif seconds < 12.24:
        h = 2.8 * (1 - (seconds - 10.99) / 1.25)
    elif seconds < 12.59:
        return None
    elif seconds < 14.39:
        return QuadraticSpec(-2, 2, -.25, 0, 3)
    elif seconds < 15.29:
        return None
    else:
        h = -2.8
    return QuadraticSpec(-2, 2, .25, h)


def colored_dot_centers(frame: Image.Image, kind: str) -> list[tuple[float, float]]:
    """Locate the colored point markers in the graph, excluding lower captions."""
    rgb = np.asarray(frame)[200:620, 40:536, :3]
    if kind == "green":
        mask = (rgb[:, :, 1] > 100) & (rgb[:, :, 0] < 95) & (rgb[:, :, 2] < 165)
    else:
        mask = (rgb[:, :, 0] > 160) & (rgb[:, :, 1] < 175) & (rgb[:, :, 2] < 135)
    columns = np.flatnonzero(mask.sum(axis=0) >= 2)
    if not len(columns):
        return []
    splits = np.split(columns, np.flatnonzero(np.diff(columns) > 1) + 1)
    centers = []
    for run in splits:
        if len(run) < 4:
            continue
        ys, xs = np.nonzero(mask[:, run[0]:run[-1] + 1])
        if len(xs) < 30:
            continue
        centers.append((float(xs.mean() + run[0] + 40),
                        float(ys.mean() + 200)))
    return centers


def point_pixel(spec: QuadraticSpec, x: float) -> tuple[float, float]:
    # Axes dimensions and location in scene.py: 7.30×6.15 in a 9×16 frame.
    px = 288 + x * (7.30 / 6.6) * 64
    py = (8 - (1.50 + (spec.value(x) - 2.775) * 6.15 / 6.85)) * 64
    return px, py


def review(gif_path: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    frame_dir = output_dir / "key_frames"
    frame_dir.mkdir(exist_ok=True)
    with Image.open(gif_path) as gif:
        frames = []
        durations = []
        for index in range(gif.n_frames):
            gif.seek(index)
            frames.append(gif.convert("RGB").copy())
            durations.append(gif.info.get("duration", 0))
        loop = gif.info.get("loop")
    if not frames or any(frame.size != (576, 1024) for frame in frames):
        raise ValueError("incorrect or missing frames")
    if any(duration <= 0 for duration in durations):
        raise ValueError("nonpositive frame duration")
    cumulative = []
    running = 0
    for duration in durations:
        cumulative.append(running)
        running += duration
    hashes = [hashlib.sha256(frame.tobytes()).hexdigest() for frame in frames]
    means = [ImageStat.Stat(frame.resize((24, 42))).mean for frame in frames]
    black_frames = [
        i for i, mean in enumerate(means) if max(mean) < 8
    ]
    changed = []
    for i in range(1, len(frames)):
        box = ImageChops.difference(
            frames[i].resize((144, 256)),
            frames[i - 1].resize((144, 256)),
        ).getbbox()
        if box:
            changed.append(i)
    math_failures = []
    math_frames_checked = 0
    for index, frame in enumerate(frames):
        seconds = cumulative[index] / 1000
        spec = expected_spec(seconds)
        if spec is None:
            continue
        state = analytic_state(spec)
        for kind, points in (
            ("green", state.minimum_points),
            ("orange", state.maximum_points),
        ):
            found = colored_dot_centers(frame, kind)
            expected = [point_pixel(spec, x) for x in points]
            if len(found) != len(expected):
                math_failures.append(
                    {"frame": index, "time": seconds, "color": kind,
                     "found": found, "expected": expected}
                )
                continue
            for (fx, fy), (ex, ey) in zip(found, expected):
                if abs(fx - ex) > 12 or abs(fy - ey) > 12:
                    math_failures.append(
                        {"frame": index, "time": seconds, "color": kind,
                         "found": found, "expected": expected}
                    )
        math_frames_checked += 1
    # Every selected panel is taken from the decoded final GIF, never rerendered.
    choices = []
    for seconds, name in KEY_TIMES:
        target_ms = seconds * 1000
        idx = min(range(len(frames)), key=lambda j: abs(cumulative[j] - target_ms))
        out = frame_dir / f"{idx:03d}_{name}.png"
        frames[idx].save(out)
        choices.append((idx, cumulative[idx] / 1000, name, out))
    cell_w, cell_h = 288, 538
    sheet = Image.new("RGB", (cell_w * 3, cell_h * 3), "#E8EEF3")
    draw = ImageDraw.Draw(sheet)
    font_path = Path("C:/Windows/Fonts/msyh.ttc")
    font = ImageFont.truetype(str(font_path), 17) if font_path.exists() else ImageFont.load_default()
    for k, (index, seconds, name, _) in enumerate(choices):
        col, row = k % 3, k // 3
        thumb = frames[index].resize((288, 512), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (col * cell_w, row * cell_h))
        draw.text((col * cell_w + 6, row * cell_h + 514),
                  f"{name}  {seconds:.2f}s", fill="#183047", font=font)
    contact = output_dir / "F031_14B_contact_sheet.png"
    sheet.save(contact)
    report = {
        "source_gif": str(gif_path.resolve()),
        "contact_sheet": str(contact.resolve()),
        "width": 576,
        "height": 1024,
        "frame_count": len(frames),
        "distinct_frames": len(set(hashes)),
        "changed_adjacent_frames": len(changed),
        "first_last_mean_abs_rgb": round(float(np.abs(
            np.asarray(frames[0], dtype=np.int16) -
            np.asarray(frames[-1], dtype=np.int16)
        ).mean()), 3),
        "duration_seconds": round(running / 1000, 3),
        "loop": loop,
        "black_frames": black_frames,
        "math_frames_checked": math_frames_checked,
        "math_marker_failures": math_failures,
        "key_frames": [
            {"index": index, "time_seconds": seconds, "state": name, "file": str(out.resolve())}
            for index, seconds, name, out in choices
        ],
    }
    (output_dir / "F031_14B_visual_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if math_failures:
        raise ValueError(f"{len(math_failures)} GIF graph markers disagree with the mathematical model")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("gif", type=Path)
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()
    print(json.dumps(review(arguments.gif, arguments.output), ensure_ascii=False, indent=2))
