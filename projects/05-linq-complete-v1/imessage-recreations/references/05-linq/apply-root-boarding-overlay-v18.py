from pathlib import Path
import json,copy,argparse
REF=Path(__file__).resolve().parent

def apply_boarding(scene):
 s=copy.deepcopy(scene);p=json.load(open(REF/'root-boarding-overlay-v18-frozen.json'));assert not any(n['id'].startswith('root-boarding-ink-detail-v18-') for n in s['layers']);s['layers']+=copy.deepcopy(p['layers']);return s
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=json.load(open(a.input))
 def absolute(n):
  if n.get('src') and not n['src'].startswith(('/','data:','http:','https:')):n['src']=str((a.input.parent/n['src']).resolve())
  for c in n.get('children',[]):absolute(c)
 for n in s['layers']:absolute(n)
 for f in s.get('fonts',[]):f['src']=str((a.input.parent/f['src']).resolve())
 a.output.write_text(json.dumps(apply_boarding(s),indent=2));print(a.output)
