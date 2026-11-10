from pathlib import Path
import json,hashlib,os,shutil
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
controls=[]
for f in[271,372,373,374,375]:
    fresh=R/'reasoning-final-controls'/f'{f/30:.3f}.png';comparison=R/'reasoning-dense-native'/fresh.name
    old=np.asarray(Image.open(comparison).convert('RGB')).astype('int16');new=np.asarray(Image.open(fresh).convert('RGB')).astype('int16')
    baseline=np.asarray(Image.open(R/'reasoning-baseline'/f'{f:06d}.png').convert('RGB')).astype('int16')
    row={'frame':f,'finalVsPilotMax':int(abs(new-old).max()),'finalVsBaselineMax':int(abs(new-baseline).max())};controls.append(row)
    if f in[271,374,375]:assert row['finalVsPilotMax']==0
    if f==372:assert row['finalVsPilotMax']<=2
    if f==373:
        assert row['finalVsBaselineMax']==0
        history=R/'reasoning-dense-native-before373.png';os.link(comparison,history)
        temp=comparison.with_suffix('.final.tmp.png');shutil.copyfile(fresh,temp);temp.replace(comparison)
metrics=json.loads((R/'reasoning-dense-metrics.json').read_text());source=np.asarray(Image.open(R/'reasoning-source/source-0373.png').convert('RGB')).astype('int16');final=np.asarray(Image.open(R/'reasoning-final-controls'/f'{373/30:.3f}.png').convert('RGB')).astype('int16')
for row in metrics['rows']:
    if row['frame']==373:row.update(after=float(abs(source-final).mean()),oldVsNewMax=0)
    if row['frame']==372:
        a=np.asarray(Image.open(R/'reasoning-source/source-0372.png').convert('RGB')).astype('int16');c=np.asarray(Image.open(R/'reasoning-final-controls'/f'{372/30:.3f}.png').convert('RGB')).astype('int16');row['after']=float(abs(a-c).mean())
changed=[row for row in metrics['rows']if 272<=row['frame']<=374 and row['frame']!=373]
metrics.update(meanBefore=float(np.mean([q['before']for q in changed])),meanAfter=float(np.mean([q['after']for q in changed])),regressions=[q for q in changed if q['after']>q['before']],finalControls=controls,changedNativeFrames=len(changed),sourceScope=[[272,372],[374,374]],preservedStronger373=True)
assert not metrics['regressions'];assert len(changed)==102
(R/'reasoning-final-metrics.json').write_text(json.dumps(metrics,indent=2))
proof=json.loads((R/'reasoning-final-controls.scene.json.scope.json').read_text());assert proof['changedFrames']==[f for f in range(272,375)if f!=373]
release={'base':'outputs/02-danieltian/final-v16/scene.json','baseSHA256':'6cc308bf03330758ec17cc97ece6054e74da42694310c463aae029f77758dcfa','helper':str(R.parent/'apply-reasoning-v17.py'),'helperSHA256':sha(R.parent/'apply-reasoning-v17.py'),'spec':str(R/'reasoning-final.json'),'specSHA256':sha(R/'reasoning-final.json'),'exactChangedRanges':[[272,372],[374,374]],'changedFrames':102,'allOutsideFramesExact':1258,'fullParentNativeScopeProof':str(R/'reasoning-final-controls.scene.json.scope.json'),'nativeMetrics':str(R/'reasoning-final-metrics.json'),'native105StatesChecked':True,'all102ChangedImprove':True,'meanBefore':metrics['meanBefore'],'meanAfter':metrics['meanAfter'],'rootHouseHelperAppliedOnlyInNativeGate':'Apply root-house-v17 after this helper. This spec retains original house unchanged.','assets':json.loads((R/'emoji-art/provenance.json').read_text()),'limitations':'Native semantic outlines are not live font text. Neutral tone/blur approximation and.08px contour simplification retain residual AA/compression differences. Five emoji use independently transformed authentic single-reference artwork, not complete frames or video playback.'}
(R/'reasoning-release.json').write_text(json.dumps(release,indent=2));print(json.dumps({k:v for k,v in release.items()if k!='assets'},indent=2))
