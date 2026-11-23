import json, math
from pathlib import Path
import numpy as np
root=Path('/tmp/sidehoe-optical-path').read_text()
p=Path(root)/'project/scene.json'
s=json.loads(p.read_text())
t=s['tracks']
def track(name,f):
 a=np.array(t[name]);return [np.interp(f,a[:,0],a[:,i]) for i in range(1,a.shape[1])]
def read(name):return json.loads((Path(root)/name).read_text())
dates=[]
for key,d in read('calendar-date.json').items():
 f,cx,cy,sx,sy,mass,*_=d
 _,_,h=track('calendarCamera',f)
 steady=h*.335
 if f<=399:
   rx,ry=(27.5,22.0) if f==397 else (29,26)
 else:
   rx=max(27.5,steady)
   ry=rx
 alpha= min(1,mass/(math.pi*rx*ry*183)*1.12)
 blurx=math.sqrt(max(.3,sx*sx-(rx/2)**2))
 blury=math.sqrt(max(.3,sy*sy-(ry/2)**2))
 heading=float(np.interp(f,[397,398,399,400,401,403],[.15,.65,.72,.82,.92,1]))
 dates.append([f,*[round(float(d),3) for d in (cx,cy,rx,ry,alpha,blurx,blury,heading)]])
for f in range(416,420):
 x,y=track('calendarDay',f)
 _,_,h=track('calendarCamera',f)
 dates.append([f,float(x),float(y),h*.335,h*.335,1,.75,.75,1])
t['calendarDateExposure']=dates
t['calendarCursorVisibility']=[[397,0],[398,.26],[399,.68],[400,.91],[401,.96],[402,1],[404,1]]
shots=read('calendar-outgoing.json')
for i,key in enumerate(('sendReplyBox','sendSuggestionBox')):
 new=[]
 for f in range(390,403):
  x,y,x1,b=track(key,f)
  a,bottom,*_=shots[str(f)][i]
  if 393<=f<=401:
   x-=4 if i==0 else 5
   x1+=2 if i==0 else 6
  new.append([f,float(x),a,float(x1),bottom])
 t[key]=[row for row in t[key] if row[0]<390]+new
t['sendExitExposure']=[[390,.38,1],[393,.52,1.35],[395,.65,1.75],[396,.9,2.45],[397,1.1,3.16],[398,1.2,3.45],[399,1.25,3.8],[400,1.4,4.7],[401,1.5,5.5],[402,1.65,6.5]]
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
