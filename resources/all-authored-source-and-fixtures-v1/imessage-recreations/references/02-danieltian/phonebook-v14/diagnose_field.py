from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
from scipy.ndimage import label
R=Path(__file__).resolve().parent;BG=253

def masks(a,y0=70,y1=210):
 g=a[y0:y1].mean(2);spread=a[y0:y1].max(2)-a[y0:y1].min(2);neutral=spread<12;v=BG-g;peak=float(np.percentile(v[neutral],99));m=(v>max(2,peak*.5))&neutral;labs,n=label(m);sizes=np.bincount(labs.ravel());keep=sizes>3;keep[0]=False;m=keep[labs];xs=np.flatnonzero(m.any(0));groups=[]
 for x in xs:
  if not groups or x-groups[-1][-1]>30:groups.append([int(x)])
  else:groups[-1].append(int(x))
 out=[]
 for gg in groups:
  x0,x1=gg[0],gg[-1]+1;yy,xx=np.nonzero(m[:,x0:x1]);b=[x0,int(yy.min()+y0),x1,int(yy.max()+y0+1)];sp=[]
  for x in np.flatnonzero(m[:,x0:x1].any(0)):
   if not sp or x>sp[-1][1]+1:sp.append([int(x),int(x)])
   else:sp[-1][1]=int(x)
  if b[2]-b[0]>100:out.append(dict(bbox=b,width=b[2]-b[0],height=b[3]-b[1],glyphs=[dict(left=z[0],width=z[1]-z[0]+1) for z in sp]))
 return dict(peakInk=peak,words=out)
rows=[];C=Image.new('RGB',(1280,360*5),'white');D=ImageDraw.Draw(C)
for i,n in enumerate([443,471,486,501,520]):
 a=np.asarray(Image.open(R/'source-native'/f'{n:06d}.png').convert('RGB')).astype(float);b=np.asarray(Image.open(R/'baseline'/f'{n/30:.3f}.png').convert('RGB')).astype(float);src=masks(a);candidate=masks(b);rows.append(dict(frame=n,source=src,candidate=candidate,globalNativeMAE=float(np.abs(a-b).mean()),row0MAE=float(np.abs(a[70:210]-b[70:210]).mean())));C.paste(Image.fromarray(a.astype('uint8')).resize((640,360)),(0,i*360));C.paste(Image.fromarray(b.astype('uint8')).resize((640,360)),(640,i*360));D.text((5,i*360+5),str(n)+' source',fill='red');D.text((645,i*360+5),'nativev13',fill='red')
base=np.asarray(Image.open(R/'source-native/000435.png').convert('RGB')).astype(float);report=dict(source435=masks(base),anchors=rows,notice='Clean row0 optical number boundaries/glyph counts distinguish spacing, glyph scale and alpha from selected capsule material. Native PNG comparison excludes encoded background level shift.');(R/'initial-diagnosis.json').write_text(json.dumps(report,indent=2));C.save(R/'source-native-contact.jpg');print('base435',[(q['bbox'],len(q['glyphs'])) for q in report['source435']['words']]);
for q in rows:print(q['frame'],'MAE',round(q['globalNativeMAE'],4),'ref',[(w['bbox'],len(w['glyphs'])) for w in q['source']['words']],'candidate',[(w['bbox'],len(w['glyphs'])) for w in q['candidate']['words']],flush=True)
# Native-size detail shows whether the apparent font mismatch survives alignment.
n=486;a=Image.open(R/'source-native'/f'{n:06d}.png');b=Image.open(R/'baseline'/f'{n/30:.3f}.png');detail=Image.new('RGB',(1400,580),'white');draw=ImageDraw.Draw(detail)
for i,box in enumerate([(420,70,1120,210),(80,200,780,340),(610,450,1310,610)]):
 detail.paste(a.crop(box),(0,i*190+20));detail.paste(b.crop(box),(700,i*190+20));draw.text((5,i*190+3),'source'+str(box),fill='red');draw.text((705,i*190+3),'nativev13',fill='red')
detail.save(R/'486-native-detail.jpg')
