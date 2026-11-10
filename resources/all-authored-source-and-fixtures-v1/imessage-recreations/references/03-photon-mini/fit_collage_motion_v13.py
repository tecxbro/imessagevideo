"""Fit independent native card poses from original static artwork + footer bands.
Analysis uses source crops; output layers remain native cards and isolated artwork.
"""
from pathlib import Path
import copy,json,hashlib
import numpy as np
from scipy.optimize import linear_sum_assignment
from PIL import Image
p=Path(__file__).parent;s=json.loads((p/'entrance-v13.scene.json').read_text());old=next(x for x in s['layers'] if x['id']=='p03-650');cards=old['children'];data=json.loads((p/'collage-v13-footer-measurements.json').read_text());source31=Image.open(p/'measured/31.png').convert('RGB');W,H=128,68;FW,FH=192,36

def patch(image,box,size,fill=253):return np.array(image.transform(size,Image.Transform.EXTENT,tuple(float(x) for x in box),Image.Resampling.BILINEAR,fillcolor=(fill,fill,fill)),dtype='float32')
def rgbimage(file):
 a=Image.open(file).convert('RGBA');b=Image.new('RGBA',a.size,(253,253,253,255));b.alpha_composite(a);return b.convert('RGB')
def art_image(card):
 art=card['children'][1];images=[x for x in art['children'] if x['type']=='image'];return rgbimage(p/images[-1]['src'])
arts=[];feet=[];centers=[];basewidths=[]
for card in cards:
 basewidths.append(390*next((q['value'] for q in card.get('keyframes',{}).get('scaleX',[]) if q['t']==31.35),1))
 arts.append(np.array(art_image(card).resize((W,H),Image.Resampling.BILINEAR),dtype='float32'))
 x,y=card['x'],card['y'];feet.append(patch(source31,(x,y+208,x+390,y+280),(FW,FH),230));centers.append([x+195,y+140])
original_widths=list(basewidths)
anchor_data=json.loads((p/'collage-v13-changes.json').read_text()) if (p/'collage-v13-changes.json').exists() else {}
anchor_row=next((r for r in anchor_data.get('measurements',[]) if r['frame']==930),{'matches':[]})
anchor_boxes={q['index']:q['pose']['box'] for q in anchor_row['matches']}
for c,box in anchor_boxes.items():
 if box[0]>2 and box[2]<1918:basewidths[c]=box[2]-box[0]
arts=np.array(arts);footmask=np.clip((225-np.array(feet).mean(3))/225,0,1);fvariants=np.array([np.roll(footmask,shift,axis=1) for shift in [-2,-1,0,1,2]]);fden=np.sqrt(np.sum(fvariants*fvariants,axis=(2,3)))+1e-8;centers=np.array(centers,dtype='float64')
# Unclipped footer width measures the true rapid camera curve, not a sparse tween.
widths={}
for row in data:
 values=[q['box'][2]-q['box'][0] for q in row['footers'] if q['box'][0]>2 and q['box'][2]<1918]
 if values:widths[row['frame']]=float(np.median(values))
widths[900]=1950.0

def width_at(frame):
 if frame in widths:return widths[frame]
 before=[f for f in widths if f<frame];after=[f for f in widths if f>frame]
 if before and after:
  a,b=max(before),min(after);u=(frame-a)/(b-a);return float(np.exp(np.log(widths[a])*(1-u)+np.log(widths[b])*u))
 return widths[min(widths,key=lambda f:abs(f-frame))]

def normalized(image,left,top,width,height):
 art=patch(image,(left,top,left+width,top+height),(W,H));xx=left+(np.arange(W)+.5)*width/W;yy=top+(np.arange(H)+.5)*height/H;valid=(yy[:,None]>=0)&(yy[:,None]<1080)&(xx[None,:]>=0)&(xx[None,:]<1920);return art,valid

def evaluate(frame,previous):
 row=data[frame-891];image=Image.open(p/'collage-native'/f'{frame-890:03}.png').convert('RGB');records=[];costs=[];median_width=width_at(frame)
 for box in [q['box'] for q in row['footers']]:
  left,ft,right,bottom=box;clipped=left<=2 or right>=1918;width=median_width if clipped else right-left
  if left<=2:left=right-width
  scale=width/390
  if bottom>=1079:bottom=ft+72*scale
  top=bottom-280*scale;foot_top=bottom-72*scale;art,valid=normalized(image,left,top,width,208*scale);foot=patch(image,(left,foot_top,left+width,bottom),(FW,FH),230);alpha=np.clip((225-foot.mean(2))/225,0,1);norm=np.sqrt(np.sum(alpha*alpha))+1e-8;cos=np.max(np.einsum('svhw,hw->sv',fvariants,alpha)/(fden*norm),axis=0);mse=np.mean(np.abs(arts[:,valid]-art[valid]),axis=(1,2))/255 if valid.sum()>50 else np.full(20,.22);score=mse*3+(1-cos)*.4
  if previous:
   point=np.array([left+width/2,top+140*scale]);pred=np.array([[q['x']+195*q['scale'],q['y']+140*q.get('scaleY',q.get('scaleY',q['scale']))] for q in previous]);distance=np.linalg.norm(pred-point,axis=1)/max(width,200);score+=np.minimum(distance,3)*.06
  records.append({'box':box,'x':float(left),'y':float(top),'width':float(width),'scale':float(scale),'art_error':mse.tolist(),'footer_cosine':cos.tolist()});costs.append(score)
 if not records:return [],None,image
 costs=np.array(costs);dummy=np.full((len(records),len(records)),.77);extended=np.concatenate([costs,dummy],axis=1);rr,cc=linear_sum_assignment(extended);matched=[]
 for r,c in zip(rr,cc):
  if c<20 and costs[r,c]<.77:matched.append((c,records[r],float(costs[r,c])))
 if frame<=902 and len(records)==1:matched=[(7,records[0],float(costs[0,7]))]
 # Native card widths differ slightly because their planes retain perspective;
 # do not mistake those width differences for vertical camera scale.
 ratios=[q['width']/basewidths[c] for c,q,cost in matched if q['box'][0]>2 and q['box'][2]<1918]
 global_scale=float(np.median(ratios)) if ratios else median_width/395
 for c,q,cost in matched:
  box=q['box'];width=q['width']
  if box[0]<=2 or box[2]>=1918:width=basewidths[c]*global_scale
  sy=width/basewidths[c];bottom=box[3] if box[3]<1079 else box[1]+72*sy
  observed_left=box[2]-width if box[0]<=2 else box[0]
  baseline_box=anchor_boxes.get(c,[cards[c]['x'],cards[c]['y']+208,cards[c]['x']+basewidths[c],cards[c]['y']+280])
  baseline_left=baseline_box[2]-basewidths[c] if baseline_box[0]<=2 else baseline_box[0]
  q['x']=float(observed_left+(cards[c]['x']-baseline_left)*sy);q['width']=float(width);q['scale']=original_widths[c]/390*sy;q['scaleY']=sy;q['y']=float(bottom-(baseline_box[3]-cards[c]['y'])*sy)
 # Complete the off-stage/partly visible field from matched native card centers.
 if len(matched)>=3:
  baseline=np.array([centers[c] for c,_,_ in matched]);target=np.array([[q['x']+q['width']/2,q['y']+140*q.get('scaleY',q.get('scaleY',q['scale']))] for _,q,_ in matched]);A=np.column_stack([baseline,np.ones(len(baseline))]);affine=np.linalg.lstsq(A,target,rcond=None)[0]
 elif matched:
  c,q,_=matched[0];scale=q['scale'];offset=np.array([q['x']+q['width']/2,q['y']+140*q.get('scaleY',scale)])-centers[c]*scale;affine=np.array([[scale,0],[0,scale],offset])
 else:affine=None
 poses=[]
 for c,card in enumerate(cards):
  match=next((q for index,q,cost in matched if index==c),None)
  if match:x,y,scale,sy=match['x'],match['y'],match['scale'],match['scaleY']
  elif affine is not None:
   center=np.r_[centers[c],1]@affine;scale=median_width/390;sy=global_scale;x=float(center[0]-195*scale);y=float(center[1]-140*sy)
  elif previous:x,y,scale,sy=previous[c]['x'],previous[c]['y'],previous[c]['scale'],previous[c].get('scaleY',previous[c]['scale'])
  else:x,y,scale,sy=card['x'],card['y'],median_width/390,global_scale
  actual,valid=normalized(image,x,y,390*scale,208*sy);dd=253-arts[c];ss=253-actual;den=np.sum(dd[valid]*dd[valid]);opacity=1.0 if match or frame<950 else float(np.clip(np.sum(dd[valid]*ss[valid])/den,0,1)) if den>50 and valid.sum()>40 else 0
  # Do not let unrelated media revive a card whose old fade has completed.
  if not match and frame>=960:opacity=min(opacity,.12)
  poses.append({'x':x,'y':y,'scale':scale,'scaleY':sy,'opacity':opacity,'matched':match is not None})
 return poses,{'frame':frame,'t':frame/30,'median_width':median_width,'matches':[{'index':int(c),'id':cards[c]['id'],'name':cards[c]['children'][2].get('text'),'cost':cost,'pose':q} for c,q,cost in matched],'poses':poses},image

measurements={};previous=None
for frame in range(930,900,-1):
 poses,record,_=evaluate(frame,previous)
 if record:measurements[frame]=record;previous=poses
previous=measurements[930]['poses']
for frame in range(931,975):
 poses,record,_=evaluate(frame,previous)
 if record:measurements[frame]=record;previous=poses
# Extrapolate each independently flying card after its footer leaves the crop.
# Holding the final detected pose invents a stationary card at32.4s.
for index in range(20):
 known=[(f,measurements[f]['poses'][index]) for f in sorted(measurements) if measurements[f]['poses'][index] is not None and measurements[f]['poses'][index]['matched']]
 for f in range(901,975):
  if f not in measurements:
   measurements[f]={'frame':f,'t':f/30,'median_width':width_at(f),'matches':[],'poses':[None]*20}
  q=measurements[f]['poses'][index]
  if q is not None and q['matched']:continue
  earlier=[(ff,qq) for ff,qq in known if ff<f]
  if f>=950 and len(earlier)>=3:
   recent=earlier[-4:];tt=np.array([ff for ff,qq in recent]);target={}
   for key in ['x','y','scale','scaleY']:
    vals=np.array([qq[key] for ff,qq in recent]);coef=np.polyfit(tt-tt[-1],vals,1);target[key]=float(np.polyval(coef,f-tt[-1]))
   target['scale']=max(.1,target['scale']);target['scaleY']=max(.1,target['scaleY']);target['matched']=False;target['opacity']=0.0
   if target['x']+390*target['scale']<0 or target['x']>1920 or target['y']+280*target['scale']<0 or target['y']>1080:target['opacity']=0
   measurements[f]['poses'][index]=target
  elif q is None:
   measurements[f]['poses'][index]=copy.deepcopy(earlier[-1][1] if earlier else measurements[930]['poses'][index]);measurements[f]['poses'][index]['opacity']=0
# Independently editable cards with explicit world poses; the old global zoom
# cannot interpolate between30.0 and30.5 correctly and is stopped at frame900.
old['end']=901/30;new={'id':'measured-collage-v13','type':'group','start':901/30,'end':32.5,'children':[]}
def reid(layer):
 layer['id']='collage13-'+layer['id']
 for c in layer.get('children',[]):reid(c)
for index,card in enumerate(cards):
 c=copy.deepcopy(card);reid(c);c['x']=0;c['y']=0;c['keyframes']={k:[] for k in ['x','y','scaleX','scaleY','opacity']}
 for frame in range(901,975):
  if frame not in measurements:continue
  q=measurements[frame]['poses'][index]
  for key,value in [('x',q['x']),('y',q['y']),('scaleX',q['scale']),('scaleY',q.get('scaleY',q['scale'])),('opacity',q['opacity'])]:c['keyframes'][key].append({'t':frame/30,'value':value,'ease':'linear'})
 new['children'].append(c)
s['layers'].insert(s['layers'].index(old)+1,new);s['source']['notes']+=' V13 collagebranch: originalstaticart/footer descriptors identify eachcard; actual native-frame footerbounds replace sparse global camera tween. Independent cardgeometry/opacity remains editable, no sourceframe/video layer.'
f=p/'late-v13.scene.json';f.write_text(json.dumps(s,indent=2));sha=hashlib.sha256(f.read_bytes()).hexdigest();(p/'collage-v13-changes.json').write_text(json.dumps({'sha256':sha,'baseline':'entrance-v13.scene.json','proposed_delta':[901,974],'measurements':[measurements[f] for f in sorted(measurements)],'limitation':'Current fit uses affine card geometry; unresolved descriptor assignments and physical3Dperspective require native visual validation.'},indent=2));print(sha);print([(f,len(measurements[f]['matches'])) for f in [901,904,915,930,941,956,960,966,974] if f in measurements])
