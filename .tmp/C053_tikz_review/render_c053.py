from pathlib import Path
import subprocess
from PIL import Image

pdf='build/conclusion_pdfs/C053_parabola_focal_chord_length_inclination.pdf'
d=Path('.tmp/C053_tikz_review')
subprocess.run(['pdftoppm','-r','190','-png',pdf,str(d/'checked')],check=True)
figures=[(2,'focal_chord_notation',(92,120,504,465)),
         (3,'angle_comparison',(92,119,504,437)),
         (4,'forward_projection',(92,156,504,502)),
         (5,'backward_projection',(92,119,504,465)),
         (8,'opening_reflection',(92,236,504,544)),
         (12,'validity_comparison',(92,119,504,431)),
         (13,'vertical_axis_angle',(92,119,504,465))]
for p,n,b in figures:
 prefix=d/('hi_'+n)
 subprocess.run(['pdftoppm','-f',str(p),'-l',str(p),'-singlefile','-r','300','-png',pdf,str(prefix)],check=True)
 Image.open(str(prefix)+'.png').crop(tuple(round(v*300/72) for v in b)).save(d/('crop_'+n+'.png'),dpi=(300,300))
print('15 complete pages at 190 DPI and 7 full-frame crops at 300 DPI rendered.')
