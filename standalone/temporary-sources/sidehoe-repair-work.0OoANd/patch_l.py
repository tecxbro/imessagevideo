from pathlib import Path
import json
import numpy as np
from phones import load, runs

project=Path('sidehoe-skill-trial/repair/project')
scene_path=project/'scene.json'
scene=json.loads(scene_path.read_text())
tracks=scene['tracks']
controls=[]
pointer=[]
keyboard=[]
for f,x,y,s in tracks['followMeasuredCamera']:
    frame=load('source',f)
    center=y+447.5*s
    if f>=650:
        start_x=max(0,round((x+143*s)/2-17))
        end_x=min(500,round((x+212*s)/2+14))
        start_y=max(0,round(center/2-23))
        end_y=min(500,round(center/2+28))
        rgb=frame[start_y:end_y,start_x:end_x]
        r,g,b=rgb.transpose(2,0,1)
        _,cols=np.where((r>155)&(b>190)&(r-g>6)&(b-g>14))
        rows=np.flatnonzero(((r>155)&(b>190)&(r-g>6)&(b-g>14)).sum(axis=1)>max(3,r.shape[1]*.13))
        if len(rows)>=4 and len(cols)>20:
            target=2*start_y+rows[0]+rows[-1]
            delta=np.clip((target-center)/s,-26,33)
        else:
            delta=controls[-1][1] if controls else 0
        if f in (673,674,675,676):
            delta=0
        delta=round(float(delta),2)
    else:
        delta=0
    controls.append([f,delta])
    # Vertical keyboard origin from the transition to a broad, gray top border.
    trial=y+(543+delta)*s
    xl=max(0,round((x+40*s)/2))
    xr=min(500,round((x+360*s)/2))
    luma=np.median(frame[:,xl:xr].mean(2),axis=1)
    guess=round(trial/2)
    top,bottom=max(3,guess-19),min(497,guess+25)
    diffs=np.array([luma[i-3:i].mean()-luma[i:i+4].mean() for i in range(top,bottom)])
    kdelta=delta
    if len(diffs) and np.max(diffs)>8:
        row=top+int(np.argmax(diffs))
        kdelta=round(float(np.clip((row*2-y)/s-543,-27,33)),2)
    keyboard.append([f,kdelta])

for f in range(624,675):
    a=load('source',f)
    # Dark isolated pointer only on the clear background beside the small phone.
    if f>661:
        break
    zone=a[55:385,385:499].max(axis=2)<105
    rows,cols=np.where(zone)
    if len(cols) and len(cols)<130:
        tip=int(np.argmin(rows))
        pointer.append([f,int(2*(cols[tip]+385)),int(2*(rows[tip]+55))])
tracks['followChipOffset']=controls
tracks['followKeyboardOffset']=keyboard
tracks['isolatedFollowPointer']=pointer
print('chip',controls[25::4]);print('keyboard',keyboard[::4]);print('pointer',pointer)
# Fit two line-ink bounds and two component veil over the editable handset.
lines=[[],[]]
for track in tracks['assistantMeasuredPosition']:
    f,x,y,width=track
    a=load('source',f)
    if f>=139:
        left,right=123,377
        upper,lower=36,round(y/2)-12
        luma=a[upper:lower,left:right].max(2)
        row_spans=runs(np.count_nonzero(luma<161,axis=1)>7)
        if 1<=len(row_spans)<=3 and f<=160:
            for j,(start,end) in enumerate(row_spans[:2]):
                _,cols=np.where(luma[start:end]<160)
                if len(cols) and end-start>=8:
                    lines[j].append([f,int(2*(left+cols.min())),int(2*(upper+start)),int(2*(cols.max()-cols.min()+1)),int(2*(end-start))])
    if f>=152:
        track[2]-=min(15,(f-151)*1.7)
# Measure the closing source positions and keep the transition exposed through frame 160.
for j in range(2):
    print('assistant lines',j,lines[j])
    tracks[f'assistantLine{j+1}']=lines[j]
scene_path.write_text(json.dumps(scene,indent=2,ensure_ascii=False)+'\n')

p=project/'render.py'
s=p.read_text()
s=s.replace('''        start=self.at("personal.line-one")''','''        start=self.at("personal.line-one")
        prefix_age=f-start''',1)
s=s.replace('''        if f<167:
            sizes=(3,7,10,14,17)
            visible=min(len(line1),sizes[f-start])''','''        if prefix_age<0:
            pass
        elif prefix_age<5 and line1:
            sizes=(3,7,10,14,17)
            visible=min(len(line1),sizes[prefix_age])''',1)
s=s.replace('''        plate=self.thread_plate("follow",f,543)''','''        keyboard_shift,=self.track("followKeyboardOffset",f)
        plate=self.thread_plate("follow",f,543+round(keyboard_shift))''',1)
s=s.replace('''        self.chip(plate,45,433,72,29,self.c["follow"][4],False,.58+.42*a,a)
        left,top,width,height=contact["yesRect"]''','''        chip_shift,=self.track("followChipOffset",f)
        self.chip(plate,45,433+chip_shift,72,29,self.c["follow"][4],False,.58+.42*a,a)
        left,top,width,height=contact["yesRect"]
        top+=chip_shift''',1)
s=s.replace('''        local=f-self.at("follow.yes-contact")''','''        pointer=self.s["tracks"]["isolatedFollowPointer"]
        if pointer and pointer[0][0]<=f<=pointer[-1][0]:
            cx,cy=interpolate(pointer,f)
        local=f-self.at("follow.yes-contact")''',1)
s=s.replace('''        amount = round(42*tint)
        if amount:
            overlay = wash(amount).convert("RGB")
            im.paste(ImageChops.multiply(im.convert("RGB"), overlay))
        title_y, = self.track("assistantTitleY", f)
        title = layer()
        for j, line in enumerate(self.c["assistant"]):
            gentle_characters(title,line,500,title_y+j*75,60,640,f,134+j*4,.20)
        composite(im,title,0,0,1-tween(f,157,161))''','''        if tint:
            im.alpha_composite(handset_veil(round(tint*100)))
        title_y,=self.track("assistantTitleY", f)
        for j,line in enumerate(self.c["assistant"]):
            first=141 if j==0 else 143
            if first<=f<=160:
                fit_ink(im,line,self.track(f"assistantLine{j+1}",f),640,
                        1,2*tween(f,158,161))
            elif f<first:
                title=layer()
                gentle_characters(title,line,500,title_y+j*75,60,640,f,134+j*4,.20)
                composite(im,title,0,0)''',1)
anchor='''def vertical_blur(image, length):'''
s=s.replace(anchor, '''@lru_cache(maxsize=28)
def handset_veil(strength):
    yy,xx=np.mgrid[0:1:200j,0:1:200j]
    pink=np.exp(-((xx-1.13+1.2*(yy-1.03))/.72)**2-((yy-1.06)/.36)**2)
    haze=np.exp(-((xx-.54-.44*(yy-1.03))/.62)**2-((yy-1.05)/.25)**2)
    weight=np.clip(pink*.86+haze*.43,0,.95)
    rgb=np.zeros((200,200,4),dtype=np.uint8)
    rgb[:,:,:3]=np.stack((225+17*haze,124+71*haze,228+21*haze),axis=2)
    rgb[:,:,3]=np.rint(weight*2.55*strength).astype(np.uint8)
    return Image.fromarray(rgb).resize((SIZE,SIZE),Image.Resampling.BICUBIC)


'''+anchor,1)
p.write_text(s)
