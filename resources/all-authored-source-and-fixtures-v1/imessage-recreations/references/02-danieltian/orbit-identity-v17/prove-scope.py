from pathlib import Path
import json,sys,hashlib
R=Path(__file__).resolve().parent;ROOT=R.parents[2];O=ROOT/'outputs/02-danieltian/orbit-identity-v17';sys.path.insert(0,str(R));from apply import apply
base=ROOT/'outputs/02-danieltian/final-v16/scene.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected='6cc308bf03330758ec17cc97ece6054e74da42694310c463aae029f77758dcfa';assert sha(base)==expected;s=json.load(open(base));b=apply(s);changed=[]
assert set(s)==set(b)
for k in s:
 if k!='layers':assert b[k] is s[k],k
assert len(s['layers'])==len(b['layers'])
for old,new in zip(s['layers'],b['layers']):
 if old is new:continue
 assert old['id']==new['id'];n=int(old['id'].split('-')[-1]);assert 560<=n<=597
 for k in old:
  if k!='children':assert old[k]==new[k],(old['id'],k)
 oldchildren={x['id']:x for x in old['children']};newchildren={x['id']:x for x in new['children']}
 assert set(oldchildren)<=set(newchildren)
 for id,node in newchildren.items():
  if id not in oldchildren:assert n<=563 and id.endswith('middle-fly-green')
  elif node is not oldchildren[id]:assert id.endswith('middle-fly-green') or n==565 and id.endswith('middle-fly-lyft')
 changed.append(dict(frame=n,before=old,after=new))
assert [q['frame'] for q in changed]==list(range(560,598));assert sha(base)==expected
control=O/'changed-group-control.json';control.write_text(json.dumps(dict(duration=s['duration'],fps=s['fps'],width=s['width'],height=s['height'],frames=round(s['duration']*s['fps']),groups=changed),indent=2));report=dict(base=str(base),baseSceneSHA256=expected,helperSHA256=sha(R/'apply.py'),patchSHA256=sha(R/'patch-spec.json'),rootLayerCount=len(s['layers']),rootMetadataUnchanged=True,fontsGradientsUnchanged=True,changedParents=[q['before']['id'] for q in changed],allOtherRootNodesAreSameObjects=True,unchangedChildrenAreSameObjects=True,retainsAllExistingActorIDs=True,newNodes='Only genuine green artwork clones560–563',sourceCanonicalBytesUnchanged=True,changedGroupControl=str(control));(O/'scope-structural-proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
