from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
P=Path(__file__).parent;R=P.parents[2];OUT=R/'outputs/06-gallery/portrait614-review-02';rows=json.load(open(P/'extended-native-metrics.json'));changed=[r for r in rows if 613<=r['frame']<=621];scope=json.load(open(P/'extended-scope.json'));optical=json.load(open(P/'optical-build.json'))+json.load(open(P/'optical-original.json'));accepted=[r for r in optical if r['accepted']]
def index(ls):
 d={}
 for n in ls:d[n['id']]=n;d.update(index(n.get('children',[])))
 return d
nodes=index(json.load(open(OUT/'scene.json'))['layers'])
for row in accepted:
 f=OUT/nodes[row['id']]['children'][0]['src'];row['immutableMaterial']=str(f);row['sha256']=hashlib.sha256(f.read_bytes()).hexdigest();assert row['sha256']==hashlib.sha256(Path(row['image']).read_bytes()).hexdigest()
provenance=dict(opticalPoseFrames=[614,615,616,617,618],independentPhotoPoses=len(accepted),photoPoses=accepted,source75BirthCamera=json.load(open(P/'photo75-birth-fit.json')),source75LateCamera=json.load(open(P/'photo75-continuation-fit.json')),restriction='No complete scene/frame/screen/video image. Each optical material is one genuine photographed object with its own soft alpha and original hidden/offscreen continuation; source RGB excludes every other photo and native UI mask regardless of z-order.',editability='Native camera/lifetime/clip remain independently editable. This brief material rasterizes projected RGB/soft alpha/shadow, not an editable3D photo or optical shader.');(P/'extended-material-provenance.json').write_text(json.dumps(provenance,indent=2));(OUT/'material-provenance.json').write_text(json.dumps(provenance,indent=2))
accept=dict(status='Accepted scoped native improvement; broader material continuation under review',sceneSha256=hashlib.sha256((OUT/'scene.json').read_bytes()).hexdigest(),changedRanges=scope['exactChangedRanges'],outsideStatesIdentical=1483-scope['changedFrames'],nativeMeanBefore=sum(r['before']for r in changed)/len(changed),nativeMeanAfter=sum(r['after']for r in changed)/len(changed),allChangedFramesImprove=all(r['after']<r['before']for r in changed),controlsPixelIdentical=all(r['controlPixelIdentical']for r in rows if r['frame']in[612,622,624]),accuracyLimit='Pixel-identical controls prove scope, not accuracy.619 still4.387,6203.943,6213.485, unchanged6223.215; remaining photograph rendering is not certified asAA-only. No100% claim.');(P/'extended-acceptance.json').write_text(json.dumps(accept,indent=2))
canvas=Image.new('RGB',(1440,5*296),'#ddd');d=ImageDraw.Draw(canvas)
for row,f in enumerate([614,615,616,618,621]):
 r=next(r for r in rows if r['frame']==f)
 for col,(label,file)in enumerate([('Source',P/'source'/f'{f:06}.png'),(f'V20 {r["before"]:.3f}',P/'baseline-v20'/f'{f:06}.png'),(f'Corrected {r["after"]:.3f}',P/'extended-final-gsap'/f'{f/30:.3f}.png')]):
  canvas.paste(Image.open(file).resize((480,270)),(col*480,row*296+26));d.text((col*480+6,row*296+6),f'{f} {label}',fill='black')
canvas.save(P/'extended-comparison.jpg',quality=94)
text='''# Extended Rene portrait native correction

Frozen02 improves every actual613–621 frame and retains all1474 outside evaluated states exactly. Frozen01 remains immutable.

The original clipped actor71 camera/blur and large79 texture errors were independently measured. Static models still missed photographed optical detail, so the parent authorized short, individually bounded genuine-photo optical materials. Source RGB is sampled only within that photo's alpha, excluding every other photo footprint and all native UI/headline masks regardless of draw order. Hidden/offscreen regions and soft edges retain the original independent static photo model. Every actor remains separate under native camera/lifetime/clip. The brief projectedRGB/softAlpha/shadow is raster material; it is not an editable3D optical scene.

The missing75 male portrait is visible in the source by618 but was opacity0 through620. A visible intersection had been treated as its full body. Its genuine static photo fits618 with full diameter169/cx568, continuing149/cx623 at619,137/cx671 at620 and130/cx720 at621. The measured622–624 poses already agree closely, so those later states are retained. This is principally an occlusion reveal, not a guessed fade.

A broad headline-band fitting exclusion was inappropriate because the headline is below the photos; removing it restores valid occlusion evidence. The rendered layer order was already correct and was not changed. The first optical diagnostic excluded only upperUI; it remained a trial. Final optical sampling excludes UI at every depth, preventing any source glyph from entering the photo material.

Rejected experiments include blind blur0, lowered79 opacity, source95/79 draw-order changes, alpha/RGB-camera decoupling and18 directional93 blur variants. These failures and the bounds/visibility pitfalls are logged before retries. No shared-engine, canonical or fullMP4 writer was used.

Native checks use actual source indices at1920×1080. Cached614 equals a fresh exact-n614 decode. The baseline encoded contribution remains separate: source/native7.859, source/encoded7.746, native/encoded.850. Native unchanged controls are scope checks, not certification of source accuracy.619–622 still show photograph-material differences and remain under review; no100% orAA-only claim.
'''
for r in rows:text+=f'\n- {r["frame"]}: nativeMAE {r["before"]:.6f}→{r["after"]:.6f}; pixel-identical={r["controlPixelIdentical"]}.'
(P/'extended-findings.md').write_text(text+'\n')
links=['extended-acceptance.json','extended-native-metrics.json','extended-scope.json','extended-structure-proof.json','extended-material-provenance.json','extended-findings.md','encoding-attribution.json','native-metrics.json','scope.json','findings.md'];(P/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Rene portrait fidelity review</title><style>body{font:16px system-ui;margin:30px;max-width:1500px}p{max-width:1100px;line-height:1.6}img{width:100%}</style><h1>Rene portrait correction613–621</h1><p>Frozen02: all9 actual frames improve; all1474 outside evaluated states identical. Original6147.859→2.573;6166.105→2.103. Independent photographed actors, genuine optical materials and full native cameras/clips; no scene/frame playback. Broader material continuation remains under review. Controls prove scope, not accuracy.</p><img src="extended-comparison.jpg"><ul>'+''.join(f'<li><a href="{x}">{x}</a></li>'for x in links)+'</ul>');print(accept)
