"""Fit early native camera to original hardware pixels; never uses source frames as output."""
from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage,optimize,signal
P=Path(__file__).parent;B=P/'early-v13-measure';sys.path.insert(0,str(P.parents[1]/'engines'));from render_pillow import state
scene=json.loads((P/'final-v12.scene.json').read_text());phone=next(l for l in scene['layers'] if l['id']=='p03-86')
robot=Image.open(P/'assets/robot.png').convert('L')
a=np.array(Image.open(P/'assets/phone-hardware.png').convert('RGBA')).astype(float);hh,ww=a.shape[:2];yy,xx=np.mgrid[:hh,:ww];mask=(a[:,:,3]>245)&(a[:,:,:3].mean(2)<180)&((xx<22)|(xx>ww-23)|(yy<24)|(yy>hh-24));y,x=np.where(mask);step=max(1,len(x)//4000);x=x[::step]*800/ww;y=y[::step]*1658/hh;v=a[np.where(mask)[0][::step],np.where(mask)[1][::step],:3].mean(1)
def components(im):
 a=np.array(im);blue=(a[:,:,2]>180)&(a[:,:,2]-a[:,:,0].astype(float)>60)&(a[:,:,1]>70)&(a[:,:,2]-a[:,:,1].astype(float)>10);labels,n=ndimage.label(blue);result=[]
 for i,sl in enumerate(ndimage.find_objects(labels),1):
  if sl is None:continue
  y,x=sl;w=x.stop-x.start;h=y.stop-y.start;area=(labels[sl]==i).sum()
  if area>25:result.append(dict(x=x.start*2,y=y.start*2,w=w*2,h=h*2,ratio=w/h,area=int(area),fill=float(area/(w*h))))
 return result

def fit(f):
 im=Image.open(B/'source'/f'{f-48:04d}.png').convert('RGB');rgb=np.array(im).astype(float);gray=rgb.mean(2);s=state(phone,f/30);sx=s['scaleX'];sy=s['scaleY'];tx=s['x'];ty=s['y'];blues=components(im)
 # Outer bezel is the left/rightmost dark pixel on long stretches of rows.
 dark=gray<75;first=np.argmax(dark,axis=1);last=gray.shape[1]-1-np.argmax(dark[:,::-1],axis=1);valid=dark.any(1)
 left=int(np.bincount(first[valid]).argmax())*2;right=int(np.bincount(last[valid]).argmax())*2
 circles=[b for b in blues if .85<b['ratio']<1.15 and b['fill']>.55 and b['w']>22]
 if circles and f>=210:
  c=max(circles,key=lambda b:b['area']);sx=sy=c['w']/78;tx=c['x']+c['w']/2-697*sx;ty=c['y']+c['h']/2-271*sy
 elif left>0 and right<1918 and right-left>250:
  sx=sy=(right-left)/768;tx=left-16*sx
 # Source first transition starts with an extreme header close-up and zooms out.
 if f<78:
  sx=sy=max(.95,(right-left)/768);tx=left-16*sx
  # Island lower edge is a strong local y anchor when visible.
  center=gray[:,430:530]<65;rows=np.where(center.mean(1)>.6)[0]
  if len(rows):ty=(rows[-1]+1)*2-121*sy
 anchors=[]
 if left>0 and right<1918 and right-left>250 and not (306<=f<=337):anchors+=[('left',left),('right',right)]
 # Use the actual island bottom when it is disconnected from the outer bezel.
 if f<=110:
  labels,n=ndimage.label(dark);islands=[]
  for i,sl in enumerate(ndimage.find_objects(labels),1):
   if sl is None:continue
   yy,xx=sl;w=2*(xx.stop-xx.start);h=2*(yy.stop-yy.start);cx=xx.start+xx.stop;area=(labels[sl]==i).sum();fill=area/((w/2)*(h/2))
   if abs(cx-960)<90 and w>80 and h<280 and fill>.65 and .65*230*sx<w<1.3*230*sx:islands.append((abs(w-230*sx),2*yy.stop))
  if islands:
   bottom=min(islands)[1];ty=bottom-121*sx;anchors.append(('island',bottom))
 elif f<=210:
  bubble=[b for b in blues if 3.5<b['ratio']<5.5 and b['w']>150]
  if bubble:
   top=max(bubble,key=lambda b:b['area'])['y'];ty=top-393*sx;anchors.append(('bubble',top))
 elif f<=305:
  # Normalized correlation preserves the robot shape through modal dimming.
  w=max(10,round(110*sx/2));T=np.array(robot.resize((w,w)),dtype=float);T-=T.mean();cx=round((tx+401*sx)/2);x0=max(0,cx-w);x1=min(960,cx+w);I=gray[:min(300,540),x0:x1]
  if I.shape[1]>=w:
   ones=np.ones(T.shape);num=signal.fftconvolve(I,T[::-1,::-1],mode='valid');su=signal.fftconvolve(I,ones,mode='valid');sq=signal.fftconvolve(I*I,ones,mode='valid');den=np.sqrt(np.maximum(1e-9,(sq-su*su/T.size)*np.sum(T*T)));corr=num/den;iy,ix=np.unravel_index(np.argmax(corr),corr.shape)
   if corr[iy,ix]>.65:ty=2*iy-160*sx;anchors.append(('robot',2*iy))
 elif f<=337:
  minimum=float(np.where(dark)[0].min()*2);ty=minimum-12*sx;anchors.append(('top',minimum))
 def residual(q):
  scale,tx,ty=q;xp=(tx+scale*x)/2;yp=(ty+scale*y)/2;inside=(xp>=2)&(xp<958)&(yp>=2)&(yp<538)
  sampled=ndimage.map_coordinates(gray,[yp,xp],order=1,mode='nearest');r=(sampled-v);r[~inside]=0;r*=np.sqrt(len(v)/max(150,inside.sum()))
  extra=[]
  for kind,value in anchors:
   predicted={'left':tx+16*scale,'right':tx+784*scale,'island':ty+121*scale,'bubble':ty+393*scale,'robot':ty+160*scale,'top':ty+12*scale}[kind]
   extra.extend([3*(predicted-value)]*100)
  return np.r_[r,extra]
 q0=np.array([sx,tx,ty]);bounds=([max(.4,sx*.65),tx-400,ty-500],[min(8,sx*1.5),tx+400,ty+500])
 r=optimize.least_squares(residual,q0,bounds=bounds,loss='soft_l1',f_scale=15,diff_step=[.002,.002,.002],max_nfev=120)
 q=r.x;return dict(frame=f,scale=float(q[0]),x=float(q[1]),y=float(q[2]),cost=float(np.mean(np.abs(residual(q)))),initial=q0.tolist(),old=[s['scaleX'],s['x'],s['y']],left=left,right=right,blues=blues,anchors=[(k,float(v)) for k,v in anchors])
if __name__=='__main__':
 fs=list(range(59,414)) if '--all' in sys.argv else [int(v) for v in sys.argv[1:]] or [59,83,98,150,159,177,195,205,220,300,311,320,334,350,358,370,390,413]
 out=[]
 for f in fs:
  r=fit(f);out.append(r);print(json.dumps({k:v for k,v in r.items() if k not in ('blues',)}),flush=True) if '--all' not in sys.argv or f%30==0 else None
 (B/('camera-fit-all.json' if '--all' in sys.argv else 'camera-fit-selected.json')).write_text(json.dumps(out,indent=2)+'\n')
 if '--all' in sys.argv:sys.exit(0)
 contact=Image.new('RGB',(960*3,570*((len(fs)+2)//3)),'#ddd')
 for i,r in enumerate(out):
  im=Image.open(B/'source'/f"{r['frame']-48:04d}.png").convert('RGB');d=ImageDraw.Draw(im);x,y,s=r['x']/2,r['y']/2,r['scale']/2;d.rectangle((x,y,x+800*s,y+1658*s),outline='lime',width=2);contact.paste(im,((i%3)*960,(i//3)*570+30));ImageDraw.Draw(contact).text(((i%3)*960+8,(i//3)*570+8),str(r['frame'])+' '+str([round(r[k],2)for k in ['scale','x','y','cost']]),fill='black')
 contact.resize((1440,round(contact.height/2))).save(B/'camera-fit-selected.jpg')
