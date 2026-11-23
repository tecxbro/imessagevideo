from pathlib import Path
import json
from phones import load, rim, track, SCENE
import numpy as np
p=Path('sidehoe-skill-trial/repair/project')
s=json.loads((p/'scene.json').read_text())
t=s['tracks']
for key,a,b in [('sofia',313,355),('follow',624,695)]:
    frames=[]
    for f in range(a,b+1):
        old_y,old_s=track(key+'Camera',f)
        source=load('source',f)
        border=rim(source,key,f)
        x=500-200*old_s
        new_s=old_s
        if border:
            l,r,top,bottom,_=border
            measured=(r-l)/200
            if abs(measured-old_s)<.33:
                x=l*2
                new_s=measured
        if key=='follow':
            contact=s['followContact']['phoneReframeY']
            shift=np.interp(f,[pair[0] for pair in contact],[pair[1] for pair in contact])
            old_y+=shift
        y=old_y
        if border:
            if key=='sofia' and 316<=f<=318 and bottom and bottom>270:
                y=2*bottom-825*new_s
            elif key=='follow' and 626<=f<=629 and bottom and bottom>310:
                y=2*bottom-825*new_s
            elif ((key=='sofia' and 319<=f<=335) or (key=='follow' and 630<=f<=659)) and top is not None:
                if abs(2*top-old_y)<46:
                    y=2*top
            elif key=='follow' and f>=660:
                # Keep the interior send target consistent while refitting the rim.
                y=old_y+(old_s-new_s)*447
            elif key=='sofia' and 336<=f<=355:
                y=old_y+(old_s-new_s)*420
        if key=='follow' and 674<=f<=676:
            x,y,new_s=500-200*old_s,old_y,old_s
        frames.append([f,round(float(x),3),round(float(y),3),round(float(new_s),5)])
    t[key+'MeasuredCamera']=frames
t['calendarCamera']=[[397,190,803,82],[398,190,833,82],[399,190,803,82],[400,190,765,82],
                      [401,190,707,82],[402,190,631,82]]+t['calendarCamera'][1:]
t['calendarDay']=[[397,154,925],[398,355,896],[399,456,836],[400,517,767],[401,560,666],
                   [402,591,566],[403,616,494],[404,637,434]]+t['calendarDay']
t['calendarArrivalOpacity']=[[397,.83],[398,.86],[399,.88],[400,.9],[401,.94],[404,1],[405,1]]
t['calendarArrivalSmear']=[[397,72],[398,41],[399,24],[400,17],[401,11],[402,8],[404,3],[408,0]]
t['sofiaExposure']=[[313,122],[314,118],[315,106],[316,86],[317,59],[318,47],[319,35],[320,20],[322,0]]
t['followExposure']=[[624,121],[625,127],[626,114],[627,98],[628,78],[629,55],[630,27],[631,21],[633,0]]
(p/'scene.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
f=p/'render.py';v=f.read_text()
a=v.index('    def suggestion_group')
v=v[:a]+'''    def expose_phone(self, im, plate, x, y, scale, smear, radius, alpha=1):
        if smear > 1:
            pad = math.ceil(smear/2)+4
            padded = layer(plate.width, plate.height+2*pad)
            padded.alpha_composite(plate,(0,pad))
            plate = vertical_blur(padded,smear)
            y -= pad*scale
        composite(im,blur(plate,radius),x,y,alpha,scale)

'''+v[a:]
v=v.replace('p=tween(f,self.at("sofia.suggestion"),340)','onset=self.at("sofia.suggestion")\n        p=tween(f,onset-3,340) if f>=onset else 0')
v=v.replace('composite(im,small,178+(1-p)*18,420+(1-p)*19,p,.88+.12*p)','''landing_y = mix(375,420,tween(f,onset,340))
            composite(im,small,178+(1-p)*18,landing_y+(1-p)*19,p,.88+.12*p)''')
v=v.replace('        y,s=self.track("sofiaCamera",f)\n        x=500-200*s','        x,y,s=self.track("sofiaMeasuredCamera",f)')
v=v.replace('            trail = 93*(1-tween(f,313,319))\n            composite(im,vertical_blur(blur(plate,entrance+push),trail),x,y,a,s)',
'''            trail, = self.track("sofiaExposure",f)
            self.expose_phone(im,plate,x,y,s,trail,entrance+push,a)''')
v=v.replace('        x,y,r=self.track("calendarCursor",f)\n        cursor(cal,x,y,r,tween(f,402,405),.98)','''        x,y,r=self.track("calendarCursor",f)
        cursor(cal,x,y,r,tween(f,398,405),.98)''')
v=v.replace('        composite(im,blur(cal,4.5*(1-tween(f,398,410))+2*tween(f,472,479)),\n                  0,0,tween(f,397,405)*(1-tween(f,477,482)))',
'''        a, = self.track("calendarArrivalOpacity",f)
        smear, = self.track("calendarArrivalSmear",f)
        if smear:
            cal = vertical_blur(cal,smear)
        composite(im,blur(cal,4.5*(1-tween(f,398,410))+2*tween(f,472,479)),
                  0,0,a*(1-tween(f,477,482)))''')
v=v.replace('''        y,s=self.track("followCamera",f)
        x=500-200*s
        contact=self.s["followContact"]
        y_shift,=interpolate(contact["phoneReframeY"],f)
        y+=y_shift''','''        x,y,s=self.track("followMeasuredCamera",f)
        contact=self.s["followContact"]''')
v=v.replace('''        a=tween(f,self.at("follow.no")-1,653)
        b=tween(f,self.at("follow.yes")-1,654)''','''        no_frame=self.at("follow.no")
        yes_frame=self.at("follow.yes")
        a=mix(.79,1,tween(f,no_frame,653)) if f>=no_frame else 0
        b=mix(.72,1,tween(f,yes_frame,654)) if f>=yes_frame else 0''')
v=v.replace('''        exposed = blur(plate,6*(1-tween(f,624,633))+2.5*max(0,1-abs(f-665)/7)+3*tween(f,690,696))
        composite(im,vertical_blur(exposed,102*(1-tween(f,624,630))),x,y,1,s)''','''        trail, = self.track("followExposure",f)
        softness=5*(1-tween(f,624,633))+2.2*max(0,1-abs(f-665)/7)+3*tween(f,690,696)
        self.expose_phone(im,plate,x,y,s,trail,softness)''')
f.write_text(v)
