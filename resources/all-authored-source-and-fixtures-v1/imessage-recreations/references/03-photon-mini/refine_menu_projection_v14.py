"""Correct measured anisotropic row projection; preserve immutable v13."""
from pathlib import Path
import json,hashlib
p=Path(__file__).parent;s=json.loads((p/'final-v13.scene.json').read_text());clip=next(x for x in s['layers'] if x['id']=='measured-menu-clip-v13');menu=clip['children'][0];body=next(x for x in menu['children'] if x['id']=='menu13-p03-202');records={r['frame']:r for r in json.loads((p/'menu-world-v13-measurements.json').read_text())};notes=[]
for i,row in enumerate(body['children']):
 for q in row['keyframes']['scaleX']:q['value']=1
 for q in row['keyframes']['x']:
  r=records[round(q['t']*30)];q['value']+=553*(r.get('body_scale',r['scale'])-r['scale'])/r['scale']
 for node in row['children']:
  prov=node.get('provenance',{})
  if prov.get('kind','').startswith('bounded original glyph'):
   ref=records[prov['source_frame']];photo=ref['matches'][i];box=prov['source_box'];node['x']=553+(box[0]-photo['x'])/ref['scale'];node['scaleX']=1/ref['scale']
 # Each separately cropped original food photo already includes its genuine
 # plus control. The old extra circle and font glyph duplicated that artwork.
 before=len(row['children']);row['children']=[n for n in row['children'] if not (n['type']=='circle' or n['type']=='text' and n.get('text')=='+')];notes.append({'row':i,'removed_duplicate_plus_layers':before-len(row['children'])})
s['source']['notes']+=' V14 measured menu projection: horizontal row scale follows actual photo width; vertical scale follows row pitch. Analytic affine registration of source651→700 proved unequal axes (.9334 horizontal,.9697 vertical), not AA. Removed duplicated native plus overlay because the declared original food photo already contains its exact original plus control; bitmap-control limitation declared.'
f=p/'projection-v14.scene.json';f.write_text(json.dumps(s,indent=2));(p/'menu-projection-v14-changes.json').write_text(json.dumps({'baseline':'final-v13.scene.json','declared_delta':[618,734],'diagnostic':'menu-row-demo-v14/fit.json','rows':notes,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()},indent=2));print('built projection prototype')
