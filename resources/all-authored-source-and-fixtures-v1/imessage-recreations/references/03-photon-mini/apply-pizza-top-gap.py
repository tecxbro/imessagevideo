"""Append only the measured original pizza exit at native738–740."""
from pathlib import Path
import argparse,copy,json,hashlib
R=Path(__file__).resolve().parent
DEFAULT=R/'pizza-top-gap/pizza-gap-elements.json'
def apply_pizza_gap(scene,spec_path=None):
 p=Path(spec_path or DEFAULT);spec=json.loads(p.read_text());s=copy.deepcopy(scene)
 if any(n['id']==spec['layer']['id']for n in s['layers']):raise ValueError('Pizza gap already applied')
 s['layers'].append(copy.deepcopy(spec['layer']));s['pizza_top_gap_repair']={'scope':spec['scope'],'specSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'notice':spec['notice']};return s
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=json.loads(a.input.read_text())
 def absolute(n):
  if n.get('src')and not n['src'].startswith(('/','data:','http:','https:')):n['src']=str((a.input.parent/n['src']).resolve())
  for c in n.get('children',[]):absolute(c)
 for n in s['layers']+s.get('fonts',[]):absolute(n)
 a.output.write_text(json.dumps(apply_pizza_gap(s),separators=(',',':')));print(a.output)
