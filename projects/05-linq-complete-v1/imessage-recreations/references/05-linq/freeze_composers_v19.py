"""Freeze accepted intro and Cash input component data; retain immutable V18."""
from pathlib import Path
import json,hashlib,shutil
D=Path(__file__).resolve().parent;R=D.parent.parent;P=D/'composer-v19-frozen-elements.json';s=json.loads((D/'scene-composers-caret-v19.json').read_text());data=json.loads((D/'measurements/composer-v19/measurements.json').read_text());cash=next(q for q in s['layers']if q['id']=='linq-measured-v6-group-36');payload={'ranges':[[0,98],[768,826]],'removedIntroRootIDs':data['removedIntroRootIDs'],'intro':next(q for q in s['layers']if q['id']=='v19-intro-composer'),'cashComposer':next(q for q in cash['children']if q['id']=='v10-cash-composer'),'notice':'Original native outline components and measured dense cameras/lifecycles. Bounded existing Cash UI material has only former cyan caret pixels restored from one genuine static pre-caret plate776; one original13x53 detail is independently animated. No complete source frame or source video layer.'};assets={}
def freeze(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src'and isinstance(v,str)and '/measurements/composer-v19/'in v:
    p=Path(v);h=hashlib.sha256(p.read_bytes()).hexdigest();q=D/'assets/composer-v19'/f'{h[:16]}-{p.name}';q.parent.mkdir(exist_ok=True,parents=True)
    if q.exists():assert q.read_bytes()==p.read_bytes()
    else:shutil.copyfile(p,q)
    o[k]=str(q.resolve());assets[str(q.relative_to(R))]=h
   else:freeze(v)
 elif isinstance(o,list):
  for q in o:freeze(q)
freeze(payload);assert not P.exists();P.write_text(json.dumps(payload,indent=2)+'\n');h=hashlib.sha256(P.read_bytes()).hexdigest();report={'elements':str(P.relative_to(R)),'elementsSHA256':h,'assets':assets,'nativeGate':'verification/05-v19-composer-native-gate.json','ranges':payload['ranges'],'changedFrames':158};(D/'composer-v19-release.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
