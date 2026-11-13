"""Decode every delivered GIF frame and save real-frame visual evidence."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw

p = Path(sys.argv[1])
im = Image.open(p)
frames, times = [], []
elapsed = 0
for i in range(im.n_frames):
    im.seek(i)
    frames.append(np.array(im.convert('RGB')))
    times.append(elapsed)
    elapsed += im.info['duration']
first = frames[0].astype(float)
footer_delta = max(float(np.abs(f[915:1005].astype(float)-first[915:1005]).mean()) for f in frames)
loop_delta = float(np.abs(frames[-1].astype(float)-first).mean())
colored = []
for f in frames:
    graph = f[230:670, 55:530].astype(int)
    colored.append(int(((graph.max(2)-graph.min(2)) > 45).sum()))
report = dict(frame_count=len(frames), duration_seconds=elapsed/1000,
              size=list(im.size), minimum_graph_colored_pixels=min(colored),
              footer_max_mean_channel_delta=footer_delta,
              loop_end_mean_channel_delta=loop_delta,
              sha256=hashlib.sha256(p.read_bytes()).hexdigest())
assert im.size == (576,1024)
assert min(colored) > 500
assert footer_delta < 2, report
assert loop_delta < 2, report
targets = [0,3000,9000,14000,20000,elapsed-1]
sheet = Image.new('RGB',(576*3,1055*2),'white')
draw = ImageDraw.Draw(sheet)
for j,t in enumerate(targets):
    index = max(i for i,s in enumerate(times) if s <= t)
    f = Image.fromarray(frames[index])
    f.save(p.parent/f'keyframe_{t}.png')
    x,y = j%3*576,j//3*1055
    sheet.paste(f,(x,y))
    draw.text((x+12,y+1030),f'{t/1000:.2f} s / frame {index}',fill='black')
sheet.save(p.parent/'contact_sheet_final.png')
(p.parent/'frame_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
