"""Freeze reviewed independent photo patches; source/reference scene untouched."""
from pathlib import Path
import json,copy,hashlib,subprocess
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/06-portrait614';REF=R/'references/06-gallery';BASE=R/'outputs/06-gallery/final-v20';OUT=R/'outputs/06-gallery/portrait614-review-01';B=json.load(open(BASE/'scene.json'));S=json.load(open(P/'color-fit.scene.json'))
def absolute(ls,base):
 for n in ls:
  if n.get('src')and not n['src'].startswith(('/','data:','http:','https:')):n['src']=str((base/n['src']).resolve())
  absolute(n.get('children',[]),base)
absolute(B['layers'],BASE)
def index(ls):
 d={}
 for n in ls:d[n['id']]=n;d.update(index(n.get('children',[])))
 return d
bi,si=index(B['layers']),index(S['layers']);updates={}
for id,n in si.items():
 original=bi[id];delta={k:copy.deepcopy(v)for k,v in n.items()if k!='children'and v!=original.get(k)}
 if delta:updates[id]=delta
assert all(k.startswith(('rene-portrait-v18-613-','rene-portrait-v18-614-','rene-portrait-v18-615-'))for k in updates)
assert set(si)==set(bi)
assert all(set(v)<={'keyframes','shadow','src','width','height'}for v in updates.values()),[(k,list(v))for k,v in updates.items()]
spec=dict(changed_ranges=[[613,615]],node_updates=updates,definition='Only independent static photographed actors613–615. Native editable camera/blur/shadow, higher-resolution genuine79 photo UV, small measured RGB contrast. No complete-source-frame/screen/video sequence.',baseSha256=hashlib.sha256((BASE/'scene.json').read_bytes()).hexdigest())
(REF/'portrait614-review-elements.json').write_text(json.dumps(spec,indent=2));subprocess.run(['python',str(REF/'apply-portrait614-review.py'),'--input',str(BASE/'scene.json'),'--output',str(P/'candidate.scene.json')],check=True)
subprocess.run(['python',str(R/'engines/snapshot_scene.py'),str(P/'candidate.scene.json'),str(OUT)],check=True)
F=json.load(open(OUT/'scene.json'));fi=index(F['layers'])
for id,delta in updates.items():
 if 'src'in delta:
  delta['src']=str((OUT/fi[id]['src']).resolve())
(OUT/'portrait614-review-elements.json').write_text(json.dumps(spec,indent=2));(REF/'portrait614-review-elements.json').write_text(json.dumps(spec,indent=2));print(json.dumps(dict(changedIds=len(updates),sha256=hashlib.sha256((OUT/'scene.json').read_bytes()).hexdigest(),snapshot=str(OUT))))
