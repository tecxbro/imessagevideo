"""Read-only dense source/G/P sampling comparison for frozen05 final20."""
from pathlib import Path
import json, hashlib, os, html
import numpy as np
from PIL import Image, ImageDraw

R=Path.cwd()
D=R/'verification/method-parity/05-linq/native-review/aa4-lifecycle'
assert not (D/'promotion-journal.json').exists(),'Released AA4 study is frozen; numerical baseline is preserved and must not be recomputed against the promoted cache'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgb(p):return np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
def metric(a,b):
 d=np.abs(a-b)
 return {'mae':float(d.mean()),'maxChannelDelta':int(d.max()),'differentPixels':int(np.any(d,axis=2).sum())}
capture=json.loads((D/'capture.json').read_text())
rows=[]
for f in range(98,131):
 paths={'source':D/'source'/f'{f:06}.png','gsap':R/f'outputs/05-linq/frames-gsap/{f:06}.png','currentPillow':R/f'outputs/05-linq/cache/pillow/{f:06}.png','aa4':D/'aa4'/f'{f:06}.png'}
 images={k:rgb(v)for k,v in paths.items()}
 row={'frame':f,'time':f/30,'files':{k:{'path':str(v.relative_to(R)),'sha256':sha(v)}for k,v in paths.items()},'sourceVsG':metric(images['source'],images['gsap']),'sourceVsCurrentP':metric(images['source'],images['currentPillow']),'sourceVsAA4':metric(images['source'],images['aa4']),'currentPVsG':metric(images['currentPillow'],images['gsap']),'aa4VsG':metric(images['aa4'],images['gsap']),'aa4VsCurrentP':metric(images['aa4'],images['currentPillow'])}
 row['sourceMAEImprovement']=row['sourceVsCurrentP']['mae']-row['sourceVsAA4']['mae']
 row['gsapMAEImprovement']=row['currentPVsG']['mae']-row['aa4VsG']['mae']
 rows.append(row)
controls=[]
for f in [98,111,130]:
 a=D/'aa1-controls'/f'{f:06}.png';b=R/f'outputs/05-linq/cache/pillow/{f:06}.png'
 controls.append({'frame':f,'freshAA1VsCurrentP':metric(rgb(a),rgb(b)),'freshSHA256':sha(a),'currentSHA256':sha(b)})
# Every captured pose is shown in five pages, preserving both unchanged guards
# and any source tradeoffs. Full native PNGs stay available for close inspection.
for first in range(98,131,7):
 selected=[r for r in rows if first<=r['frame']<first+7]
 w,h=240,180;pad=24
 sheet=Image.new('RGB',(w*4,(h+pad)*len(selected)), '#eeeeee');draw=ImageDraw.Draw(sheet)
 for i,row in enumerate(selected):
  for j,k in enumerate(['source','gsap','currentPillow','aa4']):
   im=Image.open(R/row['files'][k]['path']).convert('RGB').resize((w,h),Image.Resampling.LANCZOS)
   sheet.paste(im,(j*w,i*(h+pad)+pad))
   label=f"{row['frame']} {k}"
   if k=='currentPillow':label+=f" srcMAE {row['sourceVsCurrentP']['mae']:.3f}"
   if k=='aa4':label+=f" srcMAE {row['sourceVsAA4']['mae']:.3f}"
   draw.text((j*w+3,i*(h+pad)+3),label,fill='#000000')
 sheet.save(D/f'contact-{first:06}.jpg',quality=95)
for f in [101,105,111,113,120,126,127,129]:
 row=next(r for r in rows if r['frame']==f)
 # Native full-size comparison, including an amplified AA4/G difference.
 sheet=Image.new('RGB',(960*4,720+24),'#eeeeee');draw=ImageDraw.Draw(sheet)
 for j,k in enumerate(['source','gsap','currentPillow','aa4']):
  sheet.paste(Image.open(R/row['files'][k]['path']).convert('RGB'),(j*960,24));draw.text((j*960+4,4),f'{f} {k}',fill='#000000')
 sheet.save(D/f'native-{f:06}.jpg',quality=96)
report={'sceneSHA256':capture['sceneSHA256'],'engineSHA256':capture['engineSHA256'],'source':{'path':'references/05-linq/source.mp4','sha256':sha(R/'references/05-linq/source.mp4'),'nativeFrameIndices':[98,130],'resolution':[960,720],'fps':30},'protectedProductionPictureSHA256':capture['protectedProductionPictureSHA256'],'capture':'capture.json','rows':rows,'freshAA1Controls':controls,'scopeMeasured':[98,130],'sourceDecode':'Original native frames98–130 decoded once in order with ffmpeg select, passthrough cadence, no scaling.','manualReview':'pending','summary':{'frames':len(rows),'sourceImproved':[r['frame']for r in rows if r['sourceMAEImprovement']>1e-9],'sourceRegressed':[r['frame']for r in rows if r['sourceMAEImprovement']< -1e-9],'sourceSame':[r['frame']for r in rows if abs(r['sourceMAEImprovement'])<=1e-9],'meanCurrentPSourceMAE':float(np.mean([r['sourceVsCurrentP']['mae']for r in rows])),'meanAA4SourceMAE':float(np.mean([r['sourceVsAA4']['mae']for r in rows]))},'notice':'Quarantine only; no production master, PNG, source or engine edits. AA4 denotes published native engine --aa4 supersampling, not copied G/source pixels.'}
(D/'dense-metrics.json').write_text(json.dumps(report,indent=2)+'\n')
blocks=[]
for row in rows:
 cells=[]
 for k in ['source','gsap','currentPillow','aa4']:
  rel=os.path.relpath(R/row['files'][k]['path'],D)
  cells.append(f'<figure><figcaption>{html.escape(k)}</figcaption><a href="{html.escape(rel)}"><img src="{html.escape(rel)}" loading="lazy"></a></figure>')
 blocks.append(f'<section id="frame-{row["frame"]}"><p><b>Frame {row["frame"]} ({row["time"]:.6f}s)</b> — source MAE current P {row["sourceVsCurrentP"]["mae"]:.6f}, AA4 {row["sourceVsAA4"]["mae"]:.6f}; improvement {row["sourceMAEImprovement"]:+.6f}</p><div>{"".join(cells)}</div></section>')
(D/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Linq menu AA4 quarantine</title><style>body{font:15px system-ui;margin:24px;background:#eee;color:#111}section{border-top:1px solid #aaa;margin:22px 0}section>div{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}figure{margin:0}figcaption{font-weight:bold}img{width:100%;background:white}p{line-height:1.5}code{overflow-wrap:anywhere}</style><h1>Native Pillow menu sampling quarantine</h1><p>Every native frame98–130: original source, accepted GSAP, retained production Pillow AA1, and independently rendered Pillow AA4. No production file is changed. Click each image for its native960×720 PNG. <a href="dense-metrics.json">Dense hash-bound metrics</a>; <a href="capture.json">capture provenance and production guards</a>.</p><p>Frozen scene <code>'+capture['sceneSHA256']+'</code>; engine <code>'+capture['engineSHA256']+'</code>. AA4 means the existing engine renders at4× spatial resolution then downsamples; all scene content, authored camera and timing remain unchanged.</p>'+''.join(blocks))
print(json.dumps(report['summary'],indent=2))
print('AA1 controls',[(c['frame'],c['freshAA1VsCurrentP'])for c in controls])
for r in rows:print(r['frame'],round(r['sourceVsCurrentP']['mae'],6),round(r['sourceVsAA4']['mae'],6),round(r['sourceMAEImprovement'],6),round(r['aa4VsG']['mae'],6))
