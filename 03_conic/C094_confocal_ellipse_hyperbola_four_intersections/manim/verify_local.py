"""Decode the actual C094 GIF and check stationary branding and moving points."""
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageSequence

from model import ConfocalPair


def verify(work):
    gif_path=work/'confocal_four_intersections.gif'
    audit=json.loads((work/'scene_audit.json').read_text(encoding='utf-8'))
    times=np.array([row['time'] for row in audit])
    key_times=[0,2.5,4.1,5.8,7.8,10.5,12.5,14.5,17,19.5,21.3]
    captured=set()
    footer_hashes=set()
    footer_deltas=[]
    footer_ious=[]
    footer_reference=None
    bad_points=[]
    max_residual=0
    elapsed=0
    first=last=None
    frame_count=0
    for row in audit:
        m=ConfocalPair(a_h=row['a_h'])
        for p in row['points']:
            max_residual=max(max_residual,*map(abs,m.residuals(p)))
    with Image.open(gif_path) as gif:
        for index,frame in enumerate(ImageSequence.Iterator(gif)):
            rgb=frame.convert('RGB')
            array=np.array(rgb,dtype=np.int16)
            if first is None:
                first=array.copy()
            last=array.copy()
            # Both lines are entirely in this independently reserved region.
            footer=rgb.crop((35,936,541,1005))
            footer_hashes.add(sha256(footer.tobytes()).hexdigest())
            footer_array=np.array(footer,dtype=np.int16)
            if footer_reference is None:
                footer_reference=footer_array.copy()
            footer_deltas.append(float(np.abs(footer_array-footer_reference).mean()))
            ink=footer_array.mean(axis=2)<175
            reference_ink=footer_reference.mean(axis=2)<175
            footer_ious.append(float((ink&reference_ink).sum()/(ink|reference_ink).sum()))
            if float(array.std())<5:
                raise AssertionError(f'empty frame {index}')
            row=audit[int(np.argmin(abs(times-elapsed)))]
            for n,(x,y) in enumerate(row['points']):
                px=round((.82*x+4.5)*64)
                py=round((8-(1.15+.82*y))*64)
                patch=array[py-8:py+9,px-8:px+9]
                distance=np.linalg.norm(patch-np.array([183,125,18]),axis=2)
                if np.count_nonzero(distance<60)<3:
                    bad_points.append((index,n,round(elapsed,3)))
            for target in key_times:
                if target not in captured and elapsed>=target:
                    rgb.save(work/f'key_{target:04.1f}s.png')
                    captured.add(target)
            elapsed+=frame.info['duration']/1000
            frame_count+=1
    # H.264 and the frozen 128-colour GIF export introduce small pixel noise.
    # Check the entire text ink footprint and colour drift instead of byte equality.
    if max(footer_deltas)>3 or min(footer_ious)<.94:
        raise AssertionError('branding moved, faded, or changed beyond encoding tolerance')
    if bad_points:
        raise AssertionError(f'expected gold intersection pixels missing: {bad_points[:12]}')
    if max_residual>1e-10:
        raise AssertionError(f'rendered-state model residual {max_residual}')
    result={'frames_checked':frame_count,'duration_seconds':round(elapsed,3),
            'footer_crop_unique_hashes_encoding_noise':len(footer_hashes),
            'footer_max_mean_channel_delta':max(footer_deltas),
            'footer_min_ink_mask_intersection_over_union':min(footer_ious),
            'four_gold_intersections_present_every_frame':True,
            'rendered_state_count':len(audit),'max_conic_residual':max_residual,
            'seam_mean_absolute_pixel_difference':float(np.abs(first-last).mean()),
            'keyframes_seconds':sorted(captured)}
    (work/'local_checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    verify(Path(sys.argv[1]))
