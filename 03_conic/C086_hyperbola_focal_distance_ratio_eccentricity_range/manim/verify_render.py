"""Audit actual rendered model states, GIF safety, and source preservation."""
import argparse
from pathlib import Path
import json
import hashlib
import numpy as np
from PIL import Image, ImageSequence
from model import residuals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('render_dir', type=Path)
    parser.add_argument('baseline', type=Path)
    args = parser.parse_args()
    audit_path = args.render_dir/'media'/'C086_frame_math.json'
    states = json.loads(audit_path.read_text(encoding='utf-8'))
    assert len(states)>50, 'missing motion samples'
    counts = {s['count'] for s in states}
    assert counts == {0,1,2}
    max_error = 0
    for s in states:
        assert 2 <= s['c'] <= 3.5
        assert s['ratio']==2 and s['r1']==4 and s['r2']==2
        for row in residuals(s):
            max_error = max(max_error,max(row))
        assert s['count']==(0 if s['c']>3+1e-10 else (1 if abs(s['c']-3)<1e-10 else 2))
    assert max_error<1e-10
    gif_path = args.render_dir/'focal_distance_ratio_range.gif'
    review = args.render_dir/'review'
    review.mkdir(exist_ok=True)
    targets = [0,3,5.5,9,13,16,19,20.5,22,25,27.9]
    boxes, times, t, saved = [], [], 0, []
    with Image.open(gif_path) as gif:
        frames = []
        for i, frame in enumerate(ImageSequence.Iterator(gif)):
            rgb = frame.convert('RGB')
            arr = np.asarray(rgb).astype(int)
            mask = np.max(np.abs(arr-arr[0,0]),axis=2)>40
            ys,xs = np.where(mask)
            assert len(xs)>200, f'empty frame {i}'
            box = [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]
            assert box[0]>=24 and box[2]<=552 and box[1]>=20 and box[3]<=1004, (i,box)
            boxes.append(box)
            frames.append(rgb.copy())
            times.append(t)
            t += frame.info.get('duration',0)/1000
        for target in targets:
            i = min(range(len(times)),key=lambda j:abs(times[j]-target))
            path = review/f'frame_{times[i]:05.2f}.png'
            frames[i].save(path)
            saved.append({'time':round(times[i],3),'file':path.name})
        # Full-size true GIF frames remain available; contact sheet is navigation.
        thumbs = [frames[min(range(len(times)),key=lambda j:abs(times[j]-target))].resize((288,512)) for target in targets]
        sheet = Image.new('RGB',(288*4,512*3),'#F7F8FA')
        for j,im in enumerate(thumbs):
            sheet.paste(im,((j%4)*288,(j//4)*512))
        sheet.save(review/'contact_sheet.png')
    root = Path(__file__).resolve().parents[1]
    baseline = json.loads(args.baseline.read_text(encoding='utf-8-sig'))
    for row in baseline:
        p = root/row['Path']
        assert hashlib.sha256(p.read_bytes()).hexdigest().upper()==row['Hash'], f'changed original {p}'
    report = dict(model_samples=len(states),counts=sorted(counts),max_geometry_error=max_error,
                  gif_frames=len(boxes),duration=round(t,3),
                  content_bbox=[min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)],
                  source_files_preserved=len(baseline),keyframes=saved)
    (review/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
