from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parent;mapping=json.loads((ROOT/'verification/final/02-danieltian/source-gsap-v14/native-peaks/mapping.json').read_text());rows=[]
for f in[772,817,842,920]:
 imgs={k:np.asarray(Image.open(mapping[k][str(f)]).convert('RGB'))for k in mapping};s=imgs['reference'].astype(float);blue=(s[:,:,2]-s[:,:,0]>90)&(s[:,:,1]-s[:,:,0]>40)&(s[:,:,0]<120);lab,n=ndimage.label(blue);sizes=np.bincount(lab.ravel());sizes[0]=0;mask=lab==int(sizes.argmax());mask=ndimage.binary_fill_holes(mask);ys,xs=np.nonzero(mask);bb=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)];inside=ndimage.binary_erosion(mask,iterations=5);l,t,r,b=bb;crop=[max(0,l-80),max(0,t-45),min(1920,r+80),min(1080,b+45)];o=Image.new('RGB',(crop[2]-crop[0],2*(crop[3]-crop[1])),'white');d=ImageDraw.Draw(o);row={'frame':f,'sourceBlueBounds':bb}
 for j,(kind,a)in enumerate(imgs.items()):
  white=(a.min(2)>205)&inside;pink=(a[:,:,0].astype(float)>a[:,:,1].astype(float)+60)&(a[:,:,0]>150)&(a[:,:,2]>65)&(a[:,:,2]<200);pink[:700]=False;pink[:,:200]=False;pink[:,850:]=False;row[kind]={'whiteInkInsideBlue':int(white.sum()),'lowerAirbnbPinkPixels':int(pink.sum())};o.paste(Image.fromarray(a).crop(crop),(0,j*(crop[3]-crop[1])));d.text((5,j*(crop[3]-crop[1])+5),kind,fill='red')
 o.save(R/f'blue-{f}-native-pair.jpg');rows.append(row)
(R/'native-confirmation.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
