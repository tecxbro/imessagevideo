from pathlib import Path
import json,copy
from PIL import Image
p=Path(__file__).parent
s=json.loads((p/'final-v3.scene.json').read_text())
assets=[]
for t,box,name in [(6,(539,455,1174,791),'mail-preview-original-art.png'),(20,(704,557,1227,834),'food-preview-original-art.png')]:
 Image.open(p/'measured'/f'{t}.png').crop(box).save(p/'assets'/name)
 assets.append({'file':'assets/'+name,'source_time':t,'source_box':list(box),'purpose':'Original individual mini-app preview interior artwork; bitmap text declared; outer editable bubble/footer retained.'})
changed=[]
def visit(layer):
 if layer['type']=='group':
  directtexts=[x.get('text')for x in layer.get('children',[]) if x['type']=='text']
  if 'Uber Eats' in directtexts:
   for child in layer['children']:
    if child['type']=='group' and child.get('clip',{}).get('height')==278:
     child['children']=[{'id':'food-preview-original-interior-v4','type':'image','src':'assets/food-preview-original-art.png','x':0,'y':0,'width':520,'height':278}];changed.append(child['id'])
  if 'Mail' in directtexts:
   for child in layer['children']:
    if child['type']=='group' and child.get('clip',{}).get('height')==274:
     child['children']=[{'id':'mail-preview-original-interior-v4','type':'image','src':'assets/mail-preview-original-art.png','x':0,'y':0,'width':517,'height':274}];changed.append(child['id'])
 for child in layer.get('children',[]):visit(child)
for layer in s['layers']:visit(layer)
s['source']['notes']+=' Candidate-v4: original individual mail/food preview interiors as declared bitmap artwork; outer bubble/footer remain editable. Frozen final-v3 scene unchanged.'
(p/'candidate-v4.scene.json').write_text(json.dumps(s,indent=2));(p/'candidate-v4-art-provenance.json').write_text(json.dumps(assets,indent=2));print('changedgroups',changed)
