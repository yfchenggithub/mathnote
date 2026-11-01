"""Full-frame local checks plus actual GIF keyframes for human review."""
import json
import sys
from hashlib import sha256
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageSequence, ImageStat

path=Path(sys.argv[1]); out=path.parent/'qa'; out.mkdir(exist_ok=True)
times=[0,2.8,6.5,9,11.3,14.6,17.5,18.9]
selected={}; elapsed=0; baseline=None; footer_error=0; footer_shape=0; margins_ok=True; populated=True; count=0
with Image.open(path) as gif:
    for frame in ImageSequence.Iterator(gif):
        rgb=frame.convert('RGB'); duration=frame.info['duration']/1000
        for t in times:
            if elapsed<=t<elapsed+duration:
                selected[t]=rgb.copy()
        crop=rgb.crop((20,929,556,1008))
        if baseline is None: baseline=crop.copy()
        footer_error=max(footer_error,sum(ImageStat.Stat(ImageChops.difference(baseline,crop)).mean)/3)
        masks=[c.convert('L').point(lambda v:255 if v<160 else 0) for c in (baseline,crop)]
        footer_shape=max(footer_shape,ImageStat.Stat(ImageChops.difference(*masks)).mean[0]/255)
        # Safe edges are background throughout the encoded animation.
        bg=Image.new('RGB',rgb.size,rgb.getpixel((0,0)))
        diff=ImageChops.difference(rgb,bg)
        for box in [(0,0,576,12),(0,1012,576,1024),(0,0,12,1024),(564,0,576,1024)]:
            margins_ok &= max(v[1] for v in diff.crop(box).getextrema())<16
        populated &= diff.crop((30,200,546,690)).getbbox() is not None
        elapsed+=duration; count+=1
# Allow MP4 compression and palette dithering; detect movement/disappearance.
assert footer_error<2 and footer_shape<.005,'Footer changes during animation'
assert margins_ok,'Content enters safe edge'
assert populated,'Empty diagram frame'
sheet=Image.new('RGB',(576*4,1060*2),'white'); draw=ImageDraw.Draw(sheet)
for i,(t,rgb) in enumerate(selected.items()):
    rgb.save(out/f'key_{t:04.1f}.png')
    x=(i%4)*576; y=(i//4)*1060
    sheet.paste(rgb,(x,y+30)); draw.text((x+15,y+8),f't = {t:.1f}s',fill='black')
sheet.save(out/'contact.png')
result=dict(frames=count,duration=round(elapsed,3),fixed_footer=True,
            footer_mean_pixel_error=footer_error,footer_mask_difference=footer_shape,safe_margins=True,
            nonempty_diagram=True,actual_keyframes=list(selected))
(out/'full_frame_checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
