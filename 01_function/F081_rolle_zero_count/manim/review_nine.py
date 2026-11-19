"""Streaming full-frame audit and real keyframe extraction for F081 nine paths."""
from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3]
BUILD=ROOT/'build/manim/F081-nine-paths-20261119'
NAME='zero_derivative_nine_paths'
GIF=BUILD/'F081'/NAME/(NAME+'.gif')
OUT=BUILD/'review';OUT.mkdir(parents=True,exist_ok=True)
states=json.loads((BUILD/'key_states.json').read_text(encoding='utf-8'))
selections=[('first',0)]
for s in states:
    selections.append((s['name'],max(0,s['time']-.15)))
    if s['name'].endswith('_origin'):
        a=s['values']['a'];b=s['values']['b'];hold=.8 if a*b<0 else .6 if a==b==0 else .5
        selections.append((s['name'].replace('_origin','_left_scan'),s['time']-hold-.375))
best={n:(float('inf'),None,None,None) for n,_ in selections}
im=Image.open(GIF);ref=np.asarray(im.convert('RGB').crop((18,930,558,1012)),dtype=float);refmask=ref.mean(axis=2)<165
maes=[];ious=[];max_edge=0;elapsed=0;durations=[]
for i in range(im.n_frames):
    im.seek(i);f=im.convert('RGB');dt=im.info.get('duration',0)
    foot=np.asarray(f.crop((18,930,558,1012)),dtype=float);mask=foot.mean(axis=2)<165
    maes.append(float(np.abs(foot-ref).mean()));ious.append(float(np.logical_and(mask,refmask).sum()/np.logical_or(mask,refmask).sum()))
    pixels=np.asarray(f)
    edge=np.concatenate([pixels[:9,:,:].reshape(-1,3),pixels[1017:,:,:].reshape(-1,3),pixels[:,:9,:].reshape(-1,3),pixels[:,567:,:].reshape(-1,3)])
    max_edge=max(max_edge,int((edge.min(axis=1)<180).sum()))
    for name,sec in selections:
        err=abs(elapsed-sec)
        if err<best[name][0]:best[name]=(err,i,elapsed,f.copy())
    durations.append(dt);elapsed+=dt/1000
    last=f.copy()
best['last']=(0,im.n_frames-1,elapsed-dt/1000,last)
selected=[]
for name,(_,i,sec,f) in best.items():
    f.save(OUT/(name+'.png'));selected.append({'name':name,'frame':i,'time':round(sec,3)})
for start in range(0,len(selected),6):
    sheet=Image.new('RGB',(900,1110),'#e5e7eb');draw=ImageDraw.Draw(sheet)
    for j,e in enumerate(selected[start:start+6]):
        f=Image.open(OUT/(e['name']+'.png'));f.thumbnail((282,502));ox=(j%3)*300+9;oy=(j//3)*550+32
        sheet.paste(f,(ox,oy));draw.text((ox,oy-22),e['name'],fill='#213044')
    sheet.save(OUT/f'contact-{start//6+1}.png')
assert im.size==(576,1024) and im.info.get('loop')==0
assert max_edge==0,('outer-edge clipping',max_edge)
assert max(maes)<2 and min(ious)>.93,('footer instability',max(maes),min(ious))
report={'status':'PASS','frames':im.n_frames,'duration_seconds':round(elapsed,3),'size':[576,1024],'loop':0,'footer_max_mae_255':max(maes),'footer_min_ink_mask_iou':min(ious),'outer_edge_dark_pixels':max_edge,'keyframes':selected,'footer_note':'Compression and palette noise allowed; presence and shape checked on every frame.','gif_sha256':hashlib.sha256(GIF.read_bytes()).hexdigest()}
(OUT/'frame_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='keyframes'},indent=2));print('Real keyframes:',len(selected))
