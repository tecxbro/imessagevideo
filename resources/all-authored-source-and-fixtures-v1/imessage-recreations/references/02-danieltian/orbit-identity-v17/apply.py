"""Apply only measured orbit actor changes. Never writes an input scene file."""
from pathlib import Path
import copy,json,hashlib
HERE=Path(__file__).resolve().parent
PROPS=('x','y','scaleX','scaleY')
def signature(node):
 d=copy.deepcopy(node)
 def walk(n):
  if 'src' in n:n['src']=Path(n['src']).name
  for c in n.get('children',[]):walk(c)
 walk(d)
 def canon(v):
  if isinstance(v,float) and v.is_integer():return int(v)
  if isinstance(v,dict):return {k:canon(x) for k,x in v.items()}
  if isinstance(v,list):return [canon(x) for x in v]
  return v
 return hashlib.sha256(json.dumps(canon(d),sort_keys=True,separators=(',',':')).encode()).hexdigest()
def apply(scene):
 spec=json.load(open(HERE/'patch-spec.json'));result=dict(scene);result['layers']=list(scene['layers']);parents={p['id']:(i,p) for i,p in enumerate(scene['layers'])}
 for op in spec['operations']:
  i,old=parents[op['parent']];assert abs(old['start']-op['frame']/scene['fps'])<1e-9 and abs(old['end']-(op['frame']+1)/scene['fps'])<1e-9
  new=dict(old);new['children']=list(old['children']);result['layers'][i]=new;parents[old['id']]=(i,new)
  if op['kind']=='update':
   j=next(j for j,n in enumerate(new['children']) if n['id']==op['id']);node=new['children'][j];assert signature(node)==op['oldSignature'],('actor baseline changed',op['id']);q=copy.deepcopy(node)
   for k,v in op['pose'].items():q[k]=v
   for k in PROPS:q.get('keyframes',{}).pop(k,None)
   if q.get('keyframes')=={}:q.pop('keyframes')
   if op.get('imageOverride'):
    assert len(q.get('children',[]))==1 and q['children'][0]['type']=='image'
    q['children'][0].update(op['imageOverride'])
   new['children'][j]=q
  else:
   assert not any(n['id']==op['id'] for n in new['children']);_,templateParent=parents[op['cloneParent']];node=next(n for n in templateParent['children'] if n['id']==op['cloneID']);assert signature(node)==op['cloneSignature'];q=copy.deepcopy(node)
   def rename(n):
    n['id']=n['id'].replace('root-orbit-566-','root-orbit-'+str(op['frame'])+'-')
    for c in n.get('children',[]):rename(c)
   rename(q)
   assert q['id']==op['id'];q.update(op['pose']);q.pop('keyframes',None)
   if op.get('imageOverride'):
    assert len(q.get('children',[]))==1 and q['children'][0]['type']=='image'
    q['children'][0].update(op['imageOverride'])
   new['children'].insert(3,q)
 return result
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('output');a=p.parse_args();s=json.load(open(a.input));out=apply(s);Path(a.output).write_text(json.dumps(out,indent=2));print({'output':a.output,'operations':len(json.load(open(HERE/'patch-spec.json'))['operations'])})
