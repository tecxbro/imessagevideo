import json
from pathlib import Path
from PIL import Image
import numpy as np
root=Path('/tmp/sidehoe-optical-path').read_text()
draft=Path(root)/'project/scene.json'
scene=json.loads(draft.read_text())
t=scene['tracks']
orig=Path('/tmp/sidehoe-hyperframes.wG3QA2')
marks=json.loads((Path(root)/'sofia-landmarks.json').read_text())
read=lambda f:np.array(Image.open(orig/'source-stage'/f'{f:06}.png').convert('RGB'),dtype=np.int16)
shutters={333:(2.0,3.5),334:(3.5,6),335:(7,10),336:(12,16),337:(10,16),338:(8,14),339:(6,11),340:(2,4),341:(0,0)}
def interp(name,f):
 keys=np.asarray(t[name])
 return np.array([np.interp(f,keys[:,0],keys[:,j]) for j in range(1,keys.shape[1])])
def smooth01(f,a,b):
 p=np.clip((f-a)/(b-a),0,1)
 return p*p*(3-2*p)
data=[]
camera=[]
keyboardtrack=[]
for f,x,y,s in t['sofiaMeasuredCamera']:
 if f<320 or f>351:
  camera.append([f,x,y,s])
  continue
 mark, old=marks[str(f)]
 a=read(f)
 rows=a[:,420:581].mean(axis=(1,2))
 if f<=336:
  hull=np.flatnonzero(rows[:max(18,int(y+60))]<185)
  if hull.size:
   y=float(hull[0]) if f<336 else -2.0
 # Foreground edge thickness during the push includes an optical streak.
 if 335<=f<=339 and all(mark[0]):
  xnew=mark[0][0][0]
  right=mark[0][1][1]
  snew=(right-xnew)/400
  x=.71*x+.29*xnew
  s=.71*s+.29*snew
 camera.append([f,round(x,3),round(y,3),round(s,6)])
 att=t['sofiaKeyboardY']
 r,g,b=a[:,340:650,:].transpose(2,0,1)
 tray=((r>185)&(r<227)&(b-r>=3)&(b-r<29)).mean(1)
 wanted=int(np.interp(f,[320,326,331,335,338,341,346,353],[557,636,676,709,756,805,828,838]))
 q=np.flatnonzero((tray>.65)&(np.abs(np.arange(1000)-wanted)<41))
 components=[q for q in np.split(q,np.flatnonzero(np.diff(q)>1)+1) if q.size>=4]
 ky=min(components,key=lambda q:abs(int(q[0])-wanted))[0]-1 if components else wanted
 keyboardtrack.append([f,round(float((ky-y)/s),3)])
 history=0
 if mark[3] and f<=340:
  push=smooth01(f,331,341)
  history=(mark[3][1]-y)/s-(178+13*push)
 elif f<=346 and len(mark[4])>=2:
  push=smooth01(f,331,341)
  history=(mark[4][0][1]-y)/s-(239+12*push)
 heading=np.clip((mark[1]-y)/s,115,167) if mark[1] and f<=339 else 137
 sx,sy=shutters.get(f,(0,0))
 data.append([f,*[round(float(k),3) for k in (history,heading,sx,sy)]])
t['sofiaPlateRegistration']=data
t['sofiaMeasuredCamera']=camera
t['sofiaKeyboardY']=sorted([[*row] for row in t['sofiaKeyboardY'] if not 320<=row[0]<=351]+keyboardtrack)
sweep=json.loads((Path(root)/'calendar-exposure.json').read_text())
expo=[]
for f,incoming in sweep.items():
 f,yt,ht,yb,hb,blur,ab,av,_=incoming
 if f<400: # The lower tails extend out of the raster during the first three frames.
  ht=138
  hb=88
 # Convert effective sampled opacity to local paint alpha before the calendar fade.
 camera_opacity=interp('calendarArrivalOpacity',int(f))[0]
 expo.append([f,yt,ht,float(np.clip(ab/camera_opacity*255,0,255)),yb,hb,float(np.clip(av/camera_opacity*255,0,255)),blur])
for f in (418,419,420):
 y0,h=interp('calendarCamera',f)[1:]
 blue=y0+h*interp('calendarLisa',f)[0]
 violet=y0+h*interp('calendarMarie',f)[0]
 last=expo[-1]
 fade=(420-f)/3
 expo.append([f, float(blue*(1-fade)+(371.25-(f-418)*.8)*fade),
              float(1.5*h*(1-fade)+137*fade),float(92+5*fade),
              float(violet*(1-fade)+(450.3-(f-418)*.75)*fade),
              float(1.01*h),float(92+18*fade),.85])
t['calendarAppointmentExposure']=expo
draft.write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n')
