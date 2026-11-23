from pathlib import Path
from copy import deepcopy
import json,sys
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
p=root/'project/scene.json'
s=json.loads(p.read_text())
by_frame=s['followSettledRegistration']
profile=by_frame['631']
fits=json.loads((root/'measure-probe-a.json').read_text())
optics={}
for f in range(624,631):
    x,y,z=interpolate(s['tracks']['followMeasuredCamera'],f)
    dest_bottom=fits[str(f)][0]['bottom'][1]
    factor=max(.97,min(1.025,(dest_bottom+1.5-y)/(827*z)))
    casing_trail,case_focus,screen_trail,screen_focus=[
        [95,4.1,103,3.3],
        [48,2.2,47,3.25],
        [18,1.5,27,2.5],
        [10,1.12,15,1.9],
        [6,1.08,9,1.5],
        [3,.85,5,1.02],
        [3,.82,4,.95],
    ][f-624]
    optics[str(f)]=[round(factor,5),casing_trail,case_focus,screen_trail,screen_focus]
    if f==624:
        continue
    shape=deepcopy(profile)
    shape['coverage']=1
    step=fits[str(f)][0]
    # Screen positions are solved against observed visible rows. Top cropping
    # at f625 is carried into the color field without shortening the bubble.
    def local_y(stage):
        return round((stage-y)/(z*factor),3)
    if step['blue']:
        left,top,right,bottom=step['blue']
        shape['blue'][0]=[round((left-x)/z,3),
                          local_y(bottom)-55,
                          round((right-x)/z,3),
                          local_y(bottom)]
    for idx,(first,last) in enumerate(step['bubs'][:2]):
        box,lines=shape['bubbles'][idx]
        shift=local_y(first)-box[1]
        box[1]=local_y(first)
        box[3]=local_y(last)
        for line in lines:
            line[1]=round(line[1]+shift,3)
    tray=local_y(step['trayY']) if step['trayY'] is not None else shape['layout'][0]
    difference=tray-shape['layout'][0]
    shape['layout'][0]=tray
    shape['composerY']=round(shape['composerY']+difference,2)
    for row in shape['layout'][1]:
        row[1]=round(row[1]+difference,3)
    shape['layout'][2]=round(shape['layout'][2]+difference,3)
    by_frame[str(f)]=shape
s['followEntryOptics']=optics
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
