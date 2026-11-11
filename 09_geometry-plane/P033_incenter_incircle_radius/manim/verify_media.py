"""Full-frame GIF checks and real keyframe extraction for P033 only."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
from PIL import Image,ImageChops,ImageStat,ImageOps,ImageDraw

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts/manim'))
from verify_gif import verify_gif

SCENES={'incenter_area':'P033IncenterArea','tangent_lengths':'P033TangentLengths','special_triangles':'P033SpecialTriangles'}

def inspect(base,name,scene):
    work=base/'P033'/name
    path=work/f'{name}.gif'
    evidence=base/'review'/name;evidence.mkdir(parents=True,exist_ok=True)
    technical=verify_gif(path,width=576,height=1024)
    story=json.loads((work/'media'/f'{scene}-story.json').read_text(encoding='utf-8'))
    moments=[(0.,'first')]+[(max(0,event['time']-.25),event['name']) for event in story['keyframes']]
    if name=='incenter_area':moments += [(7.25,'motion_quarter'),(8.25,'motion_half'),(9.25,'motion_three_quarters')]
    moments.sort()
    snapshots={};footer_hashes=set();footer_differences=[];elapsed=0;blank_body=[]
    with Image.open(path) as gif:
        for i in range(gif.n_frames):
            gif.seek(i);frame=gif.convert('RGB')
            if i==0:
                first=frame.copy()
                footer_reference=frame.crop((0,925,576,1024))
            last=frame.copy()
            footer=frame.crop((0,925,576,1024))
            footer_hashes.add(sha256(footer.tobytes()).hexdigest())
            footer_differences.append(max(ImageStat.Stat(ImageChops.difference(footer_reference,footer)).mean))
            body=frame.crop((35,165,541,900))
            background=Image.new('RGB',body.size,frame.getpixel((1,1)))
            delta=ImageChops.difference(body,background).convert('L')
            visible=sum(delta.histogram()[21:])
            if visible<300:blank_body.append(i)
            for when,label in moments:
                if label not in snapshots and elapsed+gif.info['duration']/1000>=when:
                    snapshots[label]=frame.copy()
                    frame.save(evidence/f'{label}.png')
            elapsed+=gif.info['duration']/1000
        snapshots['last']=last;last.save(evidence/'last.png')
    difference=ImageStat.Stat(ImageChops.difference(first,last)).mean
    columns=3;rows=(len(snapshots)+columns-1)//columns
    sheet=Image.new('RGB',(columns*300,rows*550),'#D7DCE3');draw=ImageDraw.Draw(sheet)
    for i,(label,frame) in enumerate(snapshots.items()):
        x=(i%columns)*300;y=(i//columns)*550
        sheet.paste(ImageOps.contain(frame,(288,512)),(x+6,y+25));draw.text((x+8,y+7),label,fill='black')
    sheet.save(evidence/'contact.png')
    result={'path':path.relative_to(ROOT).as_posix(),'technical':technical,
            'footer_distinct_regions':len(footer_hashes),'footer_max_mean_absolute_difference':max(footer_differences),
            'footer_encoding_tolerance':2.0,'blank_body_frames':blank_body,
            'first_last_mean_absolute_difference':difference,'keyframes':list(snapshots)}
    # MP4 is lossy and the frozen GIF exporter quantizes colors. Byte-identical
    # patches are therefore inappropriate: permit < 2/255 RGB mean variation,
    # while the actual footer objects and coordinates remain fixed in the Scene.
    if max(footer_differences)>2:raise AssertionError(f'{name}: footer visibly changed between frames')
    if blank_body:raise AssertionError(f'{name}: blank teaching region {blank_body}')
    if max(difference)>1:raise AssertionError(f'{name}: loop endpoints do not match: {difference}')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('build_root',type=Path);parser.add_argument('names',nargs='*')
    args=parser.parse_args();base=args.build_root.resolve()
    if not base.is_relative_to((ROOT/'build/manim').resolve()):raise ValueError('build root outside dynamic pipeline')
    results={name:inspect(base,name,SCENES[name]) for name in (args.names or SCENES)}
    (base/'review').mkdir(exist_ok=True)
    report=base/'review'/('media-'+('-'.join(args.names) or 'all')+'.json')
    report.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(results,ensure_ascii=False,indent=2))
