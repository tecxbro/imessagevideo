"""Apply only the15 measured independent food/Order! roots for730–799.
Import apply_food(scene) for the joint scene merge; native UI/phone/backplane data is preserved.
"""
from pathlib import Path
import argparse,copy,json,hashlib
R=Path(__file__).resolve().parent

def apply_food(scene,spec_path=None):
 p=Path(spec_path) if spec_path else R/'food-orbit-final.json';spec=json.loads(p.read_text());result=copy.deepcopy(scene);replace=spec['replacements'];present={n['id'] for n in result['layers']}
 if set(replace)-present:raise ValueError('Expected food roots absent: '+str(set(replace)-present))
 result['layers']=[copy.deepcopy(replace.get(n['id'],n)) for n in result['layers']];result.setdefault('source',{})['notes']=result.get('source',{}).get('notes','')+' Source730–799 independent food/order refinement: authentic separate Apple artwork under native measured two-rotation affine poses; separate native Order! bodies/text retain actual source short-word bounds/visibility. Bitmap food internals and2D projection/lighting limits are declared. No full-source-frame/video layer.';result['food_orbit_refinement']={'spec':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':[730,799],'roots':list(replace),'editability':spec['provenance']['limitations']};return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--spec',type=Path);a=p.parse_args();scene=json.loads(a.input.read_text())
 def absolute(n):
  if isinstance(n,dict):
   if n.get('src') and not n['src'].startswith(('data:','http:','https:','/')):n['src']=str((a.input.parent/n['src']).resolve())
   for v in n.values():absolute(v)
  elif isinstance(n,list):
   for v in n:absolute(v)
 absolute(scene);a.output.write_text(json.dumps(apply_food(scene,a.spec),indent=2));print(a.output)
if __name__=='__main__':main()
