"""Merge the stable598–629 header/Muse fix and175–179 flight/burst ordering by ID."""
from pathlib import Path
import argparse,json,copy,hashlib
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--spec',type=Path,default=Path(__file__).with_name('header-formation-prototype.json'));a=p.parse_args();s=json.loads(a.input.read_text());spec=json.loads(a.spec.read_text());replacement=spec['replacements'];seen={n['id'] for n in s['layers']}
if set(replacement)-seen:raise ValueError('Required stable IDs absent')
s['layers']=[copy.deepcopy(replacement.get(n['id'],n)) for n in s['layers']];flight=next(n for n in s['layers'] if n['id']=='early-sent-message-flight');s['layers']=[n for n in s['layers'] if n['id']!=flight['id']];i=next(i for i,n in enumerate(s['layers']) if n['id']=='group-968');s['layers'].insert(i,flight)
def absolute(n):
 if isinstance(n,dict):
  if n.get('src') and not n['src'].startswith(('data:','http:','https:','/')):n['src']=str((a.input.parent/n['src']).resolve())
  for v in n.values():absolute(v)
 elif isinstance(n,list):
  for v in n:absolute(v)
absolute(s);s['source']['notes']+=' Final-v12 scoped source598–629 formation: separate native semantic title/pill contours and original bounded glass-circle3D texture poses preserve moving inner logos/material/refraction. Internal sphere artwork and refracted copy are bitmap, not live elements; separate early Muse portrait/typing/caption poses/fade are measured. Source175–179 send burst paints above the independent flight, restoring the blue circular send button. All other source picture states remain unchanged.';s['headerFormationRelease']={'spec':str(a.spec.resolve()),'sha256':hashlib.sha256(a.spec.read_bytes()).hexdigest(),'changedFrames':[[175,179],[598,629]],'editability':'Native title/pill contours and independent circle/widget poses. Bounded original3D sphere internals are bitmap; no complete-frame image or source-video playback.'};a.output.write_text(json.dumps(s,indent=2));print(a.output)
