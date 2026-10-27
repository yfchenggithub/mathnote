"""Record/verify read-only formal C084 inputs; no mutations outside build."""
import hashlib,json,sys
from pathlib import Path
uid=Path(__file__).resolve().parent.parent;root=uid.parents[1]
output=root/'build/manim/C084/focal_bisector/formal_sources.json'
files=[p for p in uid.iterdir() if p.is_file()]+list((uid/'images').glob('*'))+list((uid/'pdfs').glob('*'))+list((root/'assets/tikz').glob('C084_*.tex'))
hashes={str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}
if '--record' in sys.argv:
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(hashes,indent=2),encoding='utf8');print(f'Recorded {len(hashes)} formal inputs')
else:
 assert hashes==json.loads(output.read_text(encoding='utf8')),'Formal C084 inputs changed'
 print(f'PASS: all {len(hashes)} formal input hashes unchanged')
