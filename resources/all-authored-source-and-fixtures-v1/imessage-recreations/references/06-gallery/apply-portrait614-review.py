"""ID-scoped independent photo camera/material corrections."""
from pathlib import Path
import argparse,json,copy
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--elements',type=Path,default=Path(__file__).with_name('portrait614-review-elements.json'));a=p.parse_args();s=json.load(open(a.input));spec=json.load(open(a.elements));counts=dict.fromkeys(spec['node_updates'],0)
def walk(ls):
 for n in ls:
  if n.get('src')and not n['src'].startswith(('/','data:','http:','https:')):n['src']=str((a.input.parent/n['src']).resolve())
  if n['id']in spec['node_updates']:
   counts[n['id']]+=1;updates=copy.deepcopy(spec['node_updates'][n['id']]);keys=updates.pop('keyframes',None);n.update(updates)
   if keys:n.setdefault('keyframes',{}).update(keys)
  walk(n.get('children',[]))
walk(s['layers'])
if any(x!=1 for x in counts.values()):raise ValueError('Expected unique photo IDs: '+str(counts))
for f in s.get('fonts',[]):
 if not f['src'].startswith(('/','data:','http:','https:')):f['src']=str((a.input.parent/f['src']).resolve())
s['source']['notes']+=' '+spec['definition']+' '+spec.get('materialEditability','')
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(s,indent=2));print(json.dumps(dict(ids=counts,ranges=spec['changed_ranges'],output=str(a.output))))
