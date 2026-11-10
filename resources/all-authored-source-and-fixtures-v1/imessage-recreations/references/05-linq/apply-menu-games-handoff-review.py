"""Apply only the native127–129 outgoing-menu/Games handoff; preserve accepted130+."""
from pathlib import Path
import argparse,json,copy
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--elements',type=Path,default=Path(__file__).with_name('menu-games-handoff-review-elements.json'));a=p.parse_args();s=json.loads(a.input.read_text());spec=json.loads(a.elements.read_text());counts=dict.fromkeys(spec['gates'],0);layers=[]
def absolute(l):
 if l.get('src') and not l['src'].startswith(('data:','http:','https:','/')):l['src']=str((a.input.parent/l['src']).resolve())
 for c in l.get('children',[]):absolute(c)
if any(l['id']=='handoff-outgoing-menu-127' for l in s['layers']):raise ValueError('Handoff already applied')
for l in s['layers']:
 absolute(l);id=l['id']
 for n in spec['insert_before'].get(id,[]):layers.append(copy.deepcopy(n))
 if id in spec['gates']:l.update(spec['gates'][id]);counts[id]+=1
 if id in spec['prepend_children']:l['children']=copy.deepcopy(spec['prepend_children'][id])+l['children']
 layers.append(l)
if any(c!=1 for c in counts.values()):raise ValueError('Expected unique menu/Games IDs '+str(counts))
for f in s.get('fonts',[]):
 if not f['src'].startswith(('data:','http:','https:','/')):f['src']=str((a.input.parent/f['src']).resolve())
s['layers']=layers;s['source']['notes']+=' Exact menu/Games handoff127–129: faded menu127, white128, blurred Games129. Separate semantic labels/icons/cards/header assets, native geometry/lifetimes. All accepted Games130+ and other source phases preserved.';a.output.write_text(json.dumps(s,indent=2));print(json.dumps(dict(ids=counts,ranges=spec['changed_frame_ranges'],output=str(a.output))))
