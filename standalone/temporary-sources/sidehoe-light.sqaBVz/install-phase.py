from pathlib import Path
import json,sys
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
base=Path('/Users/darshan/Documents/ChatGPT/imessage-video/sidehoe-skill-trial/sofia-and-title-review/project/scene.json')
old=json.loads(base.read_text())
s=json.loads(base.read_text())
def apply(track,sequence):
    readings={row[0]:row[1:] for row in old['tracks'][track]}
    for f,v in sequence.items():
        readings[f]=v
    s['tracks'][track]=[[f,*v] for f,v in sorted(readings.items())]
follow=json.loads(Path('/tmp/sidehoe-sofia.fuoOwt/follow-entry-fit.json').read_text())
for key,index in [('followMeasuredCamera',(0,3)),('followKeyboardY',(3,4)),('followExposure',(4,5)),
                  ('followMessageLift',(5,6)),('followLowerLift',(6,7))]:
     a,b=index
     # Freeze the control frames just outside the revised window.
     rows={f:values[a:b] for f,_,_,__,values in follow}
     rows.update({f:interpolate(old['tracks'][key],f) for f in [623,631]})
     apply(key,rows)
light=json.loads(Path('/tmp/sidehoe-sofia.fuoOwt/veil-fit.json').read_text())
for key,(a,b) in [('assistantLighting',(0,16)),('assistantWashResponse',(16,18))]:
    rows={f:values[a:b] for f,_,__,values in light}
    rows[154]=interpolate(old['tracks'][key],154)
    apply(key,rows)
(root/'project/scene.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
