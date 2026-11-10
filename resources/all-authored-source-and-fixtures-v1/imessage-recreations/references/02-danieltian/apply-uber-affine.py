"""Bounded native affine entrance refinement, independent of other phonebook edits."""
from pathlib import Path
import argparse,json,copy,math
import numpy as np
REF=Path(__file__).resolve().parent;E=REF.parents[1]/'verification/fidelity-review/02-phonebook-branch'

def allnodes(layers):
 for l in layers:
  yield l
  yield from allnodes(l.get('children',[]))
def sample(l,k,f):
 t=f/30;keys=l.get('keyframes',{}).get(k)
 if not keys:return l.get(k,1 if k.startswith('scale') else 0)
 for a,b in zip(keys,keys[1:]):
  if a['t']<=t<=b['t']:
   p=(t-a['t'])/(b['t']-a['t']);return a['value']+(b['value']-a['value'])*p
 return keys[0 if t<keys[0]['t'] else -1]['value']
def track(p):return [dict(t=f/30,value=float(v),ease='linear') for f,v in p]
def apply(scene):
 scene=copy.deepcopy(scene);ns=list(allnodes(scene['layers']));uber=next(l for l in ns if l['id']=='pb-uber-eats');entry=next(l for l in ns if l['id']=='pbr-uber-entry');foreground=next(l for l in ns if l['id']=='pbr-uber-foreground');assert not any(l['id']=='pbr-uber-affine' for l in ns)
 fits=json.loads((E/'uber-entry-affines.json').read_text());fits[0]['params']=json.loads((E/'uber-affine-fit.json').read_text())['params']
 vals={k:[] for k in ['x','y','rotation','scaleX','scaleY','innerrotation']};measure=[]
 D=np.diag([entry['width']/595,entry['height']/110]);delta=np.array([entry['x'],entry['y']])
 for q in fits:
  f=q['frame'];a,b,e,tx,ty=q['params'];M=np.array([[a,b],[0,e]]);td=np.array([1160+tx,150+ty])-M@np.array([297.5,55]);G=np.diag([sample(uber,'scaleX',f),sample(uber,'scaleY',f)]);gt=np.array([sample(uber,'x',f),sample(uber,'y',f)]);W=np.linalg.inv(G)@M@np.linalg.inv(D);wt=np.linalg.inv(G)@(td-gt)-W@delta
  U,S,Vt=np.linalg.svd(W)
  if np.linalg.det(U)<0:U[:,1]*=-1;Vt[1,:]*=-1
  assert np.max(np.abs(U@np.diag(S)@Vt-W))<1e-10
  r1=math.degrees(math.atan2(U[1,0],U[0,0]));r2=math.degrees(math.atan2(Vt[1,0],Vt[0,0]));vv=[wt[0],wt[1],r1,S[0],S[1],r2]
  for k,v in zip(vals,vv):vals[k].append((f,v))
  measure.append(dict(frame=f,forward_asset_matrix=M.tolist(),forward_asset_translation=td.tolist(),relative_matrix=W.tolist(),relative_translation=wt.tolist(),outer_rotation=r1,inner_rotation=r2,singular_values=S.tolist()))
 innerimage=copy.deepcopy(entry);innerimage['id']='pbr-uber-affine-image';innerimage.pop('keyframes',None)
 inner=dict(type='group',id='pbr-uber-affine-inner',children=[innerimage],keyframes={'rotation':track(vals.pop('innerrotation'))})
 wrapper=dict(type='group',id='pbr-uber-affine',start=477/30,end=480/30,children=[inner],keyframes={k:track(v) for k,v in vals.items()})
 entry['keyframes']['opacity']=track([(475,1),(476,1),(477,0),(479,0),(480,1),(489,0)])
 foreground['children'].append(wrapper)
 scene['source']['notes']+=' Source15.9–15.9667s Uber entrance uses fitted native affine shear represented by two nested rotations and nonuniform scale; no new bitmap pose or schema feature.'
 return scene,measure
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();s,measure=apply(json.loads(args.input.read_text()));args.output.write_text(json.dumps(s,indent=2));meta=dict(input=str(args.input),output=str(args.output),changed_frame_ranges=[[477,479]],native_affine_measurements=measure,assets_added=0,notice='Three native frames only; native sampled validation accepted, intermediate projection remains a planar affine approximation.');(REF/'uber-affine-refinement.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2))
