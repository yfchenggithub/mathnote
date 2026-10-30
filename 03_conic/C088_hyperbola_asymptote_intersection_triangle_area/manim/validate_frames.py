"""Inspect every decoded GIF frame and extract real timestamped evidence."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from PIL import Image, ImageChops, ImageStat, ImageSequence
from model import KEY_STATES

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts' / 'manim'))
from verify_gif import verify_gif


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('gif', type=Path)
    args = parser.parse_args()
    path = args.gif.resolve()
    evidence = path.parent / 'evidence'
    evidence.mkdir(exist_ok=True)
    report = verify_gif(path, width=576, height=1024)
    frames = []
    spans = []
    elapsed = 0
    with Image.open(path) as gif:
        for frame in ImageSequence.Iterator(gif):
            rgb = frame.convert('RGB')
            frames.append(rgb.copy())
            duration = frame.info['duration'] / 1000
            spans.append((elapsed, elapsed + duration))
            elapsed += duration

    keys = dict(KEY_STATES)
    keys['loop_end'] = elapsed - .15
    report['real_keyframes'] = {}
    for name, t in keys.items():
        index = next(i for i, (a, b) in enumerate(spans) if a <= t < b)
        output = evidence / f'{name}.png'
        frames[index].save(output)
        report['real_keyframes'][name] = {'frame': index, 'time_seconds': t, 'file': str(output.relative_to(ROOT))}

    # MP4 compression can perturb RGB values in stationary text before GIF
    # encoding. Test glyph stability and RGB error, not byte-identical pixels.
    footer_box = (0, 916, 576, 1004)
    ref = frames[0].crop(footer_box)
    mask = ref.convert('L').point(lambda v: 255 if v < 170 else 0)
    max_mean = 0
    min_iou = 1
    for im in frames:
        crop = im.crop(footer_box)
        max_mean = max(max_mean, sum(ImageStat.Stat(ImageChops.difference(ref, crop)).mean) / 3)
        other = crop.convert('L').point(lambda v: 255 if v < 170 else 0)
        intersection = sum(ImageChops.darker(mask, other).get_flattened_data())
        union = sum(ImageChops.lighter(mask, other).get_flattened_data())
        min_iou = min(min_iou, intersection / union)
    report['footer_max_mean_rgb_delta'] = round(max_mean, 6)
    report['footer_min_glyph_mask_iou'] = round(min_iou, 6)
    report['footer_fixed_all_frames'] = max_mean < 1 and min_iou > .97
    report['empty_math_frames'] = sum(max(ImageStat.Stat(im.crop((55, 190, 521, 600))).stddev) < 2 for im in frames)
    # Nothing authored may enter the outermost 14 px on any frame.
    edge_counts = []
    for im in frames:
        bg = im.getpixel((0, 0))
        count = 0
        for box in [(0, 0, 14, 1024), (562, 0, 576, 1024), (0, 0, 576, 14), (0, 1010, 576, 1024)]:
            crop = im.crop(box)
            count += sum(max(abs(p[j] - bg[j]) for j in range(3)) > 45 for p in crop.get_flattened_data())
        edge_counts.append(count)
    report['max_outer_edge_ink_pixels'] = max(edge_counts)
    report['first_last_mean_absolute_difference'] = round(sum(ImageStat.Stat(ImageChops.difference(frames[0], frames[-1])).mean) / 3, 6)
    report['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    if (not report['footer_fixed_all_frames'] or report['empty_math_frames'] or
            report['max_outer_edge_ink_pixels'] or report['first_last_mean_absolute_difference'] > 1):
        raise ValueError(json.dumps(report))
    (evidence / 'frame_validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
