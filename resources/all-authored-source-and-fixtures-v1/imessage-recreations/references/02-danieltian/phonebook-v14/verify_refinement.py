from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parent;a=json.loads((R/'elements-candidate.json').read_text());b=json.loads((R/'elements-refined.json').read_text());assert a['scope']==b['scope'] and a['gates']==b['gates'];assert[n['id']for n in a['layers']]==[n['id']for n in b['layers']];rows=[]
for x,y in zip(a['layers'],b['layers']):
 if x==y:continue
 assert x['start']==y['start'] and x['end']==y['end'];f=round(x['start']*30);assert abs(x['end']-(f+1)/30)<1e-12;assert 436<=f<=525;assert x['id'].startswith(('pb14-field-','pb14-query-'));rows.append({'id':x['id'],'frame':f})
frames=sorted({q['frame']for q in rows});assert frames==json.loads((R/'refinement-changed-frames.json').read_text());C=R/'native-check-refined';C.mkdir(exist_ok=True)
for f in range(435,527):
 source=R/'native-check'/f'{f/30:.3f}.png';dest=C/source.name;shutil.copy2(source,dest)
 assert source.stat().st_ino!=dest.stat().st_ino
rep={'oldSpecSha256':hashlib.sha256((R/'elements-candidate.json').read_bytes()).hexdigest(),'newSpecSha256':hashlib.sha256((R/'elements-refined.json').read_bytes()).hexdigest(),'rootOrderAndAllUnchangedNodesExact':True,'changedOneFrameRootCount':len(rows),'exactChangedFrames':frames,'changedRoots':rows,'originalGatesAndScopeExact':True,'nativeInheritance':'Independent PNG copies for states outside the exact changed one-frame-root union; full root values/order are identical there. Boundary435/526 will also be recaptured. No production/cache hardlink is overwritten.'};(R/'refinement-structural-proof.json').write_text(json.dumps(rep,indent=2));print(json.dumps({k:v for k,v in rep.items()if k!='changedRoots'}))
