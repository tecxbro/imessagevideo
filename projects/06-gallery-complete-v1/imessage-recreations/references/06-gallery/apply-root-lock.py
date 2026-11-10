"""Merge the independently measured lockscreen/chat stages by stable root IDs."""
from pathlib import Path
import argparse,json,copy,hashlib
REF=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();source=a.input.resolve();scene=json.loads(source.read_text());patch_file=REF/'root-lock-physical-patch.json';patch_file=patch_file if patch_file.exists() else REF/'root-lock-patch.json';patch=json.loads(patch_file.read_text())
def absolute(layer):
 if layer.get('src') and not layer['src'].startswith(('data:','http:','https:')):layer['src']=str((source.parent/layer['src']).resolve())
 for c in layer.get('children',[]):absolute(c)
found=set()
for i,l in enumerate(scene['layers']):
 if l['id'] in patch['replacements']:scene['layers'][i]=copy.deepcopy(patch['replacements'][l['id']]);found.add(l['id'])
 else:absolute(l)
for font in scene.get('fonts',[]):
 if not font['src'].startswith(('data:','http:','https:')):font['src']=str((source.parent/font['src']).resolve())
if found!=set(patch['replacements']):raise ValueError('Missing measured root IDs')
# The phone backplate must sit behind the independently tracked conversation.
chat=next(l for l in scene['layers'] if l['id']=='g-1197');scene['layers'].remove(chat)
index=next(i for i,l in enumerate(scene['layers']) if l['id']=='g-1237');scene['layers'].insert(index+1,chat)
scene['root_lock_provenance']=patch['provenance'];scene['root_lock_patch']={'file':str(patch_file),'sha256':hashlib.sha256(patch_file.read_bytes()).hexdigest()};scene['source']['notes']+=' Lockscreen/chat handoff measured at native frame indices, with independent caption, bounded original device art, native bubble bodies and semantic glyph outlines. Internal original product artwork is bitmap; no complete reference frame/video layer.'
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(scene,indent=2));print(a.output)
