"""Apply bounded native613–615 photo anchors to the merged immutablev18 scene."""
from pathlib import Path
import argparse,copy,json,math
P=Path(__file__).parent

def apply_native_giant(scene,spec):
 s=copy.deepcopy(scene)
 for u in spec['updates']:
  frame,id=u['frame'],u['photo'];t=frame/30;groups=[g for g in s['layers']if g.get('semanticPhotoId')=='rene-final11-group-'+id and g.get('start',0)<=t<g.get('end',s['duration'])]
  if len(groups)!=1:raise ValueError(f'Expected one native photo {id} at{frame}, got{len(groups)}')
  g=groups[0];w,h=g['children'][0]['width'],g['children'][0]['height'];D=u['diameter'];values={'x':u['cx']-D/2,'y':u['cy']-D/2,'scaleX':D/w,'scaleY':D/h,'blur':u['blurFraction']*w,'opacity':u['opacity']}
  if not all(math.isfinite(v)for v in values.values()):raise ValueError('Nonfinite camera')
  for key,value in values.items():
   keys=g['keyframes'][key]
   if not any(abs(q['t']-t)<1e-9 for q in keys):raise ValueError(f'Missing native frame key {frame} {id} {key}')
   keys[:]=[q for q in keys if abs(q['t']-t)>1e-9];keys.append({'t':t,'value':float(value),'ease':'linear'});keys.sort(key=lambda q:q['t'])
  g['nativeScreenAnchor']='Bounded partial-offscreen native camera calibrated against the actual source; no source-frame bitmap or identity change.'
 s['source']['notes']+=' Bounded native613–615 giant-photo anchor refinement retains the same static original photographed discs and source depth order.'
 return s

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--spec',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=json.load(open(a.input))
 def absolute(ls):
  for l in ls:
   if l.get('src')and not l['src'].startswith(('data:','http:','https:','/')):l['src']=str((a.input.parent/l['src']).resolve())
   absolute(l.get('children',[]))
 absolute(s['layers'])
 for f in s.get('fonts',[]):
  if not f['src'].startswith(('data:','http:','https:','/')):f['src']=str((a.input.parent/f['src']).resolve())
 result=apply_native_giant(s,json.load(open(a.spec)));a.output.write_text(json.dumps(result,indent=2)+'\n');print(a.output)
