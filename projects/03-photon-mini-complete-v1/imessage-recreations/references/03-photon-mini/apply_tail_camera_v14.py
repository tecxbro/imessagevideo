"""Correct the measured lunch-phone endpoint without changing world food poses."""
from pathlib import Path
import json,copy,sys
p=Path(__file__).parent;sys.path.insert(0,str(p.parents[1]/'engines'));from render_pillow import state

def apply_tail(scene):
 s=copy.deepcopy(scene)
 if s.get('tail_camera_v14'):return s,s['tail_camera_v14']
 roots={x['id']:x for x in s['layers']};data=json.loads((p/'celebration-tail-camera-v14-proposals.json').read_text());proof=[];baseline={key:copy.deepcopy(roots[key]) for key in ['measured-lunch-device-v13','measured-lunch-ui-v13','measured-lunch-bezel-overlay-v13']}
 for r in data:
  f=r['frame'];t=f/30;a=r['source'];b=r['candidate']
  if a is None or b is None:raise ValueError(r)
  rx=(a[2]-a[0])/(b[2]-b[0]);ry=(a[3]-a[1])/(b[3]-b[1]);poses={}
  for ident in ['measured-lunch-device-v13','measured-lunch-ui-v13','measured-lunch-bezel-overlay-v13']:
   node=roots[ident];old=state(baseline[ident],t);values={'x':a[0]+(old['x']-b[0])*rx,'y':a[1]+(old['y']-b[1])*ry,'scaleX':old['scaleX']*rx,'scaleY':old['scaleY']*ry};poses[ident]=values
   for key,value in values.items():
    track=node.setdefault('keyframes',{}).setdefault(key,[]);q=next((q for q in track if abs(q['t']-t)<1e-8),None)
    if q:q['value']=value;q['ease']='linear'
    else:track.append({'t':t,'value':value,'ease':'linear'});track.sort(key=lambda q:q['t'])
  proof.append({'frame':f,'source_bezel':a,'candidate_bezel':b,'ratios':[rx,ry],'poses':poses})
 s['source']['notes']+=' V14 tail phone787–799: same connected opaque-bezel component fits independent x/y bounds. Legacy26.7 next-shot endpoint wrongly enlarged frame799 beforeactualcut800. World food/order layers untouched.'
 s['tail_camera_v14']=proof
 return s,proof
if __name__=='__main__':
 s=json.loads((p/'closed-menu-v14.scene.json').read_text());s,proof=apply_tail(s);(p/'tail-camera-v14.scene.json').write_text(json.dumps(s,indent=2));(p/'tail-camera-v14-changes.json').write_text(json.dumps({'scope':[787,799],'measurements':proof,'world_food_unchanged':True},indent=2));print('appliedtail',len(proof))
