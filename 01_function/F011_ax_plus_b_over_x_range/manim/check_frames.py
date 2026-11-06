"""Inspect actual decoded GIF frames, fixed footer, seams and timed key states."""
from pathlib import Path
from hashlib import sha256
import json
from PIL import Image, ImageChops, ImageDraw, ImageOps, ImageStat

ROOT=Path(__file__).resolve().parents[3]
BUILD=ROOT/'build/manim/F011-production/F011'


def check(name,filename):
    folder=BUILD/name
    audit=json.loads((folder/'scene_audit.json').read_text(encoding='utf-8'))
    assert not audit['safe_area_violations']
    target=folder/filename
    snapshots=folder/'review'
    snapshots.mkdir(exist_ok=True)
    requested=[(s['label'],s['time']+.15) for s in audit['states']]
    if name=='branch_distance': requested.append(('general_k',17.0))
    frames=[];footer_hashes=set();bad=[];elapsed=0;footer_error=0
    with Image.open(target) as gif:
        assert gif.size==(576,1024) and gif.info['loop']==0
        for n in range(gif.n_frames):
            gif.seek(n);im=gif.convert('RGB');duration=gif.info['duration']/1000
            assert duration>0
            crop=im.crop((15,932,561,1000))
            if n==0: footer_reference=crop.copy()
            footer_hashes.add(sha256(crop.tobytes()).hexdigest())
            footer_error=max(footer_error,max(ImageStat.Stat(ImageChops.difference(footer_reference,crop)).mean))
            # A blank light or black frame cannot have visible footer and plot variation.
            if max(ImageStat.Stat(im).stddev)<5: bad.append(n)
            for label,t in requested:
                if elapsed<=t<elapsed+duration:
                    path=snapshots/f'{label}.png';im.save(path);frames.append((label,path))
            if n==0: first=im.copy()
            last=im.copy();elapsed+=duration
        # Endpoint frame timing may round past the last requested mark; inspect last explicitly.
        first.save(snapshots/'first.png');last.save(snapshots/'last.png')
    # H.264 before palette conversion introduces small block/edge quantization changes.
    # Scene footer is fixed; permit compression noise, not text movement or disappearance.
    assert footer_error<2.5, f'Footer differs beyond compression tolerance: {footer_error}'
    assert not bad, f'Blank frames: {bad}'
    difference=ImageChops.difference(first,last)
    seam_mean=sum(ImageStat.Stat(difference).mean)/3
    assert seam_mean<.5, f'Opening/closing states disagree: {seam_mean}'
    report={'gif':str(target.relative_to(ROOT)),'frames':n+1,'duration_seconds':round(elapsed,3),
        'footer_distinct_crops':len(footer_hashes),'max_footer_mean_channel_error':round(footer_error,5),'blank_frames':bad,
        'first_last_mean_pixel_difference':round(seam_mean,5),'layout_samples':audit['layout_samples'],
        'safe_area_violations':audit['safe_area_violations'],'keyframes':[label for label,_ in frames]}
    (folder/'frame_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    # True GIF frames, not separately re-rendered ideal states.
    columns=3;width=3*390;height=((len(frames)+2)//3)*730
    sheet=Image.new('RGB',(width,height),'#DFE4EA');draw=ImageDraw.Draw(sheet)
    for i,(label,p) in enumerate(frames):
        im=ImageOps.contain(Image.open(p),(384,683))
        x=(i%columns)*390;y=(i//columns)*730
        draw.text((x+8,y+8),label,fill='#213044');sheet.paste(im,(x+3,y+35))
    sheet.save(folder/'keyframes.png')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':
    check('range','F011_range.gif')
    check('branch_distance','F011_branch_distance.gif')
