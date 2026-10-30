"""Full-frame local QA and extraction of actual GIF frames, never synthetic previews."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageSequence


def run(gif_path: Path, work: Path):
    evidence=work/'qa'
    evidence.mkdir(exist_ok=True)
    source=Path(__file__).parent.parent
    sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
             for p in [*sorted(source.glob('0[1-6]_*.tex')),source/'meta.json']}
    # Actual renderer clock, including frame rounding; avoids guessing phase times.
    desired=json.loads((work/'keyframe_times.json').read_text(encoding='utf-8'))
    footer_hashes=set()
    header_hashes=set()
    margin_violations=[]
    references={}
    max_mae={'header':0.,'footer':0.}
    max_changed={'header':0.,'footer':0.}
    min_body_ink=10**9
    times=[]
    frames=[]
    with Image.open(gif_path) as gif:
        elapsed=0
        for i,fr in enumerate(ImageSequence.Iterator(gif)):
            rgb=fr.convert('RGB')
            a=np.asarray(rgb).astype(int)
            bg=a[0,0]
            diff=np.max(np.abs(a-bg),axis=2)
            body=int((diff[130:895,15:561]>65).sum())
            min_body_ink=min(min_body_ink,body)
            border=np.concatenate((diff[:4].ravel(),diff[-4:].ravel(),diff[:,:4].ravel(),diff[:,-4:].ravel()))
            if (border>40).any():margin_violations.append(i)
            footer_hashes.add(hashlib.sha256(rgb.crop((15,925,561,1015)).tobytes()).hexdigest())
            header_hashes.add(hashlib.sha256(rgb.crop((15,25,561,125)).tobytes()).hexdigest())
            for tag,box in [('footer',(15,925,561,1015)),('header',(15,25,561,125))]:
                current=np.asarray(rgb.crop(box)).astype(int)
                if tag not in references:references[tag]=current
                change=np.abs(current-references[tag])
                max_mae[tag]=max(max_mae[tag],float(change.mean()))
                max_changed[tag]=max(max_changed[tag],float((change.max(axis=2)>30).mean()))
            duration=fr.info['duration']/1000
            times.append((elapsed,elapsed+duration))
            elapsed+=duration
        desired['last']=max(0,elapsed-.03)
        selected={}
        for tag,t in desired.items():
            index=next((i for i,(a,b) in enumerate(times) if a<=t<b),len(times)-1)
            gif.seek(index)
            rgb=gif.convert('RGB')
            rgb.save(evidence/f'{tag}.png')
            selected[tag]={'frame':index,'timestamp':round(times[index][0],3)}
            frames.append((tag,rgb.copy()))
    # This summary does not replace the separate original-resolution images.
    sheet=Image.new('RGB',(576*3,1060*((len(frames)+2)//3)),'#dfe3e8')
    draw=ImageDraw.Draw(sheet)
    for i,(tag,im) in enumerate(frames):
        x=i%3*576;y=i//3*1060
        draw.text((x+12,y+8),tag,fill='black')
        sheet.paste(im,(x,y+30))
    sheet.save(evidence/'contact_sheet.png')
    result={'frames_checked':len(times),'duration_seconds':round(elapsed,3),
            'static_footer_variants':len(footer_hashes),
            'static_header_variants':len(header_hashes),
            'static_region_max_mean_pixel_error':max_mae,
            'static_region_max_materially_changed_fraction':max_changed,
            'margin_violations':margin_violations,
            'minimum_body_foreground_pixels':min_body_ink,
            'real_keyframes':selected,'formal_sources_sha256':sources}
    (evidence/'full_frame_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    assert not margin_violations, 'Content reaches image edge'
    # H.264/GIF palette quantization introduces tiny pixel differences even for
    # stationary text. A missing line or one-pixel displacement fails these bounds.
    assert all(v<2 for v in max_mae.values()), 'Static text changes materially'
    assert all(v<.002 for v in max_changed.values()), 'Static text moves or disappears'
    assert min_body_ink>0, 'Empty teaching-content frame'
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('gif',type=Path);p.add_argument('work',type=Path)
    args=p.parse_args();run(args.gif,args.work)
