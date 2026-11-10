"""Independent Muse-only helper. Accepted orbit identity/green helper stays unchanged."""
from pathlib import Path
import copy,json,hashlib
HERE=Path(__file__).resolve().parent
def signature(node):
 d=copy.deepcopy(node)
 def canon(v):
  if isinstance(v,float) and v.is_integer():return int(v)
  if isinstance(v,dict):return {k:(Path(x).name if k=='src' else canon(x)) for k,x in v.items()}
  if isinstance(v,list):return [canon(x) for x in v]
  return v
 return hashlib.sha256(json.dumps(canon(d),sort_keys=True,separators=(',',':')).encode()).hexdigest()
def apply(scene):
 spec=json.load(open(HERE/'patch-spec.json'));s=dict(scene);s['layers']=list(scene['layers']);parents={p['id']:(i,p) for i,p in enumerate(scene['layers'])}
 for op in spec['operations']:
  i,p=parents[op['parent']];assert abs(p['start']-op['frame']/scene['fps'])<1e-9 and abs(p['end']-(op['frame']+1)/scene['fps'])<1e-9;q=dict(p);q['children']=list(p['children']);j=next(j for j,n in enumerate(q['children']) if n['id']==op['id']);node=q['children'][j];assert signature(node)==op['oldSignature'],op['id'];child=copy.deepcopy(node);child.update(op['properties'])
  for k in op['properties']:child.get('keyframes',{}).pop(k,None)
  if child.get('keyframes')=={}:child.pop('keyframes')
  q['children'][j]=child;s['layers'][i]=q
 return s
