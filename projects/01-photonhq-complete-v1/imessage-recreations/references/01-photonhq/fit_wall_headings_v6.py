"""Fit source caption word projections; preserve native paths and hard edits."""
from pathlib import Path
import json,re,io,argparse
import numpy as np
from PIL import Image
from scipy import optimize,ndimage
import cairosvg
P=Path(__file__).parent;B=P/'wall-v6-measure';scene=json.load(open(P.parents[1]/'outputs/01-photonhq/final-v5/scene.json'));layers={p:[l for l in scene['layers'] if l['id'].startswith('source-heading-word-'+p+'-')]for p in ['calls','imessage','whatsapp','telegram']};out={};templates={}
for phase,ls in layers.items():
 for l in ls:
  xy=np.asarray(list(map(float,re.findall(r'-?\d+(?:\.\d+)?',l['d'])))).reshape(-1,2);x0,y0=xy.min(0)-2;x1,y1=xy.max(0)+2;w=x1-x0;h=y1-y0;aa=4;raw=cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(w*aa)}" height="{int(h*aa)}" viewBox="{x0} {y0} {w} {h}"><path d="{l["d"]}" fill="black"/></svg>'.encode());a=np.asarray(Image.open(io.BytesIO(raw)).getchannel('A')).astype(float)/255;templates[l['id']]=(a,x0,y0,w,h,xy.min(0),xy.max(0));out[l['id']]={k:[]for k in ['x','y','scaleX','scaleY']}
parser=argparse.ArgumentParser();parser.add_argument('--start',type=int,default=336);parser.add_argument('--end',type=int,default=464);args=parser.parse_args()
if args.start>336 or args.end<464:
 old=json.load(open(B/'caption-projection-fits.json'))
 for id,props in old.items():
  for k,keys in props.items():out[id][k]=[q for q in keys if not args.start<=round(q['t']*30)<=args.end]
for f in range(args.start,args.end+1):
 phase='calls' if f<355 else 'imessage' if f<390 else 'whatsapp' if f<425 else 'telegram';ls=layers[phase];q=B/('wall'if f<391 else'wall-late')/f'{f-(335 if f<391 else 390):03d}.png';a=np.asarray(Image.open(q).convert('RGB')).astype(float);top=350 if f>=450 else 450;mask=np.mean(a[top:640],axis=2)<140;lab,n=ndimage.label(mask);spans=ndimage.find_objects(lab);ysbig=[sl[0]for sl in spans if sl is not None and sl[0].stop-sl[0].start>35 and sl[1].stop-sl[1].start>2];band=np.zeros_like(mask);band[min(y.start for y in ysbig):max(y.stop for y in ysbig)]=True;mask &= band;cols=np.where(mask.any(0))[0];cols=cols[(cols>350)&(cols<1570)];gaps=np.diff(cols);cuts=np.sort(np.argsort(gaps)[-(len(ls)-1):]+1);groups=np.split(cols,cuts)
 for l,xs in zip(ls,groups):
  xlo,xhi=int(xs.min()),int(xs.max()+1);ys=np.where(mask[:,xlo:xhi].any(1))[0];ylo,yhi=int(ys.min()+top),int(ys.max()+top+1);rx0=max(0,xlo-4);rx1=min(1920,xhi+4);ry0=max(0,ylo-4);ry1=min(1080,yhi+4);target=np.clip((253-a[ry0:ry1,rx0:rx1].mean(2))/253,0,1);yy,xx=np.mgrid[:target.shape[0],:target.shape[1]];gx=rx0+xx+.5;gy=ry0+yy+.5;tpl,x0,y0,w,h,mn,mx=templates[l['id']];sx=(xhi-xlo)/(mx[0]-mn[0]);sy=(yhi-ylo)/(mx[1]-mn[1]);cx=(xlo+xhi)/2;cy=(ylo+yhi)/2;xc=(mn[0]+mx[0])/2;yc=(mn[1]+mx[1])/2
  def residual(z):
   sx,sy,cx,cy=z;px=((gx-cx)/sx+xc-x0)*tpl.shape[1]/w-.5;py=((gy-cy)/sy+yc-y0)*tpl.shape[0]/h-.5;return (ndimage.map_coordinates(tpl,[py,px],order=1,mode='constant',cval=0)-target).ravel()
  fit=optimize.least_squares(residual,[sx,sy,cx,cy],bounds=([sx*.94,sy*.94,cx-8,cy-8],[sx*1.06,sy*1.06,cx+8,cy+8]),max_nfev=25,x_scale='jac');sx,sy,cx,cy=fit.x
  for k,v in [('scaleX',sx),('scaleY',sy),('x',cx-xc*sx),('y',cy-yc*sy)]:out[l['id']][k].append({'t':f/30,'value':float(v),'ease':'linear'})
 print(f,phase,flush=True)
for props in out.values():
 for keys in props.values():keys.sort(key=lambda q:q['t'])
(B/'caption-projection-fits.json').write_text(json.dumps(out,indent=2)+'\n')
