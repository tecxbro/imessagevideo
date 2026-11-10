"""Visible viewport intersections do not imply a shrunken card. Preserve camera scale, then clip naturally."""
from pathlib import Path
import json,numpy as np
R=Path('/workspace/imessage-recreations/references/01-photonhq');p=R/'scene-final-v4.json';s=json.loads(p.read_text());ledger=json.loads((R/'wall-ocr-provenance.json').read_text());nodes={}
def visit(l):
 if l['id'].startswith('ocr-wall-') and l.get('type')=='image':nodes[l['id']]=l
 for c in l.get('children',[]):visit(c)
for l in s['layers']:visit(l)
scales={}
for rec in ledger:
 l=nodes[rec['id']];cw,ch=l['width'],l['height'];b=rec['sourceBounds']
 for m in rec['observations']:
  bb=(m['x'],m['y'],m['x']+cw*m['scaleX'],m['y']+ch*m['scaleY']);t=round(m['t'],5);key=(rec['phase'],t);scales.setdefault(key,{'x':[],'y':[]})
  if b[0]>3 and b[2]<1917 and bb[0]>3 and bb[2]<1917:scales[key]['x'].append(m['scaleX'])
  if b[1]>3 and b[3]<1077 and bb[1]>3 and bb[3]<1077:scales[key]['y'].append(m['scaleY'])
changes=[]
for rec in ledger:
 l=nodes[rec['id']];cw,ch=l['width'],l['height'];ms=[]
 for m in rec['observations']:
  bb=[m['x'],m['y'],m['x']+cw*m['scaleX'],m['y']+ch*m['scaleY']];left=bb[0]<4;right=bb[2]>1916;top=bb[1]<4;bottom=bb[3]>1076
  if not(left or right or top or bottom):continue
  global_s=scales[(rec['phase'],round(m['t'],5))];sx=m['scaleX'];sy=m['scaleY'];x,y=m['x'],m['y']
  if left or right:
   sx=float(np.median(global_s['x'])) if global_s['x'] else (sy if not(top or bottom) else sx);x=bb[2]-cw*sx if left else bb[0]
  if top or bottom:
   sy=float(np.median(global_s['y'])) if global_s['y'] else sx;y=bb[3]-ch*sy if top else bb[1]
  fixed=dict(x=x,y=y,scaleX=sx,scaleY=sy)
  for k,v in fixed.items():
   for q in l['keyframes'][k]:
    if abs(q['t']-m['t'])<.00001:q['value']=v
  ms.append(dict(t=m['t'],sourceVisibleBounds=bb,corrected=fixed))
 if ms:changes.append(dict(id=l['id'],phase=rec['phase'],measurements=ms))
s['source']['notes']+=' Viewport-clipped artwork retains measured camera scale and anchors to its visible opposite edge; visible component bounds are intersections, not a request to squash the original card.';p.write_text(json.dumps(s,indent=2));(R/'clipped-card-refinement.json').write_text(json.dumps(changes,indent=2));print('Corrected viewport clipping on',len(changes),'individual cards')
