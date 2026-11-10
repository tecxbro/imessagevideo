"""Native high-resolution original blue glyphs and independently fitted projection."""
from pathlib import Path
import json,sys,io,re
import numpy as np
from PIL import Image
from scipy import optimize
import cairosvg
P=Path(__file__).parent;B=P/'wall-v6-measure';sys.path.insert(0,str(P.parent/'02-danieltian'));from trace_glyphs import trace_alpha
fits={x['frame']:x for x in json.loads((B/'free-camera-fit.json').read_text())['measurements']}
def alpha_blue(im):
 a=np.asarray(im.convert('RGB')).astype(float);delta=np.maximum(0,a[:,:,2]-a[:,:,0]);raw=(delta>20)&(a[:,:,2]-a[:,:,1]>5)&(a[:,:,0]<235);ys,xs=np.where(raw);lo,hi=int(ys.min()),int(ys.max());row=[];pos=[]
 for y in range(lo+5,hi-4):
  q=delta[y][raw[y]]
  if len(q)>10:pos.append(y);row.append(float(np.percentile(q,90)))
 poly=np.polyfit(pos,row,2);core=np.maximum(30,np.polyval(poly,np.arange(a.shape[0])));alpha=np.clip(delta/core[:,None],0,1);alpha[:max(0,lo-2)]=0;alpha[hi+3:]=0;return alpha,raw,(int(xs.min()),lo,int(xs.max()+1),hi+1),a
parts=[];palette=[]
for f,last in [(246,False),(247,True)]:
 im=Image.open(B/'free'/f'{f-239:03d}.png');alpha,mask,box,rgb=alpha_blue(im);q=fits[f];xs=np.arange(1920);native=(xs-q['x'])/q['scaleX'];alpha[:,native<897 if last else native>=897]=0;yy,xx=np.where(alpha>.05);b=(max(0,int(xx.min())-2),max(0,int(yy.min())-2),min(1920,int(xx.max())+3),min(1080,int(yy.max())+3));d,stats=trace_alpha(alpha[b[1]:b[3],b[0]:b[2]],b[0],b[1]);xy=np.array([float(v)for v in re.findall(r'-?\d+(?:\.\d+)?',d)]).reshape(-1,2);xy[:,0]=(xy[:,0]-q['x'])/q['scaleX'];xy[:,1]=(xy[:,1]-q['y'])/q['scaleY'];it=iter(xy.ravel());canonical=re.sub(r'-?\d+(?:\.\d+)?',lambda m:f'{next(it):.5f}',d);parts.append(canonical)
 for frac in np.linspace(.05,.95,10):
  y=round(box[1]+frac*(box[3]-box[1]));sel=alpha[y]>.95
  if sel.any():palette.append((frac,np.median(rgb[y,sel],axis=0).tolist()))
blue=' '.join(parts);xy=np.array([float(v)for v in re.findall(r'-?\d+(?:\.\d+)?',blue)]).reshape(-1,2);xmin,ymin=xy.min(0);xmax,ymax=xy.max(0);xc=(xmin+xmax)/2;yc=(ymin+ymax)/2;x0=xmin-2;y0=ymin-2;w=xmax-xmin+4;h=ymax-ymin+4;aa=8;raw=cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(np.ceil(w*aa))}" height="{int(np.ceil(h*aa))}" viewBox="{x0} {y0} {w} {h}"><path d="{blue}" fill="black"/></svg>'.encode());template=np.array(Image.open(io.BytesIO(raw)).convert('RGBA').getchannel('A')).astype(float)/255;txscale=template.shape[1]/w;tyscale=template.shape[0]/h;out=[]
from scipy import ndimage
for f,q in fits.items():
 alpha,mask,box,_=alpha_blue(Image.open(B/'free'/f'{f-239:03d}.png'));x1,y1,x2,y2=box;roi=(max(0,x1-8),max(0,y1-8),min(1920,x2+8),min(1080,y2+8));rx1,ry1,rx2,ry2=roi;factor=1 if q['scaleX']<2 else 2 if q['scaleX']<10 else 4;target=np.array(Image.fromarray((alpha[ry1:ry2,rx1:rx2]*255).astype('uint8')).resize((max(1,(rx2-rx1)//factor),max(1,(ry2-ry1)//factor)),Image.Resampling.BOX)).astype(float)/255;yy,xx=np.mgrid[:target.shape[0],:target.shape[1]];gx=rx1+(xx+.5)*(rx2-rx1)/target.shape[1];gy=ry1+(yy+.5)*(ry2-ry1)/target.shape[0];initial=[q['scaleX'],q['scaleY'],q['x']+xc*q['scaleX'],q['y']+yc*q['scaleY']]
 def residual(z):
  sx,sy,cx,cy=z;px=((gx-cx)/sx+xc-x0)*txscale-.5;py=((gy-cy)/sy+yc-y0)*tyscale-.5;return (ndimage.map_coordinates(template,[py,px],order=1,mode='constant',cval=0)-target).ravel()
 sx,sy,cx,cy=initial;fit=optimize.least_squares(residual,initial,bounds=([sx*.9,sy*.9,cx-150,cy-150],[sx*1.1,sy*1.1,cx+150,cy+150]),max_nfev=80,x_scale='jac');sx,sy,cx,cy=fit.x;rec={'frame':f,'scaleX':float(sx),'scaleY':float(sy),'x':float(cx-xc*sx),'y':float(cy-yc*sy),'mask_mae':float(abs(residual(fit.x)).mean())};out.append(rec);print(rec,flush=True)
stops=[]
for frac in [0,.25,.5,.75,1]:
 samples=[c for y,c in palette if abs(y-frac)<.2];color=np.median(samples,axis=0);stops.append({'offset':f'{frac*100:g}%','color':'#'+''.join(f'{int(np.clip(round(c),0,255)):02x}'for c in color)})
(B/'free-blue-vector.json').write_text(json.dumps({'d':blue,'measurements':out,'gradient':{'id':'measured-free-gradient-v6','type':'linear','x1':'0%','y1':'0%','x2':'0%','y2':'100%','stops':stops},'provenance':{'source_frames':[246,247],'scope':'Original blue glyph outlines, higher-resolution final e from247. Sampled native gradient; fine original grain is approximated by the gradient, not a fullframe bitmap.','native_bounds':[xmin,ymin,xmax,ymax]}},indent=2)+'\n')
