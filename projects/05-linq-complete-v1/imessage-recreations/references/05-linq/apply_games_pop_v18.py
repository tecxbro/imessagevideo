"""Scoped Games material-coverage and label-motion correction; camera unchanged."""
from pathlib import Path
import copy,json
P=Path(__file__).parent

def apply_games_pop(scene,spec=None):
 spec=spec or json.load(open(P/'games-pop-v18-measure/spec-frozen-v18.json'))
 s=copy.deepcopy(scene);groups=[]
 def find(ls):
  for n in ls:
   if n['id']==spec['groupId']:groups.append(n)
   find(n.get('children',[]))
 find(s['layers']);assert len(groups)==1;g=groups[0];byid={n['id']:n for n in g['children']}
 for id,updates in spec['labelUpdates'].items():
  n=byid[id];keys=n.setdefault('keyframes',{});xs={q['frame']:q['x']for q in updates};ys={q['frame']:q['y']for q in updates}
  for q in keys['y']:
   frame=round(q['t']*30)
   if frame in ys:q['value']=ys[frame]
  if xs:
   original=n.get('x',0);keys['x']=[{'t':frame/30,'value':xs.get(frame,original),'ease':'linear'}for frame in range(130,150)]
  optics={q['frame']:q for q in updates if 'opacity'in q or'blur'in q}
  for q in keys.get('opacity',[]):
   frame=round(q['t']*30)
   if frame in optics and'opacity'in optics[frame]:q['value']=optics[frame]['opacity']
  if any('blur'in q for q in updates):keys['blur']=[{'t':f/30,'value':optics.get(f,{}).get('blur',n.get('blur',0)),'ease':'linear'}for f in range(130,150)]
 existing=set()
 def collect(ls):
  for item in ls:existing.add(item['id']);collect(item.get('children',[]))
 collect(s['layers']);newIds=[item['id']for item in spec['materialNodes']];assert len(newIds)==len(set(newIds))and not(existing&set(newIds)),'Games helper must apply only once'
 g['children'].extend(copy.deepcopy(spec['materialNodes']));s['source']['notes']+=' Games early-pop correction: existing identity camera and accurate painted pixels retained. Saturation-only crop bounds had omitted dark/desaturated lower tile material; separately bounded source-observed lower strips restore it. Native semantic label paths use independently measured source offsets instead of color-content-driven tile-top drift, with measured early opacity/blur and a single bounded blurred header pose at130; held later paths/camera remain unchanged. Bitmap animated UI internals remain declared; no whole-frame/video layer.'
 return s

if __name__=='__main__':
 import sys
 source=Path(sys.argv[1]).resolve();output=Path(sys.argv[2]).resolve();specPath=Path(sys.argv[3]).resolve();s=json.load(open(source))
 def absolute(ls):
  for n in ls:
   if n.get('src')and not n['src'].startswith(('data:','http:','https:','/')):n['src']=str((source.parent/n['src']).resolve())
   absolute(n.get('children',[]))
 absolute(s['layers'])
 for f in s.get('fonts',[]):
  if not f['src'].startswith(('data:','http:','https:','/')):f['src']=str((source.parent/f['src']).resolve())
 result=apply_games_pop(s,json.load(open(specPath)));output.write_text(json.dumps(result,indent=2)+'\n');print(output)
