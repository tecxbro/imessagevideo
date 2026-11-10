"""Bounded URL glyph poses + exact native black-word outlines for a short source transition.
No complete source frame is used as a runtime asset. Each URL tile is one independently
bounded semantic glyph pose; bitmap internals and native lifetime/position are explicit.
"""
from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0,'/workspace/imessage-recreations/references/02-danieltian')
from trace_glyphs import trace_alpha
R=Path('/workspace/imessage-recreations');REF=R/'references/01-photonhq';P=R/'verification/fidelity-review/01-intro';AS=REF/'assets/intro-review/url-glyph-poses';AS.mkdir(exist_ok=True)
spec=json.loads((REF/'intro-review-elements.json').read_text());extra=json.loads((P/'source-extra-map.json').read_text());base=json.loads((REF/'scene-intro-base-v4.json').read_text());url=next(c for q in base['layers'] if q['id']=='group-786' for c in q['children'] if c['type']=='image');raw=np.array(Image.open(url['src']).convert('RGB'));chroma=(raw[:,:,2].astype(float)-raw[:,:,0])/255;lab,n=ndimage.label(chroma>.12,np.ones((3,3)));comps=[]
for j,sl in enumerate(ndimage.find_objects(lab),1):
 if sl is not None and np.count_nonzero(lab[sl]==j)>10:comps.append((sl[1].start,j,sl))
comps.sort();assert len(comps)==17
centers=[url['x']+(sl[1].start+sl[1].stop)/2 for _,j,sl in comps];cuts=[url['x']-20]+[(comps[i][2][1].stop+comps[i+1][2][1].start)/2+url['x'] for i in range(16)]+[url['x']+url['width']+20];camera={v['frame']:v for v in spec['measurements']['URL-camera']};nodes=[];ledger=[];wordnodes=[];rows=[]
def frame(f):
 path=P/extra[str(f)];return np.array(Image.open(path).convert('RGB')).astype(float),path
for f in range(518,555):
 a,src=frame(f);roi=a[350:600,300:1600];dark=(roi.max(2)<100)&(roi.max(2)-roi.min(2)<5);ys,xs=np.where(dark);assert len(xs)
 ylo=max(350,int(ys.min())+348);yhi=min(600,int(ys.max())+353)
 # Black word alpha excludes colored URL artwork and background codec noise.
 ar=a[ylo:yhi,300:1600];alpha=(255-ar.mean(2))/255;alpha[ar.max(2)-ar.min(2)>5]=0;alpha[alpha<2/255]=0
 # Every source word is an independent native contour at its exact source pose.
 col=(alpha>.035).any(0);xx=np.where(col)[0];gaps=np.where(np.diff(xx)>18)[0];bounds=[300]+[int((xx[i]+xx[i+1])/2)+300 for i in gaps]+[1600];count=len(bounds)-1
 # Source introduces words one by one; do not infer presence from a fitted template.
 tokens=['On','us.'] if f<520 else ['Try','it','today','at'];assert count<=len(tokens),(f,count)
 for wi,(left,right) in enumerate(zip(bounds,bounds[1:])):
  al=alpha[:,left-300:right-300];yy,xx2=np.where(al>.003)
  if not len(xx2):continue
  box=[left+int(xx2.min()),ylo+int(yy.min()),left+int(xx2.max())+1,ylo+int(yy.max())+1];A=al[yy.min():yy.max()+1,xx2.min():xx2.max()+1];d,stats=trace_alpha(A,box[0],box[1]);id=f'cta-native-word-{f}-{wi}';wordnodes.append(dict(type='path',id=id,d=d,fill='#000000',semanticText=tokens[wi],start=f/30,end=(f+1)/30,sourceFrame=f,sourceBounds=box,editability='Native editable glyph contours; measured one-frame source pose.'));ledger.append(dict(id=id,kind='native semantic word contours',sourceFrame=f,sourceBounds=box,sourceSHA256=hashlib.sha256(src.read_bytes()).hexdigest(),**stats))
 if f<531:continue
 cam=camera[f];sx=cam['sx'];tx=cam['tx'];xedges=[max(0,int(round(tx+sx*x))) for x in cuts];url_ylo=yhi+7;url_yhi=min(1080,max(800,int(cam['ty']+cam['sy']*(url['y']+url['height'])+100)));glyphs=0
 for i,(xlo,xhi) in enumerate(zip(xedges,xedges[1:])):
  art=a[url_ylo:url_yhi,xlo:xhi];contrast=255-art.min(2);strong=contrast>3
  # Reject codec specks without deleting weak, spatially coherent real lettering.
  labels,num=ndimage.label(strong,np.ones((3,3)));good=np.zeros(strong.shape,bool)
  for j,sl in enumerate(ndimage.find_objects(labels),1):
   if sl is not None and np.count_nonzero(labels[sl]==j)>30:good[sl]|=labels[sl]==j
  if not good.any():continue
  good=ndimage.binary_dilation(good,iterations=5);yy,xx=np.where(good);b=[xlo+int(xx.min()),url_ylo+int(yy.min()),xlo+int(xx.max())+1,url_ylo+int(yy.max())+1];v=a[b[1]:b[3],b[0]:b[2]];D=255-v;al=D.max(2)/255;al[al<2/255]=0;rgb=np.where(al[:,:,None]>0,(v-255*(1-al[:,:,None]))/np.maximum(.00001,al[:,:,None]),0);rgba=np.concatenate((np.clip(rgb,0,255),al[:,:,None]*255),2).round().astype('uint8');path=AS/f'{f}-{i:02d}.png';Image.fromarray(rgba,'RGBA').save(path);id=f'cta-url-pose-{f}-{i}';nodes.append(dict(type='image',id=id,src=str(path),x=b[0],y=b[1],width=b[2]-b[0],height=b[3]-b[1],start=f/30,end=(f+1)/30,semanticText='photon.codes/beta'[i],sourceFrame=f,sourceBounds=b,editability='Independent bounded original glyph pose artwork; native pose/lifetime editable, bitmap internals.'));ledger.append(dict(id=id,kind='bounded semantic glyph pose artwork',sourceFrame=f,sourceBounds=b,asset=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),sourceSHA256=hashlib.sha256(src.read_bytes()).hexdigest()));glyphs+=1
 rows.append(dict(frame=f,blackWords=count,urlGlyphs=glyphs))
# Gate the previous whole On-us path at518, preserving its earlier settled hold.
spec['gate_overrides']['text-783-source-outline']['end']=518/30;spec['insert_before'].pop('text-783-source-outline',None);spec['insert_before']['group-786']=[dict(type='group',id='cta-measured-entry',start=518/30,end=555/30,children=wordnodes+nodes)];spec['assets']+=ledger;spec['measurements']['CTA-pose-art']=rows;spec['notice']='Measured native intro + CTA transition. Native word contours, native independent transforms; brief bounded per-glyph original URL pose artwork preserves gray/blur/cyan reveal. Bitmap internals disclosed; no complete source-frame or video playback. Settled18.5+ and walls unchanged.'
(REF/'intro-review-elements.json').write_text(json.dumps(spec,indent=2));(REF/'cta-pose-art-provenance.json').write_text(json.dumps(dict(notice=spec['notice'],rows=rows,assets=ledger),indent=2));print('native words',len(wordnodes),'URL glyph artwork',len(nodes));print(rows)
