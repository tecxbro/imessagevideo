"""Derive focused typography revision from frozen measured-fit parent."""
from pathlib import Path
import json
p=Path(__file__).parent
s=json.loads((p/'scene-v2-nativefit.json').read_text())
menu=next(l for l in s['layers'] if l.get('start')==10.15 and any(c.get('text')=='Mexican' for c in l.get('children',[])))
for child in menu['children']:
 if child.get('type')=='text':child['fontFamily']='SF Pro Display'
s['source']['notes']+=' Final typography correction: six native option-list labels use SF Pro Display60; reference blue Mexican ink212px at12s and264px at11s establishes1.245camera scale and family.'
(p/'scene-v3-typography.json').write_text(json.dumps(s,indent=2))
