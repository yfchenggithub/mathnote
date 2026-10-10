"""Extract actual GIF frames for R028's mathematical and visual review."""

from pathlib import Path
import json
import sys

from PIL import Image, ImageDraw, ImageFont


MARKS = [
    ("00_loop_start", 0.0),
    ("01_all", 1.3),
    ("02_partition", 3.5),
    ("03_d_before", 4.3),
    ("04_d_after", 6.0),
    ("05_h_before", 6.6),
    ("06_h_after", 8.2),
    ("07_positives_ready", 9.0),
    ("08_merging", 10.0),
    ("09_new_population", 12.9),
    ("10_numerator", 14.4),
    ("11_fraction", 16.2),
    ("12_result", 17.9),
    ("13_loop_end", 20.0),
]


def main():
    source = Path(sys.argv[1])
    output = Path(sys.argv[2])
    output.mkdir(parents=True, exist_ok=True)
    frames = []
    with Image.open(source) as gif:
        t = 0.0
        for index in range(gif.n_frames):
            gif.seek(index)
            frame = gif.convert("RGB")
            frames.append((t, frame.copy(), index))
            t += gif.info.get("duration", 0) / 1000
    chosen = []
    for name, target in MARKS:
        stamp, image, index = min(frames, key=lambda entry: abs(entry[0] - target))
        image.save(output / f"{name}.png")
        chosen.append((name, stamp, index, image))
    tile_w, tile_h = 288, 536
    sheet = Image.new("RGB", (tile_w * 4, tile_h * 4), "#E8ECF0")
    draw = ImageDraw.Draw(sheet)
    for slot, (name, stamp, index, frame) in enumerate(chosen):
        x, y = (slot % 4) * tile_w, (slot // 4) * tile_h
        sheet.paste(frame.resize((288, 512)), (x, y))
        draw.text((x + 7, y + 515), f"{name}  {stamp:.2f}s  f{index}", fill="#213044")
    sheet.save(output / "contact_sheet.png")
    foreground_counts = []
    edge_counts = []
    for _, frame, _ in frames:
        small = frame.resize((144, 256))
        pixels = list(small.get_flattened_data())
        foreground_counts.append(sum(min(rgb) < 180 for rgb in pixels))
        edge_counts.append(sum(
            min(rgb) < 180 for i, rgb in enumerate(pixels)
            if i // 144 < 3 or i // 144 >= 253 or i % 144 < 3 or i % 144 >= 141
        ))
    metrics = {
        "frame_count": len(frames),
        "empty_light_frames": sum(count == 0 for count in foreground_counts),
        "minimum_foreground_pixels_at_144x256": min(foreground_counts),
        "maximum_dark_edge_pixels_at_144x256": max(edge_counts),
        "keyframes": [{"name": name, "seconds": round(stamp, 2), "frame": index}
                      for name, stamp, index, _ in chosen],
    }
    (output / "qa_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, stamp, index, _ in chosen:
        print(f"{name}: {stamp:.2f}s frame={index}")
    print(f"contact_sheet: {output / 'contact_sheet.png'}")
    print(json.dumps({key: value for key, value in metrics.items() if key != "keyframes"}))


if __name__ == "__main__":
    main()
