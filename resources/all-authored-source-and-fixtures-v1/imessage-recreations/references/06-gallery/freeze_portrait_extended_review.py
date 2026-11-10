"""Freeze combined independent camera/material repair, without changing frozen01."""
from pathlib import Path
import json,copy,hashlib,subprocess
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/06-portrait614';REF=R/'references/06-gallery';BASE=R/'outputs/06-gallery/final-v20';OUT=R/'outputs/06-gallery/portrait614-review-02';B=json.load(open(BASE/'scene.json'));S=json.load(open(P/'optical-original.scene.json'))
def absolute(ls,base):
 for n in ls:
  if n.get('src')and not n['src'].startswith(('/','data:','http:','https:')):n['src']=str((base/n['src']).resolve())
  absolute(n.get('children',[]),base)
absolute(B['layers'],BASE)
def index(ls):
 d={}
 for n in ls:d[n['id']]=n;d.update(index(n.get('children',[])))
 return d
bi,si=index(B['layers']),index(S['layers']);assert set(bi)==set(si);updates={}
def same(k,x,y):
 if k=='src'and x and y and not str(x).startswith(('data:','http:','https:'))and not str(y).startswith(('data:','http:','https:')):return hashlib.sha256(Path(x).read_bytes()).digest()==hashlib.sha256(Path(y).read_bytes()).digest()
 return x==y
for ident,n in si.items():
 original=bi[ident];delta={k:copy.deepcopy(v)for k,v in n.items()if k!='children'and not same(k,v,original.get(k))}
 if delta:updates[ident]=delta
allowed=tuple(f'rene-portrait-v18-{f}-'for f in range(613,622));assert all(k.startswith(allowed)for k in updates),[k for k in updates if not k.startswith(allowed)];assert all(set(v)<={'keyframes','shadow','src','x','y','width','height'}for v in updates.values())
spec=dict(changed_ranges=[[613,621]],node_updates=updates,definition='Only independently bounded photographed actors.613–615 original measured camera/material correction retained as immutable01.614–618 add permitted per-photo optical materials with original offscreen/hidden continuation, no other photo or UI sampled.618–621 photo75 full occlusion-reveal camera;622+ preserved. Not a scene/screen/frame/video texture.',opticalPoseFrames=[614,615,616,617,618],materialEditability='Every photo remains an independently editable native actor/camera/clip. The short optical pose rasterizes its projected RGB/soft alpha/shadow; it is not an editable3D photograph or editable optical shader.',baseSha256=hashlib.sha256((BASE/'scene.json').read_bytes()).hexdigest())
(REF/'portrait614-review-elements.json').write_text(json.dumps(spec,indent=2));subprocess.run(['python',str(REF/'apply-portrait614-review.py'),'--input',str(BASE/'scene.json'),'--output',str(P/'extended-candidate.scene.json')],check=True);subprocess.run(['python',str(R/'engines/snapshot_scene.py'),str(P/'extended-candidate.scene.json'),str(OUT)],check=True);fi=index(json.load(open(OUT/'scene.json'))['layers'])
for ident,delta in updates.items():
 if 'src'in delta:delta['src']=str((OUT/fi[ident]['src']).resolve())
(OUT/'portrait614-review-elements.json').write_text(json.dumps(spec,indent=2));(REF/'portrait614-review-elements.json').write_text(json.dumps(spec,indent=2));print(json.dumps(dict(changedIds=len(updates),sha256=hashlib.sha256((OUT/'scene.json').read_bytes()).hexdigest(),snapshot=str(OUT))))
