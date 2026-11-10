from pathlib import Path
import copy,json,math,sys
sys.path.insert(0,"/tmp/imessage-food-cv")
import cv2
import numpy as np
from PIL import Image
from scipy import ndimage
R=Path(__file__).resolve().parent;chat=json.loads((R/'chat-original.json').read_text());nodes={}
def walk(n):
 nodes[n['id']]=n
 for c in n.get('children',[]):walk(c)
walk(chat)
spec={'base':'outputs/02-danieltian/final-v14/scene.json','originalPropertyEdits':{},'insertAfter':{},'changedFrames':[],'provenance':{'method':'Existing semantic vector lettering clipped to native bubble interior, original avatar artwork under measured native poses, and five padded bounded rich-link product-art textures only. No complete source frame/video layer.','diagnosis':'Late reveal lifecycles; original white paths also contain bubble exterior corners, so only the correction interval is interior-clipped. Provider label and avatar geometry already existed but started late; bad842and868/869 orb bboxes came from hue-fragment selection. Photo840–844 crops truncated blur and included duplicate provider copy.'}}
def add_after(id,layer):spec['insertAfter'].setdefault(id,[]).append(layer)
def gate(id,frames):
 # Existing affected layers have no authored opacity animation except white glyphs; use exact native hold guards.
 n=nodes[id];ks=copy.deepcopy(n.get('keyframes',{}).get('opacity',[]));fset=set(frames);first=min(fset);last=max(fset)
 def old(f):
  t=f/30
  if not ks:return n.get('opacity',1)
  if t<=ks[0]['t']:return ks[0]['value']
  for a,b in zip(ks,ks[1:]):
   if t<=b['t']:
    p=(t-a['t'])/(b['t']-a['t']);return a['value']+(b['value']-a['value'])*p
  return ks[-1]['value']
 merged={q['t']:copy.deepcopy(q)for q in ks if not(first/30<=q['t']<=(last+1)/30)}
 for f in range(first-1,last+2):merged[f/30]={'t':f/30,'value':0 if f in fset else old(f),'ease':'hold'}
 spec['originalPropertyEdits'].setdefault(id,{})['opacityTrack']=sorted(merged.values(),key=lambda q:q['t']);spec['changedFrames']+=list(frames)
for role,first,last,W,H,dotlast in [('budget-reply',770,778,466,124,773),('love-it',920,926,180,92,922)]:
 glyph=copy.deepcopy(nodes['middle-glyphs-'+role]);glyph['id']='post-v14-interior-copy-'+role;glyph['start']=first/30;glyph['end']=(last+1)/30;glyph['opacity']=1;glyph.pop('keyframes',None);glyph['keyframes']={'opacity':[{'t':f/30,'value':json.loads((R/'copy-opacity-refined.json').read_text())[str(f)]}for f in range(first,last+1)]};glyph['clip']={'x':20,'y':20,'width':W-40,'height':H-40};glyph['editability']='Original native semantic vector lettering; correction interval excludes paper corners from original source-derived path.';gate('middle-glyphs-'+role,range(first,last+1));add_after('middle-glyphs-'+role,glyph)
 for k in range(3):gate(f'middle-source-dot-{role}-{k}',range(first,dotlast+1))
# Native source original avatar pixel bounds under independent translation/scale, only objectively wrong native states.
rows=json.loads((R/'avatar-measurements-refined.json').read_text())['rows'];av=nodes['middle-avatar-how-about'];bad=[q for q in rows if q.get('needsCorrection')];gate(av['id'],[q['frame']for q in bad])
for q in bad:
 f=q['frame'];layer=copy.deepcopy(av);layer['id']=f'post-v14-airbnb-orb-{f}';layer['start']=f/30;layer['end']=(f+1)/30;layer.pop('keyframes',None);layer.update(q['measuredPose']);layer['opacity']=q['opacity'];layer['children'][0]['id']=f'post-v14-airbnb-orb-art-{f}';layer['sourceMeasurement']=q['sourceColorBounds'];add_after(av['id'],layer)
label=nodes['middle-airbnb-card-sender-label'];rows=json.loads((R/'label-measurements-refined.json').read_text())['rows'];bad=[q for q in rows if q.get('needsCorrection')];gate(label['id'],[q['frame']for q in bad])
for q in bad:
 f=q['frame'];layer=copy.deepcopy(label);layer['id']=f'post-v14-airbnb-label-{f}';layer['start']=f/30;layer['end']=(f+1)/30;layer.pop('keyframes',None);layer.update(q['measuredPose']);layer['opacity']=q['opacity'];layer['sourceMeasurement']=q['matchedGlyphBounds'];add_after(label['id'],layer)
# Preserve soft local optical deformation as original bounded product artwork with explicit paper matting.
# Provider label stays independently native and is excluded above. Avatar is independently native above this card layer.
# Exact native typing silhouette, tail and all three dot phases; original typing is unchanged after840.
gate("middle-airbnb-typing", range(812,841))
for layer in json.loads((R/'typing-elements.json').read_text()):add_after('middle-airbnb-typing',layer)
# Body width changes by a hard source cut; the inherited tail drifted continuously to the wrong horizontal anchor.
def value(n,key,f):
 track=n.get('keyframes',{}).get(key,[]);t=f/30
 if not track:return n.get(key,1 if key.startswith('scale')else 0)
 if t<=track[0]['t']:return track[0]['value']
 for a,b in zip(track,track[1:]):
  if t<=b['t']:return a['value']+(b['value']-a['value'])*(t-a['t'])/(b['t']-a['t'])
 return track[-1]['value']
tail=nodes['middle-outgoing-tail-budget-reply'];body=nodes['middle-body-budget-reply'];gate(tail['id'],[f for f in range(754,779)if f!=765])
for f in [f for f in range(754,779)if f!=765]:
 layer=copy.deepcopy(tail);layer['id']=f'post-v14-budget-tail-{f}';layer.pop('keyframes',None);layer.update({'start':f/30,'end':(f+1)/30,'x':value(tail,'x',f) if f in[763,764]else value(body,'width',f)-467,'scaleY':1});add_after(tail['id'],layer)
# First two original body heights were measured from the viewport-clipped portion. The intrinsic capsule remains124high.
spec['originalPropertyEdits'].setdefault(body['id'],{})['heightTrack']=[{'t':753/30,'value':value(body,'height',753),'ease':'hold'},{'t':754/30,'value':124,'ease':'hold'},{'t':755/30,'value':124,'ease':'hold'},{'t':756/30,'value':124,'ease':'hold'}]+[q for q in body['keyframes']['height']if q['t']>756/30]
# Preserve genuine native three-dot poses and measure each source color phase at its opaque interior.
message=nodes['middle-message-budget-reply']
for index in range(3):
 dot=nodes[f'middle-source-dot-budget-reply-{index}'];track=[]
 for f in range(754,770):
  image=np.asarray(Image.open(R/'source-native'/f'source-{f:04d}.png').convert('RGB'));sx=value(message,'scaleX',f);sy=value(message,'scaleY',f);cx=value(message,'x',f)+(dot['x']+dot['width']/2)*sx;cy=value(message,'y',f)+(dot['y']+dot['height']/2)*sy;radius=min(dot['width']*sx,dot['height']*sy)*.24;yy,xx=np.mgrid[max(0,int(cy-radius)):min(1080,int(cy+radius+1)),max(0,int(cx-radius)):min(1920,int(cx+radius+1))];pixels=image[yy,xx][(xx-cx)**2+(yy-cy)**2<radius**2];color=np.median(pixels,axis=0).round().astype(int);track.append({'t':f/30,'value':dot['fill']if f in[765,915]else'#'+''.join(f'{v:02x}'for v in color),'ease':'hold'})
 track.append({'t':770/30,'value':dot['fill'],'ease':'hold'});spec['originalPropertyEdits'].setdefault(dot['id'],{})['fillTrack']=track
# Independent review confirmed the same inherited static-color pulse on Love it912–919.
message=nodes['middle-message-love-it']
for index in range(3):
 dot=nodes[f'middle-source-dot-love-it-{index}'];track=[]
 for f in range(912,920):
  image=np.asarray(Image.open(R/'source-native'/f'source-{f:04d}.png').convert('RGB'));sx=value(message,'scaleX',f);sy=value(message,'scaleY',f);cx=value(message,'x',f)+(dot['x']+dot['width']/2)*sx;cy=value(message,'y',f)+(dot['y']+dot['height']/2)*sy;radius=min(dot['width']*sx,dot['height']*sy)*.24;yy,xx=np.mgrid[max(0,int(cy-radius)):min(1080,int(cy+radius+1)),max(0,int(cx-radius)):min(1920,int(cx+radius+1))];pixels=image[yy,xx][(xx-cx)**2+(yy-cy)**2<radius**2];color=np.median(pixels,axis=0).round().astype(int);track.append({'t':f/30,'value':dot['fill']if f in[765,915]else'#'+''.join(f'{v:02x}'for v in color),'ease':'hold'})
 track.append({'t':920/30,'value':dot['fill'],'ease':'hold'});spec['originalPropertyEdits'].setdefault(dot['id'],{})['fillTrack']=track
spec['changedFrames']+=[f for f in range(912,920)if f!=915]
photo=[]
for f in range(840,845):
 a=np.asarray(Image.open(R/'source-native'/f'source-{f:04d}.png').convert('RGB')).astype(float);q=next(q for q in rows if q['frame']==f);labelBottom=q['matchedGlyphBounds'][3];x0=480 if f in[840,841]else 470;y0=int(math.floor(q['matchedGlyphBounds'][1]-40));x1={840:650,841:700,842:960,843:1140,844:1210}[f];y1={840:835,841:825,842:945,843:1025,844:1050}[f];crop=a[y0:y1,x0:x1].copy();left,top,right,bottom=q['matchedGlyphBounds'];mask=np.zeros(crop.shape[:2],dtype='uint8');yl=max(0,int(top)-y0-2);yr=min(crop.shape[0],int(bottom)-y0+3);xl=max(0,int(left)-x0-2);xr=min(crop.shape[1],int(right)-x0+3);letters=(crop[yl:yr,xl:xr].max(2)<235)&(crop[yl:yr,xl:xr].max(2)-crop[yl:yr,xl:xr].min(2)<15);mask[yl:yr,xl:xr]=letters.astype('uint8')*255;mask=cv2.dilate(mask,np.ones((3,3),dtype='uint8'));crop=cv2.inpaint(crop.astype('uint8'),mask,3,cv2.INPAINT_TELEA).astype(float);delta=np.max(abs(crop-253),axis=2);alpha=np.clip(delta/253,0,1);alpha[delta<=3]=0
 # Remove only independently reconstructed original sender orb from this original local card texture.
 avrow=next(q for q in json.loads((R/'avatar-measurements-refined.json').read_text())['rows']if q['frame']==f);l,t,r,b=avrow['sourceColorBounds'];yy,xx=np.mgrid[y0:y1,x0:x1];cx=(l+r)/2;cy=(t+b)/2;rr=((xx-cx)/((r-l)/2+3))**2+((yy-cy)/((b-t)/2+3))**2;alpha[rr<1]=0
 rgb=np.where(alpha[:,:,None]>0,253+(crop-253)/np.maximum(alpha[:,:,None],1e-6),0);rgba=np.dstack([np.clip(rgb,0,255),alpha*255]).round().astype('uint8');p=R/f'card-soft-original-{f}.png';Image.fromarray(rgba).save(p);oldid=f'v11-card-local-pose-{f}';gate(oldid,[f]);layer={'id':f'post-v14-soft-card-{f}','type':'group','x':x0,'y':y0,'start':f/30,'end':(f+1)/30,'sourceFrame':f,'sourceBounds':[x0,y0,x1,y1],'editability':'Bounded original product artwork for brief local deformation; bitmap internal UI/blur, independent native pose; source paper matte is transparent. Sender label/orb remain separate native actors.','children':[{'id':f'post-v14-soft-card-art-{f}','type':'image','src':str(p),'width':x1-x0,'height':y1-y0}]};add_after(oldid,layer);photo.append({'frame':f,'bounds':[x0,y0,x1,y1]})
spec['changedFrames']=sorted(set(spec['changedFrames']));spec['photoBounds']=photo;(R/'elements-candidate.json').write_text(json.dumps(spec,separators=(',',':')));print('changed',len(spec['changedFrames']),spec['changedFrames']);print('edits',len(spec['originalPropertyEdits']),'added',sum(map(len,spec['insertAfter'].values())))
