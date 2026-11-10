from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parent;ROOT=R.parents[2];O=ROOT/'outputs/02-danieltian/muse-continuation-v19';sys.path.insert(0,str(R));from apply import apply
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base=ROOT/'outputs/02-danieltian/final-v18/scene.json';expected='14657bfc3d9f77a86a92e84367a4b557e925530380a3d6893cbfaeb4420217e2';assert sha(base)==expected;scene=json.load(open(base));out=apply(scene);spec=json.load(open(R/'patch-spec.json'));changed=[]
assert set(scene)==set(out)
for k in scene:
 if k!='layers':assert scene[k] is out[k],k
assert len(scene['layers'])==len(out['layers'])
for before,after in zip(scene['layers'],out['layers']):
 if before is after:continue
 assert before['id']==after['id']==spec['parentID'];changed.append((before,after))
assert len(changed)==1;before,after=changed[0]
for k in before:
 if k!='children':assert before[k] is after[k] or before[k]==after[k]
N=len(before['children']);assert len(after['children'])==N+len(spec['complements']);avatarBefore=None;avatarAfter=None
for a,b in zip(before['children'],after['children'][:N]):
 assert a['id']==b['id']
 if a is not b:
  assert a['id']==spec['avatarID'];avatarBefore=a;avatarAfter=b
assert avatarBefore is not None
for k in avatarBefore:
 if k!='keyframes':assert avatarBefore[k] is avatarAfter[k] or avatarBefore[k]==avatarAfter[k],k
assert set(avatarBefore['keyframes'])==set(avatarAfter['keyframes'])
for k in avatarBefore['keyframes']:
 if k!='opacity':assert avatarBefore['keyframes'][k] is avatarAfter['keyframes'][k],k
for key in avatarBefore['keyframes']['opacity']:assert key in avatarAfter['keyframes']['opacity'],'original opacity key altered'
def ids(n):
 yield n['id']
 for c in n.get('children',[]):yield from ids(c)
originalIDs={id for p in scene['layers'] for id in ids(p)};newIDs=[]
for node in after['children'][N:]:
 newIDs.extend(ids(node))
 assert len(node['children'])==len(avatarBefore['children'])
 for a,b in zip(avatarBefore['children'],node['children']):assert {k:v for k,v in a.items() if k!='id'}=={k:v for k,v in b.items() if k!='id'}
assert not set(newIDs)&originalIDs and len(newIDs)==len(set(newIDs));assert sha(base)==expected
(O/'changed-parent-control.json').write_text(json.dumps(dict(duration=scene['duration'],fps=scene['fps'],frames=round(scene['duration']*scene['fps']),before=before,after=after,avatarBefore=avatarBefore,avatarAfter=avatarAfter),indent=2));proof=dict(baseSceneSHA256=expected,helperSHA256=sha(R/'apply.py'),patchSHA256=sha(R/'patch-spec.json'),rootLayerCount=len(scene['layers']),allRootMetadataIsSameObject=True,onlyChangedExistingActor=spec['avatarID'],onlyChangedExistingField='keyframes.opacity',allExistingAvatarCameraAssetLifecycleAndOtherTracksUnchanged=True,allOriginalOpacityKeysRetained=True,allOtherExistingChildrenAreSameObjects=True,allOriginalChildOrderPreserved=True,appendedOriginalArtClones=len(spec['complements']),newUniqueIDs=len(newIDs),newIDsDoNotCollide=True,sourceCanonicalUnchanged=True);(O/'scope-structural-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
