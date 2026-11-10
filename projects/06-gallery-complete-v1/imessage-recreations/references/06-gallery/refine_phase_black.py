from pathlib import Path
import json
p=Path('/workspace/imessage-recreations/references/06-gallery/scene.json');s=json.loads(p.read_text())
for g in s['layers']:
 for t in g.get('children',[]):
  if t.get('type')=='text' and t.get('fontFamily')=='Rene Word Fit':
   t['fill']='#000000'
   if t['text']=='l':t['y']=405
   if t['text']=='ve':t['x']=939.1
p.write_text(json.dumps(s,indent=2))
