"""Decode every actual GIF frame; check brand persistence, edges, and loop."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

def review(path,output):
    output.mkdir(parents=True,exist_ok=True)
    im=Image.open(path)
    frames=[]; timestamps=[]; elapsed=0; footers=[]; edge_ink=[]; footer_diffs=[]
    for i in range(im.n_frames):
        im.seek(i)
        frame=im.convert('RGB').copy()
        frames.append(frame)
        timestamps.append(elapsed)
        elapsed+=im.info.get('duration',0)
        arr=np.asarray(frame)
        # Fixed independent bottom area, below all changing math.
        region=arr[935:1005,25:551]
        footers.append(hashlib.sha256(region.tobytes()).hexdigest())
        if i==0: reference_footer=region.astype(np.int16)
        delta=np.abs(region.astype(np.int16)-reference_footer)
        footer_diffs.append((float(delta.mean()),float(np.any(delta>20,axis=2).mean())))
        edge=np.concatenate([arr[:12].reshape(-1,3),arr[-12:].reshape(-1,3),
                             arr[:,:12].reshape(-1,3),arr[:,-12:].reshape(-1,3)])
        edge_ink.append(int(np.count_nonzero(np.min(edge,axis=1)<180)))
    targets=[0,1.8,3.2,4.8,6.2,7.4,8.5,10.2,11.8,13.6,15.5,elapsed/1000-.15]
    chosen=[]
    sheet=Image.new('RGB',(3*288,4*540),'white')
    draw=ImageDraw.Draw(sheet)
    for slot,t in enumerate(targets):
        index=min(range(len(timestamps)),key=lambda k:abs(timestamps[k]-t*1000))
        frames[index].save(output/f'frame-{index:03d}.png')
        row,col=divmod(slot,3)
        sheet.paste(frames[index].resize((288,512)),(col*288,row*540+24))
        draw.text((col*288+8,row*540+4),f'{index}: {timestamps[index]/1000:.2f}s',fill='black')
        chosen.append({'frame':index,'ms':timestamps[index]})
    sheet.save(output/'contact_sheet.png')
    first=np.array(frames[0],dtype=np.int16); last=np.array(frames[-1],dtype=np.int16)
    loop_delta=np.abs(first-last)
    result={'frames':len(frames),'duration_ms':elapsed,'keyframes':chosen,
            'fixed_footer_distinct_encoded_regions':len(set(footers)),
            'footer_max_mean_channel_difference':max(x[0] for x in footer_diffs),
            'footer_max_fraction_pixels_over_20':max(x[1] for x in footer_diffs),
            'edge_ink_max':max(edge_ink),'loop_mean_channel_difference':float(loop_delta.mean()),
            'loop_pixels_changed_fraction':float(np.any(loop_delta>8,axis=2).mean())}
    (output/'review.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    # MP4/GIF quantization changes a few edge pixels even for static lettering.
    if max(x[0] for x in footer_diffs)>1.5 or max(x[1] for x in footer_diffs)>.01:
        raise AssertionError('Brand footer changed visibly during animation')
    if max(edge_ink)!=0: raise AssertionError('Ink reaches the 12-pixel outer safe margin')
    if result['loop_mean_channel_difference']>1.5 or result['loop_pixels_changed_fraction']>.03:
        raise AssertionError('Loop boundary differs materially')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('gif',type=Path); parser.add_argument('output',type=Path)
    args=parser.parse_args(); review(args.gif,args.output)
