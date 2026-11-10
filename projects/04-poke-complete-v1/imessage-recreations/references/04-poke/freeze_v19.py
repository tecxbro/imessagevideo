"""Freeze a self-contained canonical native scene shared verbatim by five engines."""
from pathlib import Path
import json,hashlib,shutil,collections
p=Path(__file__).parent;root=p.parent.parent;src=p/'scene-v19-candidate.json';dst=root/'outputs/04-poke/final-v19';dst.mkdir(exist_ok=False);data=json.loads(src.read_text());assets=set();ids=[];counts=collections.Counter()
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
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);manifest.append(dict(path=rel,bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
for source in(p/'assets').glob('*provenance*.json'):shutil.copy2(source,dst/'assets'/source.name)
shutil.copy2(src,dst/'scene.json');sha=hashlib.sha256(src.read_bytes()).hexdigest();(dst/'asset-manifest.json').write_text(json.dumps(dict(sceneSHA256=sha,assets=manifest),indent=2));changes=json.loads((p/'changed-ranges-v19.json').read_text())
status=dict(scene=str(dst/'scene.json'),sceneSHA256=sha,previous_sceneSHA256=json.loads((root/'outputs/04-poke/final-v18/snapshot.json').read_text())['sceneSHA256'],width=1440,height=1080,fps_rational='30000/1001',frames=1283,duration=1283*1001/30000,native_layer_counts=dict(counts),native_nodes=sum(counts.values()),changed_frame_ranges_inclusive=changes['ranges'],changed_frames=changes['frames'],primary_caches=dict(remotion='outputs/retained-frames/remotion-measured-frames-DRRwxq',gsap='outputs/retained-frames/measured-frames-jRBOzF'),status='Frozen canonicalv19; native prototype fixes verified. Full primary capture/encode and every-frame source QA pending; no identity certification.')
(dst/'snapshot.json').write_text(json.dumps(status,indent=2));(p/'final-v19-scene.json').write_text(json.dumps(status,indent=2));print(json.dumps(status,indent=2))
