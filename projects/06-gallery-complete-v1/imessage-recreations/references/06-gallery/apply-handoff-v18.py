"""Apply measured108–119 and225–239 phone correction after accepted intro/root helpers."""
from pathlib import Path
import json,argparse
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=Path(__file__).resolve().parent
s=json.loads(a.input.read_text())
def restore(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src' and isinstance(v,str) and not v.startswith('data:'):o[k]=str((a.input.parent/v).resolve())
   else:restore(v)
 elif isinstance(o,list):
  for x in o:restore(x)
restore(s);patch=json.loads((d/'handoff-v18-patch.json').read_text())['replace'];s['layers']=[patch.get(x['id'],x) for x in s['layers']];a.output.write_text(json.dumps(s,indent=2)+'\n');print(a.output)
