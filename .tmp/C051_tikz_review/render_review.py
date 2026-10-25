from pathlib import Path
import subprocess
from PIL import Image
pdf='build/conclusion_pdfs/C051_parabola_focal_radius_coordinate.pdf'
dest=Path('.tmp/C051_tikz_review')
subprocess.run(['pdftoppm','-r','190','-png',pdf,str(dest/'checked')],check=True)
# Each crop contains the full TikZ frame plus a margin, at the original 300 dpi.
figures=[(2,'focus_directrix_split',(94,139,502,439)),
         (3,'math_audit_geometry',(94,121,502,406)),
         (5,'area_height',(94,208,502,459)),
         (7,'four_openings',(94,138,502,528)),
         (8,'on_curve_requirement',(94,138,502,415))]
for page,name,bbox in figures:
    prefix=dest/('hi_'+name)
    subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-singlefile','-r','300','-png',pdf,str(prefix)],check=True)
    im=Image.open(str(prefix)+'.png')
    crop=im.crop(tuple(round(v*300/72) for v in bbox))
    crop.save(dest/('crop_'+name+'.png'),dpi=(300,300))
print('9 pages at 190 dpi; 5 full-frame crops at 300 dpi')
