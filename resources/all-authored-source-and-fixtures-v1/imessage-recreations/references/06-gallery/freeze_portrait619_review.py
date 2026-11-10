"""Independent single-frame continuation on top of reviewed frozen02."""
from pathlib import Path
import json,copy,hashlib,subprocess
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/06-portrait614';REF=R/'references/06-gallery';BASE=R/'outputs/06-gallery/portrait614-review-02';OUT=R/'outputs/06-gallery/portrait619-optical-review-02';B=json.load(open(BASE/'scene.json'));S=json.load(open(P/'optical-tail.scene.json'))
def absolute(ls):
 for n in ls:
  if n.get('src')and not n['src'].startswith(('/','data:','http:','https:')):n['src']=str((BASE/n['src']).resolve())
  absolute(n.get('children',[]))
absolute(B['layers'])
def index(ls):
 d={}
 for n in ls:d[n['id']]=n;d.update(index(n.get('children',[])))
 return d
bi,si=index(B['layers']),index(S['layers']);assert set(bi)==set(si);updates={}
def same(k,x,y):
 if k=='src'and x and y and not str(x).startswith(('data:','http:','https:'))and not str(y).startswith(('data:','http:','https:')):return hashlib.sha256(Path(x).read_bytes()).digest()==hashlib.sha256(Path(y).read_bytes()).digest()
 return x==y
for ident,n in si.items():
 delta={k:copy.deepcopy(v)for k,v in n.items()if k!='children'and not same(k,v,bi[ident].get(k))}
 if delta:updates[ident]=delta
assert all(k.startswith('rene-portrait-v18-619-')for k in updates)
spec=dict(changed_ranges=[[619,619]],node_updates=updates,definition='Only619 independent photographed optical materials, following the source-proven continuation beyond the prior artificial618 boundary. Source RGB excludes every other photo and nativeUI mask. All1482 outside states retained relative to frozen02; no scene/frame/screen/video texture.',materialEditability='Each photo remains a native independent actor/camera/clip with bounded genuine projectedRGB/softAlpha/shadow material; optical shader/3D photo is not editable.',baseSha256=hashlib.sha256((BASE/'scene.json').read_bytes()).hexdigest())
file=P/'portrait619-review-elements.json';file.write_text(json.dumps(spec,indent=2));subprocess.run(['python',str(REF/'apply-portrait614-review.py'),'--input',str(BASE/'scene.json'),'--elements',str(file),'--output',str(P/'tail-candidate.scene.json')],check=True);subprocess.run(['python',str(R/'engines/snapshot_scene.py'),str(P/'tail-candidate.scene.json'),str(OUT)],check=True);fi=index(json.load(open(OUT/'scene.json'))['layers'])
for ident,delta in updates.items():
 if 'src'in delta:delta['src']=str((OUT/fi[ident]['src']).resolve())
(OUT/'portrait619-review-elements.json').write_text(json.dumps(spec,indent=2));print(json.dumps(dict(changedIds=len(updates),sha256=hashlib.sha256((OUT/'scene.json').read_bytes()).hexdigest(),snapshot=str(OUT))))
