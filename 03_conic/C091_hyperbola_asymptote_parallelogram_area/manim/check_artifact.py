"""Full-frame footer/safe-margin audit and actual GIF keyframe extraction."""
from pathlib import Path
import hashlib
import json
import sys
from PIL import Image, ImageDraw, ImageSequence
import numpy as np


def audit(path):
    path = Path(path)
    target = path.parent
    gif = Image.open(path)
    footer_hashes = set()
    footer_reference = None
    footer_min_ink_iou = 1.0
    footer_max_mean_difference = 0.0
    snapshots = [0, 2.5, 5.4, 7.0, 8.9, 11, 13.2, 16.4, 18.5, 21, 22]
    elapsed = 0
    picked = []
    edge_failures = []
    for n, frame in enumerate(ImageSequence.Iterator(gif)):
        rgb = frame.convert('RGB')
        footer = np.asarray(rgb.crop((30,914,546,993)))
        footer_hashes.add(hashlib.sha256(footer.tobytes()).hexdigest())
        if footer_reference is None:
            footer_reference = footer.copy()
        mask = footer.mean(axis=2) < 170
        reference_mask = footer_reference.mean(axis=2) < 170
        footer_min_ink_iou = min(footer_min_ink_iou,
                                float((mask & reference_mask).sum()/(mask | reference_mask).sum()))
        footer_max_mean_difference = max(footer_max_mean_difference,
                                        float(np.abs(footer.astype(float)-footer_reference).mean()))
        for strip in [(0,0,20,1024),(556,0,576,1024),(0,1004,576,1024)]:
            # All text and graphics must stay clear of the outer 20 px.
            extrema = rgb.crop(strip).getextrema()
            if any(lo < 180 for lo, hi in extrema):
                edge_failures.append(n)
        duration = frame.info['duration']
        for sec in snapshots[:]:
            if elapsed+duration >= sec*1000:
                name = f'key_{sec}.png'
                rgb.save(target/name)
                picked.append((sec, rgb.copy()))
                snapshots.remove(sec)
        elapsed += duration
    # MP4 compression and GIF quantization cause minor pixel differences.
    # Compare fixed-position text ink rather than claiming bit-identical pixels.
    assert footer_min_ink_iou >= .95, 'footer text shifted or disappeared'
    assert footer_max_mean_difference < 2, 'footer content changed'
    assert not edge_failures, f'outer margin ink: {edge_failures}'
    sheet = Image.new('RGB', (4*288,3*532), '#E9EDF2')
    draw = ImageDraw.Draw(sheet)
    for i, (sec, im) in enumerate(picked):
        im = im.resize((288,512))
        x,y=(i%4)*288,(i//4)*532
        sheet.paste(im,(x,y+20));draw.text((x+8,y+3),f'{sec}s',fill='black')
    sheet.save(target/'keyframes.png')
    baseline = json.loads((target/'protected_sources.json').read_text(encoding='utf-8'))
    for f, digest in baseline.items():
        assert hashlib.sha256(Path(f).read_bytes()).hexdigest() == digest, f'protected source changed: {f}'
    info = dict(frames_checked=gif.n_frames,footer_variants=len(footer_hashes),
                footer_min_ink_iou=round(footer_min_ink_iou,5),
                footer_max_mean_difference=round(footer_max_mean_difference,5),
                margin_failures=len(edge_failures),protected_files_unchanged=len(baseline),
                duration_seconds=elapsed/1000,keyframes=len(picked))
    (target/'visual_technical_audit.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
    print(json.dumps(info))


if __name__ == '__main__':
    audit(sys.argv[1])
