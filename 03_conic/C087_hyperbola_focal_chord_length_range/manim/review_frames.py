"""Inspect real GIF frames and create local review evidence for this UID."""
from pathlib import Path
import json
from PIL import Image, ImageDraw

root=Path(__file__).resolve().parents[3]
work=root/'build/manim/C087/focal_chord_range'
gif=work/'focal_chord_range.gif'
im=Image.open(gif)
targets=[.8,2.9,5.2,8.2,11.7,13.5,15.4,18.0,19.7,21.5,24.3]
frames=[]
clock=0
footer_min=[100000,100000]
next_target=0
for i in range(im.n_frames):
    im.seek(i)
    frame=im.convert('RGB')
    duration=im.info.get('duration',0)/1000
    # The requested footer must be present in every actual decoded frame.
    for line,box in enumerate([(25,944,551,975),(25,979,551,1008)]):
        crop=frame.crop(box)
        dark=sum(1 for r,g,b in crop.get_flattened_data() if max(r,g,b)<180)
        footer_min[line]=min(footer_min[line],dark)
    while next_target<len(targets) and clock+duration>=targets[next_target]:
        stamp=targets[next_target]
        frame.save(work/f'key-{stamp:04.1f}.png')
        frames.append((stamp,frame.copy()))
        next_target+=1
    clock+=duration
assert all(count>100 for count in footer_min), f'footer line missing: dark pixels {footer_min}'
sheet=Image.new('RGB',(4*288,3*540),'#e4e7eb')
draw=ImageDraw.Draw(sheet)
for j,(stamp,frame) in enumerate(frames):
    frame.thumbnail((288,512))
    x,y=(j%4)*288,(j//4)*540
    sheet.paste(frame,(x,y+24))
    draw.text((x+8,y+5),f'{stamp:.1f}s',fill='#213044')
sheet.save(work/'contact.png')
result=dict(decoded_frames=im.n_frames,duration=round(clock,3),
            footer_present_every_frame=True,footer_line_min_dark_pixels=footer_min,
            key_times=targets)
(work/'frame_review.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
