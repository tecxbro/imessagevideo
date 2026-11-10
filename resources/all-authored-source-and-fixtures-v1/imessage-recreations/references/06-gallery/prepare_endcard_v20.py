"""Replace only isolated static end-card typography with its native outline."""
from pathlib import Path
import importlib.util,json,copy
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;ROOT=D.parent.parent;INPUT=ROOT/'outputs/06-gallery/final-v19/scene.json';s=json.loads(INPUT.read_text())
def absolute(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src' and isinstance(v,str) and not v.startswith('data:'):o[k]=str((INPUT.parent/v).resolve())
   else:absolute(v)
 elif isinstance(o,list):
  for q in o:absolute(q)
absolute(s)
spec=importlib.util.spec_from_file_location('trace',D.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace)
im=np.array(Image.open(D/'assets/endcard-domain-v20-source.png').convert('RGB')).mean(2);box=[820,470,1340,600];x0,y0,x1,y1=box;alpha=(255-im)/255;path,stats=trace.trace_alpha(alpha,x0,y0)
g=next(q for q in s['layers'] if q['id']=='g-1360');old=copy.deepcopy(g);g['children']=[q for q in g['children'] if q['id']!='t-1359'];g['children'].append(dict(type='path',id='v20-endcard-original-domain',d=path,fill='#000000',semanticText='rene.co',sourceFrame=1625,sourceBounds=box))
(D/'endcard-v20-patch.json').write_text(json.dumps(dict(replace={'g-1360':g},sourceBounds=box,sourceFrame=1625,stats=stats),indent=2));(D/'scene-endcard-v20.json').write_text(json.dumps(s,indent=2)+'\n');print(stats)
