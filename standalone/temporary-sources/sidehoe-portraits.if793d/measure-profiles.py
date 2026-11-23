from pathlib import Path
from PIL import Image
from scipy.ndimage import label,binary_closing,binary_fill_holes,binary_dilation,distance_transform_edt
from scipy.optimize import least_squares
import numpy as np,json,sys
p=Path(__file__).parent
root=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
cfg=p/'project/scene.json'
j=json.loads(cfg.read_text())
data={}
for f in range(271,287):
 a=np.asarray(Image.open(root/f'{f:06}.png').convert('RGB'),dtype=np.int16)
 chars=[]
 for n in range(3):
  x,ysz=235+n*275+max(0,(f-282))*9,271
  lo,hi=max(0,round(x-136)),min(1000,round(x+146))
  region=a[ysz:565,lo:hi]
  H,W=region.shape[:2]
  R,G,B=np.moveaxis(region,2,0)
  color_mask=[(G>R+16)&(G>B+10)&(G>192), (R>G+16)&(B>G+11)&(R>214),
                  (R>B+28)&(G>B+8)&(G>174)&(R>217)][n]
  labeled,_=label(binary_closing(color_mask,iterations=2))
  weights=np.bincount(labeled.ravel());weights[0]=0
  if not np.max(weights):
   raise ValueError((f,n,'bad color mask'))
  disk=binary_fill_holes(labeled==weights.argmax())
  yy,xx=np.where(disk)
  get=lambda k:np.percentile(k,[.15,99.85])
  lx,rx=get(xx+.5+lo); ty,by=get(yy+.5+ysz)
  pix=np.array([xx+.5+lo,yy+.5+ysz]).T
  rimpt=[]
  cx0,cy0=(lx+rx)/2,(ty+by)/2
  angles=np.floor((np.arctan2(yy+.5+ysz-cy0,xx+.5+lo-cx0)+np.pi)/(2*np.pi)*90).astype(int).clip(0,89)
  radii=np.hypot(xx+.5+lo-cx0,yy+.5+ysz-cy0)
  for angle in range(90):
   px=np.flatnonzero(angles==angle)
   if px.size:rimpt.append(pix[px[radii[px].argmax()]])
  rim=np.array(rimpt)
  def err(values):
   cx,cy,rx,ry=values
   return (np.hypot((rim[:,0]-cx)/rx,(rim[:,1]-cy)/ry)-1)*max(1,ry)
  init=[cx0,cy0,(rx-lx)/2,(by-ty)/2]
  u=np.array([13,13,27,24])
  sol=least_squares(err,init,bounds=(init-u,init+u),loss='soft_l1',f_scale=1.8,max_nfev=65)
  cx,cy,rx,ry=sol.x; rx+=.5;ry+=.5
  center=np.array([cx,cy])
  px,py=np.meshgrid(np.arange(lo,hi)+.5,np.arange(ysz,565)+.5)
  distance=np.hypot((px-cx)/rx,(py-cy)/ry)
  ys=np.arange(ysz,565)+.5
  observed_gradient=[]; ramp=[]
  for dy in (.06,.14,.25,.37,.52,.66,.78,.88,.95):
   iy=cy+(dy-.5)*2*ry
   visible=(color_mask&(distance>.76)&(distance<.92)&(np.abs(py-iy)<7))
   vals=region[visible]
   if len(vals)<22:continue
   observed_gradient.append(dy)
   ramp.append(np.percentile(vals,60,axis=0))
  ycoord=np.clip((ys-(cy-ry))/(2*ry),0,1)
  rgb=np.array([np.interp(ycoord,observed_gradient,v) for v in np.array(ramp).T]).T
  ramp_rgb=np.array(ramp)
  # Infer the same nine stops for every shot frame before exporting the controls.
  stops=np.arange(0,1.01,.125)
  curve=np.array([np.interp(stops,observed_gradient,v) for v in ramp_rgb.T]).T
  head_filter=(distance<.94)&(np.max(np.abs(region-rgb[:,None,:]),axis=2)>35)&(region.min(axis=2)<185)
  parts,_=label(binary_closing(head_filter,iterations=3))
  scores=np.bincount(parts.ravel());scores[0]=0
  head=binary_fill_holes(parts==scores.argmax())
  bigger=binary_dilation(head,iterations=3)&(distance<.97)&(np.max(np.abs(region-rgb[:,None,:]),axis=2)>13)
  xx0=px[bigger];yy0=py[bigger]
  outline=[np.percentile(xx0,1)-2.2,np.percentile(yy0,.4)-1.0,np.percentile(xx0,99.8)+2.4,np.percentile(yy0,99.7)+2.2]
  end=cy+ry
  sx,ex=map(lambda k:max(0,min(1000,round(k))),(cx-130,cx+130))
  top,bot=map(round,(end+10,end+80))
  names=a[top:bot,sx:ex]
  mask=(names.mean(axis=2)<146)&(np.ptp(names,axis=2)<38)
  v,u0=np.where(mask)
  text_box=[sx+u0.min()-.5,top+v.min()-.4,u0.max()-u0.min()+2,v.max()-v.min()+1.7]
  ty=round(text_box[1]+text_box[3]+5)
  patch=a[ty:ty+81,sx:ex]
  r,g,b=np.moveaxis(patch,2,0)
  family=((g>r+9)&(g>b+7)&(g>207), (r>g+9)&(b>g+8)&(r>220),
    (r>b+12)&(g>b+8)&(r>235))[n]
  yy,xx=np.where(family)
  bar=np.array([sx+xx.min(),ty+yy.min(),sx+xx.max()+1,ty+yy.max()+1],float)
  l,y,r,b=map(int,bar)
  band=a[y:b,l:r]
  body=np.median(band.reshape(-1,3),axis=0).astype(int).tolist()
  tx0=round(l+.231*(r-l));tx1=round(r-(r-l)*.104)
  ty0=round(y+.13*(b-y));ty1=round(b-.12*(b-y))
  text=a[ty0:ty1,tx0:tx1]
  if not text.size: raise ValueError((f,n,bar))
  rank=((text.mean(axis=2)<221)&(np.ptp(text,axis=2)>35))|(text.mean(axis=2)<161)
  u,yq=np.where(rank)
  size=[tx0+yq.min()-.3,ty0+u.min()-.3,yq.max()-yq.min()+1.5,u.max()-u.min()+1.5] if len(u) else [
         l+(r-l)*.31,y+(b-y)*.24,(r-l)*.57,(b-y)*.45]
  glyph_zone=a[ty0:ty1,l+12:min(tx0+11,r)]
  gy,gx=np.where((glyph_zone.mean(axis=2)<198)&(np.ptp(glyph_zone,axis=2)>17))
  glyph=[l+12+int(gx.min())-1,ty0+int(gy.min())-1,int(gx.max()-gx.min()+3),int(gy.max()-gy.min()+3)] if len(gy) else [l+25,y+9,26,29]
  characters=[cx,cy,2*rx,2*ry]
  chars.append(dict(oval=np.round(characters,3).tolist(),tone=np.round(curve).astype(int).tolist(),
    head=np.round(outline,3).tolist(),name=np.round(text_box,3).tolist(),chip=bar.tolist(),chipColor=body,
    text=np.round(size,3).tolist(),glyph=glyph))
 if f in (271,275,281,284,286):
  print(f,chars)
 data[str(f)]=chars
j['profileRegistrations']=data
cfg.write_text(json.dumps(j,indent=2)+'\n')
