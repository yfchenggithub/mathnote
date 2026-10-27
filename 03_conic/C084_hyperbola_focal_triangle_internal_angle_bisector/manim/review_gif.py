from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageStat
import json,sys
root=Path(__file__).resolve().parents[3]
work=root/'build/manim/C084/focal_bisector';review=work/'review';review.mkdir(exist_ok=True)
gif=work/'focal_bisector.gif'
targets=[0,2.5,5.8,8.8,11.3,14.4,19.8,23.8]
with Image.open(gif) as im:
 t=0;frames=[];shots=[];selected=set()
 for i in range(im.n_frames):
  im.seek(i);rgb=im.convert('RGB');duration=im.info.get('duration',0)
  for target in targets:
   if target not in selected and t+duration/1000>=target:
    name=f'frame-{i:03d}.png';rgb.save(review/name);shots.append({'index':i,'time':round(t,3),'path':name});selected.add(target)
  frames.append(rgb.copy());t+=duration/1000
 first=frames[0];last=frames[-1]
 diff=ImageChops.difference(first,last)
 loop_mad=sum(ImageStat.Stat(diff).mean)/3
 sheet=Image.new('RGB',(4*288,2*544),'#e8e8e8');d=ImageDraw.Draw(sheet)
 for j,shot in enumerate(shots):
  thumb=Image.open(review/shot['path']).resize((288,512));x=(j%4)*288;y=(j//4)*544
  sheet.paste(thumb,(x,y+30));d.text((x+10,y+8),f"{shot['time']}s / {shot['index']}",fill='black')
 sheet.save(review/'contact.png')
 result={'frames':len(frames),'duration_seconds':round(t,3),'loop':im.info.get('loop'),'size':first.size,'loop_boundary_mean_difference':loop_mad,'keyframes':shots}
 (review/'review.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
