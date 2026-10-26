from pathlib import Path
import subprocess
from PIL import Image
pdf='build/conclusion_pdfs/C051_parabola_focal_radius_coordinate.pdf'
d=Path('.tmp/C051_tikz_review')
subprocess.run(['pdftoppm','-r','190','-png',pdf,str(d/'review')],check=True)
figures=[(2,'focus_directrix_split',(92,138,504,442)),
         (3,'math_audit_geometry',(92,119,504,408)),
         (4,'position_and_minimum',(92,119,504,412)),
         (6,'coordinate_right_triangle',(92,139,504,423)),
         (7,'inverse_two_points',(92,155,504,510)),
         (8,'area_height',(92,125,504,379)),
         (10,'four_openings',(92,137,504,530)),
         (11,'on_curve_requirement',(92,137,504,417))]
for page,name,bbox in figures:
    pre=d/('enriched_hi_'+name)
    subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-singlefile','-r','300','-png',pdf,str(pre)],check=True)
    Image.open(str(pre)+'.png').crop(tuple(round(v*300/72) for v in bbox)).save(d/('enriched_crop_'+name+'.png'),dpi=(300,300))
print('Rendered 12 pages at 190 DPI and 8 full-frame crops at 300 DPI.')
