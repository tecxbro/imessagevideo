from pathlib import Path
import json,copy,argparse
REF=Path(__file__).resolve().parent

def apply_boarding(scene):
 s=copy.deepcopy(scene);p=json.load(open(REF/'root-boarding-detail-v18-patch.json'));g=next(n for n in s['layers'] if n['id']==p['parentId']);image=next(n for n in g['children'] if n['id']==p['gateOriginalId']);assert not image.get('keyframes',{}).get('opacity');image.setdefault('keyframes',{})['opacity']=[dict(t=0,value=1),dict(t=1200/30,value=0,ease='hold'),dict(t=1221/30,value=1,ease='hold')];s['layers'].insert(s['layers'].index(g)+1,copy.deepcopy(p['layer']));return s
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=json.load(open(a.input))
 def absolute(n):
  if n.get('src') and not n['src'].startswith(('/','data:','http:','https:')):n['src']=str((a.input.parent/n['src']).resolve())
  for c in n.get('children',[]):absolute(c)
 for n in s['layers']:absolute(n)
 for f in s.get('fonts',[]):f['src']=str((a.input.parent/f['src']).resolve())
 a.output.write_text(json.dumps(apply_boarding(s),indent=2));print(a.output)
