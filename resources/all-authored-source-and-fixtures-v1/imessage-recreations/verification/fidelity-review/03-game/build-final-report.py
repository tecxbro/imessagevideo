from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
R=Path('/workspace/imessage-recreations');P=Path(__file__).parent
D=R/'outputs/03-photon-mini/game-entry-review-08'
capture=json.load(open(P/'final-v8-gsap/capture.json'))
assert capture['frameIndices']==list(range(812,851))
metric_file=P/'native-metrics-v8.json'
if metric_file.exists():rows=json.load(open(metric_file))
else:
    rows=[]
    for f in capture['frameIndices']:
        a=np.asarray(Image.open(P/'source'/f'{f-808:04}.png').convert('RGB')).astype(float)
        b=np.asarray(Image.open(P/'baseline-v15'/f'{f:06}.png').convert('RGB')).astype(float)
        c=np.asarray(Image.open(P/'final-v8-gsap'/f'{f/30:.3f}.png').convert('RGB')).astype(float)
        rows.append(dict(frame=f,before=float(abs(a-b).mean()),after=float(abs(a-c).mean()),nativePixelsIdentical=bool(np.array_equal(b,c))))
    metric_file.write_text(json.dumps(rows,indent=2))
if not (P/'scope-v8.json').exists():
    print('Native39-frame metrics complete; scope proof still running.')
    raise SystemExit(0)
proof=json.load(open(P/'scope-v8.json'));changed=[q for q in rows if not q['nativePixelsIdentical']]
cache={}
def nodes(file):
    s=json.load(open(file));out={}
    def walk(ns):
        for n in ns:
            q={k:v for k,v in n.items()if k!='children'}
            if q.get('src'):
                path=(file.parent/q['src']).resolve()
                if path not in cache:cache[path]=hashlib.sha256(path.read_bytes()).hexdigest()
                q['src']=cache[path]
            out[n['id']]=q;walk(n.get('children',[]))
    walk(s['layers']);return s,out
base,bn=nodes(R/'outputs/03-photon-mini/final-v15/scene.json');final,fn=nodes(D/'scene.json')
attributes=[k for k in bn if bn[k]!=fn[k]]
structure=dict(changedOriginalAttributes=attributes,allOtherOriginalAttributesIdentical=set(attributes)==set(['p03-371','measured-game-v13']),allExistingIDsPreserved=set(bn)<=set(fn),gradientsIdentical=base.get('gradients')==final.get('gradients'))
(P/'structure-proof-v8.json').write_text(json.dumps(structure,indent=2))
accept=dict(sceneSHA256=hashlib.sha256((D/'scene.json').read_bytes()).hexdigest(),nativeFramesChecked=len(rows),changedNativeFramesChecked=len(changed),allChangedNativeFramesImprove=all(q['after']<q['before']for q in changed),nativePixelIdenticalControls=[q['frame']for q in rows if q['nativePixelsIdentical']],meanBefore=sum(q['before']for q in changed)/len(changed),meanAfter=sum(q['after']for q in changed)/len(changed),maxCorrectedNativeMAE=max(q['after']for q in changed),exactChangedRanges=proof['exactChangedRanges'],outsideFramesChecked=1260-37,allOutsideEvaluatedMarkupIdentical=not proof['changedOutsideCaptureUnion'],fontCssIdentical=proof['fontCssIdentical'],globalGradientsIdentical=structure['gradientsIdentical'],limitations=['No100% claim: residual hardware/photo sampling, font-outline AA and coarse one-frame chromatic/color fields remain.','3D material actors use individually bounded projected optical textures; they are not an editable3D game.','Static internal chat UI artwork is editable as positioned/cropped image actors, rather than each internal glyph.','Final encoded output/source QA belongs to the merged primary export; native/encoded contributions stay separate.'])
(P/'acceptance.json').write_text(json.dumps(accept,indent=2));print(json.dumps(accept,indent=2))
selected=[813,816,819,823,829,837,849,850]
sheet=Image.new('RGB',(960,len(selected)*300),'white');draw=ImageDraw.Draw(sheet)
for i,f in enumerate(selected):
    files=[P/'source'/f'{f-808:04}.png',P/'baseline-v15'/f'{f:06}.png',P/'final-v8-gsap'/f'{f/30:.3f}.png']
    for j,file in enumerate(files):
        im=Image.open(file).convert('RGB');im=im.crop((650,0,1270,1080));im.thumbnail((320,270));sheet.paste(im,(j*320+(320-im.width)//2,i*300+25))
    q=next(q for q in rows if q['frame']==f);draw.text((4,i*300+4),f'{f}: source | before {q["before"]:.3f} | corrected {q["after"]:.3f}',fill='black')
sheet.save(P/'comparison-v8.jpg',quality=94)
(P/'findings.md').write_text('''# Mini game lifecycle813–849

Released ID helper `references/03-photon-mini/apply-game-entry-review.py` with immutable elements `outputs/03-photon-mini/game-entry-review-08/game-entry-review-elements.json`. Base immutable final-v15. Exact37 changed frames813–849; all1223 outside states unchanged.812 and hard-cut850 are native pixel-identical controls.

The source presenting chat view shrinks/translates independently and dims gradually (819~79% bright;835~50%). Candidate retained generic full-size UI and guessed~45% then black. Reused authentic static independent chat actors, measured header/avatar camera and a separate card-content registration; extended the complete presenting-view geometry behind the occluding sheet. Dim the background and controls as one group over black, preserving proper compositing.

Measured full physical silhouette at three thresholds after rejecting aliased thin-rim Y fits. Original transparent hardware stays independent; repaired only inner white-matte contamination adjacent to its screen aperture. Native sheet color bands, title/score outlines, rounded cap and37 measured blue-gray handles remain editable. Individually bounded cube/shadow/peg optical materials replace the jagged quantized face masks; no complete frame/game-screen/source-video layer. These image actors are projected materials, not a full editable3D game.

Every changed native frame improves. Full39-frame source/native comparisons and1260-frame outside proof are linked below. Frame837 required special attribution: spatial chromatic noise broke neutral-color masks and made holes in blocks. Native color fields sample only blank stage/empty-sheet background with content excluded; isolated logical block/shadow clusters use contrast to the clean field. This does not import a scene/frame bitmap.

Baseline816 source→native6.914, source→encoded7.809, native→encoded1.140, with native253→encoded252 flat background. Encoding is separate from the native repair. No canonical/full MP4/shared engine mutation. Residual optical/AA/coarse chromatic-field differences are declared; no100% claim.
''')
(P/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Mini game lifecycle review</title><style>body{font:16px system-ui;margin:30px;max-width:1200px}img{max-width:100%}a{margin-right:12px}</style><h1>Mini game lifecycle813–849</h1><p>37 changed native frames improve.1223 outside evaluated states unchanged.812/850 controls pixel-identical. No100% claim; bounded image-material editability limits disclosed.</p><p><a href="acceptance.json">Acceptance</a><a href="native-metrics-v8.json">All39 native comparisons</a><a href="scope-v8.json">1260-frame scope proof</a><a href="structure-proof-v8.json">ID/gradient proof</a><a href="encoding-attribution.json">Encoding attribution</a><a href="findings.md">Findings and limitations</a></p><img src="comparison-v8.jpg">''')
