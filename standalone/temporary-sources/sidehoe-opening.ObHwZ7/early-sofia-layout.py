from pathlib import Path
from PIL import Image
from copy import deepcopy
import json,sys,numpy as np
p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import interpolate
f=p/'project/scene.json'
s=json.loads(f.read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
observations=json.loads((p/'sofia-measured.json').read_text())
template=s['threadRegistration']['sofia']['329']
edited={}
for f0 in range(319,329):
    q=observations[str(f0)][0]
    stage=np.asarray(Image.open(source/f'{f0:06}.png').convert('RGB'),dtype=np.int16)
    lum=stage.mean(2)
    expected=interpolate(s['tracks']['sofiaMeasuredCamera'],f0)
    xx,yy,zz=expected
    outer=[q['rails'][0]['240'][0][0],q['rails'][1]['240'][0][1]]
    left, right = q['rails'][0]['221'][0][1]+1,q['rails'][1]['221'][0][0]-1
    z=(outer[1]-outer[0]-3)/400
    y=q['top']-.4
    top=q['tray']-1
    ramps=[]
    for i,j in ((outer[0]-7,left+7),(right-7,outer[1]+7)):
        luma=np.rint(np.median(lum[240:570,i:j+1],axis=0)).astype(int)
        ramps.append([i,j,luma.tolist()])
    k=.98+(z-1)*.95
    pitch=round((right-left)/10.04,3)
    measures=q['keys']
    rows=[]
    for j,length in enumerate((10,9,7)):
        ypos=top+(12+j*51.4)*z
        x=left+(4+j*17)*z
        if j==2:
            x=left+63*z
        if j<len(measures):
            span,bars=measures[j]
            if len(bars)>=length and 27<span[1]-span[0]<60 and abs(span[0]-ypos)<20:
                ypos=span[0]
                x=bars[1 if j==2 else 0][0]
        rows.append([round(x-.8,3),round(ypos-.7,3),pitch,round(pitch*.85,3),round(pitch*1.078,3),length])
    utility=round(top+163*z)
    if f0>=325 and len(measures)>=4:
        utility=measures[3][0][0]-2
    colors=np.rint(np.median(stage[top+2:top+6,461:545,:],axis=(0,1))).astype(int)
    colors=np.clip(colors,210,230).tolist()
    outgoing,follow=q['cyan'][:2]
    def cap_rect(rect,text_offset=.44):
        x0,y0,x1,y1=rect;w,h=x1-x0,y1-y0
        return [x0+h*text_offset,y0+h*.36,w-h*.90,h*.30]
    upperx,uppery,endx,endy=outgoing
    sample=np.median(stage[uppery+7:uppery+13,upperx+30:upperx+58],axis=(0,1))
    bubbles=[]
    for i,(l,t,r,b) in enumerate(q['received']):
        ink=q['ink'][i] if i<len(q['ink']) else None
        if ink is None:
            ink=[l+15,t+9,min(r-12,l+(164 if i==0 else 255)*z),t+22]
        il,it,ir,ib=ink
        bubbles.append([[l-2,t-1,r+1,b+1],[[il-.5,it-.8,ir-il+1,ib-it+2]]])
    if len(bubbles)!=2:
        continue
    head=q['chrome'][-1][1]
    footer_y=round(utility+round(z*87))
    house=None
    if f0==319:
        home_values=[]
        upper=round(y+z*784)
        lower=min(999,round(y+z*824))
        for j in range(upper,lower):
            if (lum[j,438:560]<125).sum()>87:
                home_values.append(j)
        if home_values:
            house=[round(500-z*65),min(home_values),round(500+z*65),max(home_values)]
    screen_focus=([0,0,1.65],[0,0,1.35],[0,0,1.15],[0,0,1.08],[0,0,.94],[0,0,.86],[0,0,.80],[0,0,.74],[0,0,.72],[0,0,.69])[f0-319]
    today=(q['today'] or [486,bubbles[-1][0][3]+25,515,bubbles[-1][0][3]+33])
    today_y=max(today[1]-2,bubbles[-1][0][3]+21)
    edited[str(f0)]=dict(rails=[left,right],keys=[top,colors,rows],items=bubbles,today=[486,today_y,29*z,8.4*z],
        blue=outgoing,blueInk=cap_rect(outgoing),bluePaint=np.rint(sample).astype(int).tolist(),
        edgeRamps=ramps,corners=[18*z,18*z],focus=screen_focus,
        railSpan=[round(y+z*40),round(y+z*88),round(y+z*(827-87)),round(y+z*(827-38))],
        casing=[outer[0]+.45,y,z,round((head-y)/z),max(0,2.8-(f0-319)*.72),max(.60,2.55-(f0-319)*.38)],
        utilityRow=[utility,round(z*41)],keyboardFooter=[footer_y,house],earlierReply=[follow,cap_rect(follow,.33)])
s['threadRegistration']['sofia'].update(edited)
f.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
