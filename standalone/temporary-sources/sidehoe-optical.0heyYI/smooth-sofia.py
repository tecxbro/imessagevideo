import json
from pathlib import Path
import numpy as np
scratch=Path(Path('/tmp/sidehoe-optical-path').read_text())
project=scratch/'project/scene.json'
baseline=Path('sidehoe-skill-trial/hyperframes-review/project/scene.json')
scene=json.loads(project.read_text())
old=json.loads(baseline.read_text())['tracks']
t=scene['tracks']
def blend(f):
 u=float(np.clip((f-330)/5,0,1))
 return u*u*(3-2*u)
def interp(arr,f,j):
 a=np.asarray(arr)
 return np.interp(f,a[:,0],a[:,j])
for key in ('sofiaMeasuredCamera','sofiaKeyboardY'):
 for row in t[key]:
  f=row[0]
  if 320<=f<=334:
   weight=blend(f)
   row[1:]=[round(float(v*weight+interp(old[key],f,i)*(1-weight)),6) for i,v in enumerate(row[1:],1)]
for row in t['sofiaPlateRegistration']:
 f,hdr,heading,sx,sy=row
 weight=blend(f)
 row[1:]=[round(hdr*weight,3),round(137+(heading-137)*weight,3),round(sx*.77,3),round(sy*.77,3)]
project.write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n')
