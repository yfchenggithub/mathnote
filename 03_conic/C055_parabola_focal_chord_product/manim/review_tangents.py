"""Decode all GIF frames, inspect safe margins/footer, export actual key frames."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageStat

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "manim"))
from verify_gif import verify_gif


def review(path: Path, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    technology = verify_gif(path, width=576, height=1024)
    targets = [0, 2, 4, 5.6, 7.5, 9.5, 12, 14, 15.7]
    saved = []
    footer_counts = []
    edge_counts = []
    footer_differences = []
    first = None
    elapsed = 0
    with Image.open(path) as gif:
        for index in range(gif.n_frames):
            gif.seek(index)
            frame = gif.convert("RGB")
            duration = gif.info["duration"] / 1000
            if first is None:
                first = frame.copy()
            pixels = np.asarray(frame).astype(np.int16)
            background = pixels[0, 0]
            foreground = np.max(np.abs(pixels - background), axis=2) > 55
            footer_counts.append(int(foreground[925:1008, 20:556].sum()))
            edge_counts.append(int(
                foreground[:12].sum() + foreground[-12:].sum()
                + foreground[:, :12].sum() + foreground[:, -12:].sum()
            ))
            footer_diff = ImageChops.difference(
                first.crop((20, 925, 556, 1008)), frame.crop((20, 925, 556, 1008))
            )
            footer_differences.append(max(ImageStat.Stat(footer_diff).mean))
            for target in targets:
                if elapsed <= target < elapsed + duration:
                    filename = f"key_{target:04.1f}s.png"
                    frame.save(output / filename)
                    saved.append((target, frame.copy(), filename, index))
            elapsed += duration
        last = frame
    loop_difference = max(ImageStat.Stat(ImageChops.difference(first, last)).mean)
    result = {
        "technology": technology,
        "minimum_footer_foreground_pixels": min(footer_counts),
        "maximum_footer_mean_difference": round(max(footer_differences), 4),
        "maximum_foreground_pixels_in_12px_edge": max(edge_counts),
        "first_last_mean_difference": round(loop_difference, 4),
        "key_frames": [dict(time=t, file=f, frame=i) for t, _, f, i in saved],
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }
    assert min(footer_counts) > 1000, "Footer disappeared during animation"
    assert max(footer_differences) < 1.5, "Footer changed during animation"
    assert max(edge_counts) == 0, "Content reached the 12px canvas edge"
    assert loop_difference < 0.5, "Opening and ending states disagree"
    assert len(saved) == len(targets), "Missing a requested real key frame"
    contact = Image.new("RGB", (900, 1662), "#e2e5e8")
    draw = ImageDraw.Draw(contact)
    for j, (time, frame, _, _) in enumerate(saved):
        frame.thumbnail((288, 512))
        x, y = j % 3 * 300 + 6, j // 3 * 554 + 26
        contact.paste(frame, (x, y))
        draw.text((x, y - 20), f"{time:.1f}s", fill="#213044")
    contact.save(output / "key_frames.png")
    (output / "frame_review.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gif", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    review(args.gif, args.output)
