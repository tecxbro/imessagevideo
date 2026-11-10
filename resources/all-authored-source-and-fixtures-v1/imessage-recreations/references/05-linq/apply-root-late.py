"""Apply the independently measured late-sequence replacements by stable IDs."""
from pathlib import Path
import argparse,json,copy
REF=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
source=a.input.resolve();scene=json.loads(source.read_text())
def absolute(layer,base):
 if layer.get('src') and not layer['src'].startswith(('data:','http:','https:')):layer['src']=str((base/layer['src']).resolve())
 for c in layer.get('children',[]):absolute(c,base)
for l in scene['layers']:absolute(l,source.parent)
for font in scene.get('fonts',[]):
 if not font['src'].startswith(('data:','http:','https:')):font['src']=str((source.parent/font['src']).resolve())
replacements={};provenance=[]
for file in ['root-four-patch.json','root-boarding-gallery-patch.json','root-games-patch.json']:
 path=REF/file
 if path.exists():
  patch=json.loads(path.read_text());replacements.update(patch['replacements']);provenance.append({'file':file,'changed_ranges':patch['changed_ranges']})
  for gradient in patch.get('gradients',[]):
   scene['gradients']=[g for g in scene.get('gradients',[]) if g['id']!=gradient['id']]+[gradient]
found=set()
for i,l in enumerate(scene['layers']):
 if l['id'] in replacements:scene['layers'][i]=copy.deepcopy(replacements[l['id']]);found.add(l['id'])
if found!=set(replacements):raise ValueError('Missing target IDs '+str(set(replacements)-found))
scene['source']['notes']+=' Late sequence measured from exact native source frames: independent Four in a Row counters, panel positions and boarding/gallery camera. Bounded branded UI artwork is static; no full-frame or source-video layer.'
scene['root_late_provenance']=provenance;a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(scene,indent=2))
print(json.dumps({'output':str(a.output),'replaced_ids':sorted(found)}))
