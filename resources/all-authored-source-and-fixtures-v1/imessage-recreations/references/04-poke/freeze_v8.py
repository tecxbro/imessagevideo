"""One immutable render manifest and asset payload shared by every engine."""
from pathlib import Path
import json,hashlib,shutil,collections
p=Path(__file__).parent;root=p.parent.parent;src=p/'scene-v8-batch-candidate.json';dst=root/'outputs/04-poke/final-v8';dst.mkdir(exist_ok=False)
data=json.loads(src.read_text());assets=set();ids=[];counts=collections.Counter()
def walk(nodes):
    for layer in nodes:
        ids.append(layer['id']);counts[layer['type']]+=1
        if layer['type']=='image':assets.add(layer['src'])
        walk(layer.get('children',[]))
walk(data['layers'])
if len(ids)!=len(set(ids)):raise ValueError('Duplicate editable ids')
for font in data.get('fonts',[]):assets.add(font['src'])
manifest=[]
for rel in sorted(assets):
    source=p/rel;target=dst/rel
    if not source.is_file()or not rel.startswith('assets/')or'..'in Path(rel).parts:raise ValueError(rel)
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    manifest.append(dict(path=rel,bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
for source in (p/'assets').glob('*provenance*.json'):shutil.copy2(source,dst/'assets'/source.name)
shutil.copy2(src,dst/'scene.json');sha=hashlib.sha256(src.read_bytes()).hexdigest()
if hashlib.sha256((dst/'scene.json').read_bytes()).hexdigest()!=sha:raise ValueError('Snapshot differs')
(dst/'asset-manifest.json').write_text(json.dumps({'sceneSHA256':sha,'assets':manifest},indent=2))
status=dict(scene=str(dst/'scene.json'),sceneSHA256=sha,width=1440,height=1080,fps_rational='30000/1001',frames=1283,duration=1283*1001/30000,native_layer_counts=dict(counts),native_nodes=sum(counts.values()),changed_frame_ranges_inclusive=[[2,551],[578,887],[1125,1216]],primary_caches=dict(remotion='outputs/retained-frames/remotion-measured-frames-DRRwxq',gsap='outputs/retained-frames/measured-frames-jRBOzF'),status='Frozen canonicalv8; final primary renders and every-frame QA pending.')
(dst/'snapshot.json').write_text(json.dumps(status,indent=2));(p/'final-v8-scene.json').write_text(json.dumps(status,indent=2));print(json.dumps(status,indent=2))
