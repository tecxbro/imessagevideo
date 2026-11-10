"""Separate inbox-row UI camera, physical bezel and island from favorites."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy import ndimage
p=Path(__file__).parent
def box(mask):
 y,x=np.where(mask);return[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]if len(x)else None
def objects(mask):
 labels,_=ndimage.label(mask);rows=[]
 for i,sl in enumerate(ndimage.find_objects(labels),1):
  if sl is None:continue
  yy,xx=sl;rows.append({'id':i,'bbox':[xx.start,yy.start,xx.stop,yy.stop],'width':xx.stop-xx.start,'height':yy.stop-yy.start,'area':int((labels[sl]==i).sum())})
 return labels,rows
reference=np.array(Image.open(p/'measurements-v8/decoded/000120.png').convert('RGB'));refmask=(reference[670:740,440:900].max(2)<80);b=box(refmask);ref_name=[b[0]+440,b[1]+670,b[2]+440,b[3]+670];rows=[]
for n in range(2,142):
 a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB'));c=a.astype(int);r={'frame':n,'time':n*1001/30000};lo=780 if n<109 else 650;roi=a[lo:1080,:1000];gray=(roi.max(2)-roi.min(2)<10)&(roi.max(2)<235)
 if n<109:gray&=roi.min(2)>150
 linked=ndimage.binary_dilation(gray,structure=np.ones((1,35),bool));labels,parts=objects(linked);text=[q for q in parts if q['width']>80 and 12<q['height']<180 and q['width']/q['height']>3]
 if text:
  chosen=min(text,key=lambda q:q['bbox'][1]);actual=gray&(labels==chosen['id']);b=box(actual)
  if b:
   b=[b[0],b[1]+lo,b[2],b[3]+lo];h=b[3]-b[1];r['name_ink_bbox']=b;r['ui_scale_ratio'] =h/(ref_name[3]-ref_name[1]);values=roi.mean(2)[actual];r['ui_opacity']=float(np.clip(1-np.percentile(values,10)/255,0,1))
 labels,dark=objects(a.max(2)<80);tall=[q for q in dark if q['height']>800 and q['width']>2]
 if tall:r['physical_bbox']=[min(q['bbox'][0]for q in tall),min(q['bbox'][1]for q in tall),max(q['bbox'][2]for q in tall),max(q['bbox'][3]for q in tall)]
 islands=[q for q in dark if q['width']>150 and 20<q['height']<250 and q['width']/q['height']>2.5 and q['bbox'][1]<250 and 500<(q['bbox'][0]+q['bbox'][2])/2<950]
 if islands:r['island_bbox']=max(islands,key=lambda q:q['area'])['bbox']
 rows.append(r)
assets=[]
for name,roi in [('nikki',(342,707,430,795)),('jony',(342,907,430,995)),('nikki-emoji',(985,735,1029,779))]:
 file=p/'assets'/f'intro-{name}-native4.png';Image.fromarray(reference).crop(roi).save(file);assets.append({'asset':'assets/'+file.name,'source_frame':120,'source_crop':list(roi),'purpose':'Genuine individual Memoji/emoji contact artwork only; editable native row type/layout remains separate.'})
ref_name=next(row['name_ink_bbox']for row in rows if row['frame']==120)
for row in rows:
 if row.get('name_ink_bbox'):row['ui_scale_ratio']=(row['name_ink_bbox'][3]-row['name_ink_bbox'][1])/(ref_name[3]-ref_name[1])
(p/'assets/intro-native-v8-provenance.json').write_text(json.dumps(assets,indent=2));(p/'measurements-v8/intro-ui-fit.json').write_text(json.dumps({'reference_frame':120,'reference_name_ink_bbox':ref_name,'method':'Native inbox title ink gives independent UI camera/opacity; tall bezel and contiguous island measure physical camera separately. No whole source frame is an output layer.','measurements':rows},indent=2));print('referenceName',ref_name)
for n in [30,60,98,108,109,120,131]:print(next(r for r in rows if r['frame']==n))
