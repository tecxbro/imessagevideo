from pathlib import Path
import json,copy,argparse,hashlib
REF=Path(__file__).resolve().parent

def apply_phone(scene):
 s=copy.deepcopy(scene);file=REF/'root-phone532-patch.json';p=json.loads(file.read_text());s['layers']=[l for l in s['layers'] if not l['id'].startswith('root-phone532-')];device=next(l for l in s['layers'] if l['id']=='g-1237');device.setdefault('keyframes',{})['opacity']=[dict(t=0,value=1),dict(t=532/30,value=0,ease='hold'),dict(t=533/30,value=1,ease='hold')];chat=next(l for l in s['layers'] if l['id']=='g-1197')
 for c in chat['children']:
  if c['id'] in p['gateChatIDs']:c['end']=c['start']
 pose=copy.deepcopy(p['layers'][0]);body=copy.deepcopy(pose);body['id']='root-phone532-backplate';body['children']=pose['children'][:1];pose['id']='root-phone532-content';pose['children']=pose['children'][1:];index=s['layers'].index(chat);s['layers'].insert(index,body);index=s['layers'].index(chat)+1;s['layers'].insert(index,pose);s['root_phone532_patch']={'scope':p['scope'],'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'notice':p['notice']};return s
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=json.loads(a.input.read_text())
 def absolute(l):
  if l.get('src') and not l['src'].startswith(('/','data:','http:','https:')):l['src']=str((a.input.parent/l['src']).resolve())
  for c in l.get('children',[]):absolute(c)
 for l in s['layers']:absolute(l)
 for f in s.get('fonts',[]):
  if not f['src'].startswith(('/','data:','http:','https:')):f['src']=str((a.input.parent/f['src']).resolve())
 a.output.write_text(json.dumps(apply_phone(s),indent=2));print(a.output)
