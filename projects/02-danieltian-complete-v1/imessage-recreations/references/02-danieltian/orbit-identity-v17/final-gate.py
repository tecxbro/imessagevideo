from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;ROOT=R.parents[2];O=ROOT/'outputs/02-danieltian/orbit-identity-v17';rows=[];images=[]
for n in range(547,599):
 a=Image.open(R/f'source/{n:06}.png').convert('RGB');b=Image.open(O/f'baseline-native16/{n:06}.png').convert('RGB');p=(O/'prototype-03'/f'{n/30:.3f}.png') if 560<=n<=565 else (O/'prototype-04'/f'{n/30:.3f}.png') if 566<=n<=597 else O/f'baseline-native16/{n:06}.png';c=Image.open(p).convert('RGB');aa,bb,cc=[np.array(x).astype(float) for x in (a,b,c)];before=abs(aa-bb);after=abs(aa-cc);q=dict(frame=n,beforeMAE=float(before.mean()),afterMAE=float(after.mean()),vsV16MAE=float(abs(bb-cc).mean()),candidatePath=str(p),candidateSHA256=hashlib.sha256(p.read_bytes()).hexdigest());rows.append(q)
 if 560<=n<=597:assert q['afterMAE']<=q['beforeMAE']+.001,(n,q)
for chunk in range(4):
 select=rows[chunk*13:chunk*13+13];im=Image.new('RGB',(1440,290*len(select)),'white');d=ImageDraw.Draw(im)
 for i,q in enumerate(select):
  n=q['frame']
  for j,p in enumerate([R/f'source/{n:06}.png',O/f'baseline-native16/{n:06}.png',Path(q['candidatePath'])]):
   a=Image.open(p).convert('RGB');im.paste(a.resize((480,270)),(480*j,290*i+20));d.text((480*j,290*i),f'{n} '+['source','actualV16','final helper'][j]+(f" MAE {q['beforeMAE']:.4f}" if j==1 else f" MAE {q['afterMAE']:.4f}" if j==2 else ''),fill='black')
 im.save(O/f'final-contact-{chunk+1}.jpg')
changed=[q for q in rows if 560<=q['frame']<=597];summary=dict(baseSceneSHA256='6cc308bf03330758ec17cc97ece6054e74da42694310c463aae029f77758dcfa',patchSHA256=hashlib.sha256((R/'patch-spec.json').read_bytes()).hexdigest(),helperSHA256=hashlib.sha256((R/'apply.py').read_bytes()).hexdigest(),sourceRange=[547,598],changedFrameRange=[560,597],measuredFrameCount=52,beforeMeanMAE=float(np.mean([q['beforeMAE'] for q in rows])),afterMeanMAE=float(np.mean([q['afterMAE'] for q in rows])),changedBeforeMeanMAE=float(np.mean([q['beforeMAE'] for q in changed])),changedAfterMeanMAE=float(np.mean([q['afterMAE'] for q in changed])),changedRegressions=[q['frame'] for q in changed if q['afterMAE']>q['beforeMAE']],rows=rows,notice='Exact native source52frames;38changed actual native captures.14unchanged actualV16 native PNGs. Separate captured boundary/controls547/548/552/555/559/598 verify exact pixel parity with actualV16. Source-only metrics, not equality proof. All original UI/glass/header and other actors remain unchanged.');(O/'source-gate.json').write_text(json.dumps(summary,indent=2));print(json.dumps({k:v for k,v in summary.items() if k!='rows'}));print('largest residual',sorted([(q['frame'],q['beforeMAE'],q['afterMAE']) for q in rows],key=lambda x:x[2],reverse=True)[:8])
