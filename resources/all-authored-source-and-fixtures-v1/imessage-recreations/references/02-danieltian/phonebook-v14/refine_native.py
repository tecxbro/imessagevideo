"""Targeted actual-error correction: selected bold glyphs and smooth query optical reveal."""
from pathlib import Path
import json,math,importlib.util,time
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;spec=json.loads((R/'elements-candidate.json').read_text());measure=json.loads((R/'dense-measurements.json').read_text());s=importlib.util.spec_from_file_location('trace',R.parent/'trace_glyphs.py');trace=importlib.util.module_from_spec(s);s.loader.exec_module(trace)
def paths(a,x,y,id,levels):
 peak=float(a.max());out=[]
 if peak<.003:return out
 previous=0.
 for j,t in enumerate(np.linspace(.5/levels,1-.5/levels,levels)):
  d,stats=trace.trace_alpha(a,x,y,threshold=float(t*peak));level=min(1,peak*(j+1)/levels);opacity=(level-previous)/(1-previous) if previous<1 else 0;previous=level
  if d:out.append(dict(id=id+'-'+str(j),type='path',d=d,fill='#000000',opacity=float(opacity)))
 return out
selected={'pb-number-1-1':'+1 (702) 555-0179','pb-number-1-3':'+1 (971) 555-0117','pb-number-3-2':'+1 (718) 555-0136','pb-number-6-2':'+1 (503) 555-0163'};new=[];changed=[];ledger=[];cache={};start=time.monotonic()
for n in spec['layers']:
 id=n['id'];f=round(n['start']*30);replace=None
 if id.startswith('pb14-query-'):
  src=cache.setdefault(f,np.asarray(Image.open(R/'source-native'/f'{f:06d}.png').convert('RGB')).astype(float));L,T,RR,B=n['provenance']['bounds'];ar=src[T:B,L:RR];a=np.clip((253-ar.mean(2))/253,0,1)*(ar.max(2)-ar.min(2)<12);replace={**n,'children':paths(a,L,T,id+'-ink',48)};ledger.append(dict(frame=f,id=id,kind='48-level native optical query contour',bounds=[L,T,RR,B]))
 elif id.startswith('pb14-field-'):
  cell='pb-number-'+id.rsplit('pb-number-',1)[1]
  if cell in selected:
   q=next(q for q in measure[str(f)]['cells']if q['id']==cell);M=np.array(q['matrix']);W,H=q['width'],q['height'];corn=M@np.array([[0,W,W,0],[0,0,H,H],[1,1,1,1]]);L=max(0,int(math.floor(corn[0].min()))-10);T=max(0,int(math.floor(corn[1].min()))-10);RR=min(1920,int(math.ceil(corn[0].max()))+11);B=min(1080,int(math.ceil(corn[1].max()))+11);src=cache.setdefault(f,np.asarray(Image.open(R/'source-native'/f'{f:06d}.png').convert('RGB')).astype(float));ar=src[T:B,L:RR];a=np.clip((253-ar.mean(2))/253,0,1)*(ar.max(2)-ar.min(2)<18)
   if a.max()>.35:
    replace=dict(id=id,type='group',start=n['start'],end=n['end'],semanticCopy=selected[cell],provenance={'sourceFrame':f,'bounds':[L,T,RR,B],'material':'native semantic outline of actual selected-weight phone number; no bitmap text replacement'},children=paths(a,L,T,id+'-selected-ink',7));ledger.append(dict(frame=f,id=id,kind='native selected-weight phone glyphs',bounds=[L,T,RR,B],peak=float(a.max())))
 if replace is not None:new.append(replace);changed.append(f)
 else:new.append(n)
 if len(new)%200==0:print('processed',len(new),'seconds',round(time.monotonic()-start,1),flush=True)
spec['layers']=new;spec['notes']+=' Selected phone numbers use their measured native weight-change contours. Query optical reveal uses48 nested native contours to avoid9-level posterization. The isolated source477 chroma macroblock cast is not fabricated as a full-frame texture.';(R/'elements-refined.json').write_text(json.dumps(spec,separators=(',',':')));(R/'refinement-ledger.json').write_text(json.dumps(ledger,indent=2));(R/'refinement-changed-frames.json').write_text(json.dumps(sorted(set(changed))));print('DONE',len(ledger),'replacements',len(set(changed)),'frames',time.monotonic()-start,flush=True)
