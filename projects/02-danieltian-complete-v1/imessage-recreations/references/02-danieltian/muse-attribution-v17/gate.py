from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;ROOT=R.parents[2];OLD=R.parent/'orbit-identity-v17';OO=ROOT/'outputs/02-danieltian/orbit-identity-v17';O=ROOT/'outputs/02-danieltian/muse-attribution-v17';P=O/'prototype-01';rows=[]
for n in range(552,589):
 source=OLD/f'source/{n:06}.png';before=OO/('prototype-03' if n<=565 else 'prototype-04')/f'{n/30:.3f}.png' if n>=560 else OO/f'baseline-native16/{n:06}.png';candidate=P/f'{n/30:.3f}.png';a,b,c=[np.array(Image.open(x).convert('RGB')).astype(float) for x in [source,before,candidate]];row=dict(frame=n,beforeMAE=float(abs(a-b).mean()),afterMAE=float(abs(a-c).mean()),beforeVsAfterMAE=float(abs(b-c).mean()),source=str(source),before=str(before),candidate=str(candidate),candidateSHA256=hashlib.sha256(candidate.read_bytes()).hexdigest());rows.append(row);print(n,round(row['beforeMAE'],6),round(row['afterMAE'],6),'delta',round(row['afterMAE']-row['beforeMAE'],6))
for k in range(3):
 select=rows[k*13:(k+1)*13];im=Image.new('RGB',(1440,290*len(select)),'white');d=ImageDraw.Draw(im)
 for i,q in enumerate(select):
  for j,label in enumerate(['source','before','candidate']):im.paste(Image.open(q[label]).convert('RGB').resize((480,270)),(480*j,290*i+20));d.text((480*j,290*i),f"{q['frame']} {label}",fill='black')
 im.save(O/f'contact-{k+1}.jpg')
report=dict(baseSceneSHA256='6cc308bf03330758ec17cc97ece6054e74da42694310c463aae029f77758dcfa',acceptedOrbitHelperSpecSHA256='5ac43bdccb626772e7ddc21736f760e04bfb3d616ed6dc6fd945686462c9dc4f',patchSHA256=hashlib.sha256((R/'patch-spec.json').read_bytes()).hexdigest(),helperSHA256=hashlib.sha256((R/'apply.py').read_bytes()).hexdigest(),testedFrames=[552,588],meanBefore=float(np.mean([x['beforeMAE'] for x in rows])),meanAfter=float(np.mean([x['afterMAE'] for x in rows])),regressions=[x for x in rows if x['afterMAE']>x['beforeMAE']+1e-9],guardsIdentical=all(x['beforeVsAfterMAE']==0 for x in rows if x['frame'] in [552,588]),rows=rows);(O/'source-gate.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['rows','regressions']}));print('regressions',[(x['frame'],x['afterMAE']-x['beforeMAE']) for x in report['regressions']])
