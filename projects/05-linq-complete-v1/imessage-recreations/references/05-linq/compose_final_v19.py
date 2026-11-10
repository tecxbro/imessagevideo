"""Compose independently frozen V19 components; preserve prior releases."""
from pathlib import Path
import copy,json,hashlib,importlib.util
D=Path(__file__).resolve().parent;R=D.parent.parent;B=R/'outputs/05-linq/final-v18';source=B/'scene.json';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source)=='f7f499b4ecdf1060135465f41cf27130f27738f01b10f200a1c8c48880af2a8f'
frozen=R/'outputs/05-linq/root-white-pawn-v19/frozen/scene.json';assert sha(frozen)=='b2d9836be6249ce424c1fa5a002ff17ccbda9538cbb46d86ce50ba91b87ca2bc'
s=json.loads(source.read_text())
def absolute(o,base):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src'and isinstance(v,str)and not v.startswith(('data:','http:','https:','/')):o[k]=str((base/v).resolve())
   else:absolute(v,base)
 elif isinstance(o,list):
  for q in o:absolute(q,base)
def mod(name,path):
 z=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(z);z.loader.exec_module(m);return m
absolute(s,B);s=mod('composer19',D/'apply-composers-v19.py').apply_composers(s);s=mod('shadow19',D/'apply-intro-shadow-v19.py').apply_shadow(s);s=mod('pawn19',D/'apply-root-white-pawn-v19.py').apply_white_pawn(s)
# Confirm the actually applied pawn subtree equals the independently frozen release,
# allowing only content-addressed asset filenames to differ.
def find(nodes,identity):
 for q in nodes:
  if q['id']==identity:return q
  z=find(q.get('children',[]),identity)
  if z:return z
def material(o):
 if isinstance(o,dict):return{k:('asset-sha256:'+sha(v)if k=='src'and isinstance(v,str)and not v.startswith('data:')else material(v))for k,v in o.items()}
 if isinstance(o,list):return[material(v)for v in o]
 return o
root=json.loads(frozen.read_text());absolute(root,frozen.parent);assert material(find(s['layers'],'broad-v5-group-20'))==material(find(root['layers'],'broad-v5-group-20'))
release=json.loads((R/'outputs/05-linq/root-cash-control-v19/native-release.json').read_text())
for path,key in [('references/05-linq/apply-root-cash-native-v19.py','helperSHA256'),(release['payload'],'payloadSHA256'),('references/05-linq/root-cash-control-v19/native-measurements.json','measurementsSHA256'),(release['singleStaticAsset'],'assetSHA256')]:assert sha(R/path)==release[key],path
s=mod('cash19',D/'apply-root-cash-native-v19.py').apply_cash_native(s)
assert find(s['layers'],'root-cash-native-control-v19')==json.loads((R/release['payload']).read_text())
s['rebuildRevision']='final-v19'
s['source']['notes']+=' Final V19 restores the first native composer lifecycle0–98: original independent glyphs and actual typing/control births, native closing camera, and measured native field/circle shadows. Cash input768–826 separates one static caret detail from the bounded UI material and animates actual blinks;818–826 uses measured independent input exit. Native Cash pulse774–831 uses a native backing/circle with measured geometry, gray and stroke plus one authentic static plus detail; amount and original panel camera are unchanged. Independent white pawn226–239 restores actual move228–234 and selected-cell/undo state. No source video or complete source-frame sequence is rendered. Static internal UI text remains bitmap where declared; residual original optics, filtering and compression are measured rather than claimed exact.'
out=D/'scene-v19-composed.json';out.write_text(json.dumps(s,indent=2)+'\n');print(out);print(sha(out));print('frozen pawn subtree exact by asset bytes and complete native properties')
