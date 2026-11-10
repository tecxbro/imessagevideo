"""ID-scoped application of already generated reviewer elements; no image extraction."""
import argparse,copy,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
ref=Path(__file__).resolve().parent
scene=json.loads(args.input.read_text());spec=json.loads((ref/'phonebook-review-elements.json').read_text());counts={'group-1007':0,'pb-uber-eats':0};insert=None
if any(l.get('id')=='pbr-late-query' for l in scene['layers']):raise ValueError('Review patch already applied')
for i,l in enumerate(scene['layers']):
 id=l.get('id')
 if id=='group-1007':l['end']=13.;insert=i+1;counts[id]+=1
 elif id=='pb-uber-eats':scene['layers'][i]=copy.deepcopy(spec[id]);counts[id]+=1
if counts!={'group-1007':1,'pb-uber-eats':1}:raise ValueError(f'Unexpected target counts: {counts}')
scene['layers'].insert(insert,copy.deepcopy(spec['pbr-late-query']))
scene['source']['notes']+=' Review patch: bounded original query glyph states, magnifier, cap-preserving border and three Uber capsule camera/art poses. Internal copy is bitmap, native transforms/alpha are editable; no full-source frame/video playback. Intermediate perspective and tracking remain approximations.'
args.output.write_text(json.dumps(scene,indent=2));print(json.dumps({'input':str(args.input),'output':str(args.output),'changed_frame_ranges':[[390,415],[463,511]],'replaced_ids':list(counts)}))
