"""ID-scoped source01 intro and CTA transition repair, preserving walls and settled holds."""
from pathlib import Path
import argparse,copy,json
REF=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--elements',type=Path,default=REF/'intro-review-elements.json');a=p.parse_args();scene=json.loads(a.input.read_text());spec=json.loads(a.elements.read_text())
if any(l['id']=='intro-free-before8' for l in scene['layers']):raise ValueError('Intro patch already applied')
counts={id:0 for id in spec['replacements']};layers=[]
for l in scene['layers']:
 id=l['id']
 for node in spec['insert_before'].get(id,[]):layers.append(copy.deepcopy(node))
 if id in spec.get('gate_overrides',{}):l=copy.deepcopy(l);l.update(spec['gate_overrides'][id]);counts[id]+=1
 elif id=='group-27':l=copy.deepcopy(l);l['start']=8;counts[id]+=1
 elif id in spec['replacements']:l=copy.deepcopy(spec['replacements'][id]);counts[id]+=1
 layers.append(l)
if any(v!=1 for v in counts.values()):raise ValueError('Missing/duplicate replacement IDs: '+str(counts))
scene['layers']=layers;scene['source']['notes']+=' Intro repair: neutral per-element source masks prevent colored Photon glyphs/channel labels contaminating black-word bounds. Native independent word entrances/exits and measured positions/scales replace phrase-wide transforms. Pill geometry/alpha are measured independently with explicit exit. Bounded original gradient-word typing/entry poses are bitmap; black copy is native semantic glyph outlines. Short URL gray/blur/cyan reveal uses independently bounded original glyph pose artwork; native semantic word contours preserve prefix entrances. Bitmap internals are explicit. All walls, settled18.5+ CTA and original free zoom8+ are unchanged.'
a.output.write_text(json.dumps(scene,indent=2));print(json.dumps(dict(input=str(a.input),output=str(a.output),replaced_ids=list(counts),changed_frame_ranges=spec['changed_frame_ranges'])))
