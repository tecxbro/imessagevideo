from pathlib import Path
from PIL import Image
import numpy as np,json,sys
from scipy.signal import find_peaks
sys.path.insert(0,'/tmp/imessage-food-cv');import cv2
R=Path(__file__).resolve().parent;ROOT=R.parents[2];SRC=R.parent/'assets/middle-every-frame';asset=ROOT/'outputs/02-danieltian/final-v18/assets/c5968c7a63d20083211360f8af2a8a2ea732595908c62ab0a129f917f4ecbcaf.png';raw=np.array(Image.open(asset).convert('RGBA')).astype(np.float32);K=(253-raw[:,:,:3])*raw[:,:,3:]/255;Kgray=K.mean(2);rows=[]
for n in range(660,711):
 a=np.array(Image.open(SRC/f'source-{n:04}.png').convert('RGB')).astype(np.float32);S=253-a[:,240:420];gray=S.mean(2);corr=cv2.matchTemplate(gray,Kgray,cv2.TM_CCORR_NORMED);corr[~np.isfinite(corr)]=0;vertical=corr.max(axis=1);idx,_=find_peaks(vertical,height=.75,distance=110,prominence=.05);opts=[]
 for y in idx:
  x=int(np.argmax(corr[y]));part=S[y:y+K.shape[0],x:x+K.shape[1]];alpha=float(np.sum(K*part)/np.sum(K*K));mae=float(abs(part-alpha*K).mean());opts.append(dict(x=x+240,y=int(y),width=K.shape[1],height=K.shape[0],alpha=alpha,ncc=float(corr[y,x]),mae=mae))
 rows.append(dict(frame=n,avatars=opts));print(n,[(q['x'],q['y'],round(q['alpha'],3),round(q['ncc'],4)) for q in opts])
(R/'audit-660-710.json').write_text(json.dumps(dict(asset=str(asset),method='Read-only original-art normalized contrast correlation in x240:420 full-stage strip. No moving y search window. Alpha is a diagnostic linear RGB contrast fit at integer template size/position; final subpixel/scale fit follows. Peaks require NCC>.75 and110px separation. Missing peaks below threshold do not establish absence.',frames=rows),indent=2))
