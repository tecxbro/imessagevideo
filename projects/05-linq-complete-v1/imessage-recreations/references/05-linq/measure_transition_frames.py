"""Native source analysis cache. These frames are NEVER recreation layers."""
from pathlib import Path
import subprocess,json,numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label,find_objects
D=Path(__file__).resolve().parent;O=D/'measurements/native-transition';O.mkdir(parents=True,exist_ok=True)
features=[]
def bbox(mask,mincount=20):
 y,x=np.nonzero(mask)
 return None if len(x)<mincount else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
def components(mask,minarea=100):
 labels,n=label(mask);out=[]
 for sl in find_objects(labels):
  if sl is None:continue
  y,x=sl
  if (y.stop-y.start)*(x.stop-x.start)>=minarea:out.append([int(x.start),int(y.start),int(x.stop),int(y.stop)])
 return out
for start,end in [(99,471),(705,1150)]:
 p=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-ss',str(start/30),'-i',str(D/'source.mp4'),'-t',str((end-start+1)/30),'-f','rawvideo','-pix_fmt','rgb24','-threads','1','pipe:1'],stdout=subprocess.PIPE)
 for f in range(start,end+1):
  raw=p.stdout.read(960*720*3)
  if len(raw)!=960*720*3:raise RuntimeError('Short native analysis decode')
  a=np.frombuffer(raw,np.uint8).reshape(720,960,3);z=a.astype(np.int16)
  Image.fromarray(a).save(O/f'{f:06}.png',compress_level=1)
  row={'frame':f}
  blue=(z[:,:,2]-z[:,:,0]>35)&(z[:,:,2]-z[:,:,1]>15)&(z[:,:,1]>70)
  row['blue']=components(blue,500)
  neutral=(z.max(axis=2)-z.min(axis=2)<9)
  gray=neutral&(z.mean(axis=2)>195)&(z.mean(axis=2)<249);row['gray']=components(gray,5000)
  dark=neutral&(z.max(axis=2)<80);row['dark']=components(dark,10000)
  if 205<=f<=270:
   m=z.min(axis=2)<250;m[200:]=False;cc=np.where(m.sum(axis=0)>20)[0];rr=np.where(m.sum(axis=1)>20)[0];row['board_top_bounds']=None if not len(cc) or not len(rr) else [int(cc.min()),int(rr.min()),int(cc.max()+1),int(rr.max()+1)]
  if 840<=f<=946:
   yellow=(z[:,:,0]-z[:,:,1]>7)&(z[:,:,1]-z[:,:,2]>8);yellow[110:620]=False;xx=np.where(yellow.sum(axis=0)>80)[0];row['chess_panel_xbounds']=None if not len(xx) else [int(xx.min()),int(xx.max()+1)]
  if 1050<=f<=1150:
   colorful=(z.max(axis=2)-z.min(axis=2)>30)&(z.min(axis=2)<220);colorful[:,:190]=False;colorful[:,774:]=False;rr=np.where(colorful.sum(axis=1)>150)[0];row['restaurant_photo_y']=None if not len(rr) else [int(rr.min()),int(rr.max()+1)]
  features.append(row)
 p.wait();assert p.returncode==0
(D/'measurements/transition-features.json').write_text(json.dumps(features,indent=2))
for name,start,end,stride in [('first-chess-flight',195,270,3),('flight-reply',312,356,3),('fare-seat',405,469,3),('cash',705,866,6),('old-chess-exit',930,945,1),('foodash',990,1074,6),('restaurant',1059,1149,3)]:
 fs=list(range(start,end+1,stride));sheet=Image.new('RGB',(320*4,260*((len(fs)+3)//4)),'#ddd')
 for i,f in enumerate(fs):
  p=O/f'{f:06}.png'
  if not p.exists():continue
  im=Image.open(p).convert('RGB').resize((320,240));sheet.paste(im,(i%4*320,i//4*260+20));ImageDraw.Draw(sheet).text((i%4*320,i//4*260),f'{f/30:.4f} [{f}]',fill='black')
 sheet.save(D/'measurements'/f'{name}-source.jpg')
print('Analysis-only native cache and feature records complete',len(features))
