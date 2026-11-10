"""Recover actual final free-title camera from an isolated native f outline."""
from pathlib import Path
import json,re,sys,io
import numpy as np
from PIL import Image
from scipy import ndimage,optimize
import cairosvg
P=Path(__file__).parent;B=P/'wall-v6-measure';s=json.loads((P.parents[1]/'outputs/01-photonhq/final-v5/scene.json').read_text());group=next(l for l in s['layers'] if l['id']=='group-27');d=next(l for l in group['children'] if l['type']=='path')['d'];contours=[]
for part in re.split(r'(?=M)',d):
 xy=np.array([float(v)for v in re.findall(r'-?\d+(?:\.\d+)?',part)]).reshape(-1,2) if part.strip() else np.zeros((0,2))
 if len(xy) and xy[:,0].min()>960 and xy[:,0].max()<1010 and xy[:,1].max()>560:contours.append(part)
assert contours;path=' '.join(contours);points=np.array([float(v)for v in re.findall(r'-?\d+(?:\.\d+)?',path)]).reshape(-1,2);xmin,ymin=points.min(0);xmax,ymax=points.max(0);xc=(xmin+xmax)/2;yc=(ymin+ymax)/2;aa=16;x0=xmin-2;y0=ymin-2;w=xmax-xmin+4;h=ymax-ymin+4;raw=cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(np.ceil(w*aa))}" height="{int(np.ceil(h*aa))}" viewBox="{x0} {y0} {w} {h}"><path d="{path}" fill="black"/></svg>'.encode());template=np.array(Image.open(io.BytesIO(raw)).convert('RGBA').getchannel('A')).astype(float)/255;txscale=template.shape[1]/w;tyscale=template.shape[0]/h;out=[]
sys.path.insert(0,str(P.parents[1]/'engines'));from render_pillow import state
for frame in range(240,249):
 im=Image.open(B/'free'/f'{frame-239:03d}.png').convert('RGB');gray=np.array(im).mean(2);labels,n=ndimage.label(gray<80);old=state(group,frame/30);predx=old['x']+old['scaleX']*xc;candidates=[]
 for i,sl in enumerate(ndimage.find_objects(labels),1):
  if sl is None:continue
  y,x=sl;ww=x.stop-x.start;hh=y.stop-y.start
  if ww>8 and hh>40:candidates.append((abs((x.start+x.stop)/2-predx),i,(x.start,y.start,x.stop,y.stop)))
 _,label,box=min(candidates);x1,y1,x2,y2=box;sx=(x2-x1)/(xmax-xmin);sy=(y2-y1)/(ymax-ymin) if y1>0 and y2<1080 else sx;cx=(x1+x2)/2;cy=y2-(ymax-yc)*sy;pad=max(8,round(sx*2));roi=(max(0,x1-pad),max(0,y1-pad),min(1920,x2+pad),min(1080,y2+pad));mask=ndimage.binary_dilation(labels==label,iterations=3);alpha=np.clip((253-gray)/253,0,1)*mask;rx1,ry1,rx2,ry2=roi;factor=1 if sx<4 else 2 if sx<10 else 4;target=np.array(Image.fromarray((alpha[ry1:ry2,rx1:rx2]*255).astype('uint8')).resize((max(1,(rx2-rx1)//factor),max(1,(ry2-ry1)//factor)),Image.Resampling.BOX)).astype(float)/255;yy,xx=np.mgrid[:target.shape[0],:target.shape[1]];gx=rx1+(xx+.5)*(rx2-rx1)/target.shape[1];gy=ry1+(yy+.5)*(ry2-ry1)/target.shape[0]
 def residual(q):
  ssx,ssy,ccx,ccy=q;px=((gx-ccx)/ssx+xc-x0)*txscale-.5;py=((gy-ccy)/ssy+yc-y0)*tyscale-.5;return (ndimage.map_coordinates(template,[py,px],order=1,mode='constant',cval=0)-target).ravel()
 initial=[sx,sy,cx,cy];result=optimize.least_squares(residual,initial,bounds=([sx*.6,sy*.6,cx-180,cy-300],[sx*1.5,sy*1.5,cx+180,cy+300]),x_scale='jac',max_nfev=100,ftol=1e-8,xtol=1e-8);sx,sy,cx,cy=result.x;rec={'frame':frame,'scaleX':float(sx),'scaleY':float(sy),'x':float(cx-xc*sx),'y':float(cy-yc*sy),'glyph_mask_mae':float(abs(residual(result.x)).mean()),'source_f_bounds':list(map(int,box))};out.append(rec);print(rec,flush=True)
(B/'free-camera-fit.json').write_text(json.dumps({'reference_glyph_bounds':[xmin,ymin,xmax,ymax],'measurements':out,'diagnosis':'Final10x zoom was a sparse extrapolation. Fit original isolated black f geometry to actual source masks, independently solvingx/y/scales and preserving black native glyphs.'},indent=2)+'\n')
