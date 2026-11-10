from pathlib import Path
import json,copy,sys
source=Path(sys.argv[1]).resolve();dest=Path(sys.argv[2]).resolve();scene=json.loads(source.read_text());patch=json.loads((Path(__file__).parent/'middle-refinement.json').read_text())
def rebase(l,root):
 if l.get('src') and not str(l['src']).startswith(('data:','http:','https:')):l['src']=str((root/l['src']).resolve())
 for c in l.get('children',[]):rebase(c,root)
for l in scene['layers']:rebase(l,source.parent)
for l in patch['replacements'].values():rebase(l,Path(__file__).parent)
for l in patch.get('new_layers',[]):rebase(l,Path(__file__).parent)
for f in scene.get('fonts',[]):f['src']=str((source.parent/f['src']).resolve())
scene['layers']=[copy.deepcopy(patch['replacements'].get(l['id'],l)) for l in scene['layers']]
ids={g['id'] for g in patch.get('gradients',[])};scene['gradients']=[g for g in scene.get('gradients',[]) if g['id'] not in ids]+patch.get('gradients',[])
dest.write_text(json.dumps(scene,indent=2));print(dest)
