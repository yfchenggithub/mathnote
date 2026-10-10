"""Retain decoded R028 polish keyframes and direct before/after comparisons."""

import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw


MARKS = [
    ("00_loop_start", 0.00),
    ("01_all", 1.33),
    ("02_partition", 3.50),
    ("03_d_before", 4.33),
    ("04_d_after", 6.00),
    ("05_h_before", 6.58),
    ("06_h_after", 8.17),
    ("07_ready", 9.00),
    ("08_move_start", 9.75),
    ("09_move_mid", 10.25),
    ("10_move_arrive", 10.85),
    ("11_sum", 11.67),
    ("12_new_population", 12.67),
    ("13_bar_expanding", 13.42),
    ("14_bar_complete", 14.42),
    ("15_numerator", 15.83),
    ("16_formula", 18.08),
    ("17_result", 19.25),
    ("18_loop_end", 21.42),
]

TRANSITION = ["07_ready", "08_move_start", "09_move_mid", "10_move_arrive",
              "11_sum", "12_new_population", "13_bar_expanding", "14_bar_complete"]

COMPARISONS = [
    ("group_filter", 8.17, 8.17),
    ("transition_start", 9.00, 9.75),
    ("transition_middle", 10.00, 10.25),
    ("merge_sum", 11.10, 11.67),
    ("final_bar", 12.92, 14.42),
    ("numerator", 14.42, 15.83),
    ("posterior_formula", 17.92, 19.25),
]


def decode(path):
    frames = []
    with Image.open(path) as gif:
        t = 0.0
        for index in range(gif.n_frames):
            gif.seek(index)
            frames.append((t, gif.convert("RGB").copy(), index))
            t += gif.info.get("duration", 0) / 1000
    return frames


def closest(frames, time):
    return min(frames, key=lambda frame: abs(frame[0] - time))


def contact(items, path, columns=4):
    tile_w, tile_h = 288, 536
    rows = (len(items) + columns - 1) // columns
    sheet = Image.new("RGB", (tile_w * columns, tile_h * rows), "#E8ECF0")
    draw = ImageDraw.Draw(sheet)
    for slot, (name, stamp, frame) in enumerate(items):
        x, y = slot % columns * tile_w, slot // columns * tile_h
        sheet.paste(frame.resize((288, 512)), (x, y))
        draw.text((x + 6, y + 515), f"{name} {stamp:.2f}s", fill="#213044")
    sheet.save(path)


def main():
    old_path, new_path, output = map(Path, sys.argv[1:4])
    output.mkdir(parents=True, exist_ok=True)
    old_frames, new_frames = decode(old_path), decode(new_path)
    chosen = []
    entries = []
    for name, time in MARKS:
        stamp, frame, index = closest(new_frames, time)
        frame.save(output / f"{name}.png")
        chosen.append((name, stamp, frame))
        entries.append({"name": name, "seconds": round(stamp, 2), "frame": index})
    contact(chosen, output / "keyframes_contact.png")
    contact([item for item in chosen if item[0] in TRANSITION],
            output / "positive_population_transition_contact.png")
    contact([(f"f{index}", stamp, frame) for stamp, frame, index in new_frames
             if 9.60 <= stamp <= 10.95],
            output / "transition_every_motion_frame.png")
    comparison = []
    for name, old_time, new_time in COMPARISONS:
        old_stamp, old_frame, _ = closest(old_frames, old_time)
        new_stamp, new_frame, _ = closest(new_frames, new_time)
        pair = Image.new("RGB", (576 * 2, 1024 + 34), "#E8ECF0")
        pair.paste(old_frame, (0, 0))
        pair.paste(new_frame, (576, 0))
        draw = ImageDraw.Draw(pair)
        draw.text((12, 1028), f"BEFORE {old_stamp:.2f}s", fill="#213044")
        draw.text((588, 1028), f"AFTER {new_stamp:.2f}s", fill="#213044")
        pair.save(output / f"compare_{name}.png")
        comparison.extend([(f"{name} old", old_stamp, old_frame),
                           (f"{name} new", new_stamp, new_frame)])
    contact(comparison, output / "before_after_contact.png", columns=2)
    foreground = []
    edge = []
    for _, frame, _ in new_frames:
        small = frame.resize((144, 256))
        pixels = list(small.get_flattened_data())
        foreground.append(sum(min(rgb) < 180 for rgb in pixels))
        edge.append(sum(min(rgb) < 180 for i, rgb in enumerate(pixels)
                        if i // 144 < 3 or i // 144 >= 253
                        or i % 144 < 3 or i % 144 >= 141))
    metrics = {
        "frame_count": len(new_frames),
        "empty_light_frames": sum(value == 0 for value in foreground),
        "minimum_foreground_pixels_at_144x256": min(foreground),
        "maximum_dark_edge_pixels_at_144x256": max(edge),
        "keyframes": entries,
    }
    (output / "qa_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n",
                                             encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
