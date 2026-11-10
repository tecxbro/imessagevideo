"""Repair independently measured simultaneous Muse-avatar crossfades only."""
from pathlib import Path
import copy,json,hashlib
HERE=Path(__file__).resolve().parent

def signature(node):
 def canon(v):
  if isinstance(v,float) and v.is_integer():return int(v)
  if isinstance(v,dict):return {k:(Path(x).name if k=='src' else canon(x)) for k,x in v.items()}
  if isinstance(v,list):return [canon(x) for x in v]
  return v
 return hashlib.sha256(json.dumps(canon(node),sort_keys=True,separators=(',',':')).encode()).hexdigest()

def apply(scene):
 spec=json.load(open(HERE/'patch-spec.json'));assert scene['fps']==30 and scene['width']==1920 and scene['height']==1080
 i=next(i for i,p in enumerate(scene['layers']) if p['id']==spec['parentID']);parent=scene['layers'][i];j=next(j for j,c in enumerate(parent['children']) if c['id']==spec['avatarID']);avatar=parent['children'][j];assert signature(avatar)==spec['originalAvatarSignature'],'existing avatar baseline changed'
 s=dict(scene);s['layers']=list(scene['layers']);p=dict(parent);p['children']=list(parent['children']);a=dict(avatar);a['keyframes']=dict(avatar['keyframes']);track=list(avatar['keyframes']['opacity'])
 for sample in spec['guardSamples']+spec['opacitySamples']:
  t=sample['frame']/scene['fps'];assert not any(abs(k['t']-t)<1e-10 for k in track),'duplicate opacity key';track.append(dict(t=t,value=sample['value'],ease='hold'))
 a['keyframes']['opacity']=sorted(track,key=lambda q:q['t']);p['children'][j]=a
 for c in spec['complements']:
  n=c['frame'];children=copy.deepcopy(avatar['children']);counter=[0]
  def rename(node):
   counter[0]+=1;node['id']=f"muse-continuation-v19-{n}-{counter[0]}-{node.get('id','node')}"
   for ch in node.get('children',[]):rename(ch)
  for ch in children:rename(ch)
  assert len(children)==1 and children[0]['type']=='image'
  node=dict(id=f'muse-continuation-v19-complement-{n}',type='group',start=n/scene['fps'],end=(n+1)/scene['fps'],x=c['x'],y=c['y'],scaleX=c['width']/children[0]['width'],scaleY=c['height']/children[0]['height'],rotation=0,originX=0,originY=0,opacity=c['opacity'],children=children)
  assert not any(q['id']==node['id'] for q in p['children']);p['children'].append(node)
 s['layers'][i]=p
 return s
