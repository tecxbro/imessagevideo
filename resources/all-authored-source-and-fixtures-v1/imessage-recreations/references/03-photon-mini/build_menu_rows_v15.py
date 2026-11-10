"""Create six bounded static rich-app row assets, not frames or video playback."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;A=P/'assets/menu-rows-v15';A.mkdir(exist_ok=True);D=P/'menu-rows-v15';D.mkdir(exist_ok=True)
spec=[('Grilled Chicken Rice Bowl',651,[660,329,1270,532]),('Roasted Veggie Grain Bowl',651,[660,532,1270,737]),('Chicken Caesar Salad',651,[660,737,1270,943]),('Turkey Avocado Wrap',700,[670,565,1258,764]),('Falafel Pita Pocket',700,[670,764,1258,963]),('Tomato Soup & Side Salad',729,[710,804,1215,907])];records=[]
for i,(name,f,box) in enumerate(spec):
 image=np.array(Image.open(P/'lunch-native'/f'{f-609:03}.png').convert('RGB'));x,y,x2,y2=box;crop=image[y:y2,x:x2];alpha=np.where(np.all(crop==253,axis=2),0,255).astype('uint8')
 if i==5:
  domain=image[:,650:1270];g=domain.mean(2);white=(g>245)&(domain.max(2).astype('int16')-domain.min(2)<10);lab,n=ndimage.label(white,np.ones((3,3)));candidates=[]
  for j,b in enumerate(ndimage.find_objects(lab),1):
   if b is not None and b[1].stop-b[1].start>200:candidates.append((int((lab[b]==j).sum()),j))
  chosen=max(candidates)[1];front=np.zeros(white.shape,bool)
  for yy in range(1080):
   xx=np.where(lab[yy]==chosen)[0]
   if len(xx):front[yy,xx.min():xx.max()+1]=True
  alpha[~front[y:y2,x-650:x2-650]]=0
 rgba=np.dstack([crop,alpha]);rgba[alpha==0,:3]=0;file=A/f'row-{i}.png';Image.fromarray(rgba).save(file);records.append({'row':i,'name':name,'source_frame':f,'source_crop':box,'asset':str(file),'dimensions':[x2-x,y2-y],'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'editability':'The row artwork includes bitmap app UI labels, prices, descriptions, photos and its original plus control. Outer native panel/header/hardware/cart/actor selection and independently measured row motion remain editable. Original native vector rows remain available in the scene as a gated fallback.','alpha_notice':'Exact253 white-paper pixels defer to the native253 sheet. Row5 also excludes exposed Messages gray margins using the actual reference white-body row spans; no gray backplane or hardware is baked in.'})
result={'source':'../source.mp4','scope':[618,729],'static_asset_count':6,'notice':'Six independently bounded static UI rows only, captured once each; no full source frame, source video, or per-frame row playback. Bitmap internal UI copy is explicitly declared. Row5 lower content that never appears cleanly remains source-cropped, and the measured native foreground/backplane stencil controls its visibility.','rows':records};(D/'assets.json').write_text(json.dumps(result,indent=2));print([(r['row'],r['dimensions']) for r in records])
