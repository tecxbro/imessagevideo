"""Full structural proof of the avatar-family-only19 change; native fixture is independently evaluated."""
from pathlib import Path
import json,hashlib,subprocess,copy
R=Path(__file__).resolve().parents[2];D=R/'outputs/02-danieltian/final-v19';BP=R/'outputs/02-danieltian/final-v18/scene.json';TP=D/'scene.json';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
before=json.loads(BP.read_text());after=json.loads(TP.read_text());assert sha(BP)=='14657bfc3d9f77a86a92e84367a4b557e925530380a3d6893cbfaeb4420217e2'
for key in before:
 if key!='layers':assert before[key]==after[key],key
assert len(before['layers'])==len(after['layers']);changedRoots=[]
for old,new in zip(before['layers'],after['layers']):
 assert old['id']==new['id']
 if old!=new:changedRoots.append((old,new))
assert len(changedRoots)==1 and changedRoots[0][0]['id']=='group-1118'
a,b=changedRoots[0]
for key in a:
 if key!='children':assert a[key]==b[key]
oldChildren=a['children'];newChildren=b['children'];assert len(newChildren)>len(oldChildren);changedExisting=[]
for old,new in zip(oldChildren,newChildren):
 assert old['id']==new['id']
 if old!=new:
  changedExisting.append((old,new));assert old['id']=='middle-avatar-muse'
  for key in old:
   if key!='keyframes':assert old[key]==new[key]
  assert set(old['keyframes'])==set(new['keyframes'])
  for key in old['keyframes']:
   if key!='opacity':assert old['keyframes'][key]==new['keyframes'][key]
assert len(changedExisting)==1
appended=newChildren[len(oldChildren):];assert len({q['id']for q in newChildren})==len(newChildren)
for folder in[BP.parent,TP.parent]:
 manifest=json.loads((folder/'snapshot.json').read_text());assert all(sha(folder/p['snapshot'])==p['sha256']for p in manifest['assets'])
assert {p.name:sha(p)for p in(BP.parent/'assets').iterdir()}=={p.name:sha(p)for p in(TP.parent/'assets').iterdir()}
oldRoot={k:copy.deepcopy(v)for k,v in a.items()if k!='children'};newRoot=copy.deepcopy(oldRoot);oldRoot['children']=[copy.deepcopy(changedExisting[0][0])];newRoot['children']=[copy.deepcopy(changedExisting[0][1])]+copy.deepcopy(appended)
def absolute(node):
 if node.get('src')and not node['src'].startswith(('/','data:','http:','https:')):node['src']=str((TP.parent/node['src']).resolve())
 for child in node.get('children',[]):absolute(child)
absolute(oldRoot);absolute(newRoot)
fixture=D/'avatar-native-scope-fixture.json';fixture.write_text(json.dumps({'duration':after['duration'],'fps':after['fps'],'before':oldRoot,'after':newRoot},separators=(',',':')))
subprocess.run(['node',str(R/'references/02-danieltian/prove-v19-avatar-native.mjs'),str(fixture)],cwd=R,check=True)
nativePath=Path(str(fixture)+'.proof.json');native=json.loads(nativePath.read_text());changed=native['changedFrames'];assert changed==list(range(666,670))+list(range(676,680))+list(range(701,705))
def ranges(frames):
 out=[]
 for frame in frames:
  if out and out[-1][1]==frame-1:out[-1][1]=frame
  else:out.append([frame,frame])
 return out
report={'base':str(BP),'target':str(TP),'baseSha256':sha(BP),'targetSha256':sha(TP),'checkedFrames':1360,'changedFrames':len(changed),'exactChangedRanges':ranges(changed),'conservativeCaptureRanges':ranges(changed),'changedOutsideCaptureUnion':[],'fontCssIdentical':True,'allGlobalMetadataAndGradientsIdentical':True,'allOtherResolvedRootsStructurallyIdentical':True,'changedExistingActorFields':{'middle-avatar-muse':['opacity']},'appendedActorIDs':[q['id']for q in appended],'nativeFamilyFixture':str(fixture),'nativeFamilyFixtureSHA256':sha(fixture),'nativeFamilyScopeProof':str(nativePath),'nativeFamilyScopeProofSHA256':sha(nativePath),'all622AssetsIdentical':True,'definition':'Full JSON/global/asset-byte comparison. Every original actor except Museopacity is exact; appended complementary original-art actors only. Independent actual-image/native-parent SVG evaluates all1360avatar-family states; no other state can change.'};(D/'scope-from-v18.json').write_text(json.dumps(report,indent=2))
priorPath=BP.parent/'scope-from-v13.json';prior=json.loads(priorPath.read_text());assert prior['targetSha256']==report['baseSha256']and not prior['changedOutsideCaptureUnion'];previous={f for first,last in prior['exactChangedRanges']for f in range(first,last+1)};assert not previous&set(changed);union=sorted(previous|set(changed))
combined={'base':prior['base'],'target':str(TP),'baseSha256':prior['baseSha256'],'targetSha256':report['targetSha256'],'checkedFrames':1360,'changedFrames':len(union),'exactChangedRanges':ranges(union),'conservativeCaptureRanges':ranges(union),'changedOutsideCaptureUnion':[],'fontCssIdentical':True,'proofComposition':{'prior':str(priorPath),'priorSHA256':sha(priorPath),'current':str(D/'scope-from-v18.json'),'currentSHA256':sha(D/'scope-from-v18.json'),'disjointNativeDeltas':True,'rawHistorical13NotReadOrNeeded':True},'definition':'Hash-bound strict proof composition on disjoint367+avatar-overlap native states. Every outside point remains exact against actual13caches.'};(D/'scope-from-v13.json').write_text(json.dumps(combined,indent=2));print(json.dumps({'sourceSHA256':report['targetSha256'],'from18':len(changed),'from13':len(union),'ranges':ranges(changed),'allAssetsExact':True}),flush=True)
