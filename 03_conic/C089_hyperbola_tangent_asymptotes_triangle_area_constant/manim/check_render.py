"""Inspect real exported frames, model-driven P, fixed footer and protected files."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image,ImageSequence

ROOT=Path(__file__).resolve().parents[3]
WORK=ROOT/'build/manim/C089/tangent_area'
sys.path.insert(0,str(ROOT/'scripts/manim'))
from verify_gif import verify_gif


def check():
    gif=WORK/'C089_tangent_area_constant.gif'
    technical=verify_gif(gif,width=576,height=1024)
    rows=json.loads((WORK/'frame_model_checks.json').read_text(encoding='utf-8'))
    assert len(rows)>400
    times=np.array([r['time'] for r in rows])
    full=[];elapsed=0;footer_ref=None;max_footer_delta=0;max_distance=0
    key_times=[0,1.7,3.4,5.3,8.7,10.8,12.8,16.8,18.9]
    saved=set()
    with Image.open(gif) as im:
        for i,frame in enumerate(ImageSequence.Iterator(im)):
            rgb=frame.convert('RGB'); a=np.asarray(rgb).astype(float)
            # Only P uses the gold color. Locate its real pixels in every frame.
            color=np.array([183,125,18])
            mask=(np.sqrt(np.sum((a-color)**2,axis=2))<38)&(a[:,:,0]<198)&(a[:,:,1]>112)&(a[:,:,2]<40)
            yy,xx=np.where(mask)
            assert len(xx)>=8,('P absent',i)
            actual=np.array([xx.mean(),yy.mean()])
            # H264/GIF timing can straddle a neighbouring rendered sample.
            candidates=np.where(abs(times-elapsed)<.10)[0]
            assert len(candidates)
            predicted=[]
            for j in candidates:
                x,y=rows[j]['P']
                predicted.append([(4.5-3.0+1.45*x)*64,(8-.62-1.45*y)*64])
            distance=min(np.linalg.norm(actual-np.array(q)) for q in predicted)
            assert distance<5,('P/model mismatch',i,actual,distance)
            max_distance=max(max_distance,float(distance))
            footer=a[930:1004,30:546]
            if footer_ref is None: footer_ref=footer.copy()
            delta=float(np.mean(abs(footer-footer_ref)))
            # H264 encoding and GIF dithering slightly change edge shades.
            # Require <1.2% of the full color range and identical ink extent.
            assert delta<3,('footer changed',i,delta)
            def ink_extent(crop):
                ys,xs=np.where(crop.mean(axis=2)<170)
                return np.array([xs.min(),xs.max(),ys.min(),ys.max()])
            assert np.max(abs(ink_extent(footer)-ink_extent(footer_ref)))<=1
            max_footer_delta=max(max_footer_delta,delta)
            for target in key_times:
                if target not in saved and elapsed>=target:
                    rgb.save(WORK/f'key_{target:04.1f}s.png');saved.add(target)
            full.append((i,elapsed))
            elapsed+=frame.info['duration']/1000
    original=json.loads((WORK/'formal_baseline.json').read_text())
    for file,digest in original.items():
        assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==digest,file
    result={'technical':technical,'rendered_model_frames_checked':len(rows),
       'real_gif_frames_checked':len(full),'P_max_model_pixel_error':max_distance,
       'footer_max_mean_pixel_delta':max_footer_delta,'formal_files_unchanged':len(original),
       'mathematics':'PASS','keyframes':'PENDING VISUAL REVIEW',
       'teaching':'PENDING VISUAL REVIEW','visual':'PENDING VISUAL REVIEW',
       'android_device':'PENDING','user_visual':'PENDING','final_freeze':'PENDING',
       'published_synced':'NOT RUN'}
    (WORK/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    check()
