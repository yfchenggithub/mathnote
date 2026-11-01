"""Audit actual decoded C093 GIF frames and retain real key-frame evidence.

Run after the frozen exporter/verify_gif.py; this adds content, margin,
always-visible footer, loop seam, and protected-source checks.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageStat

from c093_model import KEY_TIMES


def audit(gif_path, output):
    output.mkdir(parents=True, exist_ok=True)
    keyframes = output / "keyframes"
    keyframes.mkdir(exist_ok=True)
    frames = []
    footer_hashes = set()
    footer_reference = None
    footer_reference_mask = None
    footer_max_mae = 0.0
    min_margins = [10**6]*4
    elapsed = 0.0
    with Image.open(gif_path) as gif:
        assert gif.size == (576, 1024)
        for i in range(gif.n_frames):
            gif.seek(i)
            rgb = gif.convert("RGB")
            duration = gif.info["duration"] / 1000
            footer = rgb.crop((0, 940, 576, 1024))
            footer_hashes.add(hashlib.sha256(footer.tobytes()).hexdigest())
            footer_mask = footer.convert("L").point(lambda x: 255 if x < 170 else 0)
            if footer_reference is None:
                footer_reference = footer
                footer_reference_mask = footer_mask
            # H.264 chroma and GIF palette quantization change antialias pixels
            # even in static content. Check glyph shape in both directions,
            # permitting only one pixel of antialias edge variation.
            missing = ImageChops.subtract(footer_reference_mask, footer_mask.filter(ImageFilter.MaxFilter(3)))
            added = ImageChops.subtract(footer_mask, footer_reference_mask.filter(ImageFilter.MaxFilter(3)))
            assert missing.getbbox() is None and added.getbbox() is None, f"Footer glyph structure changed at frame {i}"
            footer_mae = sum(ImageStat.Stat(ImageChops.difference(footer_reference, footer)).mean)/3
            footer_max_mae = max(footer_max_mae, footer_mae)
            assert footer_mae < 2, f"Footer contrast changed at frame {i}"
            # Ignore mild palette dithering, but include text, axes, curves,
            # and footer in the content bounds.
            background = Image.new("RGB", rgb.size, (247, 248, 250))
            mask = ImageChops.difference(rgb, background).convert("L").point(lambda x: 255 if x > 35 else 0)
            bounds = mask.getbbox()
            assert bounds is not None, f"Blank frame {i}"
            x0, y0, x1, y1 = bounds
            margins = (x0, y0, 576-x1, 1024-y1)
            min_margins = [min(a, b) for a, b in zip(min_margins, margins)]
            assert min(margins) >= 18, f"Content too close to canvas edge: frame {i}, {margins}"
            core = mask.crop((35, 190, 541, 915))
            assert core.histogram()[255] > 1000, f"Missing teaching content at frame {i}"
            frames.append((elapsed, elapsed+duration, rgb))
            elapsed += duration

    seam = ImageChops.difference(frames[0][2], frames[-1][2])
    seam_mae = sum(ImageStat.Stat(seam).mean)/3
    assert seam_mae < 0.5, f"Unexpected loop discontinuity: {seam_mae}"

    key_records = {}
    for name, time in KEY_TIMES.items():
        start, end, frame = next((f for f in frames if f[0] <= time < f[1]), frames[-1])
        frame.save(keyframes / f"{name}.png")
        key_records[name] = {"requested_seconds": time, "frame_start_seconds": round(start, 3)}

    before = json.loads((output / "protected_before.json").read_text(encoding="utf-8"))
    changed = [p for p, expected in before.items()
               if not Path(p).is_file() or hashlib.sha256(Path(p).read_bytes()).hexdigest() != expected]
    assert not changed, f"Protected source changed: {changed}"
    result = {
        "status": "PASS", "frames_checked": len(frames),
        "duration_seconds": round(elapsed, 3), "footer_glyphs_present_all_frames_1px_tolerance": True,
        "footer_max_mean_absolute_rgb_difference": round(footer_max_mae, 6),
        "footer_distinct_pixel_hashes_due_to_lossy_encoding": len(footer_hashes),
        "minimum_margins_px_left_top_right_bottom": min_margins,
        "first_last_mean_absolute_rgb_difference": round(seam_mae, 6),
        "protected_files_checked": len(before), "protected_files_changed": changed,
        "keyframes": key_records,
    }
    (output / "frame_audit.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("gif", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.gif, args.output), indent=2))
