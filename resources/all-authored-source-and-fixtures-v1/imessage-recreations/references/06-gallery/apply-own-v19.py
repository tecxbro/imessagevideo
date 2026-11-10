"""Apply only the measured email555–560 and word/soccer846–1048 corrections."""
from pathlib import Path
import argparse,json,copy
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;s=json.loads(a.input.read_text())
def absolute(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src' and isinstance(v,str) and not v.startswith('data:'):o[k]=str((a.input.parent/v).resolve())
   else:absolute(v)
 elif isinstance(o,list):
  for q in o:absolute(q)
absolute(s)
for name in ['word-v19-patch.json','soccer-v19-patch.json']:
 patch=json.loads((D/name).read_text());s['layers']=[copy.deepcopy(patch['replace'].get(q['id'],q)) for q in s['layers']]
 for node in patch['append']:
  s['layers']=[q for q in s['layers'] if q['id']!=node['id']];s['layers'].append(copy.deepcopy(node))
e=json.loads((D/'email-exit-v19-patch.json').read_text());added={q['id'] for q in e['layers']};s['layers']=[q for q in s['layers'] if q['id'] not in added];at=next(i for i,q in enumerate(s['layers']) if q['id']==e['insert_after'])+1;s['layers'][at:at]=copy.deepcopy(e['layers']);a.output.write_text(json.dumps(s,indent=2)+'\n');print(a.output)
