from pathlib import Path
import json
p=Path('/workspace/imessage-recreations/references/06-gallery/scene.json');s=json.loads(p.read_text());fps=s['fps']
def walk(nodes):
 for q in nodes:
  for key in ['start','end']:
   value=q.get(key)
   if isinstance(value,(int,float)) and abs(value*fps-round(value*fps))<1e-6:q[key]=round(value*fps)/fps
  walk(q.get('children',[]))
walk(s['layers']);p.write_text(json.dumps(s,indent=2))
