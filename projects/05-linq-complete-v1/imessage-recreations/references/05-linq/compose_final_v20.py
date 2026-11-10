"""Compose two immutable, independently validated V20 follow-ups from frozen19."""
from pathlib import Path
import hashlib, importlib.util, json
D=Path(__file__).resolve().parent
R=D.parent.parent
B=R/'outputs/05-linq/final-v19'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(B/'scene.json')=='285407b8f837e780aa4962dc9ec3ffa0b1aabce5d93a197e1670166c6ed5f519'
release=json.load(open(R/'outputs/05-linq/root-cash-plane-v20/release.json'))
for path,expected in release['hashes'].items():
    assert sha(R/path)==expected,path
assert sha(D/'restaurant-bottom-v20-frozen-elements.json')=='8b0612250438c1a64c0e3bfe1bf4741c3eeaf3fe9e88dca62e458e4b7b164075'
def absolute(o,base):
    if isinstance(o,dict):
        for k,v in o.items():
            if k=='src' and isinstance(v,str) and not v.startswith(('data:','http:','https:','/')):
                o[k]=str((base/v).resolve())
            else:
                absolute(v,base)
    elif isinstance(o,list):
        for v in o:
            absolute(v,base)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
def find(nodes,identity):
    for node in nodes:
        if node['id']==identity:
            return node
        found=find(node.get('children',[]),identity)
        if found is not None:
            return found
def material(o):
    if isinstance(o,dict):
        return {k:('asset-sha256:'+sha(v) if k=='src' and isinstance(v,str) and not v.startswith('data:') else material(v)) for k,v in o.items()}
    if isinstance(o,list):
        return [material(v) for v in o]
    return o
scene=json.load(open(B/'scene.json'))
absolute(scene,B)
scene=module('cash20',D/'apply-root-cash-plane-v20.py').apply_cash_plane(scene)
accepted=R/'outputs/05-linq/root-cash-plane-v20/scene-quantized.json'
reference=json.load(open(accepted))
absolute(reference,accepted.parent)
assert material(find(scene['layers'],'v10-cash-panel'))==material(find(reference['layers'],'v10-cash-panel'))
scene=module('restaurant20',D/'apply-restaurant-bottom-v20.py').apply_restaurant_bottom(scene)
scene['rebuildRevision']='final-v20'
scene['source']['notes']+=' Final V20 corrects the false Cash panel fading using the verified native 8-bit premultiplied-floor response and quantized L1 alpha selection. Native pulse fill/stroke are recalibrated to preserve displayed gray, with one static plus detail. Strong states remain unchanged; no diagnostic control poses are runtime layers. A single static restaurant lower-document component restores the complete price, Reported by and Find a table rows only1144–1148, under the unchanged document camera/opacity. Every local changed native frame improves. Other documented photo, board and gallery optics/material residuals remain; exact original transfer/filters and absolute1:1 have not been recovered.'
out=D/'scene-v20-composed.json'
out.write_text(json.dumps(scene,indent=2)+'\n')
print(out)
print(sha(out))
print('Applied Cash panel exactly matches its independently accepted native release by all properties and asset bytes.')
