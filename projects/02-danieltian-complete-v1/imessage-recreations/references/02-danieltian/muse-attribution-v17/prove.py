from pathlib import Path
import importlib.util,json,hashlib
R=Path(__file__).resolve().parent;ROOT=R.parents[2];O=ROOT/'outputs/02-danieltian/muse-attribution-v17';old=R.parent/'orbit-identity-v17';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
base=ROOT/'outputs/02-danieltian/final-v16/scene.json';expected='6cc308bf03330758ec17cc97ece6054e74da42694310c463aae029f77758dcfa';assert sha(base)==expected;s=json.load(open(base));green=module('accepted_orbit',old/'apply.py').apply(s);muse=module('muse_component',R/'apply.py').apply(green);changed=[]
assert set(green)==set(muse)
for k in green:
 if k!='layers':assert green[k] is muse[k]
assert len(green['layers'])==len(muse['layers'])
for before,after in zip(green['layers'],muse['layers']):
 if before is after:continue
 assert before['id']==after['id'];n=int(before['id'].split('-')[-1]);assert 553<=n<=587
 for k in before:
  if k!='children':assert before[k]==after[k]
 assert len(before['children'])==len(after['children'])
 for x,y in zip(before['children'],after['children']):
  if x is not y:assert x['id']==y['id'] and x['id'].endswith('middle-fly-muse')
 changed.append(dict(frame=n,before=before,after=after))
assert [x['frame'] for x in changed]==list(range(553,588));assert sha(base)==expected;control=O/'changed-group-control.json';control.write_text(json.dumps(dict(duration=s['duration'],fps=s['fps'],frames=round(s['duration']*s['fps']),groups=changed),indent=2));proof=dict(baseSceneSHA256=expected,acceptedOrbitHelperSHA256=sha(old/'apply.py'),acceptedOrbitSpecSHA256=sha(old/'patch-spec.json'),helperSHA256=sha(R/'apply.py'),patchSHA256=sha(R/'patch-spec.json'),allGlobalMetadataIsSameObject=True,allOtherRootNodesAreSameObjects=True,allOtherActorsAreSameObjects=True,changedParents=[x['before']['id'] for x in changed],originalSourceCanonicalUnchanged=True,definition='Full immutable V16 loaded, accepted39op orbit helper applied without mutation, independent Muse helper applied on top. Only selected Muse copies differ. No other actor, header/glass, font, gradient, global metadata, asset or parent lifecycle changes.');(O/'scope-structural-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
