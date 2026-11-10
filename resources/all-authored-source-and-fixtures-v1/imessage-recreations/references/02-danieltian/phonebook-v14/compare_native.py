from pathlib import Path
import json,numpy as np,sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;C=R/(sys.argv[1] if len(sys.argv)>1 else'native-check');frames=list(range(435,527));missing=[f for f in frames if not(C/f'{f/30:.3f}.png').exists()]
if missing:raise RuntimeError('Capture not complete; do not compare stale/partial output: '+str(missing))
rows=[]
for f in frames:
 s=np.asarray(Image.open(R/'source-native'/f'{f:06d}.png').convert('RGB')).astype(float);b=np.asarray(Image.open(R/'baseline-native'/f'{f:06d}.png').convert('RGB')).astype(float);c=np.asarray(Image.open(C/f'{f/30:.3f}.png').convert('RGB')).astype(float);rows.append(dict(frame=f,baselineMAE=float(abs(s-b).mean()),candidateMAE=float(abs(s-c).mean()),candidateVsBaseline=float(abs(b-c).mean())))
inside=[q for q in rows if 436<=q['frame']<=525];summary=dict(frames=92,scope=[436,525],baselineMean=float(np.mean([q['baselineMAE']for q in inside])),candidateMean=float(np.mean([q['candidateMAE']for q in inside])),maxCandidate=max(inside,key=lambda q:q['candidateMAE']),boundaries=[q for q in rows if q['frame']in[435,526]],rows=rows);(C/'native-comparison.json').write_text(json.dumps(summary,indent=2));top=sorted(inside,key=lambda q:q['candidateMAE'],reverse=True)[:9];contact=Image.new('RGB',(1920,3240),'white');d=ImageDraw.Draw(contact)
for i,q in enumerate(top):
 f=q['frame'];x=i%3*640;y=i//3*1080
 for j,(folder,name)in enumerate([(R/'source-native','source'),(R/'baseline-native','v13'),(C,'candidate')]):
  file=folder/(f'{f/30:.3f}.png'if folder==C else f'{f:06d}.png');contact.paste(Image.open(file).convert('RGB').resize((640,360)),(x,y+j*360));d.text((x+6,y+j*360+6),f'{f} {name}'+(f" MAE{q['candidateMAE']:.3f}"if j==2 else''),fill='red')
contact.save(C/'ranked-native-contact.jpg');print(json.dumps({k:v for k,v in summary.items()if k!='rows'},indent=2))
