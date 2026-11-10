"""Apply only measured native semantic title states321–407 and556–596.
All original source597+ title camera and portrait states remain untouched.
"""
from pathlib import Path
import argparse,copy,json,hashlib
R=Path(__file__).resolve().parent

def apply_titles(scene,elements=None):
 p=Path(elements) if elements else R/'title-review/title-elements-final.json';spec=json.loads(p.read_text());out=copy.deepcopy(scene);replace=spec['replacements'];fieldPatches=spec.get('fieldPatches',{});added={q['id'] for q in spec.get('append',[])};present={q['id'] for q in out['layers']}
 if (set(replace)|set(fieldPatches))-present:raise ValueError('Expected title roots missing:'+str((set(replace)|set(fieldPatches))-present))
 out['layers']=[{**copy.deepcopy(replace.get(q['id'],q)),**copy.deepcopy(fieldPatches.get(q['id'],{}))} for q in out['layers'] if q['id'] not in added]+copy.deepcopy(spec.get('append',[]));out['native_title_review']={'elements':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scopedNativeFrames':spec['scope'],'provenance':spec['provenance']};return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--elements',type=Path);a=p.parse_args();scene=json.loads(a.input.read_text())
 def absolute(o):
  if isinstance(o,dict):
   if o.get('src') and not o['src'].startswith(('data:','http:','https:','/')):o['src']=str((a.input.parent/o['src']).resolve())
   for v in o.values():absolute(v)
  elif isinstance(o,list):
   for v in o:absolute(v)
 absolute(scene);a.output.write_text(json.dumps(apply_titles(scene,a.elements),indent=2));print(a.output)
if __name__=='__main__':main()
