from pathlib import Path
import json
import numpy as np
from phones import load, runs

project=Path('sidehoe-skill-trial/repair/project')
scene_path=project/'scene.json'
scene=json.loads(scene_path.read_text())
t=scene['tracks']
for j,mid in enumerate((146,250,350)):
    track=[]
    for f in range(10):
        rgb=load('source',f)[216:335,mid-37:mid+37]
        lo,hi=rgb.min(2),rgb.max(2)
        coordinates=np.argwhere((hi-lo>12)&(lo<215))
        if len(coordinates)<20:
            continue
        a,b=np.percentile(coordinates,[1,99],axis=0)
        x,y,d=np.rint([b[1]+a[1]+2*(mid-37),b[0]+a[0]+432,2*max(b-a)+6]).astype(int)
        track.append([f,int(x),int(y),int(d),1 if f>=3 else .89])
    t[f'inboxIntroPin{j}']=track

scroll=[]
seeds=[[42,-65],[49,-204],[52,-327],[54,-468],[56,-668],[58,-876],[60,-1022],
       [62,-1124],[68,-1310],[82,-1388],[95,-1363],[100,-1220],[101,-1210]]
for f in range(42,102):
    a=load('source',f)[:,70:109]
    r,g,b=a.transpose(2,0,1)
    mask=(b-r>40)&(g-r>19)&(b>105)
    groups=runs(mask.sum(1)>=2)
    centers=np.array([lo+hi for lo,hi in groups if hi-lo in range(3,24)])
    seed=np.interp(f,*zip(*seeds))
    scale=np.interp(f,[42,57,79,100,101],[.986,1.009,1.002,.961,.9])
    guess=np.array([seed+(752+i*171)*scale for i in range(9)])
    choices=[(np.argmin(np.abs(guess-y)),y) for y in centers if np.min(np.abs(guess-y))<55]
    if len(choices)>1:
        shifts=[y-guess[i] for i,y in choices]
        y=seed+np.median(shifts)
    else:
        y=seed
    scroll.append([f,round(float(y),2),round(float(scale),4)])
t['inboxIdentifiedRowPose']=scroll
t['inboxScrollSmear']=[[42,0],[48,4],[49,7],[50,13],[52,26],[54,31],[55,33],
                      [56,40],[57,41],[58,38],[59,33],[60,28],[61,21],[62,14],
                      [64,6],[69,0],[101,3]]
t['inboxIntroHeader']=[[0,.72,9,39],[1,.88,4,22],[2,1,3,10],[4,1,2,0],[9,1,0,0]]
for row in t['identityMeasuredBox']:
    if row[0]==103:
        row[2]=501
        row[3:]=[308,304]
    if row[0]==104:
        row[2]=500
        row[3:]=[296,293]
for row in t['closingMeasuredBox']:
    if row[0]==696:
        row[2]=501
    elif row[0]==698:
        row[2]=502
t['badgeClosingHighlights']=[[696,75],[697,62],[698,41],[699,24],[701,0],[765,0]]
for row in t['clusterPose']:
    f=row[0]
    if f>=249:
        row[1]+=int(np.interp(f,[249,253,254,255,256,257,258],[0,-48,-66,-108,-84,-93,-73]))
t['assistantWash']=[[134,0],[137,.025],[139,.045],[141,.13],[145,.31],[149,.57],
                    [153,.85],[156,1],[161,1]]
scene_path.write_text(json.dumps(scene,indent=2,ensure_ascii=False)+'\n')
p=project/'render.py'
s=p.read_text()
s=s.replace('''        for j,((label,key),x) in enumerate(zip(self.s["inboxPins"],[169,411,651])):
            p=tween''','''        for j,((label,key),x) in enumerate(zip(self.s["inboxPins"],[169,411,651])):
            if f<10:
                continue
            p=tween''',1)
s=s.replace('''        p=tween(f,4,11)
        if p>0:''','''        p=tween(f,2.5,8) if f<10 else tween(f,4,11)
        tag=None
        if p>0:''',1)
s=s.replace('''            composite(i,tag,285,373+(1-p)*22,p)''','''            if f>=10:
                composite(i,tag,285,373+(1-p)*22,p)''',1)
s=s.replace('''        composite(i,rows,0,0,tween(f,2,10))''','''        composite(i,rows,0,0,tween(f,-.5,9) if f<10 else 1)''',1)
s=s.replace('''            measured,=self.track("inboxMeasuredScroll",f)
            y=mix(y,measured,tween(f,42,47)*.86)
            scroll_streak,=self.track("inboxScrollSmear",f)
        composite(im,vertical_blur(blur(i,amount),scroll_streak),500-410*scale,y,1,scale)''','''            y,scale=self.track("inboxIdentifiedRowPose",f)
            scroll_streak,=self.track("inboxScrollSmear",f)
        composite(im,vertical_blur(blur(i,amount),scroll_streak),500-410*scale,y,1,scale)
        if f<10:
            for j,(label,key) in enumerate(self.s["inboxPins"]):
                pin=self.s["tracks"][f"inboxIntroPin{j}"]
                if f<pin[0][0]:
                    continue
                x,cy,diam,opacity=interpolate(pin,f)
                avatar_layer=layer(225,234)
                self.avatar(avatar_layer,key,112,108,diam,opacity)
                if f>=3:
                    text(ImageDraw.Draw(avatar_layer),112,109+diam/2+15,label,25,INK,530,"center")
                composite(im,blur(avatar_layer,max(0,5-f*1.10)),x-112,cy-108)
            if tag is not None:
                composite(im,blur(tag,5*(1-p)),387,cy-157,p,.91)''',1)
s=s.replace('''        a=tween(f,102,105)
        amount=6*tween(f,129,133)''','''        a=up(f,101.7,104.4)
        amount=max(5*(1-tween(f,102,105)),6*tween(f,129,133))''',1)
s=s.replace('''        body = blur(beneath,3.8*(1-tween(f,134,139))+4*tween(f,158,161))''','''        body = blur(beneath,7*(1-tween(f,134,139))+5*tween(f,158,161))
        if f==134:
            body=vertical_blur(body,17)''',1)
s=s.replace('''        composite(im,blur(cal,4.5*(1-tween(f,398,410))+2*tween(f,472,479)),
                  0,0,a*(1-tween(f,477,482)))''','''        mosaic=tween(f,476,479)
        composite(im,blur(cal,4.5*(1-tween(f,398,410))+4*mosaic),
                  0,0,a*(1-.95*mosaic)*(1-tween(f,479,482)))''',1)
s=s.replace('''            softness=(1-depth)*1.4+4*(1-tween(f,478,483))
            ox=blur(ox,softness)''','''            softness=1.7+(1-depth)*2.9+4*(1-tween(f,478,486))
            if name=="rings" and f==478:
                trim=rounded_gradient(256,256,"#eb86c9","#ffdbec",42,"x")
                composite(trim,ox,9,9,1,.93)
                ox=trim
            ox=blur(ox,softness)''',1)
s=s.replace('''                ox=vertical_blur(exposed,125*tween(f,616,621))''','''                ox=vertical_blur(exposed,84*tween(f,616,621))''',1)
s=s.replace('''        cursor(im,cx,cy,r,1,s*.59)''','''        angle=mix(18,r,tween(f,654,662))
        cursor(im,cx,cy,angle,tween(f,624,626),s*.59)''',1)
p.write_text(s)
p=project/'artwork.py'
s=p.read_text()
s=s.replace('''    im=rounded_gradient(256,256,"#414149","#282832",roundness)
    for x,y,angle,col in [(92,121,18,"#e4aec2"),(163,121,-18,"#f1b7ca"),(127,108,2,"#eccb9a")]:
        card=rounded_gradient(54,76,col,"#dba1bc",6)
        d=ImageDraw.Draw(card)
        oval(d,27,19,7,7,"#4a3a40")
        d.rounded_rectangle((10,30,44,43),5,fill="#4a3a40")
        d.rounded_rectangle((12,50,42,54),2,fill="#886379")
        d.rounded_rectangle((17,60,37,63),1,fill="#886379")''','''    im=rounded_gradient(256,256,"#343536","#30302f",roundness)
    for x,y,angle,col in [(91,126,17,"#f5c69e"),(165,126,-17,"#efb6c1"),(128,110,0,"#f6d28d")]:
        card=rounded_gradient(64,94,col,"#eb9dc8",8)
        d=ImageDraw.Draw(card)
        oval(d,32,23,8,8,"#42352f")
        d.rounded_rectangle((14,34,50,48),6,fill="#42352f")
        d.rounded_rectangle((14,57,51,62),2,fill="#a0617a")
        d.rounded_rectangle((16,69,46,73),1,fill="#a0617a")''',1)
s=s.replace('''    heart(d,128,160,59,"#63405b")
    heart(d,128,159,51,"#f5a7d6")''','''    heart(d,128,167,68,"#6a3457")
    heart(d,128,165,54,"#ffc2eb")
    heart(d,128,166,45,"#f0a6db")''',1)
s=s.replace('''"#fc377a","#fa655f"''','''"#f32e77","#fa6963"''',1)
s=s.replace('''"#69b5ff","#386cdb"''','''"#65b5ff","#367ef0"''',1)
s=s.replace('''        d.rounded_rectangle((33,32,223,68),11,fill="#6cb4ff")
        text(d,128,72,"31",144,"#fff",595,"center")''','''        d.rounded_rectangle((6,8,250,80),25,fill="#69b1fb")
        text(d,128,67,"31",157,"#fff",550,"center")''',1)
p.write_text(s)
