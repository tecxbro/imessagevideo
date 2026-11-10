from pathlib import Path
import json,os,argparse,copy
p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('output');a=p.parse_args();source=Path(a.input).resolve();output=Path(a.output).resolve();root=Path(__file__).parent;scene=json.loads(source.read_text());patch=json.loads((root/'endcard-refinement.json').read_text())
def rebase(l,base):
 if l.get('src') and not l['src'].startswith(('data:','http:','https:')):l['src']=os.path.relpath((base/l['src']).resolve(),output.parent)
 for c in l.get('children',[]):rebase(c,base)
new=[]
for l in scene['layers']:
 if l['id'] in patch['replacements']:l=copy.deepcopy(patch['replacements'][l['id']]);rebase(l,root)
 else:rebase(l,source.parent)
 new.append(l)
scene['layers']=new
for f in scene.get('fonts',[]):
 if not f['src'].startswith(('data:','http:','https:')):f['src']=os.path.relpath((source.parent/f['src']).resolve(),output.parent)
scene['source']['notes']+=' End-card refinement uses editable native source glyph outlines with semantic copy/provenance plus individual original provider capsule artwork; capsule text is bitmap and outlined text is not live copy.';scene['endcard_refinement_provenance']=patch['provenance'];output.write_text(json.dumps(scene,indent=2));print(output)
