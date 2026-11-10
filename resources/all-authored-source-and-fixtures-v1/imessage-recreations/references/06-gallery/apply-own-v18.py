"""Apply measured source06 handoff, email rows, title/card and early phone.
Accepted opening/root lock and portrait helpers stay independent; run this after
those helpers so the birth108 gate and foreground early-phone stack are final.
"""
from pathlib import Path
import argparse,json,copy
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=Path(__file__).resolve().parent
s=json.loads(a.input.read_text())
def restore(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src' and isinstance(v,str) and not v.startswith('data:'):o[k]=str((a.input.parent/v).resolve())
   else:restore(v)
 elif isinstance(o,list):
  for q in o:restore(q)
restore(s)
for name in ['handoff-v18-patch.json','title-card-v18-patch.json']:
 patch=json.loads((d/name).read_text());s['layers']=[copy.deepcopy(patch['replace'].get(q['id'],q)) for q in s['layers']]
 for q in patch.get('append',[]):
  s['layers']=[x for x in s['layers'] if x['id']!=q['id']];s['layers'].append(copy.deepcopy(q))
e=json.loads((d/'scene-email-v18.json').read_text());email=next(q for q in e['layers'] if q['id']=='measured-email-panes-v13')
s['layers']=[copy.deepcopy(email) if q['id']==email['id'] else q for q in s['layers'] if q['id']!='context-v8-inbox-75']
a.output.write_text(json.dumps(s,indent=2)+'\n');print(a.output)
