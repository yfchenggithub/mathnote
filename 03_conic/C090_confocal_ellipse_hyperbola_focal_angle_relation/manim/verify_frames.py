"""Inspect the actual exported GIF against the C090 trajectory and footer."""
from pathlib import Path
import json
import math
import sys
import numpy as np
from PIL import Image, ImageSequence
from model import motion_h, state


def verify(path):
    footer_reference=None
    footer_mask=None
    footer_bounds=set()
    min_footer_iou=1.0
    max_footer_mean_difference=0.0
    max_dot_error=0.0
    frame_count=0
    with Image.open(path) as image:
        for index,frame in enumerate(ImageSequence.Iterator(image)):
            rgb=np.array(frame.convert('RGB'))
            assert rgb.shape==(1024,576,3)
            footer=rgb[930:1008,40:536].astype(int)
            mask=footer.mean(2)<170
            if footer_reference is None:
                footer_reference=footer
                footer_mask=mask
            # MP4 compression and GIF dithering alter edge RGB values. Test
            # glyph shape, stable bounding boxes and brightness, not byte hashes.
            iou=float(np.sum(mask & footer_mask)/np.sum(mask | footer_mask))
            mean_difference=float(np.abs(footer-footer_reference).mean())
            min_footer_iou=min(min_footer_iou,iou)
            max_footer_mean_difference=max(max_footer_mean_difference,mean_difference)
            fy,fx=np.where(mask)
            footer_bounds.add((int(fx.min()),int(fy.min()),int(fx.max()),int(fy.max())))
            assert iou>=.95 and mean_difference<2, f'Footer faded/changed at {index}'
            q=state(motion_h(index/12))
            # Orthographic camera: 9 by16, origin at image centre; no stretching.
            px=(.78*q.x+4.5)*64
            py=(8-(.78*q.y+2.5))*64
            xx,yy=int(round(px)),int(round(py))
            region=rgb[yy-11:yy+12,xx-11:xx+12]
            gold=(region[:,:,0]>135)&(region[:,:,0]<205)&(region[:,:,1]>85)&(region[:,:,1]<150)&(region[:,:,2]<65)
            iy,ix=np.where(gold)
            assert len(ix)>12, f'No gold tracking dot at frame {index}'
            dist=np.sqrt((ix+xx-11-px)**2+(iy+yy-11-py)**2)
            err=float(dist.min())
            assert err<=4.0, f'Point/trajectory mismatch at frame {index}: {err}'
            max_dot_error=max(max_dot_error,err)
            # The safe border must stay equal to the intended flat background.
            bg=np.array([247,248,250])
            for strip in (rgb[:24],rgb[-16:],rgb[:, :24],rgb[:, -24:]):
                assert np.max(np.abs(strip.astype(int)-bg))<=8, f'Unsafe border at {index}'
            frame_count+=1
    assert len(footer_bounds)==1, 'Brand footer moved'
    return {'frames_checked':frame_count,'fixed_footer_bounds':len(footer_bounds),
            'min_footer_glyph_iou':round(min_footer_iou,4),
            'max_footer_mean_rgb_difference':round(max_footer_mean_difference,4),
            'safe_borders':'PASS','tracking_dot_every_frame':'PASS',
            'max_nearest_gold_pixel_error':round(max_dot_error,3)}


if __name__=='__main__':
    print(json.dumps(verify(Path(sys.argv[1])),indent=2))
