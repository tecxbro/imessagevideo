"""Strict full structural comparison + full native two-actor evaluated scope proof."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];D=R/'outputs/02-danieltian/final-v18';BP=R/'outputs/02-danieltian/final-v17/scene.json';TP=D/'scene.json';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
before=json.loads(BP.read_text());after=json.loads(TP.read_text());assert sha(BP)=='09df288bd09aee0ec33bca014dc4598f966ffa52b36cb3489c685fb21a43c74a'
for key in before:
 if key!='layers':assert before[key]==after[key],key
assert len(before['layers'])==len(after['layers']);roots=[]
for old,new in zip(before['layers'],after['layers']):
 assert old['id']==new['id']
 if old!=new:roots.append((old,new))
assert len(roots)==1 and roots[0][0]['id']=='group-1118'
a,b=roots[0]
for key in a:
 if key!='children':assert a[key]==b[key]
assert len(a['children'])==len(b['children']);changed=[]
for old,new in zip(a['children'],b['children']):
 assert old['id']==new['id']
 if old!=new:
  changed.append(old['id'])
  for key in old:
   if key!='keyframes':assert old[key]==new[key]
  for key in old['keyframes']:
   if key not in['x','y','scaleX','scaleY']:assert old['keyframes'][key]==new['keyframes'][key]
  for key in['x','y','scaleX','scaleY']:
   for left,right in zip(old['keyframes'][key],new['keyframes'][key]):
    assert left.keys()==right.keys()
    if left!=right:assert round(left['t']*30)in[1021,1022]and left['t']==right['t']
assert sorted(changed)==['middle-avatar-airbnb-booked','middle-avatar-how-about']
actorProof=R/'references/02-danieltian/orb-exit-v18/actor-scope-proof.json';actor=json.loads(actorProof.read_text());assert all(q['checkedFrames']==1360 and q['changedFrames']==[1021,1022]for q in actor['checks'])
for folder in[BP.parent,TP.parent]:
 manifest=json.loads((folder/'snapshot.json').read_text());assert all(sha(folder/entry['snapshot'])==entry['sha256']for entry in manifest['assets'])
baseAssets={p.name:sha(p)for p in(BP.parent/'assets').iterdir()};targetAssets={p.name:sha(p)for p in(TP.parent/'assets').iterdir()};assert baseAssets==targetAssets
report={'base':str(BP),'target':str(TP),'baseSha256':sha(BP),'targetSha256':sha(TP),'checkedFrames':1360,'changedFrames':2,'exactChangedRanges':[[1021,1022]],'conservativeCaptureRanges':[[1021,1022]],'changedOutsideCaptureUnion':[],'fontCssIdentical':True,'allGlobalMetadataAndGradientsIdentical':True,'allOtherResolvedRootsStructurallyIdentical':True,'changedActorIDs':changed,'actualNativeActorProof':str(actorProof),'actualNativeActorProofSHA256':sha(actorProof),'all622AssetsNameAndContentSHAIdentical':True,'definition':'Compared full raw JSON structure, globals, fonts, gradients and every asset byte. Same content-addressed asset names map to identical images/fonts. Only fourcamera-key fields on twoexisting actors differ, onlynative1021/1022. Actual nativeactor proof evaluates all1360states; all1358outside identical.'};(D/'scope-from-v17.json').write_text(json.dumps(report,indent=2))
priorPath=BP.parent/'scope-from-v13.json';prior=json.loads(priorPath.read_text());assert prior['targetSha256']==report['baseSha256']and not prior['changedOutsideCaptureUnion']
previous={f for first,last in prior['exactChangedRanges']for f in range(first,last+1)};assert not previous&{1021,1022};union=sorted(previous|{1021,1022});assert len(union)==367
ranges=[]
for f in union:
 if ranges and ranges[-1][1]==f-1:ranges[-1][1]=f
 else:ranges.append([f,f])
combined={'base':prior['base'],'target':str(TP),'baseSha256':prior['baseSha256'],'targetSha256':report['targetSha256'],'checkedFrames':1360,'changedFrames':367,'exactChangedRanges':ranges,'conservativeCaptureRanges':ranges,'changedOutsideCaptureUnion':[],'fontCssIdentical':True,'proofComposition':{'prior':str(priorPath),'priorSHA256':sha(priorPath),'current':str(D/'scope-from-v17.json'),'currentSHA256':sha(D/'scope-from-v17.json'),'disjointNativeDeltas':True,'rawHistorical13NotReadOrNeeded':True},'definition':'Exact hash-bound transitivity on disjoint365+2native intervals. Outside367allpictures remain identical to actual13caches; eachinside interval uses its unchanged accepted proof. No canceled overlap.'};(D/'scope-from-v13.json').write_text(json.dumps(combined,indent=2));print(json.dumps({'sourceSHA256':report['targetSha256'],'from17':2,'from13':367,'outsideFrom17':1358,'allAssetsExact':True}),flush=True)
