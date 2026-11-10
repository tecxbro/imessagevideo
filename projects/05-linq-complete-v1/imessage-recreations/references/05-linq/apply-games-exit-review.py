from pathlib import Path
import argparse,json,copy
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--elements',type=Path,default=Path(__file__).with_name('games-exit-review-elements.json'));a=p.parse_args();s=json.loads(a.input.read_text());sp=json.loads(a.elements.read_text());n=0;layers=[]
def ab(l):
 if l.get('src')and not l['src'].startswith(('/','data:','http:','https:')):l['src']=str((a.input.parent/l['src']).resolve())
 for c in l.get('children',[]):ab(c)
for l in s['layers']:
 ab(l)
 if l['id']==sp['gate_id']:l['end']=sp['gate_end'];n+=1
 layers.append(l);layers+=copy.deepcopy(sp['insert_after'].get(l['id'],[]))
if n!=1:raise ValueError('Expected uniqueg138')
for f in s.get('fonts',[]):
 if not f['src'].startswith(('/','data:','http:','https:')):f['src']=str((a.input.parent/f['src']).resolve())
s['layers']=layers;s['source']['notes']+=' Exact Games146–148 exit material/lifecycle correction: avoid twice-faded UI, measured native labels/header, first chess preview148;129–145 and149+ retained.';a.output.parent.mkdir(exist_ok=True,parents=True);a.output.write_text(json.dumps(s,indent=2));print('Gamesexit',sp['changed_frame_ranges'])
