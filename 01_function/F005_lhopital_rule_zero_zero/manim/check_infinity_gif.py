"""Supplementary all-frame technical/layout checks for this F005 scene."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageSequence
p=argparse.ArgumentParser();p.add_argument('gif');p.add_argument('--report',required=True);a=p.parse_args()
g=Image.open(a.gif);brand_hashes=set();edge_ink=[];reading_failures=[];timeline=0;frames=0;brand_reference=None;max_brand_mask_difference=0;min_brand_ink=1000000
for i,fr in enumerate(ImageSequence.Iterator(g)):
 rgb=np.asarray(fr.convert('RGB'));background=rgb[0,0].astype(int)
 delta=np.max(np.abs(rgb.astype(int)-background),axis=2)
 edge=np.concatenate([delta[:12].ravel(),delta[-12:].ravel(),delta[:,:12].ravel(),delta[:,-12:].ravel()])
 if (edge>35).any():edge_ink.append(i)
 brand=rgb[930:1010,25:550]
 brand_hashes.add(hashlib.sha256(brand.tobytes()).hexdigest())
 mask=brand.mean(axis=2)<160
 if brand_reference is None:brand_reference=mask
 max_brand_mask_difference=max(max_brand_mask_difference,float(np.logical_xor(mask,brand_reference).mean()))
 min_brand_ink=min(min_brand_ink,int(mask.sum()))
 # The animated readouts must be in their lower-right reading area, even at t=0.
 # Fading transition is excluded. This checks location/presence, not OCR accuracy.
 if not 6.98<=timeline<=7.5:
  patch=delta[610:775,340:450]
  if (patch>40).sum()<80:reading_failures.append(i)
 timeline+=fr.info['duration']/1000;frames+=1
r={'frames':frames,'duration_seconds':round(timeline,3),'fixed_brand_regions':len(brand_hashes),'edge_ink_frames':edge_ink,'missing_readout_frames':reading_failures,'note':'Presence/edge checks supplement, and do not replace, mathematical and visual review.'}
# MP4 compression and GIF quantization vary antialias pixels. Require stable text
# masks (under 0.5% differing pixels) and substantial visible text on EVERY frame.
r['max_brand_dark_mask_difference_fraction']=max_brand_mask_difference
r['min_brand_dark_pixels']=min_brand_ink
r['pass']=max_brand_mask_difference<.005 and min_brand_ink>1500 and not edge_ink and not reading_failures
Path(a.report).write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r));assert r['pass']
