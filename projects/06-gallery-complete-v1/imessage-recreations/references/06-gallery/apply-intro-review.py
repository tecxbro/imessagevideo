"""ID-scoped Rene0–3.6 measured intro helper; preserves all caller states after107."""
from pathlib import Path
import json,argparse,copy
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--elements',type=Path,default=Path(__file__).with_name('intro-review-elements.json'));a=p.parse_args();scene=json.loads(a.input.read_text());spec=json.loads(a.elements.read_text());counts={id:0 for id in spec['replace_ids']+list(spec['gate_overrides'])};layers=[]
def resolve(node):
 if node.get('src') and not node['src'].startswith(('data:','http:','https:','/')):node['src']=str((a.input.parent/node['src']).resolve())
 for c in node.get('children',[]):resolve(c)
for l in scene['layers']:
 resolve(l);id=l['id']
 for node in spec['insert_before'].get(id,[]):layers.append(copy.deepcopy(node))
 if id in spec['replace_ids']:counts[id]+=1;continue
 if id in spec['gate_overrides']:l.update(spec['gate_overrides'][id]);counts[id]+=1
 layers.append(l)
if any(v!=1 for v in counts.values()):raise ValueError('Missing/duplicate ID '+str(counts))
for f in scene.get('fonts',[]):
 if not f['src'].startswith(('data:','http:','https:','/')):f['src']=str((a.input.parent/f['src']).resolve())
scene['layers']=layers;scene['source']['notes']+=' Measured opening0–3.6: explicit source edit at54; independent message births/scroll, separate physical phone camera. Bounded original static UI/message artwork has bitmap internals and native transforms/lifetimes; no complete-frame or source-video playback. Separate108–119 handoff helper is required before integration.';a.output.write_text(json.dumps(scene,indent=2));print(json.dumps({'output':str(a.output),'changed_frames':spec['changed_frame_ranges'],'ids':counts}))
