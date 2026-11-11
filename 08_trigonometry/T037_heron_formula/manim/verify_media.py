"""T037 full-frame technical checks and actual GIF teaching-state extraction."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
from PIL import Image, ImageChops, ImageStat, ImageOps, ImageDraw

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts/manim'))
from verify_gif import verify_gif

SCENES={'heron_area':'T037HeronArea','heron_incircle':'T037HeronIncircle','heron_special':'T037HeronSpecial'}


def inspect(base,name):
    work=base/'T037'/name
    path=work/f'{name}.gif'
    evidence=base/'review'/name
    evidence.mkdir(parents=True,exist_ok=True)
    technical=verify_gif(path,width=576,height=1024)
    story=json.loads((work/'media'/f'{SCENES[name]}-story.json').read_text(encoding='utf-8'))
    moments=[(0.,'first')]+[(max(0,event['time']-.25),event['name']) for event in story['keyframes']]
    # Inspect actual motion in addition to pauses; no reconstructed substitute figures.
    if name=='heron_area':moments += [(10.5,'base_motion_early'),(12.0,'base_motion_late'),(15.5,'base_motion_return')]
    if name=='heron_special':moments += [(7.3,'equilateral_motion')]
    moments.sort()
    snapshots={};elapsed=0;footer_differences=[];blank_graph=[];edge_ink=[]
    with Image.open(path) as gif:
        for i in range(gif.n_frames):
            gif.seek(i);frame=gif.convert('RGB')
            if i==0:
                first=frame.copy();footer_reference=frame.crop((0,925,576,1024))
            last=frame.copy()
            footer=frame.crop((0,925,576,1024))
            footer_differences.append(max(ImageStat.Stat(ImageChops.difference(footer_reference,footer)).mean))
            body=frame.crop((25,160,551,610))
            background=Image.new('RGB',body.size,frame.getpixel((1,1)))
            delta=ImageChops.difference(body,background).convert('L')
            if sum(delta.histogram()[25:])<450:blank_graph.append(i)
            # Check text/geometry has not reached the canvas edge (8 px strip).
            strip=Image.new('RGB',frame.size,frame.getpixel((1,1)))
            strip.paste(frame.crop((0,0,8,1024)),(0,0))
            strip.paste(frame.crop((568,0,576,1024)),(568,0))
            if sum(ImageChops.difference(strip,Image.new('RGB',frame.size,frame.getpixel((1,1)))).convert('L').histogram()[45:])>10:
                edge_ink.append(i)
            for when,label in moments:
                if label not in snapshots and elapsed+gif.info['duration']/1000>=when:
                    snapshots[label]=frame.copy();frame.save(evidence/f'{label}.png')
            elapsed+=gif.info['duration']/1000
        snapshots['last']=last;last.save(evidence/'last.png')
    difference=ImageStat.Stat(ImageChops.difference(first,last)).mean
    sheet=Image.new('RGB',(900,550*((len(snapshots)+2)//3)),'#D7DCE3');draw=ImageDraw.Draw(sheet)
    for i,(label,frame) in enumerate(snapshots.items()):
        x=(i%3)*300;y=(i//3)*550
        sheet.paste(ImageOps.contain(frame,(288,512)),(x+6,y+25));draw.text((x+8,y+7),label,fill='black')
    sheet.save(evidence/'contact.png')
    result={'technical':technical,'footer_max_mean_absolute_difference':max(footer_differences),
            'blank_graph_frames':blank_graph,'canvas_edge_ink_frames':edge_ink,
            'first_last_mean_absolute_difference':difference,'keyframes':list(snapshots)}
    # Frozen MP4+palette output is lossy: compare at a sub-visible RGB tolerance.
    if max(footer_differences)>2:raise AssertionError(f'{name}: moving footer')
    if blank_graph:raise AssertionError(f'{name}: missing teaching graph: {blank_graph}')
    if edge_ink:raise AssertionError(f'{name}: canvas edge clipping: {edge_ink}')
    if max(difference)>1:raise AssertionError(f'{name}: loop endpoints differ: {difference}')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('build_root',type=Path);parser.add_argument('names',nargs='*')
    args=parser.parse_args();base=args.build_root.resolve()
    if not base.is_relative_to((ROOT/'build/manim').resolve()):raise ValueError('build root outside animation pipeline')
    results={name:inspect(base,name) for name in (args.names or SCENES)}
    (base/'review').mkdir(exist_ok=True)
    (base/'review'/('media-'+('-'.join(args.names) or 'all')+'.json')).write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(results,ensure_ascii=False,indent=2))
