"""UID-local review of exported GIFs, never writes formal images."""
from pathlib import Path
import json,sys,hashlib
from PIL import Image,ImageDraw,ImageChops
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
BUILD=ROOT/'build/manim/F081-production-20261119'
name=sys.argv[1]
short='equal_height' if name=='rolle_equal_height' else 'zero_count'
gif=BUILD/'F081'/name/(name+'.gif')
out=BUILD/'review'/name;out.mkdir(parents=True,exist_ok=True)
states=json.loads((BUILD/(short+'_key_states.json')).read_text(encoding='utf-8'))
im=Image.open(gif);frames=[];durations=[];elapsed=0;footer_hashes=set();edge_ink=[];footer_mae=[];footer_iou=[]
reference=np.asarray(im.convert('RGB').crop((18,930,558,1012)),dtype=float)
reference_mask=reference.mean(axis=2)<165
for i in range(im.n_frames):
    im.seek(i);f=im.convert('RGB');dt=im.info.get('duration',0)
    frames.append((elapsed,f.copy()));durations.append(dt);elapsed+=dt/1000
    footer_hashes.add(hashlib.sha256(f.crop((18,930,558,1012)).tobytes()).hexdigest())
    pixels=np.asarray(f.crop((18,930,558,1012)),dtype=float);mask=pixels.mean(axis=2)<165
    footer_mae.append(float(np.abs(pixels-reference).mean()))
    footer_iou.append(float(np.logical_and(mask,reference_mask).sum()/np.logical_or(mask,reference_mask).sum()))
    # Every frame must retain safe, light outer edge strips.
    for box in [(0,0,576,9),(0,1017,576,1024),(0,0,9,1024),(567,0,576,1024)]:
        pix=f.crop(box);edge_ink.append(sum(1 for rr,gg,bb in pix.get_flattened_data() if min(rr,gg,bb)<180))
selected=[('start',0)]+[(s['name'],max(0,s['time']-.28)) for s in states]+[('end',elapsed-.1)]
selected += [('mid_transition_'+str(j),q) for j,q in enumerate([8,11,14,17.2,21] if short=='equal_height' else [7,9,12,16,19])]
if short=='zero_count':selected += [('interval_left',2.45),('interval_right',4.35)]
for title,sec in selected:
    k=min(range(len(frames)),key=lambda j:abs(frames[j][0]-sec))
    frames[k][1].save(out/(title+'.png'))
    print(title,k,round(frames[k][0],2))
for j in range(0,len(selected),6):
    sheet=Image.new('RGB',(900,1110),'#e5e7eb');draw=ImageDraw.Draw(sheet)
    for z,(title,_) in enumerate(selected[j:j+6]):
        f=Image.open(out/(title+'.png'));f.thumbnail((282,502))
        ox=(z%3)*300+9;oy=(z//3)*550+32
        sheet.paste(f,(ox,oy));draw.text((ox,oy-22),title,fill='#213044')
    sheet.save(out/f'contact-{j//6+1}.png')
report={'file':str(gif.relative_to(ROOT)),'frames':len(frames),'duration_seconds':round(elapsed,3),'loop':im.info.get('loop'),'size':[im.width,im.height],'footer_distinct_raster_count':len(footer_hashes),'footer_max_mae_255':max(footer_mae),'footer_min_ink_mask_iou':min(footer_iou),'footer_note':'Lossy MP4/GIF quantization causes small raster differences; verify text shape, not byte identity.','max_outer_edge_dark_pixels':max(edge_ink),'key_state_count':len(states),'review_images':len(selected),'gif_sha256':hashlib.sha256(gif.read_bytes()).hexdigest()}
assert im.size==(576,1024) and im.info.get('loop')==0
assert max(footer_mae)<2 and min(footer_iou)>.93,'Footer shape or presence changed during animation'
assert max(edge_ink)==0,'Content touches outermost safety strip'
(out/'frame_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
