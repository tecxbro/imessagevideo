"""Bounded individual app-plane poses for the brief strongly projected crop."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,copy
p=Path(__file__).parent;s=json.loads((p/'collage-v14.scene.json').read_text());old=next(x for x in s['layers'] if x['id']=='p03-650');grid=next(x for x in s['layers'] if x['id']=='measured-collage-v13');assetdir=p/'assets/collage-poses-v14';assetdir.mkdir(exist_ok=True);poses={'id':'measured-collage-projected-poses-v14','type':'group','start':899/30,'end':960/30,'children':[]};meta=[]
def add(frame,name,roi,mode='component'):
 a=np.array(Image.open(p/'collage-native'/f'{frame-890:03}.png').convert('RGB'));x0,y0,x1,y1=roi;crop=a[y0:y1,x0:x1].astype('int16');m=np.max(np.abs(crop-253),2)>4;l,n=ndimage.label(m);areas=np.bincount(l.ravel());areas[0]=0;label=int(areas.argmax());yy,xx=np.where(l==label);box=[x0+int(xx.min()),y0+int(yy.min()),x0+int(xx.max()+1),y0+int(yy.max()+1)];rgb=a[box[1]:box[3],box[0]:box[2]];mask=(l==label)[int(yy.min()):int(yy.max()+1),int(xx.min()):int(xx.max()+1)];mask=ndimage.binary_fill_holes(mask);rgba=np.dstack([rgb,mask.astype('uint8')*255]);file=f'assets/collage-poses-v14/{name}-{frame:04}.png';Image.fromarray(rgba).save(p/file);poses['children'].append({'id':f'app-pose-{name}-{frame}','type':'image','src':file,'x':box[0],'y':box[1],'width':box[2]-box[0],'height':box[3]-box[1],'start':frame/30,'end':(frame+1)/30,'semanticText':name,'provenance':{'source_frame':frame,'source_box':box,'kind':'Individual static rich app-plane projection pose; internal copy bitmap. No whole source frame/video.'}});meta.append({'frame':frame,'app':name,'file':file,'source_box':box})
for f in range(899,903):
 add(f,'Spectrum-mini-apps',[0,450,1200,1080])
 if f>=901:
  add(f,'Marriott-Stay',[0,0,700,300]);add(f,'Coding-Agent',[1250,650,1920,1080])
for index,c in enumerate(old['children']):
 if index!=7:c['keyframes']['opacity']=[{'t':899/30,'value':0}]
for index,c in enumerate(grid['children']):
 if index!=7:
  for q in c['keyframes']['opacity']:
   if 901/30<=q['t']<903/30:q['value']=0
# A one-frame detector dropout must not erase a plane observed on both sides.
for c in grid['children']:
 tracks=c['keyframes'];op={round(q['t']*30):q for q in tracks['opacity']}
 for f in range(950,974):
  if op[f]['value']==0 and op[f-1]['value']>.8 and op[f+1]['value']>.8:
   for name,track in tracks.items():
    d={round(q['t']*30):q for q in track};d[f]['value']=(d[f-1]['value']+d[f+1]['value'])/2
# eBay's footer stays below the stage, so footer-only visibility cannot locate
# its final partial blue app screen. Preserve bounded app-only original poses.
for f in range(950,960):
 a=np.array(Image.open(p/'collage-native'/f'{f-890:03}.png'));r=a.astype('int16');m=(r[:,:,2]>175)&(r[:,:,0]<135)&(r[:,:,1]>45)&(r[:,:,1]<175)&(r[:,:,2]-r[:,:,1]>45);m[:800]=False;m[:,1200:]=False;l,n=ndimage.label(m);best=None
 for i,b in enumerate(ndimage.find_objects(l),1):
  if b is None:continue
  yy,xx=b;area=int((l[b]==i).sum());w=xx.stop-xx.start
  if w>150 and area>1500 and (best is None or area>best[0]):best=(area,xx.start,yy.start,xx.stop)
 if best:
  _,x,y,right=best;box=[max(0,x-4),max(0,y-4),min(1920,right+4),1080];file=f'assets/collage-poses-v14/ebay-partial-{f:04}.png';Image.fromarray(a[box[1]:box[3],box[0]:box[2]]).save(p/file);poses['children'].append({'id':f'app-pose-ebay-{f}','type':'image','src':file,'x':box[0],'y':box[1],'width':box[2]-box[0],'height':box[3]-box[1],'start':f/30,'end':(f+1)/30,'semanticText':'eBay delivery info','provenance':{'source_frame':f,'source_box':box,'kind':'Bounded partial app plane, bitmap internal UI; editable camera/lifetime.'}});meta.append({'frame':f,'app':'eBay','file':file,'source_box':box})
s['layers'].insert(s['layers'].index(grid)+1,poses);s['source']['notes']+=' V14 collateral app planes899–902 use separately bounded genuine projected UI poses while their native editable containers remain. Footer-only single-frame dropouts interpolate observed neighbors. Partial eBayUI remains visible950–959 even though its footer never enters the viewport. No whole sourceframe/video asset.'
(p/'collage-v14.scene.json').write_text(json.dumps(s,indent=2));(p/'collage-poses-v14-provenance.json').write_text(json.dumps(meta,indent=2));print('bounded poses',len(meta))
