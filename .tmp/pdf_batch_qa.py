from pathlib import Path
import sys,subprocess,re,html,json,hashlib
from PIL import Image
sys.path.insert(0,str(Path.cwd()))
from scripts.build_conclusion_pdfs import build_wrapper_tex
uid=sys.argv[1];r=next(Path('03_conic').glob(uid+'_*'));p=Path('.tmp')/(uid+'_review');p.mkdir(exist_ok=True)
pdf=r/'pdfs'/(r.name+'.pdf');before=hashlib.sha256(pdf.read_bytes()).hexdigest()
(p/'diagnostic.tex').write_text(build_wrapper_tex((r/'main.tex').as_posix()),encoding='utf-8')
for dpi,name in [(200,'page'),(275,'detail')]:
 q=subprocess.run(['pdftoppm','-r',str(dpi),'-png',str(pdf),str(p/name)],capture_output=True)
 assert q.returncode==0 and not q.stderr,q.stderr[:500]
q=subprocess.run(['pdfinfo',str(pdf)],capture_output=True);info=q.stdout.decode(errors='replace');print(info)
q=subprocess.run(['pdftotext','-bbox',str(pdf),str(p/'bbox.html')],capture_output=True);assert not q.stderr
s=(p/'bbox.html').read_text(encoding='utf-8');crops=[]
for n,pg in enumerate(re.findall(r'<page .*?</page>',s,re.S),1):
 for tag in re.findall(r'<word .*?</word>',pg,re.S):
  text=html.unescape(re.sub('<[^>]+>','',tag));x=float(re.search(r'xMin="([-\d.]+)"',tag)[1]);y=float(re.search(r'yMin="([-\d.]+)"',tag)[1])
  if 105<x<115 and any(text.startswith(t) for t in sys.argv[2:]):
   box=(92,y-10.5,505,y-10.5+237)
   Image.open(p/f'detail-{n}.png').crop(tuple(round(v*275/72) for v in box)).save(p/f'crop-{n}.png');crops.append({'page':n,'title':text,'box':box});break
for _ in range(2):
 q=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','-output-directory='+str(p.resolve()),str((p/'diagnostic.tex').resolve())],capture_output=True)
 assert q.returncode==0,q.stdout[-2000:]
log=(p/'diagnostic.log').read_text(encoding='utf-8',errors='replace')
issues=[l for l in log.splitlines() if any(t in l for t in ['Overfull','Underfull','Warning','Missing character'])]
assert before==hashlib.sha256(pdf.read_bytes()).hexdigest(),'PDF changed during QA'
(p/'qa.json').write_text(json.dumps({'pdf':str(pdf),'sha256':before,'crops':crops,'issues':issues},ensure_ascii=False,indent=2),encoding='utf-8')
print('crop pages:',[c['page'] for c in crops]);print('diagnostic issues:',issues)
