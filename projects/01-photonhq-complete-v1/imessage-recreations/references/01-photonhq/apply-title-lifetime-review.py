"""ID-scoped native title/mark timing patch; preserves all intro/wall/CTA reveal nodes."""
from pathlib import Path
import json,argparse,copy
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--elements',type=Path,default=Path(__file__).with_name('title-lifetime-review-elements.json'));a=p.parse_args();s=json.loads(a.input.read_text());spec=json.loads(a.elements.read_text());ids=set(spec['replacements'])|set(spec['gate_overrides'])|{spec['mark_overrides']['id']};counts=dict.fromkeys(ids,0);layers=[]
def absolute(l):
 if l.get('src') and not l['src'].startswith(('data:','http:','https:','/')):l['src']=str((a.input.parent/l['src']).resolve())
 for c in l.get('children',[]):absolute(c)
for l in s['layers']:
 absolute(l);id=l['id']
 for g in spec['insert_before'].get(id,[]):layers.append(copy.deepcopy(g))
 if id in spec['replacements']:l=copy.deepcopy(spec['replacements'][id]);counts[id]+=1
 elif id in spec['gate_overrides']:l.update(spec['gate_overrides'][id]);counts[id]+=1
 elif id==spec['mark_overrides']['id']:
  q=spec['mark_overrides'];l['start']=q['start'];l['keyframes']=copy.deepcopy(q['keyframes']);counts[id]+=1
 layers.append(l)
if any(c!=1 for c in counts.values()):raise ValueError('Missing/duplicate ID '+str(counts))
for f in s.get('fonts',[]):
 if not f['src'].startswith(('data:','http:','https:','/')):f['src']=str((a.input.parent/f['src']).resolve())
s['layers']=layers;s['source']['notes']+=' Native title timing: independent registration words from465/468/471, badge474 and check formation; hard registration→Onus edit500 and CTA→Photon mark edit590. Native word contours and bounded badge pose artwork; preserves intro, walls and accepted URL reveal.';a.output.write_text(json.dumps(s,indent=2));print(json.dumps(dict(ids=counts,changed_frame_ranges=spec['changed_frame_ranges'],output=str(a.output))))
