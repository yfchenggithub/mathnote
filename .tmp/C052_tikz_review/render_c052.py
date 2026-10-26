from pathlib import Path
import subprocess
from PIL import Image
pdf='build/conclusion_pdfs/C052_ellipse_focal_chord_length.pdf'
d=Path('.tmp/C052_tikz_review')
subprocess.run(['pdftoppm','-r','190','-png',pdf,str(d/'checked')],check=True)
figures=[(8,'definition_pythagoras_b',(92,119,504,422)),(5,'proof_notation',(92,142,504,453)),(2,'focal_chord_split',(92,138,504,422)),
         (3,'three_directions',(92,119,504,401)),
         (4,'left_right_focus',(92,119,504,392)),
         (7,'definition_pythagoras',(92,119,504,422)),
         (11,'supplementary_angles',(92,223,504,495)),
         (14,'vertical_major_axis_angle',(92,149,504,482)),
         (15,'ordinary_chord_vs_latus',(92,119,504,400))]
for page,name,bbox in figures:
    prefix=d/('hi_'+name)
    subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-singlefile','-r','300','-png',pdf,str(prefix)],check=True)
    Image.open(str(prefix)+'.png').crop(tuple(round(v*300/72) for v in bbox)).save(d/('crop_'+name+'.png'),dpi=(300,300))
print('17 pages rendered at 190 DPI; 9 full-frame diagram crops at 300 DPI.')
