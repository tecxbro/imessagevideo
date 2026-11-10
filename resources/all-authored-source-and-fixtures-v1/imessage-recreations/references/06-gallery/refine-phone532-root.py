from pathlib import Path
from PIL import Image
from scipy import ndimage,optimize
import numpy as np,json,sys
REF=Path(__file__).resolve().parent;ROOT=REF.parents[1];sys.path.insert(0,str(ROOT/'references/02-danieltian'));from trace_glyphs import trace_alpha
base=json.load(open(REF/'root-phone532-base.json'));a=np.array(Image.open(REF/'native-transition-v18/000532.png').convert('RGB')).astype(float);hardware=next(p for p in base['parts'] if 'hardware-bounded-' in p['id']);tex=np.array(Image.open(hardware['src']).convert('RGBA'));ys,xs=np.where((tex[:,:,3]>240)&(np.indices(tex.shape[:2])[0]+hardware['y']<1050));step=max(1,len(xs)//3500);xs=xs[::step].astype(float);ys=ys[::step].astype(float);hardware_colors=tex[ys.astype(int),xs.astype(int),:3].astype(float);wx=xs+hardware['x'];wy=ys+hardware['y'];cx=hardware['x']+hardware['width']/2;cy=hardware['y']+hardware['height']/2

def residual(p):
 tx,ty,scale=p;xx=cx+(wx-cx)*scale+tx;yy=cy+(wy-cy)*scale+ty;b=np.stack([ndimage.map_coordinates(a[:,:,c],[yy,xx],order=1,mode='nearest') for c in range(3)],1);return (b-hardware_colors).ravel()
fit=optimize.least_squares(residual,[0,0,1],bounds=([-3,-3,.995],[3,3,1.005]),loss='huber',f_scale=6,max_nfev=35);tx,ty,scale=map(float,fit.x);base['parts'].remove(hardware);hardware=dict(id='root-phone532-hardware-camera',type='group',x=cx+tx-scale*cx,y=cy+ty-scale*cy,scaleX=scale,scaleY=scale,children=[hardware]);base['parts'].append(hardware)
# The corrected first-bubble core is constrained by its observed temporal ROI;
# the old<250 whole-frame mask merged this frame's249 header with the bubble.
rx0,ry0,rx1,ry1=630,380,1140,560;reg=a[ry0:ry1,rx0:rx1];g=reg.mean(2);m=(g>210)&(g<245)&(reg.max(2)-reg.min(2)<15);lab,_=ndimage.label(m,np.ones((3,3)));options=[]
for i,sl in enumerate(ndimage.find_objects(lab)):
 if sl is None:continue
 yy,xx=sl;count=int((lab[sl]==i+1).sum())
 if xx.stop-xx.start>350 and yy.stop-yy.start>60:options.append((count,sl))
_,sl=max(options);yy,xx=sl;x0=max(rx0,rx0+xx.start-3);x1=min(rx1,rx0+xx.stop+3);y0=max(ry0,ry0+yy.start-3);y1=min(ry1,ry0+yy.stop+3);roi=a[y0:y1,x0:x1];gray=roi.mean(2);neut=roi.max(2)-roi.min(2)<15;vals=roi[(gray>210)&(gray<245)&neut].astype('uint8');colors,counts=np.unique(vals,axis=0,return_counts=True);bg=colors[counts.argmax()];inkvals=roi[(gray<150)&neut].astype('uint8');colors,counts=np.unique(inkvals,axis=0,return_counts=True);ink=colors[counts.argmax()];white=float(np.median(a[390:530,1140:1180]));alpha=np.clip((white-gray)/max(1,white-float(bg.mean())),0,1);d,_=trace_alpha(alpha);parts=[dict(id='root-phone532-first-bubble-body',type='path',d=d,x=x0,y=y0,fill='#'+''.join(f'{v:02x}' for v in bg),semanticText="Heads up: Your landlord emailed about the renewal. Rent's going up8%",editability='Native first-bubble silhouette from its proper constrained source ROI.')]
alpha=np.clip((float(bg.mean())-gray)/max(1,float(bg.mean()-ink.mean())),0,1);prev=0;glyphs=[]
for i in range(12):
 d,_=trace_alpha(alpha,threshold=(i+.5)/12)
 if not d:continue
 cumulative=(i+1)/12;op=(cumulative-prev)/max(1-prev,1e-9);prev=cumulative;glyphs.append(dict(id=f'root-phone532-first-bubble-glyph-{i}',type='path',d=d,fill='#'+''.join(f'{v:02x}' for v in ink),opacity=op,semanticText="Heads up: Your landlord emailed about the renewal. Rent's going up8%",editability='Native semantic glyph optical outlines, not live text.'))
parts.append(dict(id='root-phone532-first-bubble-copy',type='group',x=x0,y=y0,children=glyphs))
new=dict(id='root-phone532-pose',type='group',start=532/30,end=533/30,children=[base['body'],*base['parts'],*parts],sourceFrame=532)
spec=dict(scope=[[532,532]],layers=[new],gateChatIDs=['root-rene-hardware-bounded-532','root-rene-gray-0-body-532','root-rene-gray-0-glyph-pose-532'],measurements=dict(hardwareFit=[tx,ty,scale],hardwareFitRMSE=float(np.sqrt(np.mean(residual(fit.x)**2))),firstBubbleBounds=[x0,y0,x1,y1],screenWhite=white,bodyFill=bg.tolist(),inkFill=ink.tolist()),notice='Single-frame detector outlier: near-white249 header was merged with first gray bubble, yielding false383px height and parentY−724. Valid531/533 header camera/boxes agree. Reuse bounded531 control material at the observed pose; independently register genuine hardware; rebuild only first bubble from constrained532 ROI. Every other532 message and every outside frame preserved.')
(REF/'root-phone532-patch.json').write_text(json.dumps(spec,indent=2));print(spec['measurements'])
