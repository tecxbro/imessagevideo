"""Gate and journal a bounded, genuine native Pillow AA4 promotion.

No scene, engine or encoded picture is edited here. Root owns re-encoding.
"""
from pathlib import Path
import os, json, hashlib, shutil, time, datetime
import numpy as np
from PIL import Image

R=Path.cwd()
D=R/'verification/method-parity/05-linq/native-review/aa4-lifecycle'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(path,value):
 t=path.with_name(path.name+f'.tmp-{os.getpid()}');t.write_text(json.dumps(value,indent=2)+'\n');t.replace(path)
def stat(path):
 s=path.stat();return {'inode':s.st_ino,'bytes':s.st_size,'mtimeNS':s.st_mtime_ns}
report=json.loads((D/'dense-metrics.json').read_text())
capture=json.loads((D/'capture.json').read_text())
scope=list(range(101,128))
rows=[r for r in report['rows']if r['frame']in scope]
assert len(rows)==27
assert all(c['freshAA1VsCurrentP']['maxChannelDelta']==0 for c in report['freshAA1Controls'])
old_mean=float(np.mean([r['sourceVsCurrentP']['mae']for r in rows]))
new_mean=float(np.mean([r['sourceVsAA4']['mae']for r in rows]))
losses=[{'frame':r['frame'],'sourceMAEIncrease':-r['sourceMAEImprovement']}for r in rows if r['sourceMAEImprovement']<0]
assert old_mean>new_mean
assert max(x['sourceMAEIncrease']for x in losses)<.025
scene=R/'outputs/05-linq/final-v20/scene.json'
engine=R/'engines/render_pillow.py'
picture=R/'outputs/05-linq/pillow.mp4'
sidecar=R/'outputs/05-linq/pillow.mp4.render.json'
cache=R/'outputs/05-linq/cache/pillow'
assert sha(scene)==report['sceneSHA256']==capture['sceneSHA256']
assert sha(engine)==report['engineSHA256']==capture['engineSHA256']
assert sha(picture)==capture['protectedProductionPictureSHA256']
for row in report['rows']:
 for name,info in row['files'].items():assert sha(R/info['path'])==info['sha256'],(row['frame'],name)
gate={
 'status':'accepted_for_bounded_native_cache_promotion_with_explicit_tiny_tradeoffs',
 'sceneSHA256':sha(scene),'engineSHA256':sha(engine),'source':report['source'],
 'beforePictureSHA256':sha(picture),'inclusiveScope':[[101,127]],'frames':27,
 'nativeSourceMeanMAEBefore':old_mean,'nativeSourceMeanMAEAfter':new_mean,
 'relativeMeanSourceImprovement':1-new_mean/old_mean,
 'nativeVsGMeanMAEBefore':float(np.mean([r['currentPVsG']['mae']for r in rows])),
 'nativeVsGMeanMAEAfter':float(np.mean([r['aa4VsG']['mae']for r in rows])),
 'improvedFrames':[r['frame']for r in rows if r['sourceMAEImprovement']>0],
 'qualifiedTradeoffs':losses,'tradeoffMeanMAEIncrease':float(np.mean([x['sourceMAEIncrease']for x in losses])),
 'tradeoffMaxMAEIncrease':max(x['sourceMAEIncrease']for x in losses),
 'freshAA1Controls':report['freshAA1Controls'],
 'guardsRetained':[98,99,100,128,129,130],
 'scopeReason':'Native g119 extreme row-shutter lifecycle101–126 plus its independently authored outgoing continuation127. Composer-only99–100, blank128 and incoming Games129+ retain their stronger current AA1 pixels.',
 'manualReview':{
  'all33MeasuredPosesViewed':True,'contactPages':['interim-contact-000098.jpg','interim-contact-000105.jpg','interim-contact-000112.jpg','contact-000119.jpg','contact-000126.jpg'],
  'nativeTradeoffCrops':['tradeoff-000101.png','tradeoff-000102.png','tradeoff-000108.png','tradeoff-000127.png'],
  'findings':'No new content, timing, viewport, artwork-loss or pose defect is introduced. AA4 removes the coarse streak/block profile visible in AA1 at111–117. The four small source tradeoffs are fine glyph/icon/card-edge sampling and faint outgoing material;101/102 increase is concentrated in the unchanged composer below y600 (menu above y600 improves).108/127 retain the same semantic content and shape; the small differences are filtering/edge tone.',
  'remainingSharedSourceLimits':'AA4 does not change the accepted authored source/G layout or recover original filters. Early source menu exposure/blur and a thin composer caret visible in source101/102 differ in the shared G/native baseline; those source/G residuals are not hidden or claimed repaired by this Pillow-only sampling change.'
 },
 'evidence':{'metrics':'dense-metrics.json','capture':'capture.json','viewer':'index.html'},
 'authorization':'Parent accepted genuine AA4 PNG promotion after full dense gate/AA1 controls, including explicitly quantified tiny coherent101–127 tradeoffs; root retains encode/parity/audio ownership.',
 'sourceIdentityClaim':False,'pixelIdentityClaim':False
}
write(D/'promotion-gate.json',gate)
report['manualReview']=gate['manualReview'];report['promotionGate']='promotion-gate.json';write(D/'dense-metrics.json',report)
before={f:{'path':str((cache/f'{f:06}.png').relative_to(R)),'sha256':sha(cache/f'{f:06}.png'),**stat(cache/f'{f:06}.png')}for f in range(1458)}
backup=R/'outputs/05-linq/iterations/pillow-before-menu-aa4-v20'
assert not backup.exists(),'Do not overwrite the original promotion evidence'
(backup/'frames').mkdir(parents=True)
os.link(picture,backup/'pillow-aa1-before.mp4')
shutil.copy2(sidecar,backup/'pillow-aa1-before.mp4.render.json')
for f in scope:os.link(cache/f'{f:06}.png',backup/'frames'/f'{f:06}.png')
write(D/'production-before-inventory.json',{'frames':before,'pictureSHA256':sha(picture),'sidecarSHA256':sha(sidecar)})
journal={'status':'prepared','createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sceneSHA256':sha(scene),'engineSHA256':sha(engine),'gate':'verification/method-parity/05-linq/native-review/aa4-lifecycle/promotion-gate.json','gateSHA256':sha(D/'promotion-gate.json'),'captureSHA256':sha(D/'capture.json'),'denseMetricsSHA256':sha(D/'dense-metrics.json'),'beforeInventorySHA256':sha(D/'production-before-inventory.json'),'oldPictureSHA256':sha(picture),'backup':str(backup.relative_to(R)),'inclusiveScope':[[101,127]],'changedFrames':[],'expectedOutsideFrames':1431,'baseAntialias':1,'boundedAntialias':4,'sourceOfPromotedPixels':'Only genuine Pillow AA4 PNGs produced by unchanged published native engine5c7; no G/source pixels copied.','encodedMasterChangedByThisOperation':False}
write(D/'promotion-journal.json',journal)
old_meta=json.loads(sidecar.read_text())
try:
 for f in scope:
  src=D/'aa4'/f'{f:06}.png';dst=cache/f'{f:06}.png';tmp=dst.with_name(dst.name+f'.aa4-promotion-{os.getpid()}')
  shutil.copy2(src,tmp);os.replace(tmp,dst)
  assert sha(dst)==sha(src)
  journal['changedFrames'].append({'frame':f,'beforeSHA256':before[f]['sha256'],'afterSHA256':sha(dst),'genuineCapture':str(src.relative_to(R))})
  write(D/'promotion-journal.json',journal)
 for f in range(1458):
  if f not in scope:assert before[f]['sha256']==sha(cache/f'{f:06}.png') and {k:before[f][k]for k in ['inode','bytes','mtimeNS']}==stat(cache/f'{f:06}.png'),f
 assert sha(picture)==journal['oldPictureSHA256']
 assert sha(scene)==journal['sceneSHA256'] and sha(engine)==journal['engineSHA256']
 meta=json.loads(sidecar.read_text());assert meta==old_meta
 event={'kind':'bounded-native-supersampling-promotion','scene':str(scene),'sceneSha256':sha(scene),'engineSha256':sha(engine),'antialias':4,'capturedFrameRanges':[[101,127]],'capturesPromoted':27,'captureEvidence':'verification/method-parity/05-linq/native-review/aa4-lifecycle/capture.json','gate':'verification/method-parity/05-linq/native-review/aa4-lifecycle/promotion-gate.json','journal':'verification/method-parity/05-linq/native-review/aa4-lifecycle/promotion-journal.json','previousPictureSHA256':journal['oldPictureSHA256'],'notice':'Existing successful genuine native AA4 captures promoted after dense source/G/current-P gate. Base cache is AA1 with this bounded AA4 override, not all1458 AA4. Root must encode the revised lossless cache before final mux.'}
 meta.setdefault('captureHistory',[]).append(event)
 meta['antialiasOverrides']=[{'inclusiveRange':[101,127],'antialias':4,'engineSha256':sha(engine),'journal':event['journal']}]
 meta['samplingProvenance']={'baseAntialias':1,'overrides':meta['antialiasOverrides'],'notice':'The legacy base antialias1 is retained; exactly101–127 are genuineAA4.'}
 write(sidecar,meta)
 journal.update(status='promoted_and_verified_encode_pending',outside1431HashesInodesSizesMtimesUnchanged=True,pictureHashUnchanged=True,sceneAndEngineHashesUnchanged=True,promotedFramesMatchGenuineAA4=True,afterSidecarSHA256=sha(sidecar),completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),rootNext='Encode only Pillow cache with scripts/final_encode.py, then rerun full1458 encoded parity/source and mux. Do not claim old encoded picture has the new cache pixels.')
 write(D/'promotion-journal.json',journal)
except BaseException:
 for f in scope:
  src=backup/'frames'/f'{f:06}.png';dst=cache/f'{f:06}.png';tmp=dst.with_name(dst.name+f'.rollback-{os.getpid()}');shutil.copy2(src,tmp);os.replace(tmp,dst)
 write(sidecar,old_meta)
 journal['status']='rolled_back_after_error';write(D/'promotion-journal.json',journal)
 raise
print(json.dumps({'status':journal['status'],'frames':len(scope),'sourceMeanBefore':old_mean,'sourceMeanAfter':new_mean,'tradeoffMax':gate['tradeoffMaxMAEIncrease'],'outsideUnchanged':1431,'journal':str((D/'promotion-journal.json').relative_to(R))},indent=2))
