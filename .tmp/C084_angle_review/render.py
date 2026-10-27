from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,json,xml.etree.ElementTree as ET
w=Path('D:/mathnote/.tmp/C084_angle_review');pdf=Path('D:/mathnote/build/conclusion_pdfs/C084_hyperbola_focal_triangle_internal_angle_bisector.pdf')
pages=sorted(w.glob('final-*.png'))
for start in range(0,len(pages),3):
 sheet=Image.new('RGB',(1890,930),'#ddd');d=ImageDraw.Draw(sheet)
 for j,p in enumerate(pages[start:start+3]):
  im=Image.open(p);im.thumbnail((630,891));sheet.paste(im,(j*630,30));d.text((j*630+15,8),p.name,fill='black')
 sheet.save(w/f'sheet-{start//3+1}.png')
heights={'先看主角':10,'第一步':8,'方法一：两个直角三角形':9,'方法四：先看三角形':8.5,'方法五：先把两条射线':8,'关于':9,'先固定横坐标':10,'防混淆':9,'倒角公式：先看':13.5}
raw=(w/'bbox.html').read_text(encoding='utf8')
doc=ET.ElementTree(ET.fromstring(''.join(c for c in raw if ord(c)>=32 or c in '\n\r\t')));ns={'x':'http://www.w3.org/1999/xhtml'}
out=[]
for n,page in enumerate(doc.findall('.//x:page',ns),1):
 words=page.findall('x:word',ns)
 title=next((q for q in words if any(t in (q.text or '') for t in heights)),None)
 if title is None:continue
 h=next(v for t,v in heights.items() if t in (title.text or ''));top=float(title.attrib['yMin'])-13.5
 subprocess.run(['pdftoppm','-f',str(n),'-l',str(n),'-r','300','-png',str(pdf),str(w/'hi')],check=True)
 p=next(w.glob('hi-*.png'));im=Image.open(p);coords=(92,top-3,503,top+h*72/2.54+3)
 target=w/f'figure-{n}.png';im.crop(tuple(round(v*300/72) for v in coords)).save(target);p.unlink()
 out.append({'page':n,'bbox':coords,'crop':target.name})
(w/'figure_map.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
