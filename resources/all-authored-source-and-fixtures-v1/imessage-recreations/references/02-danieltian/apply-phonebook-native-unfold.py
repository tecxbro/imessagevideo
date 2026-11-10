from pathlib import Path
import argparse,json,copy,hashlib
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();src=a.input.resolve();scene=json.loads(src.read_text());ref=Path(__file__).resolve().parent;specpath=ref/'phonebook-native-unfold.json';spec=json.loads(specpath.read_text())
def absolute(l):
 if l.get('src') and not l['src'].startswith(('data:','http:','https:')):l['src']=str((src.parent/l['src']).resolve())
 for c in l.get('children',[]):absolute(c)
kept=[]
for l in scene['layers']:
 if l['id'].startswith('pb-native-unfold-'):continue
 if l['id'].startswith(tuple(spec['gatedPrefixes'])) and l.get('start',0)<spec['gate_start']:
  l['start']=spec['gate_start']
  if l.get('end',scene['duration'])<=l['start']:continue
 absolute(l);kept.append(l)
for f in scene.get('fonts',[]):
 if not f['src'].startswith(('data:','http:','https:')):f['src']=str((src.parent/f['src']).resolve())
scene['layers']=kept+copy.deepcopy(spec['layers']);scene['phonebook_native_unfold']={'spec':str(specpath),'sha256':hashlib.sha256(specpath.read_bytes()).hexdigest(),'scope':spec['changed_frame_ranges'],'editability':spec['notice']};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(scene,indent=2));print(a.output)
