from pathlib import Path
import json,importlib.util,math,re
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'verification/compare.py';s=importlib.util.spec_from_file_location('compare',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);scan=json.loads((ROOT/'verification/timeline-scans/02-danieltian-v14/scan.json').read_text());frames=sorted(q['candidate_frame']for q in scan['peaks']);out=ROOT/'verification/final/02-danieltian/source-gsap-v14/native-peaks';out.mkdir(exist_ok=False);mapping={}
for kind,file in [('reference',ROOT/'references/02-danieltian/source.mp4'),('candidate',ROOT/'outputs/02-danieltian/gsap.mp4')]:
 info=m.probe(file);paths=m.batch_native_frames(file,[f/30 for f in frames],info,None,out/kind);mapping[kind]={str(f):str(p)for f,p in paths.items()};print('decoded',kind,len(paths),flush=True)
(out/'mapping.json').write_text(json.dumps(mapping,indent=2));scene=json.loads((ROOT/'outputs/02-danieltian/final-v14/scene.json').read_text());rows=[]
def walk(n,parent=''):
 text=str(n.get('text',''));name=n['id'];semantic=str(n.get('semanticCopy',''))
 if re.search(r'budget|love|typing|airbnb.*avatar|avatar.*airbnb',name+' '+text+' '+semantic,re.I):
  rows.append({k:n[k]for k in['id','type','start','end','text','semanticCopy','x','y','width','height','opacity']if k in n}|{'parent':parent,'children':len(n.get('children',[])),'keyframeProperties':list(n.get('keyframes',{}))})
 for c in n.get('children',[]):walk(c,name)
for n in scene['layers']:walk(n)
(out/'relevant-id-audit.json').write_text(json.dumps(rows,indent=2));print('relevant nodes',len(rows));print(json.dumps(rows[:50],indent=2))
