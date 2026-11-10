from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
P=Path(__file__).parent;R=P.parents[2];OUT=R/'outputs/06-gallery/portrait614-review-03';rows=json.load(open(P/'extended-native-metrics.json'));tail=json.load(open(P/'tail619-native.json'));last=json.load(open(P/'complete-tail-native.json'));images={f:P/'extended-final-gsap'/f'{f/30:.3f}.png'for f in [612,613,614,615,616,617,618,622,624]};images[619]=P/'tail619-native-gsap/20.633.png';images.update({f:P/'complete-tail-gsap'/f'{f/30:.3f}.png'for f in[620,621]})
for row in rows:
 if row['frame']==619:row['after']=tail['opticalContinuationNative']
 for new in last:
  if new['frame']==row['frame']:row['after']=new['completeNative']
 row['nativeImage']=str(images[row['frame']]);row['captureReuseProof']='complete-tail-scope.json for613–618 and controls; complete-reused619-proof.json for619; fresh frozen03 captures620/621.'
(P/'complete-native-metrics.json').write_text(json.dumps(rows,indent=2));changed=[r for r in rows if 613<=r['frame']<=621];r=dict(status='Accepted scoped improvement; no exact-match claim',sceneSha256=hashlib.sha256((OUT/'scene.json').read_bytes()).hexdigest(),changedRanges=[[613,621]],outsideStatesIdentical=1474,nativeMeanBefore=sum(q['before']for q in changed)/9,nativeMeanAfter=sum(q['after']for q in changed)/9,maxNativeAfter=max(q['after']for q in changed),allChangedFramesImprove=all(q['after']<q['before']for q in changed),scopeControlsPixelIdentical=all(q['controlPixelIdentical']for q in rows if q['frame']in[612,622,624]),limitation='Residual static photo/blur/alpha/UV/AA and source-encoding differences remain. Unchanged622 has3.215 nativeMAE; scope controls are not source-accuracy certification. No100% claim.');(P/'complete-acceptance.json').write_text(json.dumps(r,indent=2))
def index(ls):
 d={}
 for n in ls:d[n['id']]=n;d.update(index(n.get('children',[])))
 return d
nodes=index(json.load(open(OUT/'scene.json'))['layers']);materials=[]
for file in ['optical-build.json','optical-original.json','optical-tail.json','optical-tail-complete.json']:
 for q in json.load(open(P/file)):
  if not q['accepted']:continue
  q['immutableMaterial']=str(OUT/nodes[q['id']]['children'][0]['src']);q['sha256']=hashlib.sha256(Path(q['immutableMaterial']).read_bytes()).hexdigest();assert q['sha256']==hashlib.sha256(Path(q['image']).read_bytes()).hexdigest();materials.append(q)
prov=dict(independentOpticalPhotoMaterials=len(materials),frames=list(range(614,622)),materials=materials,source75MeasuredCameras=json.load(open(P/'photo75-birth-fit.json'))+json.load(open(P/'photo75-continuation-fit.json')),sourcePixelRule='Only the target photograph alpha support, excluding expanded other modeled photo footprints and every nativeUI/headline mask at any depth. Above-content alpha is also excluded. Hidden/offscreen/edge original-photo continuation retained. No complete-scene/screen/frame/video texture.',editability='Photographs remain separate native camera/lifetime/clip actors. This brief projectedRGB/softAlpha/shadow is raster material; not an editable3D optical shader.');(P/'complete-material-provenance.json').write_text(json.dumps(prov,indent=2));(OUT/'material-provenance.json').write_text(json.dumps(prov,indent=2))
canvas=Image.new('RGB',(1440,6*296),'#ddd');d=ImageDraw.Draw(canvas)
for row,f in enumerate([613,614,615,616,619,621]):
 q=next(q for q in rows if q['frame']==f)
 for col,(label,file)in enumerate([('Source',P/'source'/f'{f:06}.png'),(f'V20 {q["before"]:.3f}',P/'baseline-v20'/f'{f:06}.png'),(f'Frozen03 {q["after"]:.3f}',images[f])]):canvas.paste(Image.open(file).resize((480,270)),(col*480,row*296+26));d.text((col*480+6,row*296+6),f'{f} {label}',fill='black')
canvas.save(P/'complete-comparison.jpg',quality=94)
text='''# Complete bounded portrait repair:613–621

The original peak614 improves from7.859 to2.573 nativeMAE. Every actual613–621 source state improves; all1474 outside evaluated states are identical. Frozen01/02 and canonical final-v20 remain unchanged.

Cause: partly clipped circles were fitted from their visible intersections, and one failed/occluded75 camera was hidden with opacity0 through620. Direct source registration recovers full body geometry behind foreground occluders.79 also enlarged an inadequate150×148 static photo to roughly1700px. Blind blur removal, lower opacity, source95/79 depth swaps, alpha/RGB-camera decoupling and18 directional93 blur models were rejected against actual frame differences.

Independent camera/blur/shadow and genuine higher-resolution622 photo material improve the static model, but leave a measured photographed-material/UV residual. Under the parent's explicit permission, each short optical photo pose retains a full original photographed object and its hidden/offscreen continuation. Source RGB is admitted only in the target photo alpha support, excluding every other modeled photograph footprint, every nativeUI/headline mask regardless of draw order, and above-layer alpha. No source glyphs, foreign faces, whole scene, screen, complete frame or video playback is imported.

The headline is below the photos. A broad fitting-band exclusion was therefore inappropriate and was corrected; the rendered layer order was already right and stays unchanged. The first optical trial's upperUI-only sampling rule was not released. Final pose sampling excludes native UI at every depth.

The real material error continued into619–621: stopping the optical correction at618 would leave the source mismatch in the next frames. Frozen03 closes that measured continuation within the already owned time span.75's observed reveal camera continues through621;622+ is retained. Native controls prove scope only.622 still has3.215 nativeMAE and is not certified source-exact.

Source614 is verified pixel-identical to a fresh exact-n614 decode. Baseline614 source/native7.859, source/encoded7.746 and native/encoded.850 stay separate. No encoder, shared engine, canonical or finalMP4 writer was changed. The scene keeps native editable photo actors/cameras/lifetimes/clips; their brief projectedRGB/softAlpha/shadow materials are raster assets, not an editable3D optical scene. Remaining source-image/blur/alpha/UV/AA differences are disclosed; no100% claim.
'''
for q in rows:text+=f'\n- Frame {q["frame"]}: native MAE {q["before"]:.6f}→{q["after"]:.6f}; scope-control pixel identity={q["controlPixelIdentical"]}.'
text+='\n\nApply `references/06-gallery/apply-portrait614-review.py` using immutable `outputs/06-gallery/portrait614-review-03/portrait614-review-elements.json`. All201 ID updates are assignments and can also be applied after frozen02. No layer insertion/deletion or global definitions change.\n';(P/'complete-findings.md').write_text(text)
links=['complete-acceptance.json','complete-native-metrics.json','complete-scope.json','complete-tail-scope.json','complete-structure-proof.json','complete-reused619-proof.json','complete-material-provenance.json','complete-findings.md','encoding-attribution.json','extended-acceptance.json','scope.json','findings.md'];(P/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Rene portrait repair613–621</title><style>body{font:16px system-ui;margin:30px;max-width:1500px}p{line-height:1.6;max-width:1100px}img{width:100%}</style><h1>Rene portrait repair613–621</h1><p>Frozen03: all9 actual frames improve; all1474 outside evaluated states identical.6147.859→2.573,6166.105→2.103,6195.038→2.238,6213.644→1.755. Controls prove scope, not source accuracy. Remaining image/optical/AA/encoding differences are disclosed; no100% claim.</p><img src="complete-comparison.jpg"><p>Independent photographed actors, native cameras/lifetimes/clips, permitted bounded optical materials with original hidden/offscreen continuation. No complete source-frame/screen/scene/video playback. Brief projectedRGB/softAlpha/shadow is rasterized and not an editable3D optical shader.</p><ul>'+''.join(f'<li><a href="{q}">{q}</a></li>'for q in links)+'</ul>');print(r)
