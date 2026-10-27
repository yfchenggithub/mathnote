"""Audit actual rendered model samples and all GIF frames; save real key frames."""
from pathlib import Path
import argparse,json,math
from PIL import Image,ImageSequence,ImageChops


def verify(work:Path,gif_path:Path):
    samples=json.loads((work/'media/C085_frame_math.json').read_text(encoding='utf8'))
    # Manim reuses still frames during holds; sample count follows the 7.4 s motion,
    # not the whole movie duration. Every changing state must be audited.
    assert len(samples)>=178
    for d in samples:
        a,b,c=d['a'],d['b'],d['c'];F,M,N=d['F'],d['M'],d['N']
        def eq(x,y):assert math.isclose(x,y,rel_tol=1e-8,abs_tol=1e-8),(x,y)
        eq(c*c,a*a+b*b);eq(M[0]*M[0]/(a*a)-M[1]*M[1]/(b*b),1)
        eq(M[1],b/a*(M[0]-c));eq(N[1],-b/a*N[0]);eq(N[1],b/a*(N[0]-c))
        eq(math.dist(F,M),d['fm']);eq(math.dist(M,N),d['mn'])
        eq(math.dist(F,M)/math.dist(M,N),b*b/(a*a));eq(d['ratio'],d['e']**2-1)
        assert N[0]<M[0]<F[0] and 2.25-1e-9<=b<=4+1e-9
        x0,x1,y0,y1=d['core_bounds'];assert -4.15<x0<x1<4.15 and -3<y0<y1<5
    assert min(d['b'] for d in samples)<2.251 and max(d['b'] for d in samples)>3.999
    review=work/'review';review.mkdir(exist_ok=True)
    times=[0,2,6.5,9.5,12.1,15.4,18.5,21.7,24,27.7]
    extracted=[];next_i=0;t=0;mins=[1e9,1e9];maxs=[0,0];first=None;last=None;frame_count=0
    with Image.open(gif_path) as gif:
        for i,frame in enumerate(ImageSequence.Iterator(gif)):
            im=frame.convert('RGB');im.load();duration=frame.info['duration']/1000
            diff=ImageChops.difference(im,Image.new('RGB',im.size,im.getpixel((0,0))))
            channels=diff.split();mask=ImageChops.lighter(ImageChops.lighter(channels[0],channels[1]),channels[2]).point(lambda p:255 if p>35 else 0)
            bbox=mask.getbbox();assert bbox is not None
            x0,y0,x1,y1=bbox
            assert x0>=24 and y0>=24 and x1<=552 and y1<=1000,(i,bbox)
            mins=[min(mins[0],x0),min(mins[1],y0)];maxs=[max(maxs[0],x1),max(maxs[1],y1)]
            if first is None:first=im.copy()
            last=im.copy();frame_count+=1
            while next_i<len(times) and t+duration>times[next_i]:
                name=f'key-{next_i:02d}.png';im.save(review/name)
                extracted.append({'frame':i,'time':round(t,3),'file':name});next_i+=1
            t+=duration
        last.save(review/'key-last.png')
    loop_diff=ImageChops.difference(first,last)
    exact_loop=loop_diff.getbbox() is None
    result={'status':'PASS','actual_model_samples':len(samples),'all_gif_frames':frame_count,
            'content_bounds':[int(mins[0]),int(mins[1]),maxs[0],maxs[1]],
            'duration_seconds':round(t,3),'first_last_pixel_identical':exact_loop,
            'key_frames':extracted}
    (work/'render_audit.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('work',type=Path);p.add_argument('gif',type=Path);a=p.parse_args();verify(a.work,a.gif)
