"""Apply only the measured Foodash camera and independent solid-name root."""
from pathlib import Path
import argparse,json,copy
D=Path(__file__).resolve().parent

def apply_foodash(scene):
 replacements=json.loads((D/'foodash-v18-frozen-elements.json').read_text())
 scene['layers']=[copy.deepcopy(replacements.get(q['id'],q))for q in scene['layers']]
 return scene

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=json.loads(a.input.read_text())
 def absolute(o):
  if isinstance(o,dict):
   for k,v in o.items():
    if k=='src'and isinstance(v,str)and not v.startswith('data:'):o[k]=str((a.input.parent/v).resolve())
    else:absolute(v)
  elif isinstance(o,list):
   for q in o:absolute(q)
 absolute(s);a.output.write_text(json.dumps(apply_foodash(s),indent=2)+'\n');print(a.output)
