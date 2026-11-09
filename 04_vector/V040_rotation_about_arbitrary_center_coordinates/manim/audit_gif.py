"""Inspect every real GIF frame, fixed branding, loop seam, and key point pixels.

Run after the frozen exporter. This supplements, not replaces, its verifier.
"""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image, ImageChops, ImageDraw, ImageStat


def audit(path:Path):
    work=path.parent
    scene=json.loads((work/'scene_audit.json').read_text(encoding='utf-8'))
    assert not scene['layout']['violations'],scene['layout']
    frames=[]; times=[]; durations=[]; footers=set(); elapsed=0
    blank=[]; border_ink=[]
    with Image.open(path) as gif:
        assert gif.size==(576,1024)
        for i in range(gif.n_frames):
            gif.seek(i)
            rgb=gif.convert('RGB')
            frames.append(rgb.copy()); times.append(elapsed)
            dt=gif.info['duration']/1000
            durations.append(dt); elapsed+=dt
            footers.add(hashlib.sha256(rgb.crop((35,940,541,1007)).tobytes()).hexdigest())
            graph=rgb.crop((55,145,552,616)).convert('L')
            if ImageStat.Stat(graph).stddev[0]<2: blank.append(i)
            # The safe band must remain the clean background on every frame.
            strips=[rgb.crop((0,0,8,1024)),rgb.crop((568,0,576,1024)),
                    rgb.crop((0,0,576,12)),rgb.crop((0,1012,576,1024))]
            if any(ImageStat.Stat(s.convert('L')).extrema[0][0]<220 for s in strips):
                border_ink.append(i)
    assert not blank,blank
    assert not border_ink,border_ink
    # H.264 followed by GIF palette quantization changes some antialiased edge
    # pixels even for stationary text. Compare glyph occupancy per line rather
    # than incorrectly requiring encoded pixels to be bit-identical.
    footer_ious=[]; footer_means=[]
    for rgb in frames:
        for rect in [(35,940,541,973),(35,973,541,1007)]:
            ref=frames[0].crop(rect).convert('L')
            cur=rgb.crop(rect).convert('L')
            a=ref.point(lambda p:255 if p<170 else 0)
            b=cur.point(lambda p:255 if p<170 else 0)
            intersection=ImageChops.multiply(a,b).histogram()[255]
            union=ImageChops.lighter(a,b).histogram()[255]
            footer_ious.append(intersection/union)
            footer_means.append(ImageStat.Stat(ImageChops.difference(ref,cur)).mean[0])
    assert min(footer_ious)>.95,min(footer_ious)
    assert max(footer_means)<2.5,max(footer_means)
    seam=ImageChops.difference(frames[0],frames[-1])
    # Very small codec / quantization noise is accepted, visible jumps are not.
    seam_mean=sum(ImageStat.Stat(seam).mean)/3
    assert seam_mean<.75,seam_mean
    chosen=[]; point_checks=[]
    for event in scene['events']:
        if event['label']=='initial': target=.35
        elif event['label']=='loop_end': target=elapsed-.15
        else: target=min(event['time']+.15,elapsed-.15)
        index=max(i for i,t in enumerate(times) if t<=target)
        frame=frames[index]
        chosen.append((index,event,frame))
        x,y,_=event['screen_point']
        px=round((x+4.5)/9*576); py=round((8-y)/16*1024)
        region=frame.crop((px-6,py-6,px+7,py+7))
        hits=sum(1 for r,g,b in region.getdata() if g>70 and g>r*1.4 and b<g*1.05 and r<100)
        assert hits>=3,(event['label'],index,px,py,hits)
        point_checks.append({'label':event['label'],'frame':index,'time':times[index],
                             'angle':event['angle'],'green_point_pixels':hits})
        frame.save(work/f'key_{len(chosen)-1:02}.png')
    sheet=Image.new('RGB',(576*4,1060*2),'#e4e7eb')
    draw=ImageDraw.Draw(sheet)
    for i,(index,event,frame) in enumerate(chosen):
        col,row=i%4,i//4
        sheet.paste(frame,(col*576,row*1060+30))
        draw.text((col*576+10,row*1060+5),f"frame {index}, angle {event['angle']:.1f}",fill='black')
    sheet.save(work/'keyframes.png')
    result={'frame_count':len(frames),'duration_seconds':round(elapsed,3),
            'branding_pixel_signatures':len(footers),
            'branding_min_glyph_mask_iou':min(footer_ious),
            'branding_max_mean_luminance_difference':max(footer_means),
            'blank_graph_frames':blank,
            'unsafe_border_frames':border_ink,'loop_seam_mean_rgb_difference':seam_mean,
            'key_point_checks':point_checks,'scene_layout':scene['layout']}
    (work/'frame_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('gif',type=Path)
    print(json.dumps(audit(parser.parse_args().gif),indent=2))
