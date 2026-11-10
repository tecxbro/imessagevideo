"""Replace only group-797; preserve concurrent source02 boundary/phonebook/middle/end changes."""
from pathlib import Path
import argparse,json,copy
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--elements',type=Path,default=Path(__file__).with_name('intro797-review-elements.json'));a=p.parse_args();s=json.loads(a.input.read_text());spec=json.loads(a.elements.read_text());count=0
for i,l in enumerate(s['layers']):
 if l['id']==spec['id']:s['layers'][i]=copy.deepcopy(spec['replacement']);count+=1
if count!=1:raise ValueError('Expected exactly one '+spec['id'])
for id,changes in spec.get('gate_overrides',{}).items():
 hits=[q for q in s['layers'] if q['id']==id]
 if len(hits)!=1:raise ValueError('Expected exactly one '+id)
 hits[0].update(changes)
def absolute(l):
 if l.get('src') and not l['src'].startswith(('data:','http:','https:','/')):l['src']=str((a.input.parent/l['src']).resolve())
 for c in l.get('children',[]):absolute(c)
for l in s['layers']:absolute(l)
for f in s.get('fonts',[]):
 if not f['src'].startswith(('data:','http:','https:','/')):f['src']=str((a.input.parent/f['src']).resolve())
s['source']['notes']+=' Measured group-797 opening: observed composed0–2 artifact, reset3–5, native independent word entrances6–22, camera breathing and late shrink/blur64–67. Isolated original3D icon artwork has bitmap internals, native pose/lifetime. Source68–69 title continuation is preserved; composer start70 removes the premature plus/overlay inside this interval. No full-frame/video playback.';a.output.write_text(json.dumps(s,indent=2));print(json.dumps(dict(id=spec['id'],range=spec['changed_frame_ranges'],output=str(a.output))))
