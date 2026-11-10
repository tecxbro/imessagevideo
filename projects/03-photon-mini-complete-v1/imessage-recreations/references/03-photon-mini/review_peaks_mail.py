"""Measured semantic Mail-plane outlines and color-only material,310–334.
Physical hardware/sender remain the accepted separate camera/artwork.
"""
from pathlib import Path
import json,sys,numpy as np
from PIL import Image
from scipy import ndimage
R=Path('/workspace/imessage-recreations'); REF=R/'references/03-photon-mini'; P=R/'verification/fidelity-review/03-peaks'; BASE=R/'outputs/03-photon-mini/final-v14'; A=REF/'assets/peaks-review-mail';A.mkdir(exist_ok=True)
sys.path.insert(0,str(R/'references/02-danieltian'));from trace_glyphs import trace_alpha
scene=json.load(open(BASE/'scene.json'));phone=next(l for l in scene['layers']if l['id']=='p03-86');sheet=next(l for l in phone['children']if l['id']=='p03-77')
def value(layer,key,t,default=0):
 vs=layer.get('keyframes',{}).get(key)
 if not vs:return layer.get(key,default)
 if t<=vs[0]['t']:return vs[0]['value']
 for a,b in zip(vs,vs[1:]):
  if t<=b['t']:
   p=(t-a['t'])/(b['t']-a['t']);return a['value']+(b['value']-a['value'])*p
 return vs[-1]['value']
def filled_rows(mask):
 labels,n=ndimage.label(mask);areas=np.bincount(labels.ravel());areas[0]=0;selected=labels==areas.argmax();filled=np.zeros_like(mask)
 for y in np.where(selected.any(1))[0]:filled[y,:np.where(selected[y])[0].max()+1]=True
 return filled

def outline(mask):
 # The pane continues beyond the left/bottom viewport; extend those edges to
 # avoid manufacturing an antialiased seam at the source crop.
 padded=np.pad(mask.astype(float),((0,50),(50,0)),mode='edge');d,stats=trace_alpha(padded,-50,0);return d,stats
back=[];fore=[];measure=[]
for f in range(310,335):
 s=np.array(Image.open(P/'source-322-full'/f'{f-308:04d}.png').convert('RGB')).astype(float);g=s.mean(2);neutral=s.max(2)-s.min(2)<9
 dark=(s[600:1080,900:1400].max(2)<70).sum(0)
 indices=np.where(dark>300)[0]
 right=1160
 if len(indices):
  right=900+int(indices.max())-4
 gray_mask=(g[:,:right]>80)&neutral[:,:right];gray_mask[:230]=False;gray=filled_rows(gray_mask)
 white_mask=(g[:,:right]>205)&neutral[:,:right];white_mask[:300]=False;pane=filled_rows(white_mask);top=int(np.where(pane.any(1))[0].min());bottom=1080
 gray_d,gray_stats=outline(gray);pane_d,pane_stats=outline(pane)
 # Empty white column avoids title, grabber and blue sender material.
 colors=[]
 for y in range(1080):
  pixels=s[y,750:850];valid=(pixels.min(1)>235)&(pixels.max(1)-pixels.min(1)<8)
  colors.append(float(np.median(pixels[valid]))if valid.any()else np.nan)
 colors=np.array(colors);valid=np.where(np.isfinite(colors)&(np.arange(1080)>top+8))[0];colors=np.interp(np.arange(1080),valid,colors[valid]);colors=np.clip(ndimage.gaussian_filter1d(colors,2),240,255)
 yy,xx=np.where(pane);x0=0;x1=int(xx.max())+1;y0=int(yy.min());y1=1080;overlay=np.zeros((y1-y0,x1,4),dtype='uint8');overlay[:,:,3]=np.uint8(np.clip((255-colors[y0:y1,None])/255*pane[y0:y1,:x1],0,1)*255+.5);file=A/f'pane-color-only-{f}.png';Image.fromarray(overlay).save(file)
 # Handle is a distinct projected element; its actual contour is native.
 handle_roi=(g[top+8:min(1080,top+80),100:700]>135)&(g[top+8:min(1080,top+80),100:700]<225)&neutral[top+8:min(1080,top+80),100:700];labs,n=ndimage.label(handle_roi);objects=ndimage.find_objects(labs);candidates=[]
 for i,box in enumerate(objects,1):
  if box is None:continue
  sy,sx=box;w=sx.stop-sx.start;h=sy.stop-sy.start
  if w>80 and 3<=h<=28:candidates.append((int((labs[box]==i).sum()),i,box))
 hd='';handle_box=None;handle_color=170
 if candidates:
  _,i,(sy,sx)=max(candidates);hx0=max(0,100+sx.start-3);hx1=min(right,100+sx.stop+3);hy0=max(0,top+8+sy.start-3);hy1=min(1080,top+8+sy.stop+3);patch=g[hy0:hy1,hx0:hx1];handle_color=float(np.percentile(patch,8));alpha=np.clip((colors[hy0:hy1,None]-patch)/np.maximum(1,colors[hy0:hy1,None]-handle_color),0,1);hd,stats=trace_alpha(alpha,hx0,hy0);handle_box=[hx0,hy0,hx1,hy1]
 # Largest bold ink row is the clipped subject, not later recipient fields.
 ty0=max(0,top+180);ty1=min(1080,top+570);tx1=min(1000,right-30);alpha=np.clip((colors[ty0:ty1,None]-g[ty0:ty1,:tx1])/np.maximum(1,colors[ty0:ty1,None]),0,1);alpha[~neutral[ty0:ty1,:tx1]]=0;alpha[alpha<.02]=0;rowmask=(alpha>.18).sum(1)>3;lab,n=ndimage.label(rowmask);areas=np.array([float(alpha[lab==i].sum())for i in range(1,n+1)]);title_d='';title_box=None
 if len(areas):
  selected=areas.argmax()+1;rows=np.where(lab==selected)[0];lo=max(0,int(rows.min())-2);hi=min(len(alpha),int(rows.max())+3);tile=np.pad(alpha[lo:hi],((0,0),(50,0)),mode='edge');title_d,stats=trace_alpha(tile,-50,ty0+lo);title_box=[0,ty0+lo,tx1,ty0+hi]
 sx=value(phone,'scaleX',f/30,1)*value(sheet,'scaleX',f/30,1);sy=value(phone,'scaleY',f/30,1)*value(sheet,'scaleY',f/30,1);tx=value(phone,'x',f/30)+value(phone,'scaleX',f/30,1)*value(sheet,'x',f/30);ty=value(phone,'y',f/30)+value(phone,'scaleY',f/30,1)*value(sheet,'y',f/30)
 base=dict(type='group',x=-tx/sx,y=-ty/sy,scaleX=1/sx,scaleY=1/sy,start=f/30,end=(f+1)/30)
 b=dict(base,id=f'mini-review-mail-background-{f}',children=[dict(id=f'mini-review-mail-gray-{f}',type='path',d=gray_d,fill='#808080'),dict(id=f'mini-review-mail-pane-{f}',type='path',d=pane_d,fill='#ffffff'),dict(id=f'mini-review-mail-color-{f}',type='image',src=str(file),x=x0,y=y0,width=x1-x0,height=y1-y0)])
 nodes=[]
 if hd:nodes.append(dict(id=f'mini-review-mail-handle-{f}',type='path',d=hd,fill='#'+f'{round(handle_color):02x}'*3,semanticText='Mail drag handle'))
 if title_d:nodes.append(dict(id=f'mini-review-mail-subject-{f}',type='path',d=title_d,fill='#000000',semanticText='Dinner This Week (actual clipped visible subject glyphs)',sourceFrame=f))
 back.append(b);fore.append(dict(base,id=f'mini-review-mail-foreground-{f}',children=nodes));measure.append(dict(frame=f,roiRight=right,paneTop=top,titleBox=title_box,handleBox=handle_box,handleGray=handle_color,grayOutline=gray_stats,paneOutline=pane_stats,colorArtwork=str(file)))
 print(f,top,title_box,handle_box,flush=True)
# Gate only the old semantic pieces during the true close-up composition.
gates={}
for identifier in ['p03-52','early-native-continuous-pane-v13','p03-54','early-native-closeup-title-v13']:
 layer=next(l for l in sheet['children']if l['id']==identifier);end=layer.get('end',scene['duration']);gates[identifier]=[dict(t=309/30,value=end,ease='hold'),dict(t=310/30,value=310/30,ease='hold'),dict(t=335/30,value=end,ease='hold')]
spec=dict(parent_id='p03-77',gates=gates,insert_after={'early-native-continuous-pane-v13':back},append=fore,changed_ranges=[[310,334]],provenance=dict(measurements=measure,notice='Native semantic gray/white Mail-pane outlines, handle and actual subject glyphs. Black transparent artwork contains only a generated smooth grayscale UI color correction; no source UI pixels, whole source frame, or video layer. Physical camera/bezel/sender remain unchanged.'))
(REF/'peaks-review-mail-elements.json').write_text(json.dumps(spec,indent=2));(P/'mail-measurements.json').write_text(json.dumps(measure,indent=2));print('MAIL ELEMENTS',len(back))
