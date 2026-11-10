"""Apply the measured static-document entrance and original thread background."""
from pathlib import Path
import argparse,json,copy
D=Path(__file__).resolve().parent

def apply_jewelry(scene):
 spec=json.loads((D/'jewelry-v18-frozen-elements.json').read_text());layers=scene['layers']
 for q in layers:
  if q['id']=='broad-v5-group-59':q.clear();q.update(copy.deepcopy(spec['background']))
  if q['id']in spec['lifecyclePatches']:q.update(spec['lifecyclePatches'][q['id']])
 assert not any(q['id']==spec['entrance']['id'] for q in layers),'Helper already applied'
 i=next(i for i,q in enumerate(layers)if q['id']=='broad-v5-group-62');layers.insert(i,copy.deepcopy(spec['entrance']))
 return scene

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=json.loads(a.input.read_text())
 def absolute(o):
  if isinstance(o,dict):
   for k,v in o.items():
    if k=='src' and isinstance(v,str) and not v.startswith('data:'):o[k]=str((a.input.parent/v).resolve())
    else:absolute(v)
  elif isinstance(o,list):
   for q in o:absolute(q)
 absolute(s);a.output.write_text(json.dumps(apply_jewelry(s),indent=2)+'\n');print(a.output)
