"""Scoped flight355–397 document + authorized353–397 backdrop correction."""
from pathlib import Path
import argparse,json,copy
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--elements',type=Path,default=Path(__file__).with_name('flight-document-review-elements.json'));a=p.parse_args();s=json.loads(a.input.read_text());spec=json.loads(a.elements.read_text());counts={**dict.fromkeys(spec['gates'],0),spec['background_id']:0};layers=[]
def absolute(l):
 if l.get('src') and not l['src'].startswith(('data:','http:','https:','/')):l['src']=str((a.input.parent/l['src']).resolve())
 for c in l.get('children',[]):absolute(c)
if any(l['id']=='flight-review-continuous-document' for l in s['layers']):raise ValueError('Flight review already applied')
for l in s['layers']:
 absolute(l);id=l['id']
 layers.extend(copy.deepcopy(spec['insert_before'].get(id,[])))
 if id in spec['gates']:l.update(spec['gates'][id]);counts[id]+=1
 if id==spec['background_id']:l.setdefault('keyframes',{}).update(copy.deepcopy(spec['background_tracks']));counts[id]+=1
 layers.append(l)
if any(c!=1 for c in counts.values()):raise ValueError('Expected unique flight IDs '+str(counts))
for f in s.get('fonts',[]):
 if not f['src'].startswith(('data:','http:','https:','/')):f['src']=str((a.input.parent/f['src']).resolve())
s['layers']=layers;s['source']['notes']+=' Measured continuous flight app355–397: static top/sky/Basic/Economy UI components, native camera/shutter/independent carousel, bounded entrance color poses355–359, authorized native backdrop correction353–397. Accepted398+ preserved.';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(s,indent=2));print(json.dumps(dict(ids=counts,ranges=spec['changed_frame_ranges'],output=str(a.output))))
