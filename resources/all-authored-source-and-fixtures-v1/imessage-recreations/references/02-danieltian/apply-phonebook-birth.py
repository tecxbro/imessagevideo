"""ID-scoped five-frame birth patch. Assets are resolved against this reference root."""
from pathlib import Path
import argparse,copy,json
REF=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();scene=json.loads(a.input.read_text());spec=json.loads((REF/'phonebook-birth-elements.json').read_text())
if any(l['id'].startswith('pb-birth-') for l in scene['layers']):raise ValueError('Birth patch already applied')
counts={id:0 for id in spec['gate_existing_ids']}
for l in scene['layers']:
 if l['id'] in counts:
  if l.get('start',0)>=14:raise ValueError('Target already gated: '+l['id'])
  l['start']=spec['gate_start'];counts[l['id']]+=1
if any(v!=1 for v in counts.values()):raise ValueError('Missing or duplicate field IDs')
layers=copy.deepcopy(spec['layers'])
for group in layers:
 for l in group['children']:l['src']=str(REF/l['src'])
scene['layers'].extend(layers);scene['source']['notes']+=' Five-frame field-birth correction415–419: one central cue then staggered independently bounded original phone glyph/cell poses. Internal copy is bitmap; positions/lifetimes editable. No full-frame or video playback; all accepted420+grid/glyph and query/Uber/affine/endcard work is unchanged.'
a.output.write_text(json.dumps(scene,indent=2));print(json.dumps(dict(input=str(a.input),output=str(a.output),changed_frame_ranges=spec['changed_frame_ranges'],gated_ids=len(counts),new_elements=sum(len(l['children']) for l in layers))))
