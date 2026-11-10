"""Use measured glyph-shape matches; preserve the frozen v6 local geometry."""
from pathlib import Path
import json,hashlib
p=Path(__file__).parent;s=json.loads((p/'scene-v6-components.json').read_text());table={}
def walk(layers):
 for l in layers:table[l['id']]=l;walk(l.get('children',[]))
walk(s['layers'])
for id,weight in [('p0306',400),('p0302',500),('p0314',500)]:table[id]['fontFamily']='SF Pro Display';table[id]['fontWeight']=weight
table['p0300']['children'].insert(2,{'id':'p0300-native-map-detail','type':'image','src':'assets/zareen-map-visible-native28.png','x':0,'y':255.5,'width':388.75,'height':38.75,'start':810*1001/30000,'end':29.4})
fitfile=p/'v7-native-ink-fit.json'
if fitfile.exists():
 for row in json.loads(fitfile.read_text())['fits']:table[row['id']].update(row['fit'])
name='scene-v7-fonts.json' if fitfile.exists() else 'scene-v7-fonts-candidate.json'
s['source']['notes']+=' V7 glyph-shape correction: native source alpha masks compared with eight official SF Pro family/weight variants at identical ink bounds. Display Regular distance, Display Medium map-title/caption win spatial comparison; retained Text Regular map subtitle and Display Regular composer. Actual native browser ink fitted afterward. Density alone was not a sufficient font-match criterion. Genuine high-resolution visible map texture replaces the lower-resolution artwork in the late zoom; card body/title/subtitle remain native editable layers.'
out=p/name;out.write_text(json.dumps(s,indent=2));r={'scene':out.name,'scene_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'parent':'scene-v6-components.json','parent_sha256':hashlib.sha256((p/'scene-v6-components.json').read_bytes()).hexdigest(),'delta_from_v6_inclusive':[[733,887]],'cli_ranges_from_v6':'733:887','changed_frames':155,'modified_ids':['p0306','p0302','p0314','p0300-native-map-detail'],'font_shape_evidence':'font-shape-ranking.json','actual_native_fit':fitfile.name if fitfile.exists() else None,'status':'Native font candidate until rendered source comparison; no1:1 certification.'};(p/'final-v7-scene.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
